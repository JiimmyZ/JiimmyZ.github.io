"""Pandoc subprocess wrapper for EPUB generation."""

import subprocess
from pathlib import Path


def generate_epub(
    input_files: list[Path],
    output_file: Path,
    css_file: Path | None = None,
    metadata: dict[str, str] | None = None,
    fonts: list[Path] | None = None,
) -> bool:
    """Generate EPUB using Pandoc."""
    # Ensure output directory exists
    output_file.parent.mkdir(parents=True, exist_ok=True)

    # Verify input files exist
    missing_files = [f for f in input_files if not f.exists()]
    if missing_files:
        print(f"Error: Missing input files: {missing_files}")
        return False

    cmd = ["pandoc"]
    cmd.extend([str(f) for f in input_files])
    cmd.extend(["-f", "markdown", "-t", "epub3", "-o", str(output_file)])

    # Add resource path for images
    # Pandoc needs to know where to find image resources
    # Images are in output/images/, markdown is in output/temp/
    if input_files:
        input_dir = input_files[0].parent.resolve()
        output_dir = input_dir.parent.resolve()  # output/ directory
        # Add both temp/ and parent output/ as resource paths
        cmd.extend(["--resource-path", str(input_dir)])
        cmd.extend(["--resource-path", str(output_dir)])

    if css_file and css_file.exists():
        # Pandoc 3.0+ uses --css instead of --epub-stylesheet
        # Use absolute path for CSS file
        cmd.extend(["--css", str(css_file.resolve())])

    if metadata:
        # Pandoc metadata format: --metadata key=value
        for key, value in metadata.items():
            cmd.extend(["--metadata", f"{key}={value}"])

    if fonts:
        for font in fonts:
            if font.exists():
                cmd.extend(["--epub-embed-font", str(font)])

    # Disable automatic title page generation (we have our own cover)
    # Use --toc-depth=0 to disable TOC generation, or keep it but ensure cover is first
    # For now, keep TOC but it will appear after cover in reading order
    # Set --split-level=6 to prevent Pandoc from splitting on headings (max level is 6)
    # This ensures smooth chapter transitions without forced page breaks
    # Note: --epub-chapter-level is deprecated in Pandoc 3.8+, use --split-level instead
    # Using 6 means it won't split on any heading level (since max is h6)
    cmd.extend(
        [
            "--standalone",
            "--toc",
            "--toc-depth=3",
            "--epub-title-page=false",
            "--split-level=6",  # Don't split on headings, keep as single flow
        ]
    )

    try:
        subprocess.run(
            cmd,
            check=True,
            capture_output=True,
            text=True,
            timeout=300,  # 5 minute timeout
        )
        return True
    except FileNotFoundError:
        print("\n[ERROR] Pandoc is not installed!")
        print("Please install Pandoc first:")
        print("  - Windows: choco install pandoc")
        print("  - Or download from: https://github.com/jgm/pandoc/releases/latest")
        print("  - See INSTALL_PANDOC.md for details")
        return False
    except subprocess.CalledProcessError as e:
        print(f"Pandoc error: {e.stderr}")
        return False
    except subprocess.TimeoutExpired:
        print("Pandoc timeout: operation took longer than 5 minutes")
        return False
