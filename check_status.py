"""Check upload status."""

import json
import os
from pathlib import Path

# Load mapping
if os.path.exists("cloudinary_mapping.json"):
    with open("cloudinary_mapping.json", "r", encoding="utf-8") as f:
        mapping = json.load(f)

    print(f"Total files in mapping: {len(mapping)}")
    print(
        f"Images: {sum(1 for v in mapping.values() if isinstance(v, dict) and v.get('resource_type') == 'image')}"
    )
    print(
        f"Videos: {sum(1 for v in mapping.values() if isinstance(v, dict) and v.get('resource_type') == 'video')}"
    )
    print(
        f"Files with URLs: {sum(1 for v in mapping.values() if isinstance(v, dict) and v.get('url'))}"
    )

    # Check for duplicates in mapping
    rel_paths = list(mapping.keys())
    unique_paths = set(rel_paths)
    print(f"\nDuplicate keys in mapping: {len(rel_paths) - len(unique_paths)}")

    # Count local files
    content_path = Path("content")
    image_exts = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp"}
    video_exts = {".mp4", ".webm", ".mov", ".avi", ".ogg"}

    local_images = []
    local_videos = []
    for ext in image_exts | video_exts:
        for f in content_path.rglob(f"*{ext}"):
            if ext in image_exts:
                local_images.append(f)
            else:
                local_videos.append(f)
        for f in content_path.rglob(f"*{ext.upper()}"):
            if ext.upper() in {e.upper() for e in image_exts}:
                local_images.append(f)
            else:
                local_videos.append(f)

    # Deduplicate
    local_images = list(set(local_images))
    local_videos = list(set(local_videos))

    print("\nLocal files:")
    print(f"  Images: {len(local_images)}")
    print(f"  Videos: {len(local_videos)}")
    print(f"  Total: {len(local_images) + len(local_videos)}")

    print("\nUpload status:")
    print(f"  Uploaded: {len(mapping)}")
    print(f"  Remaining: {len(local_images) + len(local_videos) - len(mapping)}")
else:
    print("No mapping file found!")
