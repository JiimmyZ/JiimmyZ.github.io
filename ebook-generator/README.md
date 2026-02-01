# Camino Ebook Generator

A focused, production-ready ebook generator for the Camino project. Generates bilingual EPUB files from Markdown content with automatic translation, image optimization, and proper formatting.

## Features

- **AST-Based Translation**: Preserves Markdown structure (links, tables, code blocks) while translating only text content
- **Async I/O**: 10-20x faster processing with concurrent image downloads and API calls
- **Image Optimization**: Automatic resizing, compression, and optional grayscale conversion for e-readers
- **Dockerized**: Single `docker run` command, no system dependencies
- **Translation Caching**: Avoids redundant API calls with persistent cache

## Architecture

- **YAGNI Principle**: No abstract base classes, no plugin systems, no YAML configs
- **Python Configuration**: Simple `config.py` with variables
- **Single-Purpose**: Dedicated to Camino project, refactor later if needed

## Project Structure

```
ebook-generator/
├── Dockerfile                 # Bundles Python + Pandoc
├── requirements.txt          # Python dependencies
├── config.py                 # Python configuration variables
├── main.py                   # Single entry point script
├── src/
│   ├── markdown_parser.py    # AST parsing (marko)
│   ├── translator.py         # AST-based translation with Gemini
│   ├── image_processor.py     # Async image download + optimization
│   ├── cover_generator.py     # Cover page generation
│   └── pandoc_wrapper.py     # Pandoc subprocess wrapper
├── assets/
│   └── styles.css            # EPUB stylesheet
├── cache/
│   └── translations.json     # Translation cache
└── output/
    └── camino_pilgrim.epub   # Final output
```

## Setup

### Prerequisites

- Docker (for containerized execution)
- OR Python 3.11+ with Pandoc installed locally

### Configuration

1. Set your Gemini API key:
   ```bash
   export GEMINI_API_KEY="your-api-key-here"
   ```
   Or create a `.env` file:
   ```
   GEMINI_API_KEY=your-api-key-here
   ```

2. Update `config.py` with your source paths:
   ```python
   SOURCE_DIR = Path("path/to/your/content/travelogue/camino")
   CHAPTERS = [f"ch{i}/index.md" for i in range(1, 10)]
   ```

## Usage

### Docker (Recommended)

```bash
# Build Docker image
docker build -t camino-ebook .

# Run (with .env file for GEMINI_API_KEY)
docker run --env-file .env -v $(pwd)/output:/app/output camino-ebook
```

### Local Execution

```bash
# Install dependencies
pip install -r requirements.txt

# Ensure Pandoc is installed
# On Ubuntu/Debian: sudo apt-get install pandoc
# On macOS: brew install pandoc
# On Windows: Download from https://pandoc.org/installing.html

# Run
python main.py
```

## Processing Flow

1. **Parse Markdown**: Convert all chapters to AST
2. **Extract Images**: Find all image URLs in Markdown
3. **Download Images**: Async download with semaphore (20 concurrent)
4. **Optimize Images**: Resize, compress, optional grayscale
5. **Extract Text Nodes**: Get all text content from AST
6. **Translate**: Async translate with Gemini API (10 concurrent)
7. **Update AST**: Replace text nodes with translations
8. **Generate Cover**: Create cover page Markdown
9. **Combine**: Merge all chapters
10. **Generate EPUB**: Use Pandoc to create final EPUB

## Configuration Options

Edit `config.py` to customize:

- **Image Processing**:
  - `MAX_IMAGE_WIDTH`, `MAX_IMAGE_HEIGHT`: Target e-reader resolution
  - `IMAGE_QUALITY`: JPEG compression (1-100)
  - `GRAYSCALE_MODE`: Convert to grayscale for smaller file size

- **Translation**:
  - `TRANSLATION_SEMAPHORE`: Max concurrent API calls (default: 10)
  - `TRANSLATION_CACHE`: Path to cache file

- **EPUB Metadata**:
  - `COVER_TITLE_ZH`, `COVER_TITLE_EN`: Cover page titles
  - `EPUB_METADATA`: Title, author, language, description

## Output

- **EPUB File**: `output/camino_pilgrim.epub`
- **Optimized Images**: `output/images/`
- **Translation Cache**: `cache/translations.json`

Target file size: **<50MB** for optimal e-reader performance.

## Troubleshooting

### Translation Errors

If translation fails, check:
- `GEMINI_API_KEY` is set correctly
- API quota/rate limits
- Network connectivity

Translation errors are logged but don't stop processing (original text is preserved).

### Image Download Failures

Failed image downloads are logged but don't stop processing. Check:
- Image URLs are accessible
- Network connectivity
- Cloudinary/CDN access if using external images

### Pandoc Errors

Ensure Pandoc is installed and accessible:
```bash
pandoc --version
```

Check Pandoc error messages in console output.

## License

Internal project - not for distribution.
