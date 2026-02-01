"""Configuration variables for Camino ebook generator."""

import os
from pathlib import Path

# Source paths
SOURCE_DIR = Path("C:/Users/JZ/Desktop/myblog/content/travelogue/camino")
CHAPTERS = [f"ch{i}/index.md" for i in range(1, 10)]

# Translation
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
TRANSLATION_CACHE = Path("cache/translations.json")
TRANSLATION_SEMAPHORE = 10  # Max concurrent API calls

# Image processing
IMAGE_OUTPUT_DIR = Path("output/images")
MAX_IMAGE_WIDTH = 1200  # E-ink device width
MAX_IMAGE_HEIGHT = 1600
IMAGE_QUALITY = 85  # JPEG quality
GRAYSCALE_MODE = False  # Set True for smaller file size
CONCURRENT_DOWNLOADS = 20  # Semaphore limit

# Merged file (won't interfere with website)
MERGED_DIR = Path("ebook-generator/merged")
MERGED_FILE = MERGED_DIR / "camino_merged.md"

# EPUB generation
OUTPUT_FILE = Path("output/camino_pilgrim.epub")
CSS_FILE = Path("assets/styles.css")
COVER_TITLE_ZH = "萬里之外 台灣camino朝聖者見聞錄"
COVER_TITLE_EN = "From 10,000 Kilometers Away: A Taiwanese Camino Pilgrim's Journey"

# Metadata
EPUB_METADATA = {
    "title": "Camino Pilgrim",
    "author": "JZ",
    "language": "zh-TW,en",
    "description": "A journey along the Camino de Santiago",
}
