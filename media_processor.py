"""
圖片影片處理工具 (Media Processor Tool)

整合了以下功能：
1. 上傳媒體檔案到 Cloudinary
2. 更新 Markdown 檔案中的連結為 Cloudinary URL
3. 檢測並刪除 Cloudinary 中的重複檔案
4. 壓縮大型影片檔案

使用方法:
    # 上傳媒體檔案
    python media_processor.py upload

    # 更新 Markdown 檔案中的連結
    python media_processor.py update-markdown

    # 檢測重複檔案（僅檢查）
    python media_processor.py check-duplicates

    # 檢測並自動刪除重複檔案
    python media_processor.py check-duplicates --auto

    # 壓縮影片
    python media_processor.py compress <video_file> [output_file]
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Optional

import cloudinary
import cloudinary.api
import cloudinary.uploader
from dotenv import load_dotenv

# Fix Windows console encoding for Unicode characters
if sys.platform == "win32":
    os.environ["PYTHONIOENCODING"] = "utf-8"

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


# ============================================================================
# 上傳功能 (Upload Functions)
# ============================================================================


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


def normalize_url(url: str) -> str:
    """
    Normalize Cloudinary URL to ensure correct format.

    Removes any duplicate path segments and ensures proper structure:
    https://res.cloudinary.com/{cloud_name}/{resource_type}/upload/{version}/{public_id}.{ext}

    Fixes issues like:
    - Duplicate paths: /myblog/path/myblog/path/file.jpg -> /myblog/path/file.jpg
    - Missing slashes: /ch1IMG_xxx.jpg -> /ch1/IMG_xxx.jpg
    """
    # Find all /myblog/ occurrences
    myblog_indices = [m.start() for m in re.finditer(r"/myblog/", url)]

    if len(myblog_indices) >= 2:
        # Get the path segment after first /myblog/
        first_start = myblog_indices[0]
        second_start = myblog_indices[1]

        # Extract path segments
        first_path = url[first_start:second_start]  # /myblog/travelogue/camino/ch1
        first_path_suffix = first_path.replace("/myblog/", "")  # travelogue/camino/ch1

        # Get everything after second /myblog/
        remaining = url[
            second_start + len("/myblog/") :
        ]  # travelogue/camino/ch1/IMG_xxx.jpg

        # Check if remaining starts with first_path_suffix followed by /
        if remaining.startswith(first_path_suffix + "/"):
            # Found duplicate! Remove the second /myblog/... segment
            filename_part = remaining[len(first_path_suffix) + 1 :]  # IMG_xxx.jpg
            url = url[:second_start] + "/" + filename_part

    # Fix missing slashes before filenames (e.g., /ch1IMG_xxx.jpg -> /ch1/IMG_xxx.jpg)
    url = re.sub(r"(/ch\d+)(IMG_|VID_)", r"\1/\2", url)

    return url


def upload_file(
    file_path: Path, folder: str = "myblog", current: int = 0, total: int = 0
) -> Optional[Dict]:
    """
    Upload a file to Cloudinary.

    Returns dict with 'url' and 'public_id' on success, None on failure.

    The public_id is constructed as: {folder}/{relative_path_without_extension}
    Example: content/travelogue/camino/ch1/IMG_xxx.jpg -> myblog/travelogue/camino/ch1/IMG_xxx
    """
    try:
        # Create folder path based on file location
        # e.g., content/travelogue/camino/ch8/IMG_xxx.jpg -> myblog/travelogue/camino/ch8/IMG_xxx
        relative_path = file_path.relative_to(Path("content"))
        # Convert Windows path separators to forward slashes
        folder_path = str(relative_path.parent).replace("\\", "/")
        # public_id should NOT include file extension
        # Format: {folder}/{folder_path}/{filename_without_ext}
        public_id = f"{folder}/{folder_path}/{file_path.stem}".replace("\\", "/")

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
        # IMPORTANT: public_id already contains full path (folder + subfolder + filename)
        # Do NOT set 'folder' parameter, as it will cause path duplication
        # Cloudinary will construct the URL from public_id automatically
        upload_options = {
            "public_id": public_id,
            "resource_type": resource_type,
            # Don't use use_filename=True as it may interfere with our custom public_id
            "overwrite": True,  # Allow overwriting if file exists
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

        # Get URL from result and normalize it
        url = result.get("secure_url") or result.get("url")
        if url:
            # Normalize URL to remove any potential duplicate paths and fix missing slashes
            url = normalize_url(url)

        print(f"[OK] ({result.get('bytes', 0) // 1024}KB)")

        return {
            "local_path": str(file_path),
            "relative_path": str(relative_path).replace(
                "\\", "/"
            ),  # Normalize path separators
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
    # Normalize all URLs in mapping before saving
    normalized_mapping = {}
    for key, value in mapping.items():
        if isinstance(value, dict) and "url" in value:
            value["url"] = normalize_url(value["url"])
            # Also normalize relative_path
            if "relative_path" in value:
                value["relative_path"] = value["relative_path"].replace("\\", "/")
        normalized_mapping[key] = value

    with open(mapping_file, "w", encoding="utf-8") as f:
        json.dump(normalized_mapping, f, indent=2, ensure_ascii=False)
    print(f"\nMapping saved to {mapping_file}")


def cmd_upload():
    """上傳媒體檔案到 Cloudinary"""
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


# ============================================================================
# 重複檔案檢測功能 (Duplicate Detection Functions)
# ============================================================================


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
                    next_cursor=next_cursor,
                )
            else:
                result = cloudinary.api.resources(
                    type="upload",
                    resource_type=resource_type,
                    prefix=folder,
                    max_results=max_results,
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
        files_by_name[filename].append(
            {
                "public_id": public_id,
                "resource_type": resource.get("resource_type", "image"),
                "bytes": resource.get("bytes", 0),
                "created_at": resource.get("created_at", ""),
            }
        )

    # Find duplicates (files with same name but different paths)
    duplicates = {}
    for filename, files in files_by_name.items():
        if len(files) > 1:
            # Sort by creation time (oldest first) or by path length (shorter first)
            files.sort(key=lambda x: (x["created_at"], len(x["public_id"])))
            # Keep the first one, mark others for deletion
            duplicates[filename] = {"keep": files[0], "delete": files[1:]}

    return duplicates


def delete_resource(public_id, resource_type):
    """Delete a resource from Cloudinary."""
    try:
        cloudinary.uploader.destroy(public_id, resource_type=resource_type)
        return True
    except Exception as e:
        print(f"  Error deleting {public_id}: {e}")
        return False


def cmd_check_duplicates(auto_delete: bool = False):
    """檢測並刪除 Cloudinary 中的重複檔案"""
    # Check Cloudinary configuration
    if not all(
        [
            os.getenv("CLOUDINARY_CLOUD_NAME"),
            os.getenv("CLOUDINARY_API_KEY"),
            os.getenv("CLOUDINARY_API_SECRET"),
        ]
    ):
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
    if not auto_delete:
        print("\n" + "=" * 60)
        try:
            response = (
                input(f"Delete {total_to_delete} duplicate files? (yes/no): ")
                .strip()
                .lower()
            )
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


# ============================================================================
# 影片壓縮功能 (Video Compression Functions)
# ============================================================================


def check_ffmpeg():
    """檢查 FFmpeg 是否安裝"""
    try:
        subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def compress_video(input_path, output_path=None, target_size_mb=95):
    """
    壓縮視頻文件

    Args:
        input_path: 輸入視頻路徑
        output_path: 輸出視頻路徑（如果為None，則自動生成）
        target_size_mb: 目標文件大小（MB），默認95MB（留5MB余量）
    """
    input_file = Path(input_path)

    if not input_file.exists():
        print(f"Error: File not found: {input_path}")
        return False

    # 獲取原始文件大小
    original_size_mb = input_file.stat().st_size / 1024 / 1024
    print(f"Original file size: {original_size_mb:.2f} MB")

    if original_size_mb <= target_size_mb:
        print("File is already within limit, no compression needed.")
        return True

    # 生成輸出文件名
    if output_path is None:
        output_path = (
            input_file.parent / f"{input_file.stem}_compressed{input_file.suffix}"
        )

    output_file = Path(output_path)

    print("\nCompressing video...")
    print(f"Output: {output_file}")
    print("This may take several minutes...")

    # FFmpeg 命令 - 使用較激進的壓縮設定
    cmd = [
        "ffmpeg",
        "-i",
        str(input_file),
        "-c:v",
        "libx264",
        "-crf",
        "28",  # More aggressive: 28=lower quality but smaller file
        "-preset",
        "slow",  # Better compression ratio (slower but smaller)
        "-vf",
        "scale='if(gt(iw,1920),1920,-1)':'if(gt(ih,1080),1080,-1)'",  # Scale down if >1080p
        "-c:a",
        "aac",
        "-b:a",
        "96k",  # Lower audio bitrate for smaller file
        "-movflags",
        "+faststart",  # Optimize for web playback
        "-y",  # Overwrite output file
        str(output_file),
    ]

    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)

        # 檢查輸出文件大小
        if output_file.exists():
            compressed_size_mb = output_file.stat().st_size / 1024 / 1024
            print("\nCompression complete!")
            print(f"Original: {original_size_mb:.2f} MB")
            print(f"Compressed: {compressed_size_mb:.2f} MB")
            print(
                f"Reduction: {((1 - compressed_size_mb / original_size_mb) * 100):.1f}%"
            )

            if compressed_size_mb <= target_size_mb:
                print(
                    f"\n[SUCCESS] File is now {compressed_size_mb:.2f} MB (under {target_size_mb} MB limit)"
                )
                return True
            else:
                print(
                    f"\n[WARNING] File is still {compressed_size_mb:.2f} MB (over {target_size_mb} MB limit)"
                )
                print("Attempting more aggressive compression with CRF 30...")

                # Try even more aggressive compression
                cmd_aggressive = [
                    "ffmpeg",
                    "-i",
                    str(input_file),
                    "-c:v",
                    "libx264",
                    "-crf",
                    "30",  # Very aggressive compression
                    "-preset",
                    "slow",
                    "-vf",
                    "scale='if(gt(iw,1280),1280,-1)':'if(gt(ih,720),720,-1)'",  # Scale to 720p max
                    "-c:a",
                    "aac",
                    "-b:a",
                    "64k",  # Very low audio bitrate
                    "-movflags",
                    "+faststart",
                    "-y",
                    str(output_file),
                ]

                try:
                    subprocess.run(
                        cmd_aggressive, check=True, capture_output=True, text=True
                    )
                    if output_file.exists():
                        compressed_size_mb = output_file.stat().st_size / 1024 / 1024
                        print(f"Second attempt: {compressed_size_mb:.2f} MB")
                        if compressed_size_mb <= target_size_mb:
                            print(
                                f"\n[SUCCESS] File is now {compressed_size_mb:.2f} MB (under {target_size_mb} MB limit)"
                            )
                            return True
                except subprocess.CalledProcessError:
                    pass

                print(
                    "Could not compress below 100MB limit. File may be too long or high quality."
                )
                return False
        else:
            print("Error: Output file was not created")
            return False

    except subprocess.CalledProcessError as e:
        print(f"Error during compression: {e}")
        print(f"FFmpeg output: {e.stderr}")
        return False
    except FileNotFoundError:
        print("Error: FFmpeg not found!")
        print("Please install FFmpeg:")
        print("  Windows: choco install ffmpeg")
        print("  Or download from: https://ffmpeg.org/download.html")
        return False


def cmd_compress(video_file: str, output_file: Optional[str] = None):
    """壓縮大型影片檔案"""
    if not check_ffmpeg():
        print("Error: FFmpeg is not installed or not in PATH")
        print("Please install FFmpeg first:")
        print("  Windows: choco install ffmpeg")
        print("  Or download from: https://ffmpeg.org/download.html")
        return

    success = compress_video(video_file, output_file)
    if not success:
        sys.exit(1)


# ============================================================================
# Markdown 更新功能 (Markdown Update Functions)
# ============================================================================


def load_markdown_mapping(
    mapping_file: str = "cloudinary_mapping.json",
) -> Dict[str, str]:
    """Load Cloudinary URL mapping for markdown updates."""
    if not os.path.exists(mapping_file):
        print(f"Error: {mapping_file} not found!")
        print("Please run 'upload' command first.")
        return {}

    with open(mapping_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Create lookup by filename (for easy matching)
    lookup = {}
    for item in data.values():
        if isinstance(item, dict) and "relative_path" in item:
            filename = Path(item["relative_path"]).name
            lookup[filename] = item["url"]

    return lookup


def find_markdown_files(content_dir: str = "content") -> List[Path]:
    """Find all markdown files in content directory."""
    content_path = Path(content_dir)
    return sorted(content_path.rglob("*.md"))


def update_markdown_file(
    file_path: Path, url_mapping: Dict[str, str], backup: bool = True
) -> int:
    """
    Update markdown file with Cloudinary URLs.

    Returns number of replacements made.
    """
    # Read file
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return 0

    # Create backup
    if backup:
        backup_path = file_path.with_suffix(file_path.suffix + ".backup")
        if not backup_path.exists():
            shutil.copy2(file_path, backup_path)

    # Pattern to match markdown image/video syntax:
    # ![alt text](filename.jpg) or ![alt text](VID_filename.mp4)
    # Also handles: ![alt text][filename.jpg] (reference style)
    pattern = r"!\[([^\]]*)\]\(([^)]+\.(jpg|jpeg|png|gif|webp|mp4|webm|mov|avi|ogg))\)"

    replacements = 0
    original_content = content

    def replace_match(match):
        nonlocal replacements
        alt_text = match.group(1)
        filename = match.group(2)

        # Get just the filename (handle paths like ./IMG_xxx.jpg or IMG_xxx.jpg)
        filename_only = Path(filename).name

        # Look up Cloudinary URL
        if filename_only in url_mapping:
            cloudinary_url = url_mapping[filename_only]
            replacements += 1
            return f"![{alt_text}]({cloudinary_url})"
        else:
            # Not found in mapping, keep original
            return match.group(0)

    # Replace all matches
    updated_content = re.sub(pattern, replace_match, content, flags=re.IGNORECASE)

    # Write updated content if changes were made
    if updated_content != original_content:
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(updated_content)
            return replacements
        except Exception as e:
            print(f"Error writing {file_path}: {e}")
            return 0

    return 0


def cmd_update_markdown(backup: bool = True):
    """更新 Markdown 檔案中的連結為 Cloudinary URL"""
    print("Loading Cloudinary URL mapping...")
    url_mapping = load_markdown_mapping()

    if not url_mapping:
        return

    print(f"Loaded {len(url_mapping)} URLs from mapping\n")

    print("Finding markdown files...")
    markdown_files = find_markdown_files()
    print(f"Found {len(markdown_files)} markdown files\n")

    if not markdown_files:
        print("No markdown files found!")
        return

    # Update files
    total_replacements = 0
    updated_files = 0

    for md_file in markdown_files:
        replacements = update_markdown_file(md_file, url_mapping, backup=backup)
        if replacements > 0:
            print(
                f"Updated {md_file.relative_to('content')}: {replacements} replacements"
            )
            total_replacements += replacements
            updated_files += 1

    print(f"\n{'=' * 50}")
    print("Update complete!")
    print(f"  Files updated: {updated_files}")
    print(f"  Total replacements: {total_replacements}")
    if backup:
        print("\nBackup files created with .backup extension")
        print("You can review changes and delete .backup files when satisfied.")


# ============================================================================
# 主程式 (Main Program)
# ============================================================================


def main():
    """主程式入口"""
    parser = argparse.ArgumentParser(
        description="圖片影片處理工具 - 整合上傳、重複檢測、影片壓縮功能",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
範例:
  # 上傳媒體檔案
  python media_processor.py upload

  # 更新 Markdown 檔案中的連結
  python media_processor.py update-markdown

  # 檢測重複檔案（僅檢查）
  python media_processor.py check-duplicates

  # 檢測並自動刪除重複檔案
  python media_processor.py check-duplicates --auto

  # 壓縮影片
  python media_processor.py compress content/travelogue/camino/ch8/VID_xxx.mp4
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    # 上傳命令
    parser_upload = subparsers.add_parser("upload", help="上傳媒體檔案到 Cloudinary")

    # Markdown 更新命令
    parser_update = subparsers.add_parser(
        "update-markdown", help="更新 Markdown 檔案中的連結為 Cloudinary URL"
    )
    parser_update.add_argument(
        "--no-backup",
        action="store_true",
        help="不建立備份檔案",
    )

    # 重複檢測命令
    parser_duplicates = subparsers.add_parser(
        "check-duplicates", help="檢測並刪除 Cloudinary 中的重複檔案"
    )
    parser_duplicates.add_argument(
        "--auto",
        action="store_true",
        help="自動刪除重複檔案（不需要確認）",
    )

    # 壓縮命令
    parser_compress = subparsers.add_parser("compress", help="壓縮大型影片檔案")
    parser_compress.add_argument("video_file", help="要壓縮的影片檔案路徑")
    parser_compress.add_argument(
        "output_file", nargs="?", default=None, help="輸出檔案路徑（可選）"
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    # 執行對應的命令
    if args.command == "upload":
        cmd_upload()
    elif args.command == "update-markdown":
        cmd_update_markdown(backup=not args.no_backup)
    elif args.command == "check-duplicates":
        cmd_check_duplicates(auto_delete=args.auto)
    elif args.command == "compress":
        cmd_compress(args.video_file, args.output_file)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
