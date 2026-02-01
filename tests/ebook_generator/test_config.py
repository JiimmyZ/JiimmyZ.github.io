"""
Unit tests for ebook-generator/config.py

Tests cover:
- Pydantic model validation
- Environment variable loading
- Backward compatibility (UPPER_CASE attribute access)
- Field validation (ranges, types)
- Default value handling
"""

import os
from pathlib import Path

import pytest
from pydantic import ValidationError

# Import config module - adjust path for ebook-generator
import sys
from pathlib import Path

# Add ebook-generator to path
ebook_gen_path = Path(__file__).parent.parent.parent / "ebook-generator"
if str(ebook_gen_path) not in sys.path:
    sys.path.insert(0, str(ebook_gen_path))

try:
    import config
    from config import EbookConfig, EpubMetadata
except ImportError:
    # Skip tests if config module not available
    pytest.skip("ebook-generator/config.py not available", allow_module_level=True)


class TestEpubMetadata:
    """Tests for EpubMetadata model."""

    @pytest.mark.unit
    def test_epub_metadata_creation(self):
        """Test creating EpubMetadata with valid data."""
        metadata = EpubMetadata(
            title="Test Book",
            author="Test Author",
            language="zh-TW,en",
            description="Test description"
        )
        
        assert metadata.title == "Test Book"
        assert metadata.author == "Test Author"
        assert metadata.language == "zh-TW,en"
        assert metadata.description == "Test description"

    @pytest.mark.unit
    def test_epub_metadata_default_language(self):
        """Test EpubMetadata with default language."""
        metadata = EpubMetadata(
            title="Test Book",
            author="Test Author",
            description="Test description"
        )
        
        assert metadata.language == "zh-TW,en"  # Default value

    @pytest.mark.unit
    def test_epub_metadata_validation(self):
        """Test EpubMetadata field validation."""
        # Should raise ValidationError for missing required fields
        with pytest.raises(ValidationError):
            EpubMetadata(
                title="Test Book"
                # Missing author and description
            )


class TestEbookConfig:
    """Tests for EbookConfig model."""

    @pytest.mark.unit
    def test_ebook_config_defaults(self):
        """Test EbookConfig with default values."""
        # Clear environment to test defaults
        env_backup = {}
        for key in ["GEMINI_API_KEY"]:
            if key in os.environ:
                env_backup[key] = os.environ.pop(key)
        
        try:
            config_instance = EbookConfig()
            
            # Test some default values
            assert config_instance.source_dir is not None
            assert isinstance(config_instance.source_dir, Path)
            assert len(config_instance.chapters) > 0
            assert config_instance.max_image_width == 1200
            assert config_instance.max_image_height == 1600
            assert config_instance.image_quality == 85
        finally:
            # Restore environment
            os.environ.update(env_backup)

    @pytest.mark.unit
    def test_ebook_config_field_validation_ranges(self):
        """Test EbookConfig field validation for ranges."""
        # Test valid ranges
        valid_config = EbookConfig(
            max_image_width=1200,
            max_image_height=1600,
            image_quality=85,
            translation_semaphore=10,
            concurrent_downloads=20
        )
        
        assert valid_config.max_image_width == 1200
        
        # Test invalid ranges
        with pytest.raises(ValidationError):
            EbookConfig(max_image_width=50)  # Below minimum (100)
        
        with pytest.raises(ValidationError):
            EbookConfig(max_image_width=6000)  # Above maximum (5000)
        
        with pytest.raises(ValidationError):
            EbookConfig(image_quality=0)  # Below minimum (1)
        
        with pytest.raises(ValidationError):
            EbookConfig(image_quality=101)  # Above maximum (100)

    @pytest.mark.unit
    def test_ebook_config_environment_variables(self, monkeypatch):
        """Test loading configuration from environment variables."""
        # Set environment variables
        monkeypatch.setenv("GEMINI_API_KEY", "test_api_key_123")
        
        config_instance = EbookConfig()
        
        assert config_instance.gemini_api_key == "test_api_key_123"

    @pytest.mark.unit
    def test_ebook_config_path_validation(self):
        """Test that Path fields are properly validated."""
        config_instance = EbookConfig()
        
        # Verify paths are Path objects
        assert isinstance(config_instance.source_dir, Path)
        assert isinstance(config_instance.image_output_dir, Path)
        assert isinstance(config_instance.output_file, Path)
        assert isinstance(config_instance.css_file, Path)

    @pytest.mark.unit
    def test_ebook_config_backward_compatibility_upper_case(self):
        """Test backward compatibility with UPPER_CASE attribute access."""
        config_instance = EbookConfig()
        
        # Test UPPER_CASE access (should work via __getattr__)
        assert config_instance.IMAGE_OUTPUT_DIR == config_instance.image_output_dir
        assert config_instance.MAX_IMAGE_WIDTH == config_instance.max_image_width
        assert config_instance.MAX_IMAGE_HEIGHT == config_instance.max_image_height
        assert config_instance.IMAGE_QUALITY == config_instance.image_quality
        assert config_instance.SOURCE_DIR == config_instance.source_dir
        assert config_instance.CHAPTERS == config_instance.chapters

    @pytest.mark.unit
    def test_ebook_config_backward_compatibility_invalid_attribute(self):
        """Test that invalid UPPER_CASE attributes raise AttributeError."""
        config_instance = EbookConfig()
        
        with pytest.raises(AttributeError):
            _ = config_instance.INVALID_ATTRIBUTE

    @pytest.mark.unit
    def test_ebook_config_merged_file_property(self):
        """Test merged_file property."""
        config_instance = EbookConfig()
        
        merged_file = config_instance.merged_file
        
        assert isinstance(merged_file, Path)
        assert merged_file.name == "camino_merged.md"
        assert merged_file.parent == config_instance.merged_dir

    @pytest.mark.unit
    def test_ebook_config_epub_metadata_default(self):
        """Test default EpubMetadata creation."""
        config_instance = EbookConfig()
        
        assert config_instance.epub_metadata is not None
        assert isinstance(config_instance.epub_metadata, EpubMetadata)
        assert config_instance.epub_metadata.title == "Camino Pilgrim"
        assert config_instance.epub_metadata.author == "JZ"

    @pytest.mark.unit
    def test_ebook_config_custom_epub_metadata(self):
        """Test custom EpubMetadata in config."""
        custom_metadata = EpubMetadata(
            title="Custom Title",
            author="Custom Author",
            description="Custom description"
        )
        
        config_instance = EbookConfig(epub_metadata=custom_metadata)
        
        assert config_instance.epub_metadata.title == "Custom Title"
        assert config_instance.epub_metadata.author == "Custom Author"

    @pytest.mark.unit
    def test_ebook_config_translation_semaphore_range(self):
        """Test translation_semaphore field validation."""
        # Valid range: 1-50
        valid_config = EbookConfig(translation_semaphore=25)
        assert valid_config.translation_semaphore == 25
        
        with pytest.raises(ValidationError):
            EbookConfig(translation_semaphore=0)  # Below minimum
        
        with pytest.raises(ValidationError):
            EbookConfig(translation_semaphore=51)  # Above maximum

    @pytest.mark.unit
    def test_ebook_config_concurrent_downloads_range(self):
        """Test concurrent_downloads field validation."""
        # Valid range: 1-100
        valid_config = EbookConfig(concurrent_downloads=50)
        assert valid_config.concurrent_downloads == 50
        
        with pytest.raises(ValidationError):
            EbookConfig(concurrent_downloads=0)  # Below minimum
        
        with pytest.raises(ValidationError):
            EbookConfig(concurrent_downloads=101)  # Above maximum

    @pytest.mark.unit
    def test_ebook_config_chapters_default(self):
        """Test default chapters list."""
        config_instance = EbookConfig()
        
        assert len(config_instance.chapters) == 9  # ch1 through ch9
        assert all(chapter.startswith("ch") for chapter in config_instance.chapters)
        assert all(chapter.endswith("/index.md") for chapter in config_instance.chapters)

    @pytest.mark.unit
    def test_ebook_config_custom_chapters(self):
        """Test custom chapters list."""
        custom_chapters = ["ch1/index.md", "ch2/index.md"]
        
        config_instance = EbookConfig(chapters=custom_chapters)
        
        assert config_instance.chapters == custom_chapters
        assert len(config_instance.chapters) == 2
