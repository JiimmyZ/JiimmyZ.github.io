"""
Update markdown files to use Cloudinary URLs instead of local file references.

This script:
1. Loads the Cloudinary URL mapping
2. Finds all markdown files in content directory
3. Replaces local image/video references with Cloudinary URLs
4. Creates backups of original files
"""

import os
import json
import re
import shutil
from pathlib import Path
from typing import Dict, List

def load_mapping(mapping_file: str = "cloudinary_mapping.json") -> Dict[str, Dict]:
    """Load Cloudinary URL mapping."""
    if not os.path.exists(mapping_file):
        print(f"Error: {mapping_file} not found!")
        print("Please run upload_to_cloudinary.py first.")
        return {}
    
    with open(mapping_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    # Create lookup by filename (for easy matching)
    lookup = {}
    for item in data.values():
        filename = Path(item["relative_path"]).name
        lookup[filename] = item["url"]
    
    return lookup

def find_markdown_files(content_dir: str = "content") -> List[Path]:
    """Find all markdown files in content directory."""
    content_path = Path(content_dir)
    return sorted(content_path.rglob("*.md"))

def update_markdown_file(file_path: Path, url_mapping: Dict[str, str], backup: bool = True) -> int:
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
    pattern = r'!\[([^\]]*)\]\(([^)]+\.(jpg|jpeg|png|gif|webp|mp4|webm|mov|avi|ogg))\)'
    
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
            return f'![{alt_text}]({cloudinary_url})'
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

def main():
    """Main update function."""
    print("Loading Cloudinary URL mapping...")
    url_mapping = load_mapping()
    
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
        replacements = update_markdown_file(md_file, url_mapping)
        if replacements > 0:
            print(f"Updated {md_file.relative_to('content')}: {replacements} replacements")
            total_replacements += replacements
            updated_files += 1
    
    print(f"\n{'='*50}")
    print(f"Update complete!")
    print(f"  Files updated: {updated_files}")
    print(f"  Total replacements: {total_replacements}")
    print(f"\nBackup files created with .backup extension")
    print("You can review changes and delete .backup files when satisfied.")

if __name__ == "__main__":
    main()
