"""
Fix duplicate path segments in Cloudinary file paths for ch6.

Cloudinary files have paths like:
  myblog/travelogue/camino/ch6/myblog/travelogue/camino/ch6/IMG_xxx

Should be:
  myblog/travelogue/camino/ch6/IMG_xxx

This script uses Cloudinary API to rename/move files to correct paths.
Based on fix_ch7_cloudinary_paths.py but specifically for ch6.
"""

import os
import cloudinary
import cloudinary.api
import cloudinary.uploader
from dotenv import load_dotenv

load_dotenv()

cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
    secure=True
)

def fix_path(public_id):
    """
    Fix duplicate path segments in public_id.
    
    Example:
      myblog/travelogue/camino/ch6/myblog/travelogue/camino/ch6/IMG_xxx
      -> myblog/travelogue/camino/ch6/IMG_xxx
    """
    parts = public_id.split("/")
    
    # Find where the duplicate starts
    # Look for pattern: myblog/travelogue/camino/ch6/myblog/...
    if len(parts) < 5:
        return None  # Path too short to have duplicate
    
    # Check if there's a duplicate "myblog" segment
    myblog_indices = [i for i, part in enumerate(parts) if part == "myblog"]
    
    if len(myblog_indices) < 2:
        return None  # No duplicate found
    
    # Get the path after first "myblog"
    first_myblog_idx = myblog_indices[0]
    second_myblog_idx = myblog_indices[1]
    
    # Extract the path segment between first and second "myblog"
    first_segment = "/".join(parts[first_myblog_idx:second_myblog_idx])
    # Remove "myblog/" prefix
    first_segment_suffix = "/".join(parts[first_myblog_idx+1:second_myblog_idx])
    
    # Get everything after second "myblog"
    remaining = "/".join(parts[second_myblog_idx:])
    
    # Check if remaining starts with the same segment
    if remaining.startswith(f"myblog/{first_segment_suffix}/"):
        # Found duplicate! Construct correct path
        filename = parts[-1]  # Last part is the filename
        correct_path = f"myblog/{first_segment_suffix}/{filename}"
        return correct_path
    
    return None

def fix_all_paths(resource_type="image", folder="myblog/travelogue/camino/ch6", dry_run=True):
    """Fix paths for all resources in the specified folder."""
    print(f"Fetching {resource_type} resources from Cloudinary...")
    print(f"Folder: {folder}")
    print(f"Mode: {'DRY RUN' if dry_run else 'LIVE'}")
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
                    next_cursor=next_cursor
                )
            else:
                result = cloudinary.api.resources(
                    type="upload",
                    resource_type=resource_type,
                    prefix=folder,
                    max_results=500
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
    
    fixed_count = 0
    skipped_count = 0
    error_count = 0
    
    for resource in all_resources:
        old_public_id = resource.get("public_id", "")
        new_public_id = fix_path(old_public_id)
        
        if new_public_id and new_public_id != old_public_id:
            print(f"\nFixing: {old_public_id}")
            print(f"  -> {new_public_id}")
            
            if not dry_run:
                try:
                    # Use rename to move the file
                    cloudinary.uploader.rename(
                        old_public_id,
                        new_public_id,
                        resource_type=resource_type,
                        overwrite=False
                    )
                    print(f"  [OK] Renamed successfully")
                    fixed_count += 1
                except Exception as e:
                    print(f"  [ERROR] {str(e)}")
                    error_count += 1
            else:
                print(f"  (DRY RUN - would rename)")
                fixed_count += 1
        else:
            skipped_count += 1
    
    print("\n" + "=" * 60)
    print(f"Summary:")
    print(f"  Fixed: {fixed_count}")
    print(f"  Skipped: {skipped_count}")
    print(f"  Errors: {error_count}")
    
    return fixed_count, skipped_count, error_count

if __name__ == "__main__":
    import sys
    
    # Check for --live flag
    dry_run = "--live" not in sys.argv
    
    if dry_run:
        print("WARNING: Running in DRY RUN mode. Use --live to actually fix paths.")
        print()
    else:
        print("WARNING: Running in LIVE mode. This will rename files in Cloudinary!")
        response = input("Are you sure you want to continue? (yes/no): ")
        if response.lower() != "yes":
            print("Aborted.")
            sys.exit(0)
        print()
    
    # Fix images
    print("Fixing ch6 images...")
    img_fixed, img_skipped, img_errors = fix_all_paths("image", "myblog/travelogue/camino/ch6", dry_run)
    
    # Fix videos
    print("\n\nFixing ch6 videos...")
    vid_fixed, vid_skipped, vid_errors = fix_all_paths("video", "myblog/travelogue/camino/ch6", dry_run)
    
    print("\n" + "=" * 60)
    print("FINAL SUMMARY:")
    print(f"Images - Fixed: {img_fixed}, Skipped: {img_skipped}, Errors: {img_errors}")
    print(f"Videos - Fixed: {vid_fixed}, Skipped: {vid_skipped}, Errors: {vid_errors}")
    print(f"Total Fixed: {img_fixed + vid_fixed}")
