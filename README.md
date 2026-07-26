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

## 幾個月後回來怎麼用

### 先記住這站怎麼跑

你寫的是 `content/` 裡的 Markdown。Hugo 把它編成靜態 HTML 放進 `public/`，但 `public/` 是建置產物，不需要手動編輯或提交。

本站**沒有自架伺服器**。部署流程是：

```text
git push origin main
  → .github/workflows/deploy.yml
  → test → lint → hugo --minify → deploy
  → GitHub Pages（https://jiimmyz.github.io/）
```

任一測試或 lint 失敗，後面的建置與部署就不會執行。進 GitHub repo 的 **Actions** 頁可以看成功或失敗原因。

### 寫好的內容要放哪

| 類型 | 放置位置 |
|------|----------|
| 詩詞 | `content/poetry/題名.md`（檔名通常就是標題） |
| 小說 | `content/novel/` |
| 雜感 | `content/essay/` |
| 賞析 | `content/review/` |
| 遊記（常有媒體） | `content/travelogue/...` |
| 關於頁 | `content/about.md` |

可用 `hugo new poetry/題名.md` 依 archetype 建立骨架。詩詞正文每行末尾留兩個空格以強制換行，最後保留 `自註:`。

純文字更新：

```text
把 .md 放到 content/ 正確分類
  → hugo server
  → 瀏覽 http://localhost:1313
  → git add / commit / push
```

有圖或影片時，先看下方「Cloudinary CDN」與「媒體檔案」，不要直接把大量原始媒體提交進 git。

### 想改網站或部署時去哪裡

| 想改什麼 | 去哪裡改 |
|----------|----------|
| 站名、選單、首頁區塊、Giscus、不蒜子 | [`hugo.toml`](hugo.toml) |
| GitHub Actions 觸發分支、測試、建置與部署步驟 | [`.github/workflows/deploy.yml`](.github/workflows/deploy.yml) |
| Pages 發布來源 | GitHub repo → **Settings → Pages**；目前 Source 是 **GitHub Actions** |
| 自訂版型、評論、頁首頁尾腳本 | `layouts/`；盡量不要直接改 `themes/PaperMod/` 核心 |
| 近期現況與決策 | [`context.md`](context.md) |
| 歷史遷移與架構理由 | [`LEGACY.md`](LEGACY.md) |

若將來改用別的部署平台，通常要同時調整平台設定、`baseURL`（在 `hugo.toml`）及 `.github/workflows/deploy.yml`；不要只改 GitHub Pages 的畫面設定。

### 容易忘的規則

- 內容 md 新設或刪減：完成後 commit + push。
- 功能開發：可以先留在本機，等明確決定後再 push。
- 不要提交 `.env` 或 `public/`；Cloudinary 憑證只放本機 `.env`。
- 本機資料夾可能叫 `myblog`，遠端 repo 叫 `JiimmyZ.github.io`；以 `git remote -v` 顯示為準。

### Cloudinary CDN 是什麼

**Cloudinary** 是專門儲存及傳送圖片、影片的雲端服務。上傳後會得到 `res.cloudinary.com/...` 網址，Markdown 直接引用該網址。

**CDN（Content Delivery Network）** 會把媒體快取在不同地區的節點。讀者開網站時，文字與 HTML 由 GitHub Pages 提供，大檔則由 Cloudinary 較近的節點傳送，不經你的電腦，也不把所有原圖塞進 GitHub Pages。

當初 repo 約有 659 個媒體、合計 500MB 以上，造成 git 操作很慢，因此把媒體移到 Cloudinary（詳見 `LEGACY.md` 的 ADR-001）。

免費並非無限：專案導入時記錄的方案約有 25GB 儲存空間及月流量額度，單檔上限 100MB；方案可能調整，實際額度以 Cloudinary Dashboard 為準。個人部落格通常用量較低，所以免費額度暫時夠用；超額後需清理或升級。

### 大影片怎麼處理

Cloudinary 單檔上限是 100MB，本站工具以 **95MB** 為目標保留餘量。先安裝 FFmpeg：

```bash
choco install ffmpeg -y
ffmpeg -version
```

壓縮並上傳：

```bash
python media_processor.py compress content/.../影片.mp4
# 預設輸出同目錄的 影片_compressed.mp4，不覆蓋原檔

python media_processor.py upload
python media_processor.py update-markdown
hugo server
```

壓縮工具的實際策略：

- 第一輪：H.264、CRF 28、slow、最大 1080p、AAC 96k、`+faststart`（利於網頁播放）。
- 若仍超過 95MB：自動再用 CRF 30、最大 720p、AAC 64k。
- 影片超過 20MB 時，上傳改用 Cloudinary SDK `upload_large()`，並避免同步格式轉換。
- 歷史案例：115.63MB 壓成 29.46MB。

確認壓縮檔可播放、文章已換成正確 Cloudinary URL 後，才刪除原始大檔。不要把原始大影片提交進 git。

### 照片為什麼不會拖慢網站

照片原圖保存在 Cloudinary；頁面顯示時由 [`render-image.html`](layouts/_default/_markup/render-image.html) 自動產生較輕的版本：

- `f_auto`：依瀏覽器能力選 WebP、AVIF 等適合格式。
- `q_auto`：自動平衡畫質與檔案大小。
- `w_480 / 720 / 1080 / 1200`：建立 `srcset`，手機不必下載桌機尺寸原圖。
- `loading="lazy"`：圖片快進入畫面時才下載。
- `decoding="async"`：圖片解碼不阻塞頁面。
- 頁首會 preconnect / DNS prefetch Cloudinary，提早建立連線。

頁面顯示寬度上限 1200px，但點圖仍連回原始 URL，所以顯示最佳化不等於刪掉高畫質原圖。

新增照片的固定流程：

```text
照片放進 content/...（文章附近）
  → python media_processor.py upload
  → python media_processor.py update-markdown
  → 確認 Markdown 已換成 res.cloudinary.com URL
  → hugo server（桌機、窄視窗都抽查）
  → commit / push
```

不要手動把 `/upload/f_auto.../` 寫進 Markdown；render hook 會在建置時自動加轉換參數。

## 日常速查

細節見上一節；平常只需要記這份最短流程：

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
├── tests/                   # pytest 測試（CI 通過才會部署）
├── media_processor.py       # 媒體：upload / update-markdown / check-duplicates / compress
├── check_status.py          # 上傳狀態檢查
├── cloudinary_mapping.json  # 本地路徑 → Cloudinary URL
├── hugo.toml                # 設定真相來源
├── pytest.ini               # pytest 設定（含 addopts 與覆蓋率門檻）
├── .coveragerc              # coverage.py 設定
├── context.md               # 現況與近期 session
├── LEGACY.md                # 歷史與 ADR
├── requirements.txt
├── requirements-dev.txt     # pytest / ruff 等
└── README.md
```

> `ebook-generator/`（Camino EPUB 工具）已於 2026-07-25 移出本 repo，成為獨立專案。

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

部署原理與設定位置見「幾個月後回來怎麼用」。一般內容更新只需：

```bash
git add .
git commit -m "更新內容"
git push origin main
```

GitHub Actions 會依序測試、lint、建置，再部署到 GitHub Pages。

### 代碼檢查（改 Python 時）

```bash
pip install -r requirements-dev.txt
ruff check .
ruff format .
```

## 媒體檔案

統一工具：`media_processor.py`。Cloudinary 原理、圖片效能與大影片細節見上方教學。限制：單檔 **最大 100MB**（建議圖 <10MB）。

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

完整壓縮策略與注意事項見上方「大影片怎麼處理」。最短操作：

```bash
choco install ffmpeg -y   # Windows（可能需管理員）
brew install ffmpeg       # macOS

python media_processor.py compress content/travelogue/camino/ch8/VID_xxx.mp4
python media_processor.py upload
python media_processor.py update-markdown
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
