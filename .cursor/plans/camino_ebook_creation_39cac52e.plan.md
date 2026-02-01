---
name: Universal Ebook Generator
overview: Create a reusable, configurable ebook generation tool that can process markdown content from various sources, apply different themes/layouts, and generate bilingual EPUB ebooks with images and beautiful typography.
todos:
  - id: setup
    content: 創建新專案目錄結構（模組化架構）、配置檔案系統（YAML）、依賴套件（requirements.txt）
    status: pending
  - id: config_system
    content: 實作配置載入器（config_loader.py），支援 YAML 配置檔案驗證與載入
    status: pending
    dependencies:
      - setup
  - id: parser_system
    content: 建立解析器系統（base_parser.py, hugo_parser.py），支援可插拔的來源格式
    status: pending
    dependencies:
      - setup
  - id: parse_markdown
    content: 使用 Hugo parser 解析所有 9 個章節的 markdown 檔案，提取內容與 frontmatter
    status: pending
    dependencies:
      - parser_system
  - id: image_source_system
    content: 建立圖片來源系統（base_source.py, cloudinary.py），支援可插拔的圖片來源
    status: pending
    dependencies:
      - setup
  - id: download_images
    content: 使用 Cloudinary 處理器下載所有圖片（約 200+ 張），儲存到本地並更新連結
    status: pending
    dependencies:
      - parse_markdown
      - image_source_system
  - id: translator_system
    content: 建立翻譯器系統（base_translator.py），定義翻譯器介面和快取機制
    status: pending
    dependencies:
      - setup
  - id: gemini_translator
    content: 實作 Gemini 翻譯器（gemini_translator.py），整合 Google Gemini API，實作 API key 安全讀取（環境變數優先）
    status: pending
    dependencies:
      - translator_system
      - config_system
  - id: translate_content
    content: 使用 Gemini 翻譯引擎將中文內容翻譯為英文，支援可配置的翻譯策略（段落對照、章節對照等），實作翻譯快取避免重複翻譯
    status: pending
    dependencies:
      - parse_markdown
      - gemini_translator
  - id: theme_system
    content: 建立主題系統（base_theme.py），支援主題模板和 CSS 樣式
    status: pending
    dependencies:
      - setup
  - id: create_cover
    content: 使用主題系統生成封面頁，支援模板化設計
    status: pending
    dependencies:
      - theme_system
      - config_system
  - id: convert_to_html
    content: 將 markdown 轉換為符合 EPUB 3.0 規範的 XHTML
    status: pending
    dependencies:
      - parse_markdown
      - translate_content
      - download_images
  - id: design_styles
    content: 建立 Camino 主題的 CSS 樣式表，設定中英文字體、排版、圖片樣式
    status: pending
    dependencies:
      - theme_system
  - id: build_epub
    content: 使用 EPUB builder 生成 metadata 檔案（content.opf, toc.ncx）並打包成 .epub 檔案
    status: pending
    dependencies:
      - convert_to_html
      - create_cover
      - design_styles
      - config_system
  - id: create_camino_config
    content: 建立 Camino 專案的配置檔案（configs/camino.yaml）作為使用範例
    status: pending
    dependencies:
      - config_system
---

# Camino 電子書製作計畫

## 專案定位

這是一個**通用的、可重複使用的電子書生成工具**，設計目標：

1. **可配置性**：透過配置檔案定義不同的專案設定
2. **可擴展性**：模組化設計，支援不同的來源格式、排版主題、翻譯策略
3. **可重用性**：核心功能可重複使用，只需更換配置檔案即可生成不同的電子書
4. **靈活性**：支援多種來源格式（Hugo markdown、一般 markdown、其他格式）

**首次使用**：以 Camino 朝聖之路的電子書作為第一個實作案例。

## 專案結構

```
ebook-generator/                 # 新專案根目錄（通用工具）
├── README.md                    # 專案說明與使用指南
├── requirements.txt             # Python 依賴套件
├── setup.py                     # 安裝腳本（可選）
├── src/
│   ├── __init__.py
│   ├── core/                    # 核心功能模組
│   │   ├── __init__.py
│   │   ├── config_loader.py     # 配置檔案載入器
│   │   ├── content_parser.py    # 內容解析器（支援多種格式）
│   │   ├── image_processor.py   # 圖片處理器（支援多種來源）
│   │   ├── translator.py        # 翻譯引擎（可插拔）
│   │   ├── html_converter.py    # Markdown/HTML 轉換器
│   │   ├── epub_builder.py      # EPUB 生成器
│   │   └── cover_generator.py    # 封面生成器
│   ├── translators/              # 不同翻譯引擎的實作
│   │   ├── __init__.py
│   │   ├── base_translator.py   # 基礎翻譯器介面
│   │   ├── gemini_translator.py # Gemini API 翻譯器
│   │   ├── google_translator.py  # Google Translate（備用）
│   │   └── cache.py              # 翻譯快取機制
│   ├── themes/                  # 排版主題系統
│   │   ├── __init__.py
│   │   ├── base_theme.py        # 基礎主題類別
│   │   ├── camino_theme.py      # Camino 專用主題（範例）
│   │   └── default_theme.py     # 預設主題
│   ├── parsers/                 # 不同來源格式的解析器
│   │   ├── __init__.py
│   │   ├── hugo_parser.py       # Hugo markdown 解析器
│   │   ├── markdown_parser.py   # 標準 markdown 解析器
│   │   └── base_parser.py       # 基礎解析器介面
│   ├── image_sources/           # 不同圖片來源的處理器
│   │   ├── __init__.py
│   │   ├── cloudinary.py        # Cloudinary 圖片下載
│   │   ├── local.py             # 本地圖片處理
│   │   └── base_source.py       # 基礎圖片來源介面
│   └── main.py                  # 主程式入口
├── configs/                     # 配置檔案目錄
│   ├── camino.yaml              # Camino 專案配置（範例）
│   └── example.yaml             # 配置檔案範本
├── .env.example                 # 環境變數範本（包含 API key 說明）
├── .env                         # 實際環境變數（不提交到版本控制）
├── cache/                       # 快取目錄
│   └── translations.json        # 翻譯快取檔案
├── themes/                      # 主題配置檔案
│   ├── camino/
│   │   ├── styles.css           # CSS 樣式
│   │   ├── cover_template.html  # 封面模板
│   │   └── theme_config.yaml    # 主題配置
│   └── default/
│       ├── styles.css
│       ├── cover_template.html
│       └── theme_config.yaml
├── fonts/                       # 字體檔案
│   ├── chinese/
│   │   └── source-han-sans.woff2
│   └── english/
│       └── merriweather.woff2
├── output/                      # 輸出目錄
│   └── temp/                    # 暫存檔案
├── tests/                       # 測試檔案
│   └── test_*.py
└── .gitignore
```

## 設計原則

### 1. 配置驅動（Configuration-Driven）

- 所有設定透過 YAML/JSON 配置檔案定義
- 支援多個專案配置，切換配置即可生成不同電子書
- 配置包含：來源路徑、主題選擇、翻譯設定、封面資訊等

### 2. 模組化架構（Modular Architecture）

- **Parser 模組**：支援不同來源格式（Hugo、標準 Markdown、未來可擴展）
- **Image Source 模組**：支援不同圖片來源（Cloudinary、本地、未來可擴展）
- **Theme 模組**：支援不同排版主題，可自訂 CSS 和模板
- **Translator 模組**：支援不同翻譯引擎（Google Translate、DeepL、未來可擴展）

### 3. 可擴展性（Extensibility）

- 使用介面/抽象類別定義標準，易於新增新功能
- 插件式設計，新功能可獨立開發並整合

## 配置檔案範例

### `configs/camino.yaml`

```yaml
project:
  name: "Camino Pilgrim"
  output_filename: "camino_pilgrim.epub"
  
source:
  type: "hugo"  # hugo, markdown, custom
  path: "C:/Users/JZ/Desktop/myblog/content/travelogue/camino"
  pattern: "ch*/index.md"  # 檔案匹配模式
  
content:
  chapters:
 - "ch1"
 - "ch2"
    # ... ch9
  frontmatter:
    extract: true
    fields: ["title", "date"]
    
images:
  source: "cloudinary"  # cloudinary, local, custom
  download: true
  optimize: true
  max_size: "2MB"
  
translation:
  enabled: true
  source_lang: "zh-TW"
  target_lang: "en"
  provider: "gemini"  # gemini, google, deepl, custom
  api_key: "${GEMINI_API_KEY}"  # 從環境變數讀取，或直接在配置中設定
  layout: "parallel"  # parallel (中英對照), sequential (先中後英)
  model: "gemini-pro"  # Gemini 模型選擇
  
theme:
  name: "camino"
  custom_fonts:
    chinese: "fonts/chinese/source-han-sans.woff2"
    english: "fonts/english/merriweather.woff2"
  
cover:
  type: "text"  # text, image, custom
  title_zh: "萬里之外的朝聖者 台灣朝聖者見聞錄"
  title_en: "Pilgrim from 10,000km Away: A Taiwanese Pilgrim's Journey"
  template: "themes/camino/cover_template.html"
  
metadata:
  title: "Camino Pilgrim"
  author: "JZ"
  language: "zh-TW,en"
  description: "A journey along the Camino de Santiago"
```

## 技術架構

### 1. 電子書格式選擇

- **格式**: EPUB 3.0（支援圖片、CSS 樣式、多語言）
- **優點**: 廣泛支援、可自訂排版、支援圖片嵌入、支援中英文字體

### 1.1 核心工具：Pandoc

**重要發現**：使用 **Pandoc** 作為核心轉換引擎，可以大幅簡化架構設計。

**Pandoc 的優勢**：

- ✅ 直接從 Markdown 轉換為 EPUB 3.0
- ✅ 支援自定義 CSS 樣式表
- ✅ 支援 EPUB 元數據（metadata）
- ✅ 自動處理圖片嵌入
- ✅ 自動生成目錄（TOC）
- ✅ 支援多語言和自定義字體
- ✅ 成熟穩定，廣泛使用
- ✅ 減少手動構建 EPUB 的複雜度

**架構調整**：

- 使用 Pandoc 處理 Markdown → EPUB 的核心轉換
- 保留自定義模組：翻譯、圖片處理、主題系統
- 簡化 `html_converter.py` 和 `epub_builder.py`（改為 Pandoc 包裝器）

### 2. 檔案結構

```
ebook/
├── META-INF/
│   └── container.xml
├── OEBPS/
│   ├── content.opf (metadata)
│   ├── toc.ncx (目錄)
│   ├── styles/
│   │   └── stylesheet.css (樣式)
│   ├── fonts/
│   │   ├── chinese-font.woff2 (中文字體，如思源黑體)
│   │   └── english-font.woff2 (英文字體，如 Merriweather)
│   ├── images/
│   │   └── [所有下載的圖片]
│   ├── cover.xhtml (封面頁)
│   ├── ch1.xhtml
│   ├── ch2.xhtml
│   └── ... (ch9.xhtml)
└── mimetype
```

### 3. 處理流程

#### 步驟 1: 設定來源路徑與解析 Markdown 檔案

- 在 `config.py` 中設定來源路徑：`C:\Users\JZ\Desktop\myblog\content\travelogue\camino`
- 讀取所有 `ch1/index.md` 到 `ch9/index.md`（從外部專案讀取）
- 解析 Hugo frontmatter（提取標題、日期等）
- 移除 frontmatter，保留純內容

#### 步驟 2: 圖片處理

- 從 Cloudinary URL 下載所有圖片（約 200+ 張）
- 將圖片儲存到 `ebook/OEBPS/images/` 目錄
- 更新 markdown 中的圖片連結為本地路徑
- 處理影片檔案（轉為靜態圖片或跳過）

#### 步驟 3: 中英文翻譯

- 使用 **Google Gemini API** 將中文內容翻譯為英文（提供更高品質的翻譯）
- API key 從環境變數 `GEMINI_API_KEY` 讀取（安全且方便）
- 採用段落對照方式：中文段落後緊接英文段落
- 保留圖片說明的中英文對照
- 實作翻譯快取機制，避免重複翻譯相同內容（節省 API 成本）

#### 步驟 4: Markdown 轉 EPUB（使用 Pandoc）

- 使用 **Pandoc** 將處理後的 markdown 直接轉換為 EPUB 3.0
- Pandoc 自動處理：
                                                                                                                                - Markdown → XHTML 轉換
                                                                                                                                - EPUB 結構生成（content.opf, toc.ncx）
                                                                                                                                - 圖片嵌入和路徑處理
                                                                                                                                - 樣式表嵌入
- 透過 Pandoc 參數自定義：
                                                                                                                                - 元數據（title, author, language）
                                                                                                                                - CSS 樣式表路徑
                                                                                                                                - 封面頁
                                                                                                                                - 字體嵌入

#### 步驟 5: 封面設計

- 建立純文字封面頁 `cover.xhtml`
- 標題：
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                - 中文：「萬里之外的朝聖者 台灣朝聖者見聞錄」
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                - 英文：「Pilgrim from 10,000km Away: A Taiwanese Pilgrim's Journey」
- 使用優美的 CSS 排版，中英文各自使用合適字體

#### 步驟 6: 樣式設計

- **中文字體**: 思源黑體（Source Han Sans）或 Noto Sans CJK
- **英文字體**: Merriweather 或 Georgia
- 設定適當的行距、字距、段落間距
- 圖片居中顯示，適當大小
- 標題層級清晰

#### 步驟 7: 生成 EPUB（Pandoc 自動處理）

- Pandoc 自動生成完整的 EPUB 結構：
                                                                                                                                - `content.opf`（metadata 檔案）
                                                                                                                                - `toc.ncx`（目錄檔案）
                                                                                                                                - 所有章節的 XHTML 檔案
                                                                                                                                - 打包為 `.epub` 格式
- 我們只需提供：
                                                                                                                                - 處理後的 Markdown 檔案
                                                                                                                                - CSS 樣式表
                                                                                                                                - 圖片檔案（已下載並更新路徑）
                                                                                                                                - 元數據配置

## 實作細節

### 核心模組設計

#### 1. Config Loader (`core/config_loader.py`)

- 載入 YAML/JSON 配置檔案
- 驗證配置有效性
- 提供配置存取介面

#### 2. Content Parser (`core/content_parser.py`)

- 根據配置選擇對應的 parser（Hugo、Markdown 等）
- 統一解析介面，返回標準化內容結構
- 支援 frontmatter 提取

#### 3. Image Processor (`core/image_processor.py`)

- 根據配置選擇對應的圖片來源處理器
- 下載、優化、重命名圖片
- 更新內容中的圖片連結（更新為相對路徑，供 Pandoc 使用）

#### 3.1 HTML Converter (`core/html_converter.py`) **[簡化]**

- **調整**：不再需要手動轉換 Markdown → HTML
- 改為 Markdown 預處理器：
                                                                                                                                - 處理特殊格式（如需要）
                                                                                                                                - 確保 Markdown 符合 Pandoc 標準
                                                                                                                                - 保留給 Pandoc 處理實際轉換

#### 4. Translator (`core/translator.py`)

- 根據配置選擇翻譯引擎（Gemini、Google Translate、DeepL 等）
- **Gemini 翻譯器**：使用 Google Gemini API 進行高品質翻譯
- 支援不同的翻譯策略（段落對照、章節對照等）
- 快取翻譯結果（避免重複翻譯，節省 API 成本）
- API key 管理：支援環境變數、配置檔案、安全儲存

#### 5. Pandoc Wrapper (`core/pandoc_wrapper.py`) **[新增]**

- 封裝 Pandoc 命令列工具
- 提供 Python 介面呼叫 Pandoc
- 處理 Pandoc 參數配置：
                                - 輸入檔案（Markdown）
                                - 輸出格式（EPUB 3.0）
                                - CSS 樣式表
                                - 元數據（title, author, language）
                                - 字體嵌入
                                - 封面頁
- 錯誤處理和驗證

**Pandoc 使用範例**：

```python
# src/core/pandoc_wrapper.py

import subprocess
from pathlib import Path
from typing import Optional, List

def generate_epub(
    input_files: List[str],
    output_file: str,
    css_file: Optional[str] = None,
    metadata: Optional[dict] = None,
    cover_image: Optional[str] = None,
    fonts: Optional[List[str]] = None
) -> bool:
    """
    使用 Pandoc 生成 EPUB 3.0
    
    Args:
        input_files: Markdown 檔案列表（按順序）
        output_file: 輸出 EPUB 檔案路徑
        css_file: CSS 樣式表路徑
        metadata: 元數據字典（title, author, language 等）
        cover_image: 封面圖片路徑（可選）
        fonts: 字體檔案列表（可選）
    
    Returns:
        成功返回 True，失敗返回 False
    """
    cmd = ["pandoc"]
    
    # 輸入檔案
    cmd.extend(input_files)
    
    # 輸出格式
    cmd.extend(["-f", "markdown", "-t", "epub3"])
    
    # 輸出檔案
    cmd.extend(["-o", output_file])
    
    # CSS 樣式表
    if css_file:
        cmd.extend(["--css", css_file])
    
    # 元數據
    if metadata:
        for key, value in metadata.items():
            cmd.extend([f"--epub-metadata={key}:{value}"])
        # 或使用 metadata 檔案
        # cmd.extend(["--epub-metadata", "metadata.xml"])
    
    # 封面
    if cover_image:
        cmd.extend(["--epub-cover-image", cover_image])
    
    # 字體
    if fonts:
        for font in fonts:
            cmd.extend(["--epub-embed-font", font])
    
    # 其他選項
    cmd.extend([
        "--standalone",  # 生成完整文檔
        "--toc",  # 生成目錄
        "--toc-depth=3",  # 目錄深度
    ])
    
    try:
        result = subprocess.run(
            cmd,
            check=True,
            capture_output=True,
            text=True
        )
        return True
    except subprocess.CalledProcessError as e:
        print(f"Pandoc 錯誤: {e.stderr}")
        return False
    except FileNotFoundError:
        print("錯誤: 找不到 Pandoc。請先安裝 Pandoc。")
        return False
```

**實際使用範例**：

```python
# 生成 EPUB
success = generate_epub(
    input_files=[
        "cover.md",
        "ch1.md",
        "ch2.md",
        # ... ch9.md
    ],
    output_file="output/camino_pilgrim.epub",
    css_file="themes/camino/styles.css",
    metadata={
        "title": "Camino Pilgrim",
        "author": "JZ",
        "language": "zh-TW,en",
        "description": "A journey along the Camino de Santiago"
    },
    fonts=[
        "fonts/chinese/source-han-sans.woff2",
        "fonts/english/merriweather.woff2"
    ]
)
```

#### 4.1 Gemini Translator (`translators/gemini_translator.py`)

**核心功能**：

- 整合 `google-generativeai` 套件
- 實作 `BaseTranslator` 介面
- 支援批次翻譯和單句翻譯
- 自動重試機制（處理 API 限制）
- 翻譯品質優化提示詞

**API Key 讀取流程**：

1. 檢查環境變數 `GEMINI_API_KEY`
2. 讀取 `.env` 檔案
3. 從配置檔案讀取（支援 `${VAR}` 格式）
4. 如果都沒有，提示用戶輸入

**快取機制**：

- 使用 MD5 hash 作為快取 key
- 快取檔案：`cache/translations.json`
- 支援清除快取功能
- 避免重複翻譯相同內容

#### 6. Theme System (`themes/`)

- 基礎主題類別定義標準介面
- 每個主題包含：CSS、封面模板、配置檔案
- 支援主題繼承和覆蓋

#### 7. EPUB Builder (`core/epub_builder.py`) **[簡化]**

- **調整**：不再手動構建 EPUB 結構
- 改為 Pandoc 的包裝器：
                                                                                                                                - 準備 Pandoc 所需的檔案（Markdown、CSS、圖片）
                                                                                                                                - 呼叫 `pandoc_wrapper.py` 生成 EPUB
                                                                                                                                - 處理後續優化（如需要）

### 使用方式

#### 0. 安裝 Pandoc（必要）

**Windows**：

```bash
# 方式 1: 使用 Chocolatey
choco install pandoc

# 方式 2: 使用 Scoop
scoop install pandoc

# 方式 3: 從官網下載安裝程式
# https://pandoc.org/installing.html

# 驗證安裝
pandoc --version
```

**注意**：Pandoc 是系統級工具，需要單獨安裝。Python 套件 `pypandoc` 只是包裝器，仍需要系統已安裝 Pandoc。

#### 1. 設定 API Key

**重要說明**：我無法直接存取 Cursor 設定中的 API key，但程式碼會自動嘗試多種方式讀取：

```bash
# 方式 1: 環境變數（推薦，在 Cursor 終端中設定）
# Windows PowerShell:
$env:GEMINI_API_KEY="your-api-key-here"

# Windows CMD:
set GEMINI_API_KEY=your-api-key-here

# 方式 2: .env 檔案（最方便，一次設定永久使用）
# 在專案根目錄建立 .env 檔案：
echo GEMINI_API_KEY=your-api-key-here > .env

# 方式 3: 配置檔案中直接設定（不推薦，但可用於測試）
# 在 configs/camino.yaml 中：
# translation:
#   api_key: "your-api-key-here"  # 直接寫入（不提交到 git）
```

**程式碼會按以下優先順序讀取 API key**：

1. 環境變數 `GEMINI_API_KEY`（最高優先）
2. `.env` 檔案中的 `GEMINI_API_KEY`
3. 配置檔案中的 `translation.api_key`
4. 如果都沒有，程式會提示用戶輸入（互動模式）

**建議**：使用 `.env` 檔案，這樣設定一次後就不需要每次都輸入。

#### 2. 執行生成

```bash
# 使用預設配置
python src/main.py --config configs/camino.yaml

# 指定輸出目錄
python src/main.py --config configs/camino.yaml --output ./my_ebooks

# 僅生成特定章節（開發測試用）
python src/main.py --config configs/camino.yaml --chapters ch1,ch2

# 清除翻譯快取（重新翻譯）
python src/main.py --config configs/camino.yaml --clear-cache
```

### Gemini 翻譯器實作細節

#### API Key 管理實作

```python
# src/translators/gemini_translator.py

import os
from dotenv import load_dotenv
from typing import Optional
import hashlib
import json
from pathlib import Path

def get_api_key(config: dict) -> Optional[str]:
    """
    讀取 API key，優先順序：
    1. 環境變數 GEMINI_API_KEY
    2. .env 檔案
    3. 配置檔案中的 api_key
    4. 互動式輸入（如果都沒有）
    """
    # 載入 .env 檔案
    load_dotenv()
    
    # 優先順序 1: 環境變數
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key:
        return api_key
    
    # 優先順序 2: 配置檔案
    api_key = config.get("translation", {}).get("api_key")
    if api_key:
        # 支援 ${VAR} 格式的環境變數替換
        if api_key.startswith("${") and api_key.endswith("}"):
            var_name = api_key[2:-1]
            api_key = os.getenv(var_name)
        if api_key:
            return api_key
    
    # 優先順序 3: 互動式輸入
    print("未找到 GEMINI_API_KEY，請輸入您的 API key:")
    api_key = input("GEMINI_API_KEY: ").strip()
    if api_key:
        # 可選：自動儲存到 .env 檔案
        save_to_env = input("是否儲存到 .env 檔案？(y/n): ").strip().lower()
        if save_to_env == 'y':
            with open('.env', 'a') as f:
                f.write(f"\nGEMINI_API_KEY={api_key}\n")
        return api_key
    
    return None

class TranslationCache:
    """翻譯快取機制"""
    def __init__(self, cache_file: str = "cache/translations.json"):
        self.cache_file = Path(cache_file)
        self.cache_file.parent.mkdir(parents=True, exist_ok=True)
        self.cache = self._load_cache()
    
    def _load_cache(self) -> dict:
        """載入快取"""
        if self.cache_file.exists():
            with open(self.cache_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def _save_cache(self):
        """儲存快取"""
        with open(self.cache_file, 'w', encoding='utf-8') as f:
            json.dump(self.cache, f, ensure_ascii=False, indent=2)
    
    def get(self, text: str) -> Optional[str]:
        """取得快取的翻譯"""
        key = hashlib.md5(text.encode('utf-8')).hexdigest()
        return self.cache.get(key)
    
    def set(self, text: str, translation: str):
        """儲存翻譯到快取"""
        key = hashlib.md5(text.encode('utf-8')).hexdigest()
        self.cache[key] = translation
        self._save_cache()
```

#### 翻譯提示詞設計

```python
def create_translation_prompt(chinese_text: str, context: str = "") -> str:
    """
    針對電子書內容優化的提示詞
    """
    prompt = f"""請將以下中文內容翻譯成英文，要求：
1. 保持原文的語調和風格（這是遊記類內容，保持敘述的親切感）
2. 保留專有名詞（如地名、人名）的原始拼寫
3. 確保翻譯自然流暢，符合英文閱讀習慣
4. 如果是對話或引述，保持口語化的自然感
5. 保留原文的段落結構和格式

{context}

中文內容：
{chinese_text}

請只輸出英文翻譯，不要包含任何解釋或註釋。"""
    return prompt
```

### 擴展新功能範例

1. **新增新的來源格式**：

                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                - 在 `parsers/` 建立新的 parser
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                - 實作 `BaseParser` 介面
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                - 在配置檔案中指定 `source.type`

2. **新增新的主題**：

                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                - 在 `themes/` 建立新主題目錄
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                - 建立 CSS、模板、配置檔案
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                - 在配置檔案中指定 `theme.name`

3. **新增新的圖片來源**：

                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                - 在 `image_sources/` 建立新的處理器
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                - 實作 `BaseImageSource` 介面
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                - 在配置檔案中指定 `images.source`

4. **新增新的翻譯引擎**：

                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                - 在 `translators/` 建立新的翻譯器
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                - 實作 `BaseTranslator` 介面
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                - 在配置檔案中指定 `translation.provider`

### 依賴套件

**系統依賴**（需手動安裝）：

- **Pandoc**: 核心轉換工具
                                                                                                                                - Windows: 從 [Pandoc 官網](https://pandoc.org/installing.html) 下載安裝
                                                                                                                                - 或使用 `choco install pandoc`（Chocolatey）
                                                                                                                                - 或使用 `scoop install pandoc`（Scoop）
                                                                                                                                - 驗證安裝：`pandoc --version`

**Python 依賴**：

**核心依賴**：

- `pypandoc>=1.11`: Pandoc 的 Python 包裝器（可選，也可直接用 subprocess）
- `pyyaml>=6.0`: YAML 配置檔案解析
- `pillow>=10.0.0`: 圖片處理（調整大小、優化）
- `requests>=2.31.0`: HTTP 請求（下載圖片、API 呼叫）

**翻譯相關**：

- `google-generativeai>=0.3.0`: Google Gemini API 客戶端（翻譯用）
- `python-dotenv>=1.0.0`: 環境變數管理（API key 安全讀取）

**已移除的依賴**（由 Pandoc 處理）：

- ~~`markdown`~~: Pandoc 內建 Markdown 解析
- ~~`beautifulsoup4`~~: Pandoc 處理 HTML
- ~~`ebooklib`~~: Pandoc 生成 EPUB

**版本要求**：

- Python 3.8+
- Pandoc 2.0+（建議最新版本）
- 所有 Python 依賴套件版本將在 `requirements.txt` 中明確指定

### 封面設計範例

```html
<div class="cover">
  <h1 class="chinese-title">萬里之外的朝聖者</h1>
  <h2 class="chinese-subtitle">台灣朝聖者見聞錄</h2>
  <div class="divider"></div>
  <h1 class="english-title">Pilgrim from 10,000km Away</h1>
  <h2 class="english-subtitle">A Taiwanese Pilgrim's Journey</h2>
</div>
```

## 注意事項

1. **Pandoc 安裝**: Pandoc 是系統級工具，必須先安裝才能使用。建議在 README 中明確說明安裝步驟。

2. **圖片下載**: 需要處理 Cloudinary URL，可能需要 API key 或直接下載公開圖片。下載後更新 Markdown 中的圖片路徑為相對路徑，供 Pandoc 使用。

3. **翻譯品質**: 使用 Gemini API 可提供較高品質的翻譯，但仍建議後續人工校對。

4. **API Key 安全**: 

                                                                                                                                                                                                - 優先使用環境變數（`GEMINI_API_KEY`）
                                                                                                                                                                                                - 避免將 API key 直接寫入配置檔案並提交到版本控制
                                                                                                                                                                                                - 使用 `.env` 檔案（已加入 `.gitignore`）
                                                                                                                                                                                                - 程式碼會自動處理 API key 的讀取，支援多種方式

5. **API 成本**: Gemini 免費版有使用限制，建議實作快取機制避免重複翻譯。

6. **檔案大小**: 200+ 張圖片可能讓 EPUB 檔案較大（建議壓縮圖片）。

7. **字體授權**: 使用開源字體（思源黑體、Merriweather）避免授權問題。

8. **Pandoc 參數**: 需要仔細配置 Pandoc 參數以確保 EPUB 3.0 格式正確，包括：

                                                                                                                                                                                                - `--epub-version=3`
                                                                                                                                                                                                - `--epub-cover-image`（如使用圖片封面）
                                                                                                                                                                                                - `--css`（CSS 樣式表）
                                                                                                                                                                                                - `--epub-metadata`（元數據）
                                                                                                                                                                                                - `--epub-embed-font`（字體嵌入）

## 輸出

### 首次使用（Camino 專案）

- `output/camino_pilgrim.epub`: 最終電子書檔案

### 未來使用

- 只需建立新的配置檔案（如 `configs/my_new_book.yaml`）
- 選擇或建立新的主題（如 `themes/my_theme/`）
- 執行 `python src/main.py --config configs/my_new_book.yaml`
- 即可生成新的電子書

## 擴展性設計

### 未來可擴展的功能

1. **PDF 輸出**：新增 PDF 生成器模組
2. **更多來源格式**：Word、HTML、其他 CMS 格式
3. **更多圖片來源**：Imgur、S3、其他 CDN
4. **更多翻譯引擎**：OpenAI、Claude、本地翻譯模型（Gemini 已實作）
5. **互動式封面**：支援圖片封面、動態封面
6. **多語言支援**：不只中英文，支援任意語言對
7. **批次處理**：一次處理多個專案配置
8. **Web UI**：提供網頁介面進行配置和生成

## 開發流程建議

### 階段 1: 基礎架構（Setup）

1. 建立專案目錄結構
2. 設定依賴套件和環境
3. 實作配置載入器

### 階段 2: 內容處理（Content Processing）

1. 實作 Hugo parser
2. 實作圖片下載器（Cloudinary）
3. 實作 Markdown 轉 HTML

### 階段 3: 翻譯功能（Translation）

1. 實作翻譯器基礎架構
2. 整合 Gemini API
3. 實作快取機制

### 階段 4: 主題與樣式（Theming）

1. 建立主題系統
2. 設計 Camino 主題（CSS 樣式表）
3. 實作封面生成器（Markdown 或 HTML）

### 階段 5: Pandoc 整合（Pandoc Integration）

1. 實作 Pandoc 包裝器（`pandoc_wrapper.py`）
2. 測試 Pandoc 命令列參數
3. 整合 CSS、字體、元數據
4. 驗證 EPUB 輸出品質

### 階段 6: EPUB 生成（EPUB Generation）

1. 整合所有模組
2. 使用 Pandoc 生成 EPUB
3. 測試完整流程
4. 驗證 EPUB 檔案格式

### 階段 7: 優化與測試（Optimization）

1. 圖片優化
2. 翻譯品質調整
3. Pandoc 參數調優
4. 錯誤處理和日誌
5. 完整測試

## 測試策略

### 單元測試

- 每個模組獨立測試
- Mock 外部 API 呼叫
- 測試邊界情況

### 整合測試

- 測試完整生成流程
- 驗證 EPUB 檔案格式
- 檢查翻譯品質

### 效能測試

- 大量圖片處理
- 長文本翻譯
- 快取機制效率

## 錯誤處理

### API 錯誤

- Gemini API 限制處理
- 網路錯誤重試機制
- API key 驗證

### 檔案錯誤

- 來源檔案不存在
- 圖片下載失敗
- 權限問題

### 配置錯誤

- 配置檔案格式驗證
- 必要欄位檢查
- 路徑有效性驗證