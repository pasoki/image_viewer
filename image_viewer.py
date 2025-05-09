import os
import json
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QLineEdit, QFileSystemModel, QTreeView, QScrollArea, QFrame,
    QGridLayout, QSplitter, QMessageBox, QFileDialog
)
from PySide6.QtGui import QPixmap, QClipboard, QFont
from PySide6.QtCore import Qt, QDir, QPropertyAnimation, QEasingCurve, QTimer
from natsort import natsorted


class ImageViewer(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("圖片描述管理工具 V7.1")
        self.resize(1400, 900)
        self.json_folder = os.path.join(os.getcwd(), "descriptions")
        os.makedirs(self.json_folder, exist_ok=True)

        self.image_folder = ""
        self.image_files = []
        self.image_descriptions = {}
        self.image_cards = {}
        self.batch_index = 0
        self.batch_size = 10

        self.setStyleSheet("""
            QWidget {
                background-color: #1e1e1e;  /* 主背景顏色：深灰色 */
                color: #f1f1f1;              /* 預設文字顏色：淺灰白 */
            }

            QLineEdit {
                background-color: #2b2b2b;  /* 輸入框背景：稍亮的深灰 */
                color: #fff;                /* 輸入文字顏色：白色 */
                border: 1px solid #555;     /* 淺灰邊框 */
                border-radius: 6px;         /* 圓角邊框 */
                padding: 4px;               /* 內距 */
            }

            QPushButton {
                background-color: #333;      /* 按鈕背景：灰黑色 */
                color: #fff;                /* 按鈕文字：白色 */
                border-radius: 6px;         /* 圓角邊框 */
                padding: 6px 12px;          /* 上下6px，左右12px 內距 */
                border: 1px solid #444;     /* 深色邊框 */
            }

            QPushButton:hover {
                background-color: #444;     /* 滑鼠懸停時加亮 */
            }

            QScrollArea {
                background-color: #1e1e1e;  /* 保持與主背景一致 */
            }

            QTreeView {
                background-color: #262626;  /* 側邊欄背景稍亮 */
                color: #ccc;                /* 淺灰文字 */
                border: none;               /* 無邊框 */
            }

            QScrollBar:vertical, QScrollBar:horizontal {
                background: #1e1e1e;        /* 滑桿軌道背景 */
                width: 10px;                /* 垂直滑桿寬度 */
                height: 10px;               /* 水平滑桿高度 */
                margin: 0px;                /* 無邊距 */
            }

            QScrollBar::handle:vertical, QScrollBar::handle:horizontal {
                background: #555;           /* 滑塊預設顏色 */
                min-height: 20px;           /* 垂直最小高度 */
                min-width: 20px;            /* 水平最小寬度 */
                border-radius: 5px;         /* 圓角滑塊 */
            }

            QScrollBar::handle:vertical:hover, QScrollBar::handle:horizontal:hover {
                background: #888;           /* 滑鼠懸停時更亮 */
            }

            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical,
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                height: 0px;                /* 隱藏上下左右按鈕 */
                width: 0px;
            }

            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical,
            QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {
                background: none;           /* 移除多餘背景 */
            }

            QLabel[name="imageLabel"] {
                background-color: #1e1e1e;  /* 背景色與整體主題一致 */
                color: #f1f1f1;              /* 淺灰白文字顏色 */
                border: none;                /* 無邊框更清爽 */
                border-radius: 0px;          /* 無圓角保持簡潔 */
                padding: 2px 4px;            /* 較小內距避免搶焦點 */
                font-size: 16pt;             /* 適中字體大小 */
                qproperty-alignment: AlignCenter;  /* 置中對齊 */
            }
        """)

        
        # 主畫面分割
        self.splitter = QSplitter()
        self.splitter.setHandleWidth(1)

        # 側邊欄
        self.sidebar = QWidget()
        self.sidebar_layout = QVBoxLayout(self.sidebar)

        self.path_input = QLineEdit()
        self.path_input.setPlaceholderText("輸入資料夾路徑後按 Enter")
        self.path_input.returnPressed.connect(self.jump_to_path)

        self.folder_model = QFileSystemModel()
        self.folder_model.setRootPath(QDir.rootPath())
        self.folder_model.setFilter(QDir.AllDirs | QDir.NoDotAndDotDot)

        self.folder_tree = QTreeView()
        self.folder_tree.setModel(self.folder_model)
        self.folder_tree.setHeaderHidden(True)
        self.folder_tree.setColumnWidth(0, 250)
        self.folder_tree.clicked.connect(self.load_images_from_index)

        self.sidebar_layout.addWidget(self.path_input)
        self.sidebar_layout.addWidget(self.folder_tree)

        # 圖片展示區
        self.scroll_area = QScrollArea()
        self.scroll_widget = QWidget()
        self.grid_layout = QGridLayout(self.scroll_widget)
        self.grid_layout.setSpacing(20)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.scroll_widget)

        # 工具列
        self.toggle_button = QPushButton("≡ 資料夾")
        self.toggle_button.clicked.connect(self.toggle_sidebar)

        self.loadjson_button = QPushButton("載入 JSON")
        self.loadjson_button.clicked.connect(self.load_json_file)

        self.save_button = QPushButton("儲存描述")
        self.save_button.clicked.connect(self.save_descriptions)

        self.clear_button = QPushButton("清空所有描述")
        self.clear_button.clicked.connect(self.clear_descriptions)

        toolbar = QHBoxLayout()
        toolbar.addWidget(self.toggle_button)
        toolbar.addWidget(self.loadjson_button)
        toolbar.addWidget(self.save_button)
        toolbar.addWidget(self.clear_button)
        toolbar.addStretch()

        # 主畫面右側
        right_side = QWidget()
        right_layout = QVBoxLayout(right_side)
        right_layout.addLayout(toolbar)
        right_layout.addWidget(self.scroll_area)

        self.splitter.addWidget(self.sidebar)
        self.splitter.addWidget(right_side)
        self.splitter.setSizes([250, 1150])

        main_layout = QHBoxLayout(self)
        main_layout.addWidget(self.splitter)
        self.setLayout(main_layout)

        # 側邊欄動畫
        self.sidebar_animation = QPropertyAnimation(self.sidebar, b"maximumWidth")
        self.sidebar_animation.setDuration(300)
        self.sidebar_animation.setEasingCurve(QEasingCurve.InOutQuad)
        self.sidebar_expanded = True

    def toggle_sidebar(self):
        if self.sidebar_expanded:
            self.sidebar_animation.setStartValue(self.sidebar.width())
            self.sidebar_animation.setEndValue(0)
        else:
            self.sidebar_animation.setStartValue(0)
            self.sidebar_animation.setEndValue(250)
        self.sidebar_animation.start()
        self.sidebar_expanded = not self.sidebar_expanded

    def jump_to_path(self):
        path = self.path_input.text().strip()
        if os.path.isdir(path):
            index = self.folder_model.index(path)
            self.folder_tree.setCurrentIndex(index)
            self.folder_tree.scrollTo(index)
            self.load_images(path)
        else:
            QMessageBox.warning(self, "錯誤", "無效的資料夾路徑")

    def load_images_from_index(self, index):
        path = self.folder_model.filePath(index)
        self.path_input.setText(path)
        self.load_images(path)

    def load_images(self, folder_path):
        self.image_folder = folder_path
        self.image_descriptions.clear()
        self.image_cards.clear()
        self.image_files.clear()
        self.batch_index = 0

        for i in reversed(range(self.grid_layout.count())):
            widget = self.grid_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        images = [f for f in os.listdir(folder_path)
                  if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        self.image_files = natsorted(images)
        self.load_json_descriptions()

        QTimer.singleShot(50, self.load_image_batch)

    def load_image_batch(self):
        if self.batch_index >= len(self.image_files):
            return

        for i in range(self.batch_index, min(self.batch_index + self.batch_size, len(self.image_files))):
            image_name = self.image_files[i]
            row = i // 5
            col = i % 5
            card = self.create_image_card(image_name)
            self.grid_layout.addWidget(card, row, col)

        self.batch_index += self.batch_size
        QTimer.singleShot(100, self.load_image_batch)

    def create_image_card(self, image_name):
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                font-size: 16pt;
                border: 1px solid #ccc;
                border-radius: 10px;
            }
        """)

        layout = QVBoxLayout(frame)

        img_path = os.path.join(self.image_folder, image_name)
        original_pixmap = QPixmap(img_path)

        # 根據圖片實際尺寸縮放，最大寬或高為 300px，保持比例
        max_width = 300
        max_height = 400
        scaled_pixmap = original_pixmap.scaled(
            max_width, max_height, Qt.KeepAspectRatio, Qt.SmoothTransformation
        )

        label = QLabel()
        label.setPixmap(scaled_pixmap)
        label.setAlignment(Qt.AlignCenter)
        label.mouseDoubleClickEvent = lambda e: self.copy_description(image_name)

        # 設定卡片寬度根據縮圖大小擴展（略加 padding）
        frame.setFixedWidth(scaled_pixmap.width() + 20)

        name_label = QLabel(image_name)
        name_label.setAlignment(Qt.AlignCenter)
        name_label.setFont(QFont("Arial", 9))
        name_label.setObjectName("imageLabel")

        desc_edit = QLineEdit()
        desc_edit.setPlaceholderText("請輸入描述")
        desc_edit.setText(self.image_descriptions.get(image_name, ""))
        desc_edit.textChanged.connect(lambda text, img=image_name: self.image_descriptions.__setitem__(img, text))

        layout.addWidget(label)
        layout.addWidget(name_label)
        layout.addWidget(desc_edit)

        self.image_cards[image_name] = desc_edit
        return frame

    def copy_description(self, image_name):
        text = self.image_descriptions.get(image_name, "")
        clipboard = QApplication.clipboard()
        clipboard.setText(text)
        QMessageBox.information(self, "複製成功", f"{image_name} 的描述已複製。")

    def save_descriptions(self):
        if not self.image_folder:
            return
        folder_name = os.path.basename(self.image_folder)
        save_path = os.path.join(self.json_folder, f"{folder_name}_descriptions.json")
        with open(save_path, "w", encoding="utf-8") as f:
            json.dump(self.image_descriptions, f, indent=2, ensure_ascii=False)
        QMessageBox.information(self, "儲存成功", f"已儲存描述到 {save_path}")

    def clear_descriptions(self):
        for image, editor in self.image_cards.items():
            editor.setText("")
        self.image_descriptions = {img: "" for img in self.image_cards}
        QMessageBox.information(self, "已清除", "所有描述已清除。")

    def load_json_descriptions(self):
        folder_name = os.path.basename(self.image_folder)
        json_path = os.path.join(self.json_folder, f"{folder_name}_descriptions.json")
        if os.path.exists(json_path):
            with open(json_path, "r", encoding="utf-8") as f:
                self.image_descriptions = json.load(f)

    def load_json_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "選擇 JSON 檔", "", "JSON Files (*.json)")
        if path:
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    matched = 0
                    for imgname in self.image_cards:
                        name_no_ext = os.path.splitext(imgname)[0]
                        if imgname in data:
                            self.image_cards[imgname].setText(data[imgname])
                            self.image_descriptions[imgname] = data[imgname]
                            matched += 1
                        elif name_no_ext in data:
                            self.image_cards[imgname].setText(data[name_no_ext])
                            self.image_descriptions[imgname] = data[name_no_ext]
                            matched += 1
                        else:
                            matched += 1
                            continue
                    QMessageBox.information(self, "載入完成", f"成功載入 {matched} 筆描述資料。")
                    if not self.image_folder:
                        return
                    folder_name = os.path.basename(self.image_folder)
                    save_path = os.path.join(self.json_folder, f"{folder_name}_descriptions.json")
                    with open(save_path, "w", encoding="utf-8") as f:
                        json.dump(self.image_descriptions, f, indent=2, ensure_ascii=False)
            except Exception as e:
                QMessageBox.warning(self, "錯誤", f"無法載入 JSON 檔案：{e}")


app = QApplication([])
viewer = ImageViewer()
viewer.show()
app.exec()

