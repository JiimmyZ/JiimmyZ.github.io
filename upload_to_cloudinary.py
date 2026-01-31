"""
Upload media files to Cloudinary and generate URL mapping.

This script:
1. Scans content directories for image and video files
2. Uploads them to Cloudinary
3. Generates a mapping file (JSON) of local paths to Cloudinary URLs
4. Optionally updates markdown files with Cloudinary URLs
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional

import cloudinary
import cloudinary.uploader
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Cloudinary
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
    secure=True,
)

# Supported media extensions
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp"}
VIDEO_EXTENSIONS = {".mp4", ".webm", ".mov", ".avi", ".ogg"}


def find_media_files(content_dir: str = "content") -> List[Path]:
    """Find all media files in content directory."""
    media_files = set()  # Use set to avoid duplicates
    content_path = Path(content_dir)

    # Search for all extensions (case-insensitive on Windows)
    for ext in IMAGE_EXTENSIONS | VIDEO_EXTENSIONS:
        # Search both lowercase and uppercase, but use set to deduplicate
        media_files.update(content_path.rglob(f"*{ext}"))
        media_files.update(content_path.rglob(f"*{ext.upper()}"))

    return sorted(media_files)  # Convert set to sorted list


def upload_file(
    file_path: Path, folder: str = "myblog", current: int = 0, total: int = 0
) -> Optional[Dict]:
    """
    Upload a file to Cloudinary.

    Returns dict with 'url' and 'public_id' on success, None on failure.
    """
    try:
        # Create folder path based on file location
        # e.g., content/travelogue/camino/ch8/IMG_xxx.jpg -> myblog/travelogue/camino/ch8/IMG_xxx
        relative_path = file_path.relative_to(Path("content"))
        folder_path = str(relative_path.parent).replace("\\", "/")
        public_id = f"{folder}/{folder_path}/{file_path.stem}"

        # Determine resource type
        ext = file_path.suffix.lower()
        resource_type = "video" if ext in VIDEO_EXTENSIONS else "image"

        # Show progress counter
        if current > 0 and total > 0:
            print(
                f"[{current}/{total}] Uploading {file_path.name}...",
                end=" ",
                flush=True,
            )
        else:
            print(f"Uploading {file_path.name}...", end=" ", flush=True)

        # Upload with optimization
        upload_options = {
            "public_id": public_id,
            "resource_type": resource_type,
            "folder": f"{folder}/{folder_path}",
            "use_filename": True,
            "unique_filename": False,
        }

        # Add image-specific optimizations
        if resource_type == "image":
            upload_options.update(
                {
                    "quality": "auto:good",  # Auto quality with good compression
                    "fetch_format": "auto",  # Auto format (WebP when supported)
                }
            )

        # Add video-specific optimizations
        if resource_type == "video":
            file_size_mb = file_path.stat().st_size / 1024 / 1024

            # For videos over 20MB, don't specify format conversion to avoid sync processing
            # Cloudinary will store the original format
            if file_size_mb > 20:
                print(
                    f"(Large video {file_size_mb:.1f}MB - uploading without conversion...)"
                )
                upload_options.update(
                    {
                        "resource_type": "video",
                        # Don't specify format to avoid processing
                    }
                )
            else:
                upload_options.update(
                    {
                        "resource_type": "video",
                        "format": "mp4",
                    }
                )

            # Use upload_large for videos over 20MB for better reliability
            if file_size_mb > 20:
                result = cloudinary.uploader.upload_large(
                    str(file_path), **upload_options
                )
            else:
                result = cloudinary.uploader.upload(str(file_path), **upload_options)
        else:
            result = cloudinary.uploader.upload(str(file_path), **upload_options)

        url = result.get("secure_url") or result.get("url")
        print(f"[OK] ({result.get('bytes', 0) // 1024}KB)")

        return {
            "local_path": str(file_path),
            "relative_path": str(relative_path),
            "public_id": public_id,
            "url": url,
            "resource_type": resource_type,
            "bytes": result.get("bytes", 0),
        }

    except Exception as e:
        print(f"[ERROR] {e}")
        return None


def load_existing_mapping(mapping_file: str = "cloudinary_mapping.json") -> Dict:
    """Load existing URL mapping to avoid re-uploading."""
    if os.path.exists(mapping_file):
        with open(mapping_file, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_mapping(mapping: Dict, mapping_file: str = "cloudinary_mapping.json"):
    """Save URL mapping to JSON file."""
    with open(mapping_file, "w", encoding="utf-8") as f:
        json.dump(mapping, f, indent=2, ensure_ascii=False)
    print(f"\nMapping saved to {mapping_file}")


def main():
    """Main upload function."""
    # Check Cloudinary configuration
    if not all(
        [
            os.getenv("CLOUDINARY_CLOUD_NAME"),
            os.getenv("CLOUDINARY_API_KEY"),
            os.getenv("CLOUDINARY_API_SECRET"),
        ]
    ):
        print("Error: Cloudinary credentials not found!")
        print("Please create a .env file with:")
        print("  CLOUDINARY_CLOUD_NAME=your_cloud_name")
        print("  CLOUDINARY_API_KEY=your_api_key")
        print("  CLOUDINARY_API_SECRET=your_api_secret")
        return

    print("Finding media files...")
    media_files = find_media_files()
    print(f"Found {len(media_files)} media files\n")

    if not media_files:
        print("No media files found!")
        return

    # Load existing mapping
    mapping = load_existing_mapping()

    # Create sets for checking - use both relative_path and local_path
    existing_relative_paths = set(mapping.keys())
    existing_local_paths = {
        item["local_path"]
        for item in mapping.values()
        if isinstance(item, dict) and "local_path" in item
    }

    # Upload new files
    uploaded_count = 0
    skipped_count = 0
    total_files = len(media_files)

    # Count files that need upload
    need_upload = []
    for file_path in media_files:
        file_str = str(file_path)
        relative_path = str(file_path.relative_to(Path("content")))
        if (
            relative_path not in existing_relative_paths
            and file_str not in existing_local_paths
        ):
            need_upload.append(file_path)

    print(f"Files to upload: {len(need_upload)}")
    if len(need_upload) > 0:
        print("Starting upload...\n")
    else:
        print("All files already uploaded!\n")
        return

    for index, file_path in enumerate(need_upload, 1):
        file_str = str(file_path)
        relative_path = str(file_path.relative_to(Path("content")))

        result = upload_file(file_path, current=index, total=len(need_upload))
        if result:
            # Use relative path as key for easy lookup
            # Double-check to prevent duplicates
            rel_path = result["relative_path"]
            if rel_path not in mapping:
                mapping[rel_path] = result
                uploaded_count += 1
            else:
                print(
                    f"  Warning: {file_path.name} already in mapping, skipping duplicate"
                )
                skipped_count += 1

    # Save updated mapping
    save_mapping(mapping)

    print(f"\n{'=' * 50}")
    print("Upload complete!")
    print(f"  Uploaded: {uploaded_count}")
    print(f"  Skipped: {skipped_count} (already in mapping)")
    print(f"  Total in mapping: {len(mapping)}")
    if uploaded_count > 0:
        print("\nNext step: Run update_markdown.py to update your markdown files")


if __name__ == "__main__":
    main()
