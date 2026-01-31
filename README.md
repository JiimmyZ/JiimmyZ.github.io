# JZ隨筆 - Hugo Blog

## 專案簡介

這是一個使用 Hugo 建置的靜態網站部落格，主要內容包含詩詞、小說、雜感、賞析和遊記等文學創作。網站使用 PaperMod 主題，並透過 Cloudinary CDN 管理媒體檔案（圖片和影片）。

### 網站資訊
- **網站標題**: JZ隨筆
- **語言**: 繁體中文 (zh-TW)
- **部署**: GitHub Pages
- **網址**: https://jiimmyz.github.io/

## 技術棧

### 核心技術
- **Hugo**: 靜態網站生成器
- **PaperMod**: Hugo 主題
- **Cloudinary**: 媒體檔案 CDN 儲存與優化
- **Python**: 媒體管理自動化腳本
- **GitHub Pages**: 靜態網站託管

### Python 依賴
- `cloudinary>=1.36.0`: Cloudinary SDK
- `python-dotenv>=1.0.0`: 環境變數管理

## 專案結構

```
myblog/
├── content/                    # Hugo 內容目錄
│   ├── about.md               # 關於頁面
│   ├── poetry/                # 詩詞文章
│   ├── novel/                 # 小說文章
│   ├── essay/                 # 雜感文章
│   ├── review/                # 賞析文章
│   └── travelogue/            # 遊記（含大量媒體檔案）
│       └── camino/            # Camino 遊記系列
│
├── themes/                    # Hugo 主題
│   └── PaperMod/              # PaperMod 主題
│
├── layouts/                   # 自訂佈局
│   ├── _default/             # 預設佈局
│   ├── partials/             # 部分模板
│   └── shortcodes/           # 短代碼
│
├── static/                    # 靜態檔案（favicon, robots.txt 等）
├── public/                    # Hugo 生成的靜態網站（gitignore）
│
├── upload_to_cloudinary.py    # 媒體檔案上傳腳本
├── update_markdown.py         # Markdown 連結更新腳本
├── check_duplicates.py         # Cloudinary 重複檔案檢測
├── check_status.py            # 上傳狀態檢查
├── compress_video.py          # 影片壓縮工具
├── analyze_upload_time.py     # 上傳時間分析
│
├── cloudinary_mapping.json    # 本地檔案 → Cloudinary URL 對應表
├── requirements.txt           # Python 依賴
├── hugo.toml                  # Hugo 設定檔
├── context.md                 # 專案上下文與決策記錄
└── README.md                  # 本檔案
```

## 環境設定

### 前置需求
1. **Hugo**: 安裝 Hugo 靜態網站生成器
   ```bash
   # Windows (使用 Chocolatey)
   choco install hugo-extended
   
   # macOS (使用 Homebrew)
   brew install hugo
   
   # 或從官網下載: https://gohugo.io/installation/
   ```

2. **Python 3.8+**: 用於執行媒體管理腳本
   ```bash
   python --version
   ```

3. **Cloudinary 帳號**: 免費帳號即可（25GB 儲存空間）

### 安裝步驟

1. **複製專案**
   ```bash
   git clone <repository-url>
   cd myblog
   ```

2. **安裝 Python 依賴**
   ```bash
   pip install -r requirements.txt
   ```

3. **設定 Cloudinary 憑證**
   
   建立 `.env` 檔案（在專案根目錄）：
   ```env
   CLOUDINARY_CLOUD_NAME=your_cloud_name
   CLOUDINARY_API_KEY=your_api_key
   CLOUDINARY_API_SECRET=your_api_secret
   ```
   
   > **注意**: `.env` 檔案已加入 `.gitignore`，不會被提交到版本控制

4. **驗證 Hugo 安裝**
   ```bash
   hugo version
   ```

## 開發工作流程

### 本地開發

1. **啟動 Hugo 開發伺服器**
   ```bash
   hugo server
   ```
   
   伺服器會在 `http://localhost:1313` 啟動，支援熱重載。

2. **建立新文章**
   ```bash
   # 使用 Hugo archetypes
   hugo new poetry/新詩名.md
   hugo new novel/新小說名.md
   hugo new essay/新雜感名.md
   hugo new review/新賞析名.md
   hugo new travelogue/camino/ch10/index.md
   ```

3. **建置靜態網站**
   ```bash
   hugo
   ```
   
   生成的檔案會輸出到 `public/` 目錄。

### 媒體檔案管理

#### 上傳媒體檔案到 Cloudinary

當你在 `content/` 目錄中新增圖片或影片時：

```bash
python upload_to_cloudinary.py
```

這個腳本會：
- 掃描 `content/` 目錄中的所有媒體檔案
- 上傳新檔案到 Cloudinary（跳過已上傳的檔案）
- 更新 `cloudinary_mapping.json` 對應表
- 顯示上傳進度

#### 更新 Markdown 檔案中的連結

上傳完成後，更新 Markdown 檔案中的媒體連結：

```bash
python update_markdown.py
```

這個腳本會：
- 讀取 `cloudinary_mapping.json`
- 將 Markdown 檔案中的本地檔案路徑替換為 Cloudinary CDN URL
- 自動建立 `.backup` 備份檔案
- 顯示替換統計

#### 檢查重複檔案

檢查 Cloudinary 中是否有重複檔案：

```bash
python check_duplicates.py
```

使用 `--auto` 參數自動移除重複檔案：

```bash
python check_duplicates.py --auto
```

#### 檢查上傳狀態

驗證檔案上傳狀態：

```bash
python check_status.py
```

### 部署

1. **建置網站**
   ```bash
   hugo
   ```

2. **提交變更**
   ```bash
   git add .
   git commit -m "更新內容"
   git push origin main
   ```

3. **GitHub Pages 自動部署**
   
   如果已設定 GitHub Actions，推送後會自動部署到 GitHub Pages。

## 媒體檔案處理

### 檔案大小限制

- **Cloudinary 免費方案限制**: 單一檔案最大 100MB
- **建議**: 圖片 < 10MB，影片 < 100MB

### 大檔案處理

對於超過 100MB 的影片檔案：

1. **安裝 FFmpeg**（用於影片壓縮）
   ```bash
   # Windows (需要管理員權限)
   choco install ffmpeg -y
   
   # macOS
   brew install ffmpeg
   ```

2. **壓縮影片**
   ```bash
   python compress_video.py content/travelogue/camino/ch8/VID_xxx.mp4
   ```

3. **上傳壓縮後的檔案**
   ```bash
   python upload_to_cloudinary.py
   ```

### 媒體檔案統計

目前專案狀態：
- ✅ **659 個媒體檔案**已上傳到 Cloudinary（646 張圖片 + 13 個影片）
- ✅ **6 個 Markdown 檔案**已更新為 Cloudinary URL
- ✅ **633 個連結**已替換為 CDN URL

## 內容分類

網站包含以下內容分類：

- **詩詞** (`/poetry/`): 新詩、絕句、律詩、宋詞等
- **小說** (`/novel/`): 小說創作
- **雜感** (`/essay/`): 生活隨筆、哲思
- **賞析** (`/review/`): 文學作品賞析
- **遊記** (`/travelogue/`): 旅行記錄，包含大量照片和影片

## 設定檔說明

### `hugo.toml`

主要設定檔，包含：
- 網站基本資訊（標題、語言、主題）
- 導航選單設定
- Google Analytics 設定
- 閱讀體驗設定（目錄、閱讀時間、分享按鈕等）

### `cloudinary_mapping.json`

本地檔案路徑與 Cloudinary URL 的對應表，格式：

```json
{
  "content/travelogue/camino/ch1/image.jpg": {
    "url": "https://res.cloudinary.com/.../image.jpg",
    "public_id": "travelogue/camino/ch1/image",
    "uploaded_at": "2026-01-31T14:30:00Z"
  }
}
```

## SEO 優化

本專案已實作完整的 SEO 優化設定，包括：

### 已實作的 SEO 功能

- ✅ **Meta 標籤優化**: 自動生成 title、description、keywords
- ✅ **結構化資料**: Article schema、BreadcrumbList schema
- ✅ **Open Graph 標籤**: 社群媒體分享優化
- ✅ **Twitter Cards**: Twitter 分享卡片支援
- ✅ **圖片 SEO**: 自動 alt 文字生成、響應式圖片
- ✅ **Sitemap**: 自動生成 sitemap.xml
- ✅ **robots.txt**: 搜尋引擎爬蟲指引
- ✅ **效能優化**: 圖片懶加載、CDN 加速

### SEO 最佳實踐

詳細的 SEO 指南請參考 [SEO_GUIDELINES.md](SEO_GUIDELINES.md)，包含：

- 標題優化建議（50-60 字元）
- Meta 描述撰寫（150-160 字元）
- 標題層級結構（H1-H4）
- 圖片 alt 文字最佳實踐
- 內部連結策略
- 關鍵字使用指南

### 內容建立檢查清單

建立新內容時，請確保：

1. **標題**: 獨特且描述性（50-60 字元）
2. **描述**: 在 frontmatter 中添加 `description` 欄位
3. **圖片**: 為所有圖片提供描述性 alt 文字
4. **標籤**: 添加適當的 tags 和 categories
5. **內部連結**: 連結到相關內容

### SEO 工具與驗證

- **Google Search Console**: 提交 sitemap 並監控搜尋表現
- **Google Analytics**: 追蹤流量和用戶行為
- **PageSpeed Insights**: 檢查頁面載入效能
- **Schema Markup Validator**: 驗證結構化資料

## 常見問題

### 圖片/影片無法顯示

1. 檢查 `cloudinary_mapping.json` 中是否有對應的 URL
2. 確認 Markdown 檔案已執行 `update_markdown.py` 更新
3. 驗證 Cloudinary URL 是否可正常存取

### 上傳失敗

1. 檢查 `.env` 檔案中的 Cloudinary 憑證是否正確
2. 確認網路連線正常
3. 檢查檔案大小是否超過 100MB 限制
4. 查看錯誤訊息，可能需要壓縮大檔案

### Hugo 建置錯誤

1. 確認 Hugo 版本（建議使用 extended 版本）
2. 檢查 `hugo.toml` 語法是否正確
3. 確認所有必要的目錄結構存在

## 相關文件

- [SEO 優化指南](SEO_GUIDELINES.md) - 內容建立與 SEO 最佳實踐
- [Cloudinary 設定指南](CLOUDINARY_SETUP.md)
- [專案上下文與決策記錄](context.md)
- [Hugo 官方文件](https://gohugo.io/documentation/)
- [PaperMod 主題文件](https://github.com/adityatelange/hugo-PaperMod)

## 授權

[待定]

## 貢獻

歡迎提出問題和建議！

---

**注意**: 本專案使用 Cloudinary 免費方案託管媒體檔案。如需更多儲存空間或頻寬，請考慮升級 Cloudinary 方案。
