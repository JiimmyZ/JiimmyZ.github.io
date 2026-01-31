"""
List all files in Cloudinary to see what actually exists.
"""

import os
import cloudinary
import cloudinary.api
from dotenv import load_dotenv

load_dotenv()

cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
    secure=True
)

print("Fetching files from Cloudinary...")
print("=" * 60)

# List images
try:
    result = cloudinary.api.resources(
        type="upload",
        resource_type="image",
        prefix="myblog/travelogue/camino/ch8",
        max_results=10
    )
    images = result.get("resources", [])
    print(f"\nImages in ch8: {len(images)}")
    for img in images[:5]:
        print(f"  - {img.get('public_id')}")
except Exception as e:
    print(f"Error fetching images: {e}")

# List videos
try:
    result = cloudinary.api.resources(
        type="upload",
        resource_type="video",
        prefix="myblog/travelogue/camino/ch8",
        max_results=10
    )
    videos = result.get("resources", [])
    print(f"\nVideos in ch8: {len(videos)}")
    for vid in videos[:5]:
        print(f"  - {vid.get('public_id')}")
except Exception as e:
    print(f"Error fetching videos: {e}")

# Check total count
try:
    result = cloudinary.api.resources(
        type="upload",
        prefix="myblog",
        max_results=1
    )
    total = result.get("total_count", 0)
    print(f"\nTotal files in 'myblog' folder: {total}")
except Exception as e:
    print(f"Error getting total count: {e}")
