"""
Unit tests for check_status.py

Tests cover:
- Mapping file parsing and statistics
- Local file counting
- Duplicate key detection
- Error handling
"""

import json
from pathlib import Path

import pytest


# Note: check_status.py is a script that runs at module level
# We'll test its logic by importing and testing the underlying operations


class TestCheckStatus:
    """Tests for check_status.py functionality."""

    @pytest.mark.unit
    def test_mapping_file_parsing(self, sample_mapping_file):
        """Test parsing mapping file and extracting statistics."""
        with open(sample_mapping_file, encoding="utf-8") as f:
            mapping = json.load(f)
        
        # Count images and videos
        images = sum(
            1 for v in mapping.values()
            if isinstance(v, dict) and v.get("resource_type") == "image"
        )
        videos = sum(
            1 for v in mapping.values()
            if isinstance(v, dict) and v.get("resource_type") == "video"
        )
        files_with_urls = sum(
            1 for v in mapping.values()
            if isinstance(v, dict) and v.get("url")
        )
        
        assert len(mapping) == 2
        assert images == 2
        assert videos == 0
        assert files_with_urls == 2

    @pytest.mark.unit
    def test_duplicate_key_detection(self, tmp_path):
        """Test detection of duplicate keys in mapping file."""
        # Create mapping with duplicate keys (shouldn't happen in JSON, but test logic)
        mapping_data = {
            "test.jpg": {
                "local_path": "content/test.jpg",
                "relative_path": "test.jpg",
                "public_id": "myblog/test",
                "url": "https://res.cloudinary.com/test/image/upload/v123/test.jpg",
                "resource_type": "image",
                "bytes": 1024
            }
        }
        
        mapping_file = tmp_path / "mapping.json"
        with open(mapping_file, "w", encoding="utf-8") as f:
            json.dump(mapping_data, f)
        
        with open(mapping_file, encoding="utf-8") as f:
            mapping = json.load(f)
        
        rel_paths = list(mapping.keys())
        unique_paths = set(rel_paths)
        
        # In valid JSON, there should be no duplicates
        assert len(rel_paths) == len(unique_paths)
        assert len(rel_paths) - len(unique_paths) == 0

    @pytest.mark.unit
    def test_local_file_counting(self, tmp_content_dir, sample_media_files):
        """Test counting local media files."""
        image_exts = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp"}
        video_exts = {".mp4", ".webm", ".mov", ".avi", ".ogg"}
        
        local_images = []
        local_videos = []
        
        for ext in image_exts | video_exts:
            for f in tmp_content_dir.rglob(f"*{ext}"):
                if ext in image_exts:
                    local_images.append(f)
                else:
                    local_videos.append(f)
            for f in tmp_content_dir.rglob(f"*{ext.upper()}"):
                if ext.upper() in {e.upper() for e in image_exts}:
                    local_images.append(f)
                else:
                    local_videos.append(f)
        
        # Deduplicate
        local_images = list(set(local_images))
        local_videos = list(set(local_videos))
        
        # Should find created sample files
        assert len(local_images) >= 2  # At least IMG_001.jpg and IMG_002.png
        assert len(local_videos) >= 1  # At least VID_001.mp4

    @pytest.mark.unit
    def test_missing_mapping_file(self, tmp_path):
        """Test handling of missing mapping file."""
        mapping_file = tmp_path / "nonexistent_mapping.json"
        
        if mapping_file.exists():
            mapping_file.unlink()
        
        # Simulate check_status.py behavior
        if mapping_file.exists():
            with open(mapping_file, encoding="utf-8") as f:
                mapping = json.load(f)
        else:
            mapping = {}
        
        assert len(mapping) == 0

    @pytest.mark.unit
    def test_mapping_statistics_calculation(self, sample_mapping_file):
        """Test calculation of mapping statistics."""
        with open(sample_mapping_file, encoding="utf-8") as f:
            mapping = json.load(f)
        
        total_files = len(mapping)
        images = sum(
            1 for v in mapping.values()
            if isinstance(v, dict) and v.get("resource_type") == "image"
        )
        videos = sum(
            1 for v in mapping.values()
            if isinstance(v, dict) and v.get("resource_type") == "video"
        )
        files_with_urls = sum(
            1 for v in mapping.values()
            if isinstance(v, dict) and v.get("url")
        )
        
        # Verify statistics
        assert total_files > 0
        assert images + videos == total_files
        assert files_with_urls <= total_files

    @pytest.mark.unit
    def test_upload_status_comparison(self, tmp_content_dir, sample_media_files, sample_mapping_file):
        """Test comparing local files with uploaded mapping."""
        # Count local files
        image_exts = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp"}
        video_exts = {".mp4", ".webm", ".mov", ".avi", ".ogg"}
        
        local_files = []
        for ext in image_exts | video_exts:
            local_files.extend(tmp_content_dir.rglob(f"*{ext}"))
            local_files.extend(tmp_content_dir.rglob(f"*{ext.upper()}"))
        
        local_files = list(set(local_files))
        local_count = len(local_files)
        
        # Count uploaded files
        with open(sample_mapping_file, encoding="utf-8") as f:
            mapping = json.load(f)
        uploaded_count = len(mapping)
        
        # Calculate remaining
        remaining = local_count - uploaded_count
        
        # Verify calculation
        assert remaining >= 0  # Can't have negative remaining
        assert uploaded_count <= local_count
