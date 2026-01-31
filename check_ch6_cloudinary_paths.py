"""
Check if ch6 files in Cloudinary have duplicate path segments like ch7 and ch8 did.
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
    secure=True,
)


def check_paths(resource_type="image", folder="myblog/travelogue/camino/ch6"):
    """Check paths for all resources in the specified folder."""
    print(f"Checking {resource_type} resources in Cloudinary...")
    print(f"Folder: {folder}")
    print("=" * 60)

    all_resources = []
    next_cursor = None

    while True:
        try:
            if next_cursor:
                result = cloudinary.api.resources(
                    type="upload",
                    resource_type=resource_type,
                    prefix=folder,
                    max_results=500,
                    next_cursor=next_cursor,
                )
            else:
                result = cloudinary.api.resources(
                    type="upload",
                    resource_type=resource_type,
                    prefix=folder,
                    max_results=500,
                )

            resources = result.get("resources", [])
            all_resources.extend(resources)

            next_cursor = result.get("next_cursor")
            if not next_cursor:
                break

            print(f"  Fetched {len(all_resources)} resources so far...")

        except Exception as e:
            print(f"Error fetching resources: {e}")
            break

    print(f"\nTotal resources found: {len(all_resources)}")

    # Check for duplicate paths
    duplicate_paths = []
    correct_paths = []

    for resource in all_resources:
        public_id = resource.get("public_id", "")
        parts = public_id.split("/")

        # Check if path has duplicate "myblog" segments
        myblog_indices = [i for i, part in enumerate(parts) if part == "myblog"]

        if len(myblog_indices) >= 2:
            # Potential duplicate path
            duplicate_paths.append(public_id)
        else:
            correct_paths.append(public_id)

    print(f"\nPaths with potential duplicates: {len(duplicate_paths)}")
    print(f"Paths that look correct: {len(correct_paths)}")

    if duplicate_paths:
        print("\nSample duplicate paths:")
        for path in duplicate_paths[:5]:
            print(f"  {path}")

    if correct_paths:
        print("\nSample correct paths:")
        for path in correct_paths[:5]:
            print(f"  {path}")

    # Also check if files exist at expected paths
    print("\n" + "=" * 60)
    print("Checking if files exist at expected paths...")

    # Sample a few files from markdown
    sample_files = [
        "myblog/travelogue/camino/ch6/IMG_20250615_134609",
        "myblog/travelogue/camino/ch6/IMG_20250615_182022",
        "myblog/travelogue/camino/ch6/IMG_20250615_190357",
    ]

    for public_id in sample_files:
        try:
            result = cloudinary.api.resource(public_id, resource_type=resource_type)
            print(f"  [OK] {public_id} - EXISTS")
        except Exception as e:
            print(f"  [NOT FOUND] {public_id} - {str(e)[:50]}")

    return duplicate_paths, correct_paths


if __name__ == "__main__":
    print("Checking ch6 images...")
    ch6_dup_images, ch6_correct_images = check_paths(
        "image", "myblog/travelogue/camino/ch6"
    )

    print("\n\nChecking ch6 videos...")
    ch6_dup_videos, ch6_correct_videos = check_paths(
        "video", "myblog/travelogue/camino/ch6"
    )

    print("\n" + "=" * 60)
    print("SUMMARY:")
    print(
        f"Ch6 Images - Duplicates: {len(ch6_dup_images)}, Correct: {len(ch6_correct_images)}"
    )
    print(
        f"Ch6 Videos - Duplicates: {len(ch6_dup_videos)}, Correct: {len(ch6_correct_videos)}"
    )

    # Compare with ch7 (which was fixed)
    print("\nChecking ch7 for comparison...")
    ch7_dup_images, ch7_correct_images = check_paths(
        "image", "myblog/travelogue/camino/ch7"
    )
    print(
        f"Ch7 Images - Duplicates: {len(ch7_dup_images)}, Correct: {len(ch7_correct_images)}"
    )
