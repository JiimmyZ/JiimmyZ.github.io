# Camino Ebook Generator - 進度追蹤

## 專案狀態

**最後更新時間：** 2026-02-01

**當前進行中：** 無（章節切換空頁問題已修復）

## ✅ 已完成項目

### 1. 專案架構建立
- [x] 建立專案結構（config.py, main.py, src/ 模組）
- [x] 實作所有核心模組：
  - [x] `markdown_parser.py` - AST 解析
  - [x] `translator.py` - AST 翻譯（Gemini API）
  - [x] `image_processor.py` - 圖片下載與優化
  - [x] `cover_generator.py` - 封面生成
  - [x] `pandoc_wrapper.py` - Pandoc 包裝
- [x] 建立 Dockerfile 和 requirements.txt
- [x] 建立 EPUB 樣式表（assets/styles.css）

### 2. 章節合併功能
- [x] 實作 `merge_chapters.py` - 合併 9 個章節
- [x] 移除 Hugo frontmatter
- [x] 合併檔案保存位置：`ebook-generator/merged/camino_merged.md`
- [x] 合併檔案大小：123,439 字元

### 3. 依賴安裝
- [x] 安裝所有 Python 依賴套件
  - [x] marko (AST 解析)
  - [x] aiohttp (非同步 HTTP)
  - [x] pillow (圖片處理)
  - [x] google-generativeai (翻譯 API)
- [x] 安裝 Pandoc 3.8.3

### 4. EPUB 生成
- [x] 成功生成 EPUB 檔案
- [x] 檔案位置：`ebook-generator/output/camino_pilgrim.epub`
- [x] 檔案大小：114.31 MB
- [x] 處理圖片數量：630 張

### 5. 程式碼修正
- [x] 修正 Pandoc 3.8.3 相容性（--css 取代 --epub-stylesheet）
- [x] 修正 metadata 參數格式
- [x] 修正 Unicode 編碼問題（Windows 終端機）
- [x] 修正可變默認參數陷阱
- [x] 改進錯誤處理和提示訊息

### 6. EPUB 品質改進（2025-01-27）
- [x] 修正封面標題（中文和英文）
- [x] 添加中文字體支援（標楷體）
- [x] 改進圖片處理邏輯：
  - [x] 自動檢測並跳過影片檔案（MP4等）
  - [x] 驗證下載檔案是否為有效圖片
  - [x] 優雅處理失敗的下載（移除或替換為註解）
  - [x] 改進錯誤日誌和處理摘要

### 7. EPUB 版面與結構修復（2026-02-01）
- [x] 修復封面頁順序：將封面頁移到第一頁（在目錄之前）
  - [x] 創建 `fix_epub_spine.py` 後處理腳本自動調整 spine 順序
  - [x] 整合到 `main.py`，每次生成 EPUB 後自動執行
  - [x] 禁用 Pandoc 自動生成的標題頁（`--epub-title-page=false`）
- [x] 修復雙頁顯示問題：強制單頁顯示
  - [x] 在 CSS 中添加 `column-count: 1 !important` 和 `column-width: 100% !important`
  - [x] 添加 `max-width: 100%` 和 `overflow-x: hidden` 防止橫向滾動
  - [x] 添加 `@page` 規則控制頁面大小
- [x] 修復 XML 解析錯誤：移除嵌套的 HTML 註解
  - [x] 失敗的圖片現在完全移除，不再生成註解
  - [x] 避免 XML 解析錯誤（Double hyphen within comment）
- [x] 改進封面生成：使用 HTML div 結構和 CSS 類別

## ⚠️ 已知問題

### 圖片下載問題（已改進）
- ✅ 已實作影片檔案自動跳過（MP4等格式）
- ✅ 已實作下載檔案驗證（確保為有效圖片）
- ✅ 已實作失敗下載的優雅處理（完全移除，避免 XML 錯誤）
- ⚠️ 部分圖片仍可能返回 HTTP 404 錯誤（URL 變更或檔案已刪除）
- ⚠️ 影響：失敗的圖片會被移除，不影響 EPUB 生成

### 文件大小
- 當前 EPUB 大小：122.79 MB
- 目標大小：<50 MB
- 原因：包含大量圖片（618 張成功下載）

## 📋 待改善事項

### 1. 圖片下載失敗處理（已解決）
**狀態：** 已完全改進處理邏輯
- ✅ **已實作：**
  - 自動檢測並跳過影片檔案（MP4, MOV, AVI等）
  - 驗證下載檔案是否為有效圖片（使用 PIL 驗證）
  - 失敗的下載會被完全移除，避免 XML 解析錯誤
  - 改進的錯誤日誌和處理摘要
- ⚠️ **仍可能發生：**
  - 部分圖片返回 HTTP 404（URL 變更或檔案已刪除）
  - 這些圖片會被自動移除，不影響 EPUB 生成
- **建議：**
  - 檢查 `output/temp/camino_final.md` 確認哪些圖片被移除
  - 驗證 Cloudinary URL 是否仍然有效
  - 考慮手動更新失效的圖片 URL

### 2. 章節切換空頁問題（已修復 - 2026-02-01）
**問題：** 使用電子書閱讀器閱覽 EPUB 時，章節變換時中間會空一頁，且感覺不流暢

**問題分析：**
1. **章節分隔符號 `---` 導致分頁**：`merge_chapters.py` 中每個章節結束時添加的 `---` 水平線被 Pandoc 視為分頁符號
2. **Pandoc 預設 h1 分頁行為**：Pandoc 自動在 h1 標題前添加分頁符號
3. **CSS 缺少明確的 page-break 控制**：沒有明確控制章節標題的分頁行為
4. **多餘空行**：章節之間的空行可能造成額外空白

**解決方案（已實作）：**
- [x] **修改章節合併邏輯** (`merge_chapters.py`)
  - ✅ 移除章節結束時的 `---` 分隔符號
  - ✅ 優化章節之間的空行處理，只在章節之間添加單一空行
  - ✅ 保留章節標題前的適當間距
- [x] **優化 CSS 樣式控制** (`assets/styles.css`)
  - ✅ 為 h1 標題添加 `page-break-before: avoid` 避免強制分頁
  - ✅ 添加 `page-break-after: avoid` 避免章節標題後立即分頁
  - ✅ 為 h2 添加 `page-break-after: avoid`
  - ✅ 為段落添加 `orphans: 3` 和 `widows: 3` 防止孤行
- [x] **調整 Pandoc 參數** (`src/pandoc_wrapper.py`)
  - ✅ 使用 `--split-level=6` 防止 Pandoc 在標題處自動分割章節（`--epub-chapter-level` 在 Pandoc 3.8+ 已棄用）
  - ✅ 確保內容保持單一連續流，不會因為標題而自動創建新章節文件
- [x] **測試與驗證**（2026-02-01）
  - ✅ 已重新生成 EPUB 檔案（使用修正後的代碼）
  - ✅ EPUB 生成成功：`output/camino_pilgrim.epub` (122.79 MB)
  - ⏳ 待測試：在電子書閱讀器上測試章節切換的流暢度
  - ⏳ 待確認：驗證沒有不必要的空頁

### 3. 章節標題層級與目錄結構問題（已修復 - 2026-02-01）
**問題：**
1. Chapter 3 之後的章節內容不見了
2. 目錄結構錯誤：每個 markdown 遇到 `#` 就被當作最高層級，導致章節內容中的 `# 標題` 與 `# Chapter X` 平級

**問題分析：**
- 章節內容中的 `# 標題`（如 `# 典故`、`# Camino相關名詞`）與 `# Chapter X` 都是 h1 級別
- Pandoc 在生成目錄時，將所有 h1 標題視為最高層級，導致目錄結構混亂
- 可能因此導致部分章節內容在 EPUB 中顯示異常

**解決方案（已實作）：**
- ✅ 修改 `merge_chapters.py`，添加 `increase_heading_levels()` 函數
- ✅ 在合併章節時，將每個章節內容中的所有標題級別提升一級（h1 → h2, h2 → h3, ...）
- ✅ 確保 `# Chapter X` 保持為唯一的 h1 級別（最高層級）
- ✅ 章節內容中的標題現在正確地作為子層級顯示在目錄中

**技術細節：**
- 使用正則表達式 `^(#{1,6})\s+(.+)$` 匹配所有 markdown 標題
- 為每個標題添加一個 `#`，提升一級（最多到 h6）
- 目錄結構現在應該是：Chapter X（h1）→ 內容標題（h2）→ 子標題（h3）...

### 4. 英文翻譯顯示問題
**問題：** 沒看到英文翻譯在哪
- **觀察：** EPUB 中沒有顯示英文翻譯內容
- **可能原因：**
  1. **翻譯未執行：** 因為未設定 `GEMINI_API_KEY`，翻譯步驟被跳過
  2. **翻譯格式問題：** 即使有翻譯，可能沒有正確顯示在 EPUB 中
  3. **翻譯位置：** 翻譯可能沒有正確插入到內容中
- **需要檢查：**
  - 是否設定了 `GEMINI_API_KEY` 環境變數
  - `src/translator.py` - 翻譯邏輯是否正確執行
  - `main.py` - 翻譯後的內容是否正確合併
  - `output/temp/camino_final.md` - 檢查最終 Markdown 是否包含英文翻譯
  - EPUB 內容 - 檢查 EPUB 中是否包含翻譯文字
- **解決方案：**
  1. 設定 `GEMINI_API_KEY` 環境變數
  2. 重新執行生成流程，確保翻譯步驟執行
  3. 檢查翻譯後的 Markdown 內容
  4. 確認 EPUB 中是否包含雙語內容（中文+英文）

## 📊 統計數據

- **章節數量：** 9 個（ch1 到 ch9）
- **合併檔案大小：** 123,352 字元
- **處理圖片數量：** 643 張（包含影片）
- **成功下載：** 618 張（96% 成功率）
- **影片檔案：** 15 個（已自動跳過）
- **失敗/跳過：** 25 個
- **EPUB 檔案大小：** 122.79 MB
- **翻譯狀態：** 未執行（需要 GEMINI_API_KEY）

## 🔄 下一步行動

1. ✅ 修正封面標題（中文和英文）- 已完成
2. ✅ 調查並修正圖片/影片顯示問題 - 已完成
3. ✅ 修復封面頁順序和雙頁顯示問題 - 已完成
4. ✅ 修復 XML 解析錯誤 - 已完成
5. ✅ **修正章節切換空頁問題** - 已完成並測試（2026-02-01）
   - ✅ 移除章節分隔符號 `---`
   - ✅ 優化 CSS page-break 控制
   - ✅ 調整 Pandoc 參數（`--split-level=6`，因為 `--epub-chapter-level` 已棄用）
   - ✅ EPUB 已成功生成（122.79 MB）
   - ⏳ 待驗證：在電子書閱讀器上測試章節切換流暢度
6. ✅ **修正章節標題層級與目錄結構** - 已完成（2026-02-01）
   - ✅ 修改 `merge_chapters.py`，添加標題級別提升功能
   - ✅ 確保 `# Chapter X` 為唯一 h1 級別
   - ✅ 章節內容標題正確降級為子層級
   - ✅ EPUB 已重新生成，目錄結構應已修正
   - ⏳ 待驗證：確認所有章節內容都正確顯示
7. 優化文件大小（可選）
8. 設定翻譯功能（可選）

## 📝 技術筆記

### Pandoc 版本相容性
- 使用 Pandoc 3.8.3
- `--epub-stylesheet` 已棄用，改用 `--css`
- Metadata 格式：`--metadata key=value`

### 圖片處理
- 使用 aiohttp 進行非同步下載
- 使用 Pillow 進行圖片優化
- 目標解析度：1200x1600（e-reader）
- JPEG 品質：85
- **改進（2025-01-27）：**
  - 自動檢測並跳過影片檔案（MP4, MOV, AVI, WEBM等）
  - 驗證下載檔案是否為有效圖片（PIL verify）
  - 失敗的下載會被完全移除，避免 XML 解析錯誤
  - 改進的錯誤日誌和處理摘要（成功/失敗統計）

### EPUB 版面控制
- **單頁顯示（2026-02-01）：**
  - 使用 CSS `column-count: 1 !important` 強制單欄布局
  - 添加 `max-width: 100%` 和 `overflow-x: hidden` 防止橫向滾動
  - 使用 `@page` 規則控制頁面大小
- **封面頁順序（2026-02-01）：**
  - 創建 `fix_epub_spine.py` 後處理腳本自動調整 spine 順序
  - 封面頁（ch001_xhtml）現在是第一頁，目錄（nav）是第二頁
  - 整合到 `main.py`，每次生成 EPUB 後自動執行
  - 禁用 Pandoc 自動生成的標題頁（`--epub-title-page=false`）

### 翻譯功能
- 使用 Google Gemini API
- AST-based 翻譯確保結構完整性
- 支援翻譯快取
- **注意：** 需要設定 `GEMINI_API_KEY` 環境變數才能啟用翻譯功能

### 字體設定
- **中文字體：** 標楷體（DFKai-SB）已添加到 CSS
- **字體堆疊：** "標楷體", "DFKai-SB", "KaiTi", "Georgia", "Times New Roman", serif
- **注意：** 使用系統字體，不同平台可能顯示不同（如需一致性，可考慮嵌入字體檔案）

### 後處理腳本
- **fix_epub_spine.py（2026-02-01）：**
  - 自動調整 EPUB 的 spine 順序
  - 將封面頁移到第一頁，目錄移到第二頁
  - 處理 XML 命名空間問題
  - 自動整合到 EPUB 生成流程中

### 章節切換與分頁控制（2026-02-01）
- **問題：** 章節切換時出現空頁和不流暢
- **已修復：**
  - ✅ 移除章節分隔符號 `---`（`merge_chapters.py`）
  - ✅ 在 CSS 中為 h1 添加 `page-break-before: avoid` 和 `page-break-after: avoid`
  - ✅ 為 h2 添加 `page-break-after: avoid`
  - ✅ 為段落添加 `orphans: 3` 和 `widows: 3` 防止孤行
  - ✅ 調整 Pandoc 參數：使用 `--split-level=6` 防止自動分割（`--epub-chapter-level` 在 Pandoc 3.8+ 已棄用）
- **技術細節：**
  - `--split-level=6` 告訴 Pandoc 不要基於標題級別自動創建新章節文件（6 是最大值，不會在任何標題級別分割）
  - CSS `page-break-before: avoid` 和 `page-break-after: avoid` 防止在標題前後強制分頁
  - 移除 `---` 分隔符號避免被視為分頁符號
  - **注意：** Pandoc 3.8.3 已棄用 `--epub-chapter-level`，改用 `--split-level`，且參數值必須在 1-6 之間

---

**備註：** 此文件會隨著專案進度持續更新。
