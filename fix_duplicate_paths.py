"""
Fix duplicate path segments in Cloudinary URLs.

This script removes duplicate path segments from all Cloudinary URLs in:
1. Markdown files (content/**/*.md)
2. cloudinary_mapping.json

Example:
  Before: .../myblog/travelogue/camino/ch1/myblog/travelogue/camino/ch1/IMG_xxx.jpg
  After:  .../myblog/travelogue/camino/ch1/IMG_xxx.jpg
"""

import json
import re
from pathlib import Path
from typing import Dict, List


def fix_url(url: str) -> str:
    """
    Remove duplicate path segments from Cloudinary URL.
    
    Pattern: .../myblog/path/to/file/myblog/path/to/file/filename.ext
    Result:  .../myblog/path/to/file/filename.ext
    """
    # Match pattern: /myblog/.../myblog/... and remove the duplicate
    # This regex finds the duplicate segment and removes it
    pattern = r"(/myblog/[^/]+(?:/[^/]+)*?)(/myblog/[^/]+(?:\1)?)"
    
    # More specific: find /myblog/.../myblog/... pattern
    # We need to find where the path repeats
    match = re.search(r"(/myblog/[^/]+(?:/[^/]+)*?)(\1)", url)
    if match:
        # Remove the duplicate segment
        return url.replace(match.group(2), "", 1)
    
    # Alternative approach: find the pattern more carefully
    # Look for /myblog/... followed by the same /myblog/... pattern
    parts = url.split("/")
    for i in range(len(parts) - 1):
        if parts[i] == "myblog" and i > 0:
            # Found first "myblog", check if it repeats
            first_myblog_idx = i
            # Find the path segment after this
            path_segment = "/".join(parts[first_myblog_idx:])
            # Check if this path segment repeats later
            remaining = "/".join(parts[first_myblog_idx + 1:])
            if f"/myblog/{remaining.split('/myblog/')[-1]}" in remaining:
                # Find where the duplicate starts
                for j in range(first_myblog_idx + 1, len(parts)):
                    if parts[j] == "myblog":
                        # Check if the path from first_myblog_idx to j-1 matches j onwards
                        first_path = "/".join(parts[first_myblog_idx:j])
                        second_path = "/".join(parts[j:])
                        if second_path.startswith(first_path):
                            # Remove duplicate segment
                            return "/".join(parts[:j]) + "/" + "/".join(parts[j:]).replace(first_path + "/", "", 1)
    
    # If no duplicate found, return original
    return url


def fix_url_simple(url: str) -> str:
    """
    Simpler approach: Find and remove duplicate /myblog/.../myblog/... pattern.
    """
    # Pattern: /myblog/path1/path2/.../myblog/path1/path2/.../filename
    # We want: /myblog/path1/path2/.../filename
    
    # Split by /myblog/ to find duplicates
    if "/myblog/" in url:
        parts = url.split("/myblog/", 1)
        if len(parts) == 2:
            prefix = parts[0] + "/myblog/"
            rest = parts[1]
            
            # Find where the path repeats
            # rest should be like "travelogue/camino/ch1/myblog/travelogue/camino/ch1/IMG_xxx.jpg"
            # We need to find the duplicate segment
            
            # Try to find the pattern: path/myblog/path/filename
            match = re.search(r"^([^/]+(?:/[^/]+)*?)/myblog/\1/(.+)$", rest)
            if match:
                # Found duplicate: remove the /myblog/path part
                return prefix + match.group(1) + "/" + match.group(2)
            
            # Alternative: look for any repeated segment
            # Split rest by / and find where it repeats
            rest_parts = rest.split("/")
            for i in range(1, len(rest_parts)):
                # Check if parts[0:i] repeats starting at some position
                segment = "/".join(rest_parts[:i])
                if segment and f"/myblog/{segment}/" in rest or rest.startswith(f"{segment}/myblog/{segment}/"):
                    # Found duplicate segment
                    # Remove the /myblog/segment part
                    return prefix + segment + "/" + "/".join(rest_parts[i:])
    
    return url


def fix_url_final(url: str) -> str:
    """
    Final approach: Use regex to find and remove the duplicate pattern.
    """
    # Pattern: /myblog/travelogue/camino/ch1/myblog/travelogue/camino/ch1/IMG_xxx.jpg
    # We want: /myblog/travelogue/camino/ch1/IMG_xxx.jpg
    
    # Find all /myblog/ occurrences
    myblog_indices = [m.start() for m in re.finditer(r'/myblog/', url)]
    
    if len(myblog_indices) >= 2:
        # Get the path segment after first /myblog/
        first_start = myblog_indices[0]
        second_start = myblog_indices[1]
        
        # Extract path segments
        # Find where first path ends (before second /myblog/)
        first_path = url[first_start:second_start]  # /myblog/travelogue/camino/ch1
        first_path_suffix = first_path.replace('/myblog/', '')  # travelogue/camino/ch1
        
        # Get everything after second /myblog/
        remaining = url[second_start + len('/myblog/'):]  # travelogue/camino/ch1/IMG_xxx.jpg
        
        # Check if remaining starts with first_path_suffix followed by /
        if remaining.startswith(first_path_suffix + '/'):
            # Found duplicate! Remove the second /myblog/... segment
            # Keep everything up to second_start, then add the remaining part (after duplicate)
            # remaining already has the path, we just need the filename part
            filename_part = remaining[len(first_path_suffix) + 1:]  # IMG_xxx.jpg
            return url[:second_start] + '/' + filename_part
    
    return url


def fix_markdown_files(content_dir: str = "content") -> int:
    """Fix all Cloudinary URLs in markdown files."""
    content_path = Path(content_dir)
    markdown_files = list(content_path.rglob("*.md"))
    
    fixed_count = 0
    total_replacements = 0
    
    for md_file in markdown_files:
        try:
            content = md_file.read_text(encoding="utf-8")
            original_content = content
            
            # Find all Cloudinary URLs and fix them
            url_pattern = r'https://res\.cloudinary\.com/[^)\s"]+'
            
            def fix_url_in_text(match):
                url = match.group(0)
                return fix_url_final(url)
            
            # Replace all URLs
            content = re.sub(url_pattern, fix_url_in_text, content)
            
            # If content changed, write it back
            if content != original_content:
                md_file.write_text(content, encoding="utf-8")
                # Count how many URLs were actually fixed
                original_urls = re.findall(url_pattern, original_content)
                fixed_urls = re.findall(url_pattern, content)
                replacements = sum(1 for orig, fixed in zip(original_urls, fixed_urls) if orig != fixed)
                fixed_count += 1
                total_replacements += replacements
                if replacements > 0:
                    print(f"Fixed {md_file}: {replacements} URLs")
        except Exception as e:
            print(f"Error processing {md_file}: {e}")
    
    print(f"\nFixed {fixed_count} markdown files, {total_replacements} total URL replacements")
    return total_replacements


def fix_mapping_file(mapping_file: str = "cloudinary_mapping.json") -> int:
    """Fix all URLs in cloudinary_mapping.json."""
    if not Path(mapping_file).exists():
        print(f"Mapping file {mapping_file} not found")
        return 0
    
    with open(mapping_file, "r", encoding="utf-8") as f:
        mapping = json.load(f)
    
    fixed_count = 0
    
    for key, value in mapping.items():
        if isinstance(value, dict) and "url" in value:
            original_url = value["url"]
            fixed_url = fix_url_final(original_url)
            if fixed_url != original_url:
                value["url"] = fixed_url
                fixed_count += 1
    
    if fixed_count > 0:
        with open(mapping_file, "w", encoding="utf-8") as f:
            json.dump(mapping, f, indent=2, ensure_ascii=False)
        print(f"Fixed {fixed_count} URLs in {mapping_file}")
    
    return fixed_count


def main():
    """Main function to fix all duplicate paths."""
    print("Fixing duplicate path segments in Cloudinary URLs...")
    print("=" * 60)
    
    # Fix markdown files
    print("\n1. Fixing markdown files...")
    md_replacements = fix_markdown_files()
    
    # Fix mapping file
    print("\n2. Fixing cloudinary_mapping.json...")
    mapping_fixes = fix_mapping_file()
    
    print("\n" + "=" * 60)
    print("Fix complete!")
    print(f"  Markdown files: {md_replacements} URLs fixed")
    print(f"  Mapping file: {mapping_fixes} URLs fixed")
    print(f"  Total: {md_replacements + mapping_fixes} URLs fixed")


if __name__ == "__main__":
    main()
