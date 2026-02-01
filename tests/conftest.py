"""
Shared pytest fixtures for myblog project tests.
"""

import json
import os
import shutil
from pathlib import Path
from typing import Generator
from unittest.mock import Mock

import pytest


@pytest.fixture
def tmp_content_dir(tmp_path: Path) -> Path:
    """Create a temporary content directory structure for testing."""
    content_dir = tmp_path / "content"
    content_dir.mkdir()
    
    # Create subdirectories
    (content_dir / "travelogue" / "camino" / "ch1").mkdir(parents=True)
    (content_dir / "travelogue" / "camino" / "ch2").mkdir(parents=True)
    (content_dir / "poetry").mkdir()
    (content_dir / "essay").mkdir()
    
    return content_dir


@pytest.fixture
def sample_media_files(tmp_content_dir: Path) -> dict[str, Path]:
    """Create sample media files for testing."""
    files = {}
    
    # Create sample images
    img1 = tmp_content_dir / "travelogue" / "camino" / "ch1" / "IMG_001.jpg"
    img1.write_bytes(b"fake image data")
    files["img1"] = img1
    
    img2 = tmp_content_dir / "travelogue" / "camino" / "ch2" / "IMG_002.png"
    img2.write_bytes(b"fake png data")
    files["img2"] = img2
    
    # Create sample video
    vid1 = tmp_content_dir / "travelogue" / "camino" / "ch1" / "VID_001.mp4"
    vid1.write_bytes(b"fake video data" * 100)  # Make it larger
    files["vid1"] = vid1
    
    return files


@pytest.fixture
def sample_mapping_file(tmp_path: Path) -> Path:
    """Create a sample cloudinary_mapping.json file."""
    mapping_file = tmp_path / "cloudinary_mapping.json"
    
    sample_data = {
        "travelogue/camino/ch1/IMG_001.jpg": {
            "local_path": "content/travelogue/camino/ch1/IMG_001.jpg",
            "relative_path": "travelogue/camino/ch1/IMG_001.jpg",
            "public_id": "myblog/travelogue/camino/ch1/IMG_001",
            "url": "https://res.cloudinary.com/test/image/upload/v123/myblog/travelogue/camino/ch1/IMG_001.jpg",
            "resource_type": "image",
            "bytes": 1024,
            "uploaded_at": "2024-01-01T00:00:00"
        },
        "travelogue/camino/ch2/IMG_002.png": {
            "local_path": "content/travelogue/camino/ch2/IMG_002.png",
            "relative_path": "travelogue/camino/ch2/IMG_002.png",
            "public_id": "myblog/travelogue/camino/ch2/IMG_002",
            "url": "https://res.cloudinary.com/test/image/upload/v123/myblog/travelogue/camino/ch2/IMG_002.png",
            "resource_type": "image",
            "bytes": 2048,
            "uploaded_at": "2024-01-02T00:00:00"
        }
    }
    
    with open(mapping_file, "w", encoding="utf-8") as f:
        json.dump(sample_data, f, indent=2, ensure_ascii=False)
    
    return mapping_file


@pytest.fixture
def sample_markdown_file(tmp_path: Path) -> Path:
    """Create a sample markdown file with image and video references."""
    md_file = tmp_path / "test.md"
    
    content = """# Test Post

This is a test post with images and videos.

![Alt text](IMG_001.jpg)

![Another image](IMG_002.png)

![Video](VID_001.mp4)

More content here.
"""
    
    md_file.write_text(content, encoding="utf-8")
    return md_file


@pytest.fixture
def mock_cloudinary_upload_response():
    """Mock Cloudinary upload API response."""
    return {
        "public_id": "myblog/test/image",
        "secure_url": "https://res.cloudinary.com/test/image/upload/v123/myblog/test/image.jpg",
        "url": "https://res.cloudinary.com/test/image/upload/v123/myblog/test/image.jpg",
        "bytes": 1024,
        "format": "jpg",
        "resource_type": "image",
        "created_at": "2024-01-01T00:00:00Z"
    }


@pytest.fixture
def mock_cloudinary_video_upload_response():
    """Mock Cloudinary video upload API response."""
    return {
        "public_id": "myblog/test/video",
        "secure_url": "https://res.cloudinary.com/test/video/upload/v123/myblog/test/video.mp4",
        "url": "https://res.cloudinary.com/test/video/upload/v123/myblog/test/video.mp4",
        "bytes": 1048576,  # 1MB
        "format": "mp4",
        "resource_type": "video",
        "created_at": "2024-01-01T00:00:00Z"
    }


@pytest.fixture
def mock_cloudinary_resources_response():
    """Mock Cloudinary API resources list response."""
    return {
        "resources": [
            {
                "public_id": "myblog/travelogue/camino/ch1/IMG_001",
                "resource_type": "image",
                "bytes": 1024,
                "created_at": "2024-01-01T00:00:00Z"
            },
            {
                "public_id": "myblog/travelogue/camino/ch1/IMG_001",
                "resource_type": "image",
                "bytes": 1024,
                "created_at": "2024-01-02T00:00:00Z"
            },
            {
                "public_id": "myblog/travelogue/camino/ch2/IMG_002",
                "resource_type": "image",
                "bytes": 2048,
                "created_at": "2024-01-03T00:00:00Z"
            }
        ],
        "next_cursor": None
    }


@pytest.fixture
def mock_ffmpeg_success(mocker):
    """Mock successful FFmpeg subprocess call."""
    mock_run = mocker.patch("subprocess.run")
    mock_result = Mock()
    mock_result.returncode = 0
    mock_run.return_value = mock_result
    return mock_run


@pytest.fixture
def mock_ffmpeg_not_found(mocker):
    """Mock FFmpeg not found error."""
    mock_run = mocker.patch("subprocess.run")
    mock_run.side_effect = FileNotFoundError("ffmpeg not found")
    return mock_run


@pytest.fixture
def mock_env_vars(monkeypatch):
    """Mock environment variables for Cloudinary settings."""
    monkeypatch.setenv("CLOUDINARY_CLOUD_NAME", "test_cloud")
    monkeypatch.setenv("CLOUDINARY_API_KEY", "test_key")
    monkeypatch.setenv("CLOUDINARY_API_SECRET", "test_secret")
    return {
        "CLOUDINARY_CLOUD_NAME": "test_cloud",
        "CLOUDINARY_API_KEY": "test_key",
        "CLOUDINARY_API_SECRET": "test_secret"
    }


@pytest.fixture
def cleanup_temp_files():
    """Fixture to ensure temporary files are cleaned up."""
    created_files = []
    
    def _track_file(path: Path):
        created_files.append(path)
        return path
    
    yield _track_file
    
    # Cleanup
    for file_path in created_files:
        if file_path.exists():
            if file_path.is_dir():
                shutil.rmtree(file_path)
            else:
                file_path.unlink()
