"""
Check for duplicate files in Cloudinary and delete redundant ones.

This script:
1. Lists all files in Cloudinary
2. Identifies duplicates based on filename
3. Deletes redundant copies (keeps the first one)
"""

import os
import sys
import cloudinary
import cloudinary.api
from dotenv import load_dotenv
from collections import defaultdict

# Load environment variables
load_dotenv()

# Initialize Cloudinary
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
    secure=True
)

def list_all_resources(resource_type="image", folder="myblog", max_results=500):
    """List all resources in Cloudinary."""
    all_resources = []
    next_cursor = None
    
    print(f"Fetching {resource_type} resources from Cloudinary...")
    
    while True:
        try:
            if next_cursor:
                result = cloudinary.api.resources(
                    type="upload",
                    resource_type=resource_type,
                    prefix=folder,
                    max_results=max_results,
                    next_cursor=next_cursor
                )
            else:
                result = cloudinary.api.resources(
                    type="upload",
                    resource_type=resource_type,
                    prefix=folder,
                    max_results=max_results
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
    
    return all_resources

def find_duplicates(resources):
    """Find duplicate files based on filename."""
    # Group by filename (last part of public_id)
    files_by_name = defaultdict(list)
    
    for resource in resources:
        public_id = resource.get("public_id", "")
        # Extract filename from public_id (e.g., "myblog/travelogue/camino/ch8/IMG_xxx" -> "IMG_xxx")
        filename = public_id.split("/")[-1]
        files_by_name[filename].append({
            "public_id": public_id,
            "resource_type": resource.get("resource_type", "image"),
            "bytes": resource.get("bytes", 0),
            "created_at": resource.get("created_at", ""),
        })
    
    # Find duplicates (files with same name but different paths)
    duplicates = {}
    for filename, files in files_by_name.items():
        if len(files) > 1:
            # Sort by creation time (oldest first) or by path length (shorter first)
            files.sort(key=lambda x: (x["created_at"], len(x["public_id"])))
            # Keep the first one, mark others for deletion
            duplicates[filename] = {
                "keep": files[0],
                "delete": files[1:]
            }
    
    return duplicates

def delete_resource(public_id, resource_type):
    """Delete a resource from Cloudinary."""
    try:
        from cloudinary import uploader
        uploader.destroy(public_id, resource_type=resource_type)
        return True
    except Exception as e:
        print(f"  Error deleting {public_id}: {e}")
        return False

def main():
    """Main function to check and delete duplicates."""
    # Check Cloudinary configuration
    if not all([
        os.getenv("CLOUDINARY_CLOUD_NAME"),
        os.getenv("CLOUDINARY_API_KEY"),
        os.getenv("CLOUDINARY_API_SECRET"),
    ]):
        print("Error: Cloudinary credentials not found!")
        return
    
    print("=" * 60)
    print("Checking for duplicate files in Cloudinary...")
    print("=" * 60)
    
    # Check images
    print("\n[1/2] Checking images...")
    images = list_all_resources(resource_type="image")
    print(f"Found {len(images)} images")
    
    # Check videos
    print("\n[2/2] Checking videos...")
    videos = list_all_resources(resource_type="video")
    print(f"Found {len(videos)} videos")
    
    # Combine and find duplicates
    all_resources = images + videos
    print(f"\nTotal resources: {len(all_resources)}")
    
    duplicates = find_duplicates(all_resources)
    
    if not duplicates:
        print("\n[OK] No duplicates found! All files are unique.")
        return
    
    print(f"\n[WARNING] Found {len(duplicates)} files with duplicates:")
    print("-" * 60)
    
    total_to_delete = sum(len(dup["delete"]) for dup in duplicates.values())
    print(f"Total duplicate files to delete: {total_to_delete}")
    print("\nDuplicate files:")
    
    for filename, dup_info in list(duplicates.items())[:10]:  # Show first 10
        print(f"  {filename}:")
        print(f"    Keep: {dup_info['keep']['public_id']}")
        for d in dup_info["delete"]:
            print(f"    Delete: {d['public_id']}")
    
    if len(duplicates) > 10:
        print(f"  ... and {len(duplicates) - 10} more files with duplicates")
    
    # Ask for confirmation (or use --auto flag)
    auto_mode = "--auto" in sys.argv or "-y" in sys.argv
    
    if not auto_mode:
        print("\n" + "=" * 60)
        try:
            response = input(f"Delete {total_to_delete} duplicate files? (yes/no): ").strip().lower()
            if response != "yes":
                print("Cancelled. No files deleted.")
                return
        except (EOFError, KeyboardInterrupt):
            print("\nCancelled. No files deleted.")
            return
    else:
        print(f"\n[Auto mode] Will delete {total_to_delete} duplicate files...")
    
    # Delete duplicates
    print("\nDeleting duplicates...")
    deleted_count = 0
    failed_count = 0
    
    for filename, dup_info in duplicates.items():
        for dup_file in dup_info["delete"]:
            public_id = dup_file["public_id"]
            resource_type = dup_file["resource_type"]
            print(f"Deleting {public_id}...", end=" ", flush=True)
            
            if delete_resource(public_id, resource_type):
                print("[OK]")
                deleted_count += 1
            else:
                print("[FAILED]")
                failed_count += 1
    
    print("\n" + "=" * 60)
    print("Deletion complete!")
    print(f"  Deleted: {deleted_count}")
    print(f"  Failed: {failed_count}")
    print(f"  Remaining unique files: {len(all_resources) - deleted_count}")

if __name__ == "__main__":
    main()
