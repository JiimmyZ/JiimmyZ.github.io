"""
Fix missing slashes in Cloudinary URLs.

After removing duplicate paths, some URLs are missing slashes before filenames.
Example: .../ch1IMG_xxx.jpg should be .../ch1/IMG_xxx.jpg
"""

import re
from pathlib import Path


def fix_missing_slash(url: str) -> str:
    """
    Add missing slash before filename if pattern matches.
    Pattern: .../ch1IMG_xxx.jpg -> .../ch1/IMG_xxx.jpg
    """
    # Pattern: /ch followed by number, then IMG_ or VID_ (no slash in between)
    pattern = r'(/ch\d+)(IMG_|VID_)'
    match = re.search(pattern, url)
    if match:
        # Add slash between ch number and filename
        return url[:match.end(1)] + '/' + url[match.end(1):]
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
            
            # Find all Cloudinary URLs
            url_pattern = r'https://res\.cloudinary\.com/[^)\s"]+'
            
            def fix_url_in_text(match):
                url = match.group(0)
                return fix_missing_slash(url)
            
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
    import json
    
    if not Path(mapping_file).exists():
        print(f"Mapping file {mapping_file} not found")
        return 0
    
    with open(mapping_file, "r", encoding="utf-8") as f:
        mapping = json.load(f)
    
    fixed_count = 0
    
    for key, value in mapping.items():
        if isinstance(value, dict) and "url" in value:
            original_url = value["url"]
            fixed_url = fix_missing_slash(original_url)
            if fixed_url != original_url:
                value["url"] = fixed_url
                fixed_count += 1
    
    if fixed_count > 0:
        with open(mapping_file, "w", encoding="utf-8") as f:
            json.dump(mapping, f, indent=2, ensure_ascii=False)
        print(f"Fixed {fixed_count} URLs in {mapping_file}")
    
    return fixed_count


def main():
    """Main function to fix all missing slashes."""
    print("Fixing missing slashes in Cloudinary URLs...")
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
