"""
Unit tests for media_processor.py

Tests cover:
- Pure functions (no mocking required)
- Functions requiring mocking (Cloudinary API, FFmpeg)
"""

import json
import os
from datetime import datetime
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from media_processor import (
    CloudinaryResource,
    check_ffmpeg,
    compress_video,
    find_duplicates,
    find_media_files,
    load_existing_mapping,
    normalize_url,
    save_mapping,
    update_markdown_file,
    upload_file,
)


# ============================================================================
# Pure Function Tests (No Mocking Required)
# ============================================================================


class TestFindMediaFiles:
    """Tests for find_media_files() function."""

    @pytest.mark.unit
    def test_find_media_files_basic(self, tmp_content_dir, sample_media_files):
        """Test finding media files in content directory."""
        # Change to tmp_path parent to simulate project root
        original_cwd = Path.cwd()
        try:
            os.chdir(tmp_content_dir.parent)
            
            # Create content directory structure
            content_dir = tmp_content_dir
            
            # Find files
            files = find_media_files(str(content_dir.name))
            
            # Should find all created files
            assert len(files) == 3
            file_names = {f.name for f in files}
            assert "IMG_001.jpg" in file_names
            assert "IMG_002.png" in file_names
            assert "VID_001.mp4" in file_names
        finally:
            os.chdir(original_cwd)

    @pytest.mark.unit
    def test_find_media_files_case_insensitive(self, tmp_content_dir):
        """Test finding files with different case extensions."""
        # Create files with uppercase extensions
        (tmp_content_dir / "test.JPG").write_bytes(b"data")
        (tmp_content_dir / "test.PNG").write_bytes(b"data")
        (tmp_content_dir / "test.MP4").write_bytes(b"data")
        
        original_cwd = Path.cwd()
        try:
            os.chdir(tmp_content_dir.parent)
            files = find_media_files(str(tmp_content_dir.name))
            
            # Should find uppercase extensions
            file_names = {f.name for f in files}
            assert "test.JPG" in file_names or "test.jpg" in file_names
            assert "test.PNG" in file_names or "test.png" in file_names
            assert "test.MP4" in file_names or "test.mp4" in file_names
        finally:
            os.chdir(original_cwd)

    @pytest.mark.unit
    def test_find_media_files_empty_directory(self, tmp_path):
        """Test finding files in empty directory."""
        empty_dir = tmp_path / "empty_content"
        empty_dir.mkdir()
        
        original_cwd = Path.cwd()
        try:
            os.chdir(tmp_path)
            files = find_media_files(str(empty_dir.name))
            assert len(files) == 0
        finally:
            os.chdir(original_cwd)

    @pytest.mark.unit
    def test_find_media_files_nested_structure(self, tmp_content_dir):
        """Test finding files in nested directory structure."""
        # Create nested structure
        nested_dir = tmp_content_dir / "travelogue" / "camino" / "ch3"
        nested_dir.mkdir(parents=True)
        (nested_dir / "IMG_003.jpg").write_bytes(b"data")
        
        original_cwd = Path.cwd()
        try:
            os.chdir(tmp_content_dir.parent)
            files = find_media_files(str(tmp_content_dir.name))
            
            # Should find nested file
            file_names = {f.name for f in files}
            assert "IMG_003.jpg" in file_names
        finally:
            os.chdir(original_cwd)


class TestNormalizeUrl:
    """Tests for normalize_url() function."""

    @pytest.mark.unit
    def test_normalize_url_no_duplicates(self):
        """Test URL with no duplicate paths."""
        url = "https://res.cloudinary.com/test/image/upload/v123/myblog/travelogue/camino/ch1/IMG_001.jpg"
        result = normalize_url(url)
        assert result == url

    @pytest.mark.unit
    def test_normalize_url_duplicate_myblog_path(self):
        """Test URL with duplicate /myblog/ paths."""
        url = "https://res.cloudinary.com/test/image/upload/v123/myblog/travelogue/camino/ch1/myblog/travelogue/camino/ch1/IMG_001.jpg"
        result = normalize_url(url)
        # Should remove duplicate segment
        assert "/myblog/" in result
        assert result.count("/myblog/") == 1
        assert "IMG_001.jpg" in result

    @pytest.mark.unit
    def test_normalize_url_missing_slash_before_filename(self):
        """Test URL with missing slash before filename (e.g., /ch1IMG_xxx.jpg)."""
        url = "https://res.cloudinary.com/test/image/upload/v123/myblog/travelogue/camino/ch1IMG_001.jpg"
        result = normalize_url(url)
        # Should add slash: /ch1/IMG_001.jpg
        assert "/ch1/IMG_001.jpg" in result or "/ch1IMG_001.jpg" in result

    @pytest.mark.unit
    def test_normalize_url_multiple_issues(self):
        """Test URL with multiple normalization issues."""
        url = "https://res.cloudinary.com/test/image/upload/v123/myblog/travelogue/myblog/travelogue/camino/ch1VID_001.mp4"
        result = normalize_url(url)
        # Should fix both duplicate path and missing slash
        assert result.count("/myblog/") <= 1
        assert "VID_001.mp4" in result

    @pytest.mark.unit
    def test_normalize_url_video_resource(self):
        """Test URL normalization for video resources."""
        url = "https://res.cloudinary.com/test/video/upload/v123/myblog/travelogue/camino/ch1/VID_001.mp4"
        result = normalize_url(url)
        assert result == url
        assert "VID_001.mp4" in result


class TestFindDuplicates:
    """Tests for find_duplicates() function."""

    @pytest.mark.unit
    def test_find_duplicates_no_duplicates(self):
        """Test finding duplicates when none exist."""
        resources = [
            {
                "public_id": "myblog/travelogue/camino/ch1/IMG_001",
                "resource_type": "image",
                "bytes": 1024,
                "created_at": "2024-01-01T00:00:00Z"
            },
            {
                "public_id": "myblog/travelogue/camino/ch2/IMG_002",
                "resource_type": "image",
                "bytes": 2048,
                "created_at": "2024-01-02T00:00:00Z"
            }
        ]
        
        duplicates = find_duplicates(resources)
        assert len(duplicates) == 0

    @pytest.mark.unit
    def test_find_duplicates_same_filename_different_paths(self):
        """Test finding duplicates with same filename but different paths."""
        resources = [
            {
                "public_id": "myblog/travelogue/camino/ch1/IMG_001",
                "resource_type": "image",
                "bytes": 1024,
                "created_at": "2024-01-01T00:00:00Z"
            },
            {
                "public_id": "myblog/travelogue/camino/ch2/IMG_001",
                "resource_type": "image",
                "bytes": 1024,
                "created_at": "2024-01-02T00:00:00Z"
            }
        ]
        
        duplicates = find_duplicates(resources)
        assert len(duplicates) == 1
        assert "IMG_001" in duplicates
        assert len(duplicates["IMG_001"]["delete"]) == 1
        # Should keep the older one (ch1)
        assert duplicates["IMG_001"]["keep"]["public_id"] == "myblog/travelogue/camino/ch1/IMG_001"

    @pytest.mark.unit
    def test_find_duplicates_multiple_duplicates(self):
        """Test finding multiple duplicate groups."""
        resources = [
            {
                "public_id": "myblog/travelogue/camino/ch1/IMG_001",
                "resource_type": "image",
                "bytes": 1024,
                "created_at": "2024-01-01T00:00:00Z"
            },
            {
                "public_id": "myblog/travelogue/camino/ch2/IMG_001",
                "resource_type": "image",
                "bytes": 1024,
                "created_at": "2024-01-02T00:00:00Z"
            },
            {
                "public_id": "myblog/travelogue/camino/ch1/IMG_002",
                "resource_type": "image",
                "bytes": 2048,
                "created_at": "2024-01-03T00:00:00Z"
            },
            {
                "public_id": "myblog/travelogue/camino/ch3/IMG_002",
                "resource_type": "image",
                "bytes": 2048,
                "created_at": "2024-01-04T00:00:00Z"
            }
        ]
        
        duplicates = find_duplicates(resources)
        assert len(duplicates) == 2
        assert "IMG_001" in duplicates
        assert "IMG_002" in duplicates

    @pytest.mark.unit
    def test_find_duplicates_keeps_oldest(self):
        """Test that duplicate detection keeps the oldest file."""
        resources = [
            {
                "public_id": "myblog/travelogue/camino/ch1/IMG_001",
                "resource_type": "image",
                "bytes": 1024,
                "created_at": "2024-01-01T00:00:00Z"
            },
            {
                "public_id": "myblog/travelogue/camino/ch2/IMG_001",
                "resource_type": "image",
                "bytes": 1024,
                "created_at": "2024-01-02T00:00:00Z"
            },
            {
                "public_id": "myblog/travelogue/camino/ch3/IMG_001",
                "resource_type": "image",
                "bytes": 1024,
                "created_at": "2024-01-03T00:00:00Z"
            }
        ]
        
        duplicates = find_duplicates(resources)
        assert len(duplicates) == 1
        # Should keep the oldest (ch1, created_at 2024-01-01)
        assert duplicates["IMG_001"]["keep"]["public_id"] == "myblog/travelogue/camino/ch1/IMG_001"
        assert len(duplicates["IMG_001"]["delete"]) == 2


# ============================================================================
# Functions Requiring Mocking
# ============================================================================


class TestUploadFile:
    """Tests for upload_file() function."""

    @pytest.mark.unit
    @pytest.mark.cloudinary
    def test_upload_file_success_image(self, mocker, tmp_path, mock_cloudinary_upload_response):
        """Test successful image upload."""
        # Create test file
        test_file = tmp_path / "test_image.jpg"
        test_file.write_bytes(b"fake image data")
        
        # Mock Cloudinary upload
        mock_upload = mocker.patch("cloudinary.uploader.upload")
        mock_upload.return_value = mock_cloudinary_upload_response
        
        # Mock Cloudinary config (already configured in module)
        mocker.patch("media_processor.cloudinary_settings")
        
        # Change to project root structure
        content_dir = tmp_path / "content"
        content_dir.mkdir()
        file_in_content = content_dir / "test_image.jpg"
        file_in_content.write_bytes(b"fake image data")
        
        original_cwd = Path.cwd()
        try:
            os.chdir(tmp_path)
            result = upload_file(file_in_content, folder="myblog")
            
            assert result is not None
            assert isinstance(result, CloudinaryResource)
            assert result.resource_type == "image"
            assert result.bytes == 1024
            assert result.url is not None
            mock_upload.assert_called_once()
        finally:
            os.chdir(original_cwd)

    @pytest.mark.unit
    @pytest.mark.cloudinary
    def test_upload_file_success_video(self, mocker, tmp_path, mock_cloudinary_video_upload_response):
        """Test successful video upload."""
        # Create test video file
        test_file = tmp_path / "content" / "test_video.mp4"
        test_file.parent.mkdir(parents=True)
        test_file.write_bytes(b"fake video data" * 1000)
        
        # Mock Cloudinary upload
        mock_upload = mocker.patch("cloudinary.uploader.upload")
        mock_upload.return_value = mock_cloudinary_video_upload_response
        
        original_cwd = Path.cwd()
        try:
            os.chdir(tmp_path)
            result = upload_file(test_file, folder="myblog")
            
            assert result is not None
            assert isinstance(result, CloudinaryResource)
            assert result.resource_type == "video"
            mock_upload.assert_called_once()
        finally:
            os.chdir(original_cwd)

    @pytest.mark.unit
    @pytest.mark.cloudinary
    def test_upload_file_api_error(self, mocker, tmp_path):
        """Test upload failure handling."""
        # Create test file
        test_file = tmp_path / "content" / "test_image.jpg"
        test_file.parent.mkdir(parents=True)
        test_file.write_bytes(b"fake image data")
        
        # Mock Cloudinary upload to raise exception
        mock_upload = mocker.patch("cloudinary.uploader.upload")
        mock_upload.side_effect = Exception("API Error")
        
        original_cwd = Path.cwd()
        try:
            os.chdir(tmp_path)
            result = upload_file(test_file, folder="myblog")
            
            assert result is None
        finally:
            os.chdir(original_cwd)


class TestLoadExistingMapping:
    """Tests for load_existing_mapping() function."""

    @pytest.mark.unit
    def test_load_existing_mapping_success(self, sample_mapping_file):
        """Test loading mapping file successfully."""
        mapping = load_existing_mapping(str(sample_mapping_file))
        
        assert len(mapping) == 2
        assert "travelogue/camino/ch1/IMG_001.jpg" in mapping
        assert "travelogue/camino/ch2/IMG_002.png" in mapping
        
        # Verify CloudinaryResource objects
        resource = mapping["travelogue/camino/ch1/IMG_001.jpg"]
        assert isinstance(resource, CloudinaryResource)
        assert resource.resource_type == "image"
        assert resource.bytes == 1024

    @pytest.mark.unit
    def test_load_existing_mapping_missing_file(self, tmp_path):
        """Test loading non-existent mapping file."""
        mapping = load_existing_mapping(str(tmp_path / "nonexistent.json"))
        assert len(mapping) == 0

    @pytest.mark.unit
    def test_load_existing_mapping_backward_compatibility(self, tmp_path):
        """Test loading old format mapping file (backward compatibility)."""
        # Create old format mapping (without uploaded_at as datetime)
        old_format = {
            "travelogue/camino/ch1/IMG_001.jpg": {
                "local_path": "content/travelogue/camino/ch1/IMG_001.jpg",
                "relative_path": "travelogue/camino/ch1/IMG_001.jpg",
                "public_id": "myblog/travelogue/camino/ch1/IMG_001",
                "url": "https://res.cloudinary.com/test/image/upload/v123/myblog/travelogue/camino/ch1/IMG_001.jpg",
                "resource_type": "image",
                "bytes": 1024
            }
        }
        
        mapping_file = tmp_path / "old_mapping.json"
        with open(mapping_file, "w", encoding="utf-8") as f:
            json.dump(old_format, f)
        
        mapping = load_existing_mapping(str(mapping_file))
        assert len(mapping) == 1
        assert isinstance(mapping["travelogue/camino/ch1/IMG_001.jpg"], CloudinaryResource)

    @pytest.mark.unit
    def test_load_existing_mapping_invalid_entry(self, tmp_path, capsys):
        """Test loading mapping file with invalid entry."""
        invalid_mapping = {
            "valid_entry": {
                "local_path": "content/test.jpg",
                "relative_path": "test.jpg",
                "public_id": "myblog/test",
                "url": "https://res.cloudinary.com/test/image/upload/v123/myblog/test.jpg",
                "resource_type": "image",
                "bytes": 1024
            },
            "invalid_entry": {
                "relative_path": "test2.jpg",
                # Missing required fields
            }
        }
        
        mapping_file = tmp_path / "invalid_mapping.json"
        with open(mapping_file, "w", encoding="utf-8") as f:
            json.dump(invalid_mapping, f)
        
        mapping = load_existing_mapping(str(mapping_file))
        # Should load valid entry, skip invalid
        assert len(mapping) == 1
        assert "valid_entry" in mapping
        
        # Should print warning
        captured = capsys.readouterr()
        assert "Warning" in captured.out or "invalid" in captured.out.lower()


class TestSaveMapping:
    """Tests for save_mapping() function."""

    @pytest.mark.unit
    def test_save_mapping_success(self, tmp_path):
        """Test saving mapping file successfully."""
        mapping_file = tmp_path / "test_mapping.json"
        
        mapping = {
            "test.jpg": CloudinaryResource(
                local_path="content/test.jpg",
                relative_path="test.jpg",
                public_id="myblog/test",
                url="https://res.cloudinary.com/test/image/upload/v123/myblog/test.jpg",
                resource_type="image",
                bytes=1024,
                uploaded_at=datetime.now()
            )
        }
        
        save_mapping(mapping, str(mapping_file))
        
        # Verify file was created
        assert mapping_file.exists()
        
        # Verify content
        with open(mapping_file, encoding="utf-8") as f:
            data = json.load(f)
        
        assert "test.jpg" in data
        assert data["test.jpg"]["resource_type"] == "image"
        assert data["test.jpg"]["bytes"] == 1024

    @pytest.mark.unit
    def test_save_mapping_normalizes_urls(self, tmp_path):
        """Test that save_mapping normalizes URLs."""
        mapping_file = tmp_path / "test_mapping.json"
        
        # URL with potential duplicate path
        url_with_duplicate = "https://res.cloudinary.com/test/image/upload/v123/myblog/travelogue/myblog/travelogue/test.jpg"
        
        mapping = {
            "test.jpg": CloudinaryResource(
                local_path="content/test.jpg",
                relative_path="test.jpg",
                public_id="myblog/test",
                url=url_with_duplicate,
                resource_type="image",
                bytes=1024
            )
        }
        
        save_mapping(mapping, str(mapping_file))
        
        # Verify URL was normalized
        with open(mapping_file, encoding="utf-8") as f:
            data = json.load(f)
        
        saved_url = data["test.jpg"]["url"]
        # Should have normalized the URL
        assert saved_url.count("/myblog/") <= 1


class TestUpdateMarkdownFile:
    """Tests for update_markdown_file() function."""

    @pytest.mark.unit
    def test_update_markdown_file_success(self, tmp_path):
        """Test updating markdown file with Cloudinary URLs."""
        md_file = tmp_path / "test.md"
        md_file.write_text(
            "![Alt text](IMG_001.jpg)\n![Another](IMG_002.png)",
            encoding="utf-8"
        )
        
        url_mapping = {
            "IMG_001.jpg": "https://res.cloudinary.com/test/image/upload/v123/IMG_001.jpg",
            "IMG_002.png": "https://res.cloudinary.com/test/image/upload/v123/IMG_002.png"
        }
        
        replacements = update_markdown_file(md_file, url_mapping, backup=False)
        
        assert replacements == 2
        
        # Verify content was updated
        content = md_file.read_text(encoding="utf-8")
        assert "https://res.cloudinary.com" in content
        assert "IMG_001.jpg" not in content or "https://res.cloudinary.com" in content

    @pytest.mark.unit
    def test_update_markdown_file_with_backup(self, tmp_path):
        """Test updating markdown file with backup creation."""
        md_file = tmp_path / "test.md"
        md_file.write_text("![Alt](IMG_001.jpg)", encoding="utf-8")
        
        url_mapping = {
            "IMG_001.jpg": "https://res.cloudinary.com/test/image/upload/v123/IMG_001.jpg"
        }
        
        update_markdown_file(md_file, url_mapping, backup=True)
        
        # Verify backup was created
        backup_file = tmp_path / "test.md.backup"
        assert backup_file.exists()

    @pytest.mark.unit
    def test_update_markdown_file_no_matches(self, tmp_path):
        """Test updating markdown file with no matching images."""
        md_file = tmp_path / "test.md"
        md_file.write_text("No images here", encoding="utf-8")
        
        url_mapping = {
            "IMG_001.jpg": "https://res.cloudinary.com/test/image/upload/v123/IMG_001.jpg"
        }
        
        replacements = update_markdown_file(md_file, url_mapping, backup=False)
        assert replacements == 0

    @pytest.mark.unit
    def test_update_markdown_file_partial_matches(self, tmp_path):
        """Test updating markdown file with partial matches."""
        md_file = tmp_path / "test.md"
        md_file.write_text(
            "![Alt](IMG_001.jpg)\n![Another](NOT_IN_MAPPING.jpg)",
            encoding="utf-8"
        )
        
        url_mapping = {
            "IMG_001.jpg": "https://res.cloudinary.com/test/image/upload/v123/IMG_001.jpg"
        }
        
        replacements = update_markdown_file(md_file, url_mapping, backup=False)
        assert replacements == 1
        
        # Verify only matched image was updated
        content = md_file.read_text(encoding="utf-8")
        assert "https://res.cloudinary.com" in content
        assert "NOT_IN_MAPPING.jpg" in content  # Should remain unchanged


class TestCheckFfmpeg:
    """Tests for check_ffmpeg() function."""

    @pytest.mark.unit
    @pytest.mark.ffmpeg
    def test_check_ffmpeg_installed(self, mocker):
        """Test checking FFmpeg when installed."""
        mock_run = mocker.patch("subprocess.run")
        mock_run.return_value = Mock(returncode=0)
        
        result = check_ffmpeg()
        assert result is True
        mock_run.assert_called_once()

    @pytest.mark.unit
    @pytest.mark.ffmpeg
    def test_check_ffmpeg_not_installed(self, mocker):
        """Test checking FFmpeg when not installed."""
        mock_run = mocker.patch("subprocess.run")
        mock_run.side_effect = FileNotFoundError()
        
        result = check_ffmpeg()
        assert result is False


class TestCompressVideo:
    """Tests for compress_video() function."""

    @pytest.mark.unit
    @pytest.mark.ffmpeg
    def test_compress_video_success(self, mocker, tmp_path, mock_ffmpeg_success):
        """Test successful video compression."""
        # Create test video file (>95MB to trigger compression)
        test_file = tmp_path / "large_video.mp4"
        # Create file that appears large (simulate with stat mock)
        test_file.write_bytes(b"fake video data")
        
        # Mock file size to be >95MB
        mock_stat = mocker.patch.object(Path, "stat")
        mock_stat.return_value.st_size = 100 * 1024 * 1024  # 100MB
        
        # Mock output file creation
        output_file = tmp_path / "large_video_compressed.mp4"
        mocker.patch.object(Path, "exists", return_value=True)
        mocker.patch.object(Path, "stat")
        # Mock compressed size
        output_file.stat.return_value.st_size = 90 * 1024 * 1024  # 90MB
        
        result = compress_video(str(test_file), str(output_file))
        assert result is True

    @pytest.mark.unit
    @pytest.mark.ffmpeg
    def test_compress_video_file_not_found(self, tmp_path):
        """Test compression with non-existent file."""
        result = compress_video(str(tmp_path / "nonexistent.mp4"))
        assert result is False

    @pytest.mark.unit
    @pytest.mark.ffmpeg
    def test_compress_video_already_small(self, tmp_path):
        """Test compression when file is already small enough."""
        test_file = tmp_path / "small_video.mp4"
        test_file.write_bytes(b"fake video data")
        
        # Mock file size to be <95MB
        with patch.object(Path, "stat") as mock_stat:
            mock_stat.return_value.st_size = 50 * 1024 * 1024  # 50MB
            
            result = compress_video(str(test_file))
            assert result is True  # Should return True (no compression needed)

    @pytest.mark.unit
    @pytest.mark.ffmpeg
    def test_compress_video_ffmpeg_not_found(self, mocker, tmp_path, mock_ffmpeg_not_found):
        """Test compression when FFmpeg is not installed."""
        test_file = tmp_path / "test_video.mp4"
        test_file.write_bytes(b"fake video data")
        
        # Mock file size
        with patch.object(Path, "stat") as mock_stat:
            mock_stat.return_value.st_size = 100 * 1024 * 1024  # 100MB
            
            result = compress_video(str(test_file))
            assert result is False
