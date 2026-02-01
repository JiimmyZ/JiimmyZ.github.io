"""
Test utility functions for myblog project tests.
"""

import json
from pathlib import Path
from typing import Any

from media_processor import CloudinaryResource


def create_temp_content_dir(base_path: Path, structure: dict[str, Any]) -> Path:
    """
    Create a temporary content directory structure.
    
    Args:
        base_path: Base temporary path
        structure: Dictionary defining directory structure
            Example: {
                "travelogue/camino/ch1": ["IMG_001.jpg", "VID_001.mp4"],
                "poetry": []
            }
    
    Returns:
        Path to created content directory
    """
    content_dir = base_path / "content"
    content_dir.mkdir()
    
    for rel_path, files in structure.items():
        dir_path = content_dir / rel_path
        dir_path.mkdir(parents=True, exist_ok=True)
        
        for filename in files:
            file_path = dir_path / filename
            # Create empty file or with minimal content
            if filename.endswith((".jpg", ".png", ".gif")):
                file_path.write_bytes(b"fake image data")
            elif filename.endswith((".mp4", ".webm", ".mov")):
                file_path.write_bytes(b"fake video data" * 100)
            else:
                file_path.write_text("", encoding="utf-8")
    
    return content_dir


def create_sample_media_files(content_dir: Path) -> list[Path]:
    """
    Create sample media files in content directory.
    
    Returns:
        List of created file paths
    """
    files = []
    
    # Create sample images
    img1 = content_dir / "travelogue" / "camino" / "ch1" / "IMG_001.jpg"
    img1.parent.mkdir(parents=True, exist_ok=True)
    img1.write_bytes(b"fake jpg data")
    files.append(img1)
    
    img2 = content_dir / "travelogue" / "camino" / "ch2" / "IMG_002.png"
    img2.parent.mkdir(parents=True, exist_ok=True)
    img2.write_bytes(b"fake png data")
    files.append(img2)
    
    # Create sample video
    vid1 = content_dir / "travelogue" / "camino" / "ch1" / "VID_001.mp4"
    vid1.parent.mkdir(parents=True, exist_ok=True)
    vid1.write_bytes(b"fake video data" * 1000)
    files.append(vid1)
    
    return files


def mock_cloudinary_response(
    public_id: str = "myblog/test/image",
    resource_type: str = "image",
    bytes_size: int = 1024,
    url: str | None = None
) -> dict[str, Any]:
    """
    Create a standardized mock Cloudinary API response.
    
    Args:
        public_id: Cloudinary public ID
        resource_type: "image" or "video"
        bytes_size: File size in bytes
        url: Custom URL (if None, generates default)
    
    Returns:
        Mock Cloudinary API response dictionary
    """
    if url is None:
        url = f"https://res.cloudinary.com/test/{resource_type}/upload/v123/{public_id}.jpg"
    
    return {
        "public_id": public_id,
        "secure_url": url,
        "url": url,
        "bytes": bytes_size,
        "format": "jpg" if resource_type == "image" else "mp4",
        "resource_type": resource_type,
        "created_at": "2024-01-01T00:00:00Z"
    }


def create_sample_mapping_file(
    output_path: Path,
    entries: list[dict[str, Any]] | None = None
) -> Path:
    """
    Create a sample cloudinary_mapping.json file.
    
    Args:
        output_path: Path where mapping file should be created
        entries: Optional list of custom entries (uses defaults if None)
    
    Returns:
        Path to created mapping file
    """
    if entries is None:
        entries = [
            {
                "relative_path": "travelogue/camino/ch1/IMG_001.jpg",
                "local_path": "content/travelogue/camino/ch1/IMG_001.jpg",
                "public_id": "myblog/travelogue/camino/ch1/IMG_001",
                "url": "https://res.cloudinary.com/test/image/upload/v123/myblog/travelogue/camino/ch1/IMG_001.jpg",
                "resource_type": "image",
                "bytes": 1024,
                "uploaded_at": "2024-01-01T00:00:00"
            }
        ]
    
    mapping = {}
    for entry in entries:
        key = entry["relative_path"]
        # Convert to CloudinaryResource-compatible format
        mapping[key] = entry
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(mapping, f, indent=2, ensure_ascii=False)
    
    return output_path
