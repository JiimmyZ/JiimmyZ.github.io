# JZ隨筆 - Hugo Blog

## 專案簡介

Hugo 靜態部落格（PaperMod），內容含詩詞、小說、雜感、賞析、遊記。媒體（圖／影片）放 Cloudinary CDN；部署於 GitHub Pages。

### 網站資訊

- **標題**: JZ隨筆
- **語言**: 繁體中文 (zh-TW)
- **網址**: https://jiimmyz.github.io/
- **Repo**: https://github.com/JiimmyZ/JiimmyZ.github.io

## 給未來的你／Agent

本站**永遠單人維護**。久久才開一次時，先讀本檔「日常速查」，再查下表。

| 要找什麼 | 看哪裡 |
|----------|--------|
| 網站／評論／不蒜子等設定 | [`hugo.toml`](hugo.toml) |
| 近期決策與現況 | [`context.md`](context.md) |
| 歷史 session、遷移、ADR | [`LEGACY.md`](LEGACY.md) |
| 媒體上傳／換連結 | 只認 [`media_processor.py`](media_processor.py)（舊腳本已刪） |

請勿擅自加第二套評論系統、協作流程或「貢獻指南」。改行為後更新 `context.md`，較大決策再記 `LEGACY.md`。

## 日常速查

```text
純文字發文：
  hugo new poetry/題名.md  → 編輯 → hugo server → git push

有圖／影片：
  檔案放進 content/... → python media_processor.py upload
  → python media_processor.py update-markdown → 預覽 → push

大影片 >100MB：
  python media_processor.py compress <video> → 再 upload
```

- 本地預覽：`hugo server` → http://localhost:1313
- 純文字不需要 Cloudinary／`.env`
- 推 `main` 後由 GitHub Actions 部署 GitHub Pages

## 技術棧

- **Hugo** + **PaperMod**
- **Cloudinary**（媒體 CDN）
- **Giscus**（GitHub Discussions 評論，僅 GitHub 登入）
- **不蒜子**（訪客統計，UI 僅關於頁）
- **字體**: PaperMod 系統字體（無外部字體）
- **Python**: `cloudinary`、`python-dotenv`、`pydantic`、`pydantic-settings`（見 `requirements.txt`）

## 專案結構

```
myblog/
├── content/                 # 文章（poetry / novel / essay / review / travelogue）
├── layouts/                 # 自訂佈局、partials、shortcodes
├── themes/PaperMod/
├── static/                  # favicon、robots.txt 等
├── public/                  # hugo 產出（gitignore）
├── ebook-generator/         # 電子書相關（獨立子專案）
├── media_processor.py       # 媒體：upload / update-markdown / check-duplicates / compress
├── check_status.py          # 上傳狀態檢查
├── cloudinary_mapping.json  # 本地路徑 → Cloudinary URL
├── hugo.toml                # 設定真相來源
├── context.md               # 現況與近期 session
├── LEGACY.md                # 歷史與 ADR
├── requirements.txt
├── requirements-dev.txt     # ruff 等
└── README.md
```

## 環境設定

### 前置需求

1. **Hugo Extended**（建議）
   ```bash
   choco install hugo-extended   # Windows
   brew install hugo             # macOS
   ```
2. **Python 3.8+**（僅媒體腳本需要）
3. **Cloudinary**（僅有媒體上傳時需要；免費方案單檔 ≤100MB）

### 安裝

```bash
git clone https://github.com/JiimmyZ/JiimmyZ.github.io.git
cd JiimmyZ.github.io   # 或本機目錄名 myblog
pip install -r requirements.txt
hugo version
```

有媒體要上傳時，根目錄建立 `.env`（已在 `.gitignore`）：

```env
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret
```

## 本地開發與部署

### 新文章

```bash
hugo new poetry/新詩名.md
hugo new novel/新小說名.md
hugo new essay/新雜感名.md
hugo new review/新賞析名.md
hugo new travelogue/camino/ch10/index.md
```

### 預覽與建置

```bash
hugo server    # http://localhost:1313
hugo           # 輸出到 public/
```

### 部署

```bash
git add .
git commit -m "更新內容"
git push origin main
```

GitHub Actions 會建置並部署到 GitHub Pages。

### 代碼檢查（改 Python 時）

```bash
pip install -r requirements-dev.txt
ruff check .
ruff format .
```

## 媒體檔案

統一工具：`media_processor.py`。限制：Cloudinary 免費單檔 **最大 100MB**（建議圖 <10MB）。

### 標準流程

1. 媒體放進 `content/...`（與文章同目錄或相對路徑）
2. `python media_processor.py upload` — 掃描並上傳新檔，更新 `cloudinary_mapping.json`
3. `python media_processor.py update-markdown` — 本地路徑換成 CDN URL（可加 `--backup`）
4. `hugo server` 確認顯示後再 push

### 其他指令

```bash
python media_processor.py check-duplicates      # 只檢查
python media_processor.py check-duplicates --auto
python media_processor.py compress path/to/video.mp4
python check_status.py                          # 驗證上傳狀態
```

### 大影片（>100MB）

先裝 FFmpeg，再壓縮後上傳：

```bash
choco install ffmpeg -y   # Windows（可能需管理員）
brew install ffmpeg       # macOS

python media_processor.py compress content/travelogue/camino/ch8/VID_xxx.mp4
python media_processor.py upload
```

初次大量遷移（約 659 檔等）細節見 [`LEGACY.md`](LEGACY.md)，不當現況統計。

## 內容分類

| 路徑 | 說明 |
|------|------|
| `/poetry/` | 詩詞 |
| `/novel/` | 小說 |
| `/essay/` | 雜感 |
| `/review/` | 賞析 |
| `/travelogue/` | 遊記（媒體多） |

## 設定索引

### `hugo.toml`

網站標題、選單、Analytics、閱讀體驗、`[params.comments.giscus]`、`[params.busuanzi]` 等都在這裡。

### 不蒜子

- 設定：`[params.busuanzi]`（`enabled`、`siteStartDate`）
- UI：僅 [`content/about.md`](content/about.md)（`showSiteStats = true`）
- 腳本：[`layouts/partials/extend_footer.html`](layouts/partials/extend_footer.html)（全站載入以累計）

### 字體

- 使用 PaperMod 內建的系統 sans-serif 字體堆疊，不載入 Google Fonts、jsDelivr 或本機字體檔。
- Giscus iframe **不繼承**本站字體（見 `LEGACY.md`）

### Giscus

設定在 `hugo.toml` → `[params.comments.giscus]`；模板 [`layouts/partials/comments.html`](layouts/partials/comments.html)。

- 僅支援 **GitHub 登入**（Discussions）
- 主題目前：`preferred_color_scheme`；顏色／其他登入方案曾評估後不改（見 `LEGACY.md`）
- 若需重設：GitHub 裝 [giscus app](https://github.com/apps/giscus) → 開 Discussions → [giscus.app](https://giscus.app/) 取 repo-id／category-id → 寫回 `hugo.toml`

### `cloudinary_mapping.json`

```json
{
  "content/travelogue/camino/ch1/image.jpg": {
    "url": "https://res.cloudinary.com/.../image.jpg",
    "public_id": "travelogue/camino/ch1/image",
    "uploaded_at": "2026-01-31T14:30:00Z"
  }
}
```

## SEO（發文時）

站內已有 meta、OG、sitemap、結構化資料、預設分享圖等（見 `layouts/partials/`、`static/og-default.png`）。

新文章檢查：

1. 標題清楚（約 50–60 字元）
2. frontmatter 填 `summary`（或 `description`）
3. 圖片有描述性 alt（`![說明](url)`）
4. 適當 `tags`／`categories`
5. 佔位／空頁可加 `robotsNoIndex = true` 與 `[sitemap] disable = true`

## 常見問題

### 圖片／影片無法顯示

1. `cloudinary_mapping.json` 是否有該檔
2. 是否已跑 `python media_processor.py update-markdown`
3. Cloudinary URL 是否可開啟

### 上傳失敗

1. `.env` 憑證是否正確
2. 單檔是否 >100MB（需先 compress）
3. 網路與錯誤訊息

### Hugo 建置錯誤

1. 建議 Hugo **extended**
2. 檢查 `hugo.toml` 語法
3. 目錄／主題是否完整

## 相關文件

- [`context.md`](context.md) — 現況與近期決策
- [`LEGACY.md`](LEGACY.md) — 歷史 session、遷移、ADR
- [Hugo 文件](https://gohugo.io/documentation/)
- [PaperMod](https://github.com/adityatelange/hugo-PaperMod)
- [giscus](https://giscus.app/)
- [Cloudinary](https://cloudinary.com/documentation)

---

媒體使用 Cloudinary 免費方案；空間／頻寬不足再考慮升級。
