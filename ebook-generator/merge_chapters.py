"""Merge all Camino chapters into a single Markdown file."""

import re
from pathlib import Path

import config


def strip_hugo_frontmatter(content: str) -> str:
    """Remove Hugo frontmatter (+++ format) from markdown."""
    lines = content.split("\n")
    if lines and lines[0].strip() == "+++":
        # Find closing +++
        for i in range(1, len(lines)):
            if lines[i].strip() == "+++":
                return "\n".join(lines[i + 1 :])
    return content


def increase_heading_levels(content: str) -> str:
    """
    Increase all heading levels by 1 (h1 -> h2, h2 -> h3, etc.).
    This ensures Chapter titles remain as the only h1 level.
    """
    lines = content.split("\n")
    result = []

    for line in lines:
        # Match markdown headings: #, ##, ###, etc.
        heading_match = re.match(r"^(#{1,6})\s+(.+)$", line)
        if heading_match:
            # Add one more # to increase the level
            current_level = heading_match.group(1)
            heading_text = heading_match.group(2)
            # Increase level (but cap at h6)
            if len(current_level) < 6:
                new_level = "#" + current_level
                result.append(f"{new_level} {heading_text}")
            else:
                # Already h6, keep as is
                result.append(line)
        else:
            result.append(line)

    return "\n".join(result)


def merge_chapters() -> Path:
    """Merge all chapters into a single Markdown file."""
    print("Merging Camino chapters...")

    # Create merged directory (won't interfere with website)
    # Use absolute path based on current script location
    script_dir = Path(__file__).parent
    merged_dir = script_dir / "merged"
    merged_dir.mkdir(parents=True, exist_ok=True)

    merged_content = []

    # Process each chapter (cover will be added in main.py)
    for i, chapter_path in enumerate(config.CHAPTERS, 1):
        full_path = config.SOURCE_DIR / chapter_path
        if not full_path.exists():
            print(f"Warning: Chapter not found: {full_path}")
            continue

        print(f"  Processing: {chapter_path}")
        content = full_path.read_text(encoding="utf-8")

        # Remove Hugo frontmatter
        content = strip_hugo_frontmatter(content)

        # Increase all heading levels in chapter content by 1
        # This ensures Chapter titles (# Chapter X) remain as the only h1 level
        # Content headings (e.g., # 典故) become h2, h2 becomes h3, etc.
        content = increase_heading_levels(content)

        # Add chapter title with minimal spacing
        # Remove the --- separator to avoid page breaks
        if i > 1:
            # Add a single blank line before new chapter (except first chapter)
            merged_content.append("\n")
        merged_content.append(f"# Chapter {i}\n\n")
        merged_content.append(content)
        # Remove trailing separator to prevent page breaks

    # Write merged file
    merged_file = merged_dir / "camino_merged.md"
    merged_content_text = "".join(merged_content)
    merged_file.write_text(merged_content_text, encoding="utf-8")

    print(f"\n[OK] Merged file created: {merged_file}")
    print(f"  Total size: {len(merged_content_text)} characters")
    print(f"  Full path: {merged_file.absolute()}")

    return merged_file


if __name__ == "__main__":
    merge_chapters()
