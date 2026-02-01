"""
Image processor that handles image downloading and optimization.
"""

from pathlib import Path
from typing import Any

from ..image_sources.base_source import BaseImageSource
from ..image_sources.cloudinary import CloudinaryImageSource
from ..image_sources.local import LocalImageSource


class ImageProcessor:
    """Processes images from various sources."""

    def __init__(self, source_type: str, optimize: bool = True, max_size: str = "2MB"):
        """
        Initialize image processor.

        Args:
            source_type: Type of image source ('cloudinary', 'local', etc.)
            optimize: Whether to optimize images
            max_size: Maximum image size
        """
        self.source_type = source_type
        self.image_source = self._create_image_source(source_type, optimize, max_size)
        self.url_mapping: dict[str, str] = {}  # Maps original URLs to local paths

    def _create_image_source(
        self, source_type: str, optimize: bool, max_size: str
    ) -> BaseImageSource:
        """Create appropriate image source handler."""
        if source_type == "cloudinary":
            return CloudinaryImageSource(optimize=optimize, max_size=max_size)
        elif source_type == "local":
            return LocalImageSource()
        else:
            raise ValueError(f"Unsupported image source type: {source_type}")

    def process_images(
        self, content_list: list[dict[str, Any]], output_dir: Path
    ) -> list[dict[str, Any]]:
        """
        Process all images in content list.

        Args:
            content_list: List of parsed content dictionaries
            output_dir: Directory to save downloaded images

        Returns:
            Updated content list with local image paths
        """
        images_dir = output_dir / "images"
        images_dir.mkdir(parents=True, exist_ok=True)

        image_counter = 1

        for content_item in content_list:
            images = content_item.get("images", [])
            updated_content = content_item["content"]

            for image_url in images:
                # Skip if already processed
                if image_url in self.url_mapping:
                    continue

                # Generate output filename
                image_name = self._generate_image_name(image_url, image_counter)
                output_path = images_dir / image_name

                # Download image
                downloaded_path = self.image_source.download_image(
                    image_url, output_path
                )

                if downloaded_path:
                    # Map original URL to local path
                    local_path = f"images/{downloaded_path.name}"
                    self.url_mapping[image_url] = local_path
                    image_counter += 1
                else:
                    print(f"Warning: Failed to download image: {image_url}")

            # Update content with local paths
            updated_content = self.image_source.update_content_urls(
                updated_content, self.url_mapping
            )
            content_item["content"] = updated_content

        return content_list

    def _generate_image_name(self, image_url: str, counter: int) -> str:
        """Generate a filename for downloaded image."""
        # Try to extract original filename from URL
        from urllib.parse import urlparse

        parsed = urlparse(image_url)
        original_name = Path(parsed.path).name

        # Clean filename
        if original_name and "." in original_name:
            # Keep original extension
            ext = original_name.split(".")[-1]
            # Clean name (remove special chars)
            name = "".join(
                c for c in original_name.split(".")[0] if c.isalnum() or c in ("-", "_")
            )
            if not name:
                name = f"image_{counter}"
            return f"{name}.{ext}"
        else:
            # Default name
            return f"image_{counter}.jpg"
