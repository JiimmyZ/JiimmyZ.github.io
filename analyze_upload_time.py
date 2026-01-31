"""分析上传脚本预计执行时间"""

from pathlib import Path
import json
import os

# 计算需要处理的文件
content_path = Path("content")
image_exts = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp"}
video_exts = {".mp4", ".webm", ".mov", ".avi", ".ogg"}

all_files = set()
for ext in image_exts | video_exts:
    all_files.update(content_path.rglob(f"*{ext}"))
    all_files.update(content_path.rglob(f"*{ext.upper()}"))

total_files = len(all_files)

# 加载已上传的映射
if os.path.exists("cloudinary_mapping.json"):
    with open("cloudinary_mapping.json", "r", encoding="utf-8") as f:
        mapping = json.load(f)
    uploaded_count = len(mapping)
else:
    uploaded_count = 0
    mapping = {}

# 找出需要上传的文件
uploaded_paths = set(mapping.keys())
need_upload = []
for f in sorted(all_files):
    rel_path = str(f.relative_to(content_path))
    if rel_path not in uploaded_paths:
        need_upload.append(f)

print("=" * 60)
print("Upload Script Execution Time Analysis")
print("=" * 60)
print(f"\nTotal files: {total_files}")
print(f"Already uploaded: {uploaded_count}")
print(f"Need to check: {total_files - uploaded_count}")
print(f"Need to actually upload: {len(need_upload)}")

if need_upload:
    print("\nFiles to upload:")
    total_size = 0
    for f in need_upload:
        size_mb = f.stat().st_size / 1024 / 1024
        total_size += size_mb
        file_type = "Video" if f.suffix.lower() in video_exts else "Image"
        print(f"  {f.name}: {size_mb:.1f} MB ({file_type})")
    
    print(f"\nTotal size: {total_size:.1f} MB")
    
    # Estimate time
    # Assume network speed: 1-5 MB/s (depends on your network)
    # Check uploaded files: ~0.1 sec each
    # Upload images: ~1-3 sec each
    # Upload videos: ~ file_size(MB) / network_speed(MB/s)
    
    network_speed = 2  # MB/s (conservative estimate)
    
    check_time = (total_files - uploaded_count) * 0.1  # seconds
    upload_time = 0
    
    for f in need_upload:
        if f.suffix.lower() in video_exts:
            size_mb = f.stat().st_size / 1024 / 1024
            upload_time += size_mb / network_speed  # seconds
        else:
            upload_time += 2  # images ~2 sec
    
    total_time = check_time + upload_time
    
    print(f"\nEstimated execution time:")
    print(f"  Check files: {check_time:.1f} sec ({check_time/60:.1f} min)")
    print(f"  Upload files: {upload_time:.1f} sec ({upload_time/60:.1f} min)")
    print(f"  Total: {total_time:.1f} sec ({total_time/60:.1f} min)")
    print(f"\nNote: Actual time depends on network speed")
    print(f"  If network speed is 1 MB/s: ~ {total_time * 2 / 60:.1f} min")
    print(f"  If network speed is 5 MB/s: ~ {total_time * 0.4 / 60:.1f} min")
else:
    print("\nAll files already uploaded!")
