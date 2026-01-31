"""
Update Cloudinary URLs in markdown files to use v1 instead of specific version numbers.

This fixes the 404 errors by replacing version-specific URLs with v1 (or removing version).
"""

import re
import os
from pathlib import Path

def update_urls_in_file(file_path: Path) -> int:
    """Update Cloudinary URLs in a markdown file."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        original_content = content
        
        # Pattern to match Cloudinary URLs with version numbers
        # Matches: /v{version_number}/myblog/...
        pattern = r'(https://res\.cloudinary\.com/[^/]+/(?:image|video)/upload/)v\d+/(myblog/[^)]+)'
        
        # Replace with v1
        content = re.sub(pattern, r'\1v1/\2', content)
        
        if content != original_content:
            # Backup original file
            backup_path = file_path.with_suffix(file_path.suffix + ".backup")
            if not backup_path.exists():
                with open(backup_path, "w", encoding="utf-8") as f:
                    f.write(original_content)
            
            # Write updated content
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            
            # Count replacements
            matches = len(re.findall(pattern, original_content))
            return matches
        
        return 0
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return 0

def main():
    """Update all markdown files in content directory."""
    content_dir = Path("content")
    total_replacements = 0
    files_updated = 0
    
    # Find all markdown files
    markdown_files = list(content_dir.rglob("*.md"))
    
    print(f"Found {len(markdown_files)} markdown files")
    print("Updating Cloudinary URLs...")
    print("=" * 60)
    
    for md_file in markdown_files:
        if md_file.name.endswith(".backup"):
            continue
        
        replacements = update_urls_in_file(md_file)
        if replacements > 0:
            print(f"  Updated {md_file.relative_to(content_dir)}: {replacements} URLs")
            total_replacements += replacements
            files_updated += 1
    
    print("=" * 60)
    print(f"Summary:")
    print(f"  Files updated: {files_updated}")
    print(f"  Total URL replacements: {total_replacements}")

if __name__ == "__main__":
    main()
