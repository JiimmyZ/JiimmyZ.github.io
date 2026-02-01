"""Main orchestration script for Camino ebook generation."""

import asyncio
from pathlib import Path

import config
from merge_chapters import merge_chapters
from src.cover_generator import generate_cover_markdown
from src.image_processor import ImageProcessor
from src.markdown_parser import ast_to_markdown, parse_markdown_to_ast
from src.pandoc_wrapper import generate_epub
from src.translator import ASTTranslator


async def main():
    """Orchestrate the entire pipeline."""
    print("Starting Camino ebook generation...")

    # 0. Merge all chapters into single file (won't interfere with website)
    print("Step 1: Merging chapters...")
    merged_file = merge_chapters()

    if not merged_file.exists():
        print("Error: Failed to create merged file!")
        return

    # 1. Read merged file (skip AST parsing for now to avoid HTML conversion issues)
    print("\nStep 2: Reading merged content...")
    merged_content = merged_file.read_text(encoding="utf-8")
    print(f"  Read merged file: {merged_file}")

    # 2. Process images (async, concurrent)
    print("\nStep 3: Processing images...")
    image_processor = ImageProcessor(
        config.IMAGE_OUTPUT_DIR,
        config.CONCURRENT_DOWNLOADS,
        config.MAX_IMAGE_WIDTH,
        config.MAX_IMAGE_HEIGHT,
        config.IMAGE_QUALITY,
        config.GRAYSCALE_MODE,
    )

    updated_md, image_paths = await image_processor.process_images(merged_content)
    print(f"  Processed {len(image_paths)} images")

    # 3. Translate (AST-based, async) - Skip for now if no API key
    if not config.GEMINI_API_KEY:
        print("\nStep 4: Warning: GEMINI_API_KEY not set. Skipping translation.")
        final_content = updated_md
    else:
        print("\nStep 4: Translating content...")
        # Parse to AST for translation
        ast = parse_markdown_to_ast(updated_md)
        translator = ASTTranslator(
            config.GEMINI_API_KEY,
            config.TRANSLATION_SEMAPHORE,
            config.TRANSLATION_CACHE,
        )
        translated_ast = await translator.translate_ast(ast)
        print("  Translation complete")
        # Convert back to markdown
        final_content = ast_to_markdown(translated_ast)

    # 4. Generate cover and combine
    print("\nStep 5: Preparing final content...")
    cover_md = generate_cover_markdown(config.COVER_TITLE_ZH, config.COVER_TITLE_EN)

    final_markdown = cover_md + final_content

    # Write to temp file for Pandoc
    temp_dir = Path("output/temp")
    temp_dir.mkdir(parents=True, exist_ok=True)

    temp_file = temp_dir / "camino_final.md"
    temp_file.write_text(final_markdown, encoding="utf-8")
    print(f"  Created final Markdown: {temp_file}")

    # 5. Generate EPUB with Pandoc
    print("\nStep 6: Generating EPUB with Pandoc...")
    success = generate_epub(
        [temp_file],
        config.OUTPUT_FILE,
        css_file=config.CSS_FILE,
        metadata=config.EPUB_METADATA,
    )

    if success:
        if config.OUTPUT_FILE.exists():
            file_size = config.OUTPUT_FILE.stat().st_size / (1024 * 1024)  # MB
            print(f"\n[SUCCESS] EPUB generated successfully: {config.OUTPUT_FILE}")
            print(f"  File size: {file_size:.2f} MB")

            # Post-process: Fix spine order to put cover page first
            print("\nStep 7: Fixing EPUB spine order...")
            from fix_epub_spine import fix_epub_spine

            if fix_epub_spine(config.OUTPUT_FILE):
                print("  Cover page is now the first page")
        else:
            print(
                f"\n[WARNING] EPUB generation reported success but file not found: {config.OUTPUT_FILE}"
            )
    else:
        print("\n[ERROR] EPUB generation failed")


if __name__ == "__main__":
    asyncio.run(main())
