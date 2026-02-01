"""Configuration for Camino ebook generator using Pydantic."""

import os
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class EpubMetadata(BaseModel):
    """EPUB metadata model."""

    title: str
    author: str
    language: str = Field(default="zh-TW,en")
    description: str


class EbookConfig(BaseSettings):
    """Ebook generator configuration."""

    # Source paths
    source_dir: Path = Field(
        default=Path("C:/Users/JZ/Desktop/myblog/content/travelogue/camino")
    )
    chapters: list[str] = Field(
        default_factory=lambda: [f"ch{i}/index.md" for i in range(1, 10)]
    )

    # Translation
    gemini_api_key: str | None = Field(default=None)
    translation_cache: Path = Field(default=Path("cache/translations.json"))
    translation_semaphore: int = Field(default=10, ge=1, le=50)

    # Image processing
    image_output_dir: Path = Field(default=Path("output/images"))
    max_image_width: int = Field(default=1200, ge=100, le=5000)
    max_image_height: int = Field(default=1600, ge=100, le=5000)
    image_quality: int = Field(default=85, ge=1, le=100)
    grayscale_mode: bool = Field(default=False)
    concurrent_downloads: int = Field(default=20, ge=1, le=100)

    # Merged file
    merged_dir: Path = Field(default=Path("ebook-generator/merged"))

    # EPUB generation
    output_file: Path = Field(default=Path("output/camino_pilgrim.epub"))
    css_file: Path = Field(default=Path("assets/styles.css"))
    cover_title_zh: str = Field(
        default="萬里之外 台灣camino朝聖者見聞錄"
    )
    cover_title_en: str = Field(
        default="From 10,000 Kilometers Away: A Taiwanese Camino Pilgrim's Journey"
    )

    # Metadata
    epub_metadata: EpubMetadata = Field(
        default_factory=lambda: EpubMetadata(
            title="Camino Pilgrim",
            author="JZ",
            language="zh-TW,en",
            description="A journey along the Camino de Santiago",
        )
    )

    @property
    def merged_file(self) -> Path:
        """Get merged file path."""
        return self.merged_dir / "camino_merged.md"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    def __getattr__(self, name: str):
        """
        Backward compatibility: map old UPPER_CASE names to new camelCase names.
        
        This allows existing code using config.IMAGE_OUTPUT_DIR to work
        with the new config.image_output_dir structure.
        """
        # Map old constant names to new field names
        name_mapping = {
            "SOURCE_DIR": "source_dir",
            "CHAPTERS": "chapters",
            "GEMINI_API_KEY": "gemini_api_key",
            "TRANSLATION_CACHE": "translation_cache",
            "TRANSLATION_SEMAPHORE": "translation_semaphore",
            "IMAGE_OUTPUT_DIR": "image_output_dir",
            "MAX_IMAGE_WIDTH": "max_image_width",
            "MAX_IMAGE_HEIGHT": "max_image_height",
            "IMAGE_QUALITY": "image_quality",
            "GRAYSCALE_MODE": "grayscale_mode",
            "CONCURRENT_DOWNLOADS": "concurrent_downloads",
            "MERGED_DIR": "merged_dir",
            "MERGED_FILE": "merged_file",
            "OUTPUT_FILE": "output_file",
            "CSS_FILE": "css_file",
            "COVER_TITLE_ZH": "cover_title_zh",
            "COVER_TITLE_EN": "cover_title_en",
            "EPUB_METADATA": "epub_metadata",
        }
        
        if name in name_mapping:
            return getattr(self, name_mapping[name])
        
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")


# Create singleton instance for backward compatibility
config = EbookConfig()

# Backward compatibility: export old constant names as properties
# This allows both config.IMAGE_OUTPUT_DIR and config.image_output_dir to work
SOURCE_DIR = config.source_dir
CHAPTERS = config.chapters
GEMINI_API_KEY = config.gemini_api_key
TRANSLATION_CACHE = config.translation_cache
TRANSLATION_SEMAPHORE = config.translation_semaphore
IMAGE_OUTPUT_DIR = config.image_output_dir
MAX_IMAGE_WIDTH = config.max_image_width
MAX_IMAGE_HEIGHT = config.max_image_height
IMAGE_QUALITY = config.image_quality
GRAYSCALE_MODE = config.grayscale_mode
CONCURRENT_DOWNLOADS = config.concurrent_downloads
MERGED_DIR = config.merged_dir
MERGED_FILE = config.merged_file
OUTPUT_FILE = config.output_file
CSS_FILE = config.css_file
COVER_TITLE_ZH = config.cover_title_zh
COVER_TITLE_EN = config.cover_title_en
EPUB_METADATA = config.epub_metadata
