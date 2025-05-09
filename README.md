<html>
<body>
<h1>Image_Viewer</h1>
這是一套基於 PySide6 製作的圖片瀏覽與描述編輯工具，支援 JSON 描述自動載入、儲存與同步顯示。具備現代化暗色主題、滑桿樣式美化、動態卡片載入與 UI 優化設計。
目的在於方便管理wildcard圖片，雙擊可以複製描述。

## ✨ 功能介紹
- 🖼️ **圖片顯示**：圖片以卡片方式顯示，含縮圖、檔名與描述輸入欄  
- ✍️ **描述編輯**：支援即時儲存、雙擊圖片複製描述  
- 📁 **資料夾導覽**：左側目錄樹可快速切換資料夾，也可手動輸入路徑  
- 📂 **JSON 整合**：開啟資料夾時自動載入描述、手動載入也支援（不含副檔名比對）  
- 🧹 **描述清除**：一鍵清空所有圖片描述


![image](https://github.com/pasoki/image_viewer/blob/main/images/user_interface.png?raw=true)
<hr>
<h2>🖥️ 執行畫面預覽</h2>
<blockquote>
<p>圖片卡片包含：</p>
<ul>
<li>上方縮圖</li>
<li>中間檔名（自定樣式）</li>
<li>下方描述欄（可即時儲存）</li>
</ul>
</blockquote>
<p>左側為資料夾選擇器，可收合以擴大主視窗寬度。操作按鈕置於上方工具列。</p>
<hr>
<h2>🚀 執行方式</h2>
<h3>安裝環境（一次性）：</h3>
<pre><code class="language-bash">pip install PySide6 natsor
</code></pre>
<pre><code class="language-bash">python image_viewer.py
</code></pre>
<hr>
<p>📁 JSON 格式說明</p>
<p>每個資料夾對應一個 JSON 檔，預設儲存在 <code>./descriptions</code> 資料夾中。檔名格式為：</p>
<pre><code class="language-jsx">&lt;資料夾名稱&gt;_descriptions.json
</code></pre>
<h3>範例內容：</h3>
<pre><code class="language-json">{
  &quot;cat_01&quot;: &quot;這是一隻愛的貓咪&quot;,
  &quot;girl_002&quot;: &quot;穿著洋裝的女孩&quot;
}

</code></pre>
<!-- notionvc: 98ea7c55-2e5c-43b2-9218-198704e34c43 --><!--EndFragment-->
</body>
</html>
