"""Async image download and optimization for e-reader."""

import asyncio
import contextlib
import hashlib
import re
from pathlib import Path

import aiohttp
from PIL import Image


class ImageProcessor:
    """Processes images: async download + optimization."""

    def __init__(
        self,
        output_dir: Path,
        semaphore_limit: int = 20,
        max_width: int = 1200,
        max_height: int = 1600,
        quality: int = 85,
        grayscale: bool = False,
    ):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.semaphore = asyncio.Semaphore(semaphore_limit)
        self.max_width = max_width
        self.max_height = max_height
        self.quality = quality
        self.grayscale = grayscale

    def _is_video_url(self, url: str) -> bool:
        """Check if URL points to a video file."""
        video_extensions = (".mp4", ".mov", ".avi", ".webm", ".mkv", ".flv", ".m4v")
        url_lower = url.lower()
        return (
            any(url_lower.endswith(ext) for ext in video_extensions)
            or "video" in url_lower
        )

    def _is_valid_image(self, filepath: Path) -> bool:
        """Validate that downloaded file is actually an image."""
        try:
            with Image.open(filepath) as img:
                img.verify()
            return True
        except Exception:
            return False

    async def download_image(self, url: str, filename: str) -> Path | None:
        """Download image with rate limiting."""
        # Skip video files
        if self._is_video_url(url):
            print(f"Skipping video file: {url}")
            return None

        async with self.semaphore:
            try:
                async with (
                    aiohttp.ClientSession() as session,
                    session.get(
                        url, timeout=aiohttp.ClientTimeout(total=30)
                    ) as response,
                ):
                    if response.status == 200:
                        # Check content-type to avoid downloading videos
                        content_type = response.headers.get("Content-Type", "").lower()
                        if "video" in content_type:
                            print(
                                f"Skipping video (Content-Type: {content_type}): {url}"
                            )
                            return None

                        data = await response.read()
                        filepath = self.output_dir / filename
                        filepath.write_bytes(data)

                        # Validate downloaded file is actually an image
                        if not self._is_valid_image(filepath):
                            print(f"Downloaded file is not a valid image: {url}")
                            filepath.unlink()  # Remove invalid file
                            return None

                        return filepath
                    else:
                        print(f"Failed to download {url}: HTTP {response.status}")
                        return None
            except Exception as e:
                print(f"Error downloading {url}: {e}")
                return None

    def optimize_image(self, image_path: Path) -> Path | None:
        """Optimize image for e-reader. Returns None if optimization fails."""
        try:
            # Re-open image (verify() closed it)
            img = Image.open(image_path)

            # Convert RGBA to RGB if needed (JPEG doesn't support alpha)
            if img.mode in ("RGBA", "LA", "P"):
                background = Image.new("RGB", img.size, (255, 255, 255))
                if img.mode == "P":
                    img = img.convert("RGBA")
                background.paste(
                    img, mask=img.split()[-1] if img.mode in ("RGBA", "LA") else None
                )
                img = background
            elif img.mode != "RGB":
                img = img.convert("RGB")

            # Resize if needed
            if img.width > self.max_width or img.height > self.max_height:
                img.thumbnail(
                    (self.max_width, self.max_height), Image.Resampling.LANCZOS
                )

            # Convert to grayscale if requested
            if self.grayscale:
                img = img.convert("L")

            # Save as JPEG (aggressive compression)
            output_path = image_path.with_suffix(".jpg")
            img.save(output_path, "JPEG", quality=self.quality, optimize=True)

            # Remove original if converted
            if output_path != image_path:
                image_path.unlink()

            return output_path
        except Exception as e:
            print(f"Error optimizing {image_path}: {e}")
            # Clean up failed file
            with contextlib.suppress(Exception):
                image_path.unlink()
            return None

    async def process_images(self, markdown_content: str) -> tuple[str, list[Path]]:
        """Extract, download, optimize all images in Markdown."""
        # Extract image URLs with their alt text
        image_pattern = r"!\[([^\]]*)\]\((.*?)\)"
        image_matches = re.findall(image_pattern, markdown_content)

        if not image_matches:
            return markdown_content, []

        image_urls = [url for _, url in image_matches]

        # Generate unique filenames based on URL hash
        download_tasks = []
        url_to_filename = {}
        for i, url in enumerate(image_urls):
            # Create filename from URL hash
            url_hash = hashlib.md5(url.encode("utf-8")).hexdigest()[:8]
            filename = f"img_{i + 1}_{url_hash}.jpg"
            url_to_filename[url] = filename
            download_tasks.append(self.download_image(url, filename))

        # Download concurrently
        downloaded_paths = await asyncio.gather(*download_tasks)

        # Filter out None results and optimize
        optimized_paths = []
        valid_urls = []
        failed_urls = []

        for url, path in zip(image_urls, downloaded_paths, strict=False):
            if path:
                optimized_path = self.optimize_image(path)
                if optimized_path:
                    optimized_paths.append(optimized_path)
                    valid_urls.append(url)
                else:
                    failed_urls.append(url)
            else:
                failed_urls.append(url)

        # Update Markdown: replace successful downloads with local paths
        updated_content = markdown_content
        for url, path in zip(valid_urls, optimized_paths, strict=False):
            relative_path = f"images/{path.name}"
            # Replace image markdown syntax: ![alt](url) -> ![alt](relative_path)
            escaped_url = re.escape(url)
            pattern = rf"!\[([^\]]*)\]\({escaped_url}\)"
            replacement = rf"![\1]({relative_path})"
            updated_content = re.sub(pattern, replacement, updated_content)

        # Remove failed downloads from Markdown (remove entirely to avoid XML issues)
        for url in failed_urls:
            escaped_url = re.escape(url)
            pattern = rf"!\[([^\]]*)\]\({escaped_url}\)"
            # Remove the image markdown entirely to avoid XML parsing errors
            # EPUB readers don't need to see error messages
            replacement = ""
            updated_content = re.sub(pattern, replacement, updated_content)

        # Log summary
        total = len(image_urls)
        success = len(valid_urls)
        failed = len(failed_urls)
        print(
            f"\nImage processing summary: {success}/{total} successful, {failed} failed/skipped"
        )

        return updated_content, optimized_paths
