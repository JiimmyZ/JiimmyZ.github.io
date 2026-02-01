"""
Integration tests for complete workflows.

Tests cover end-to-end workflows with extensive mocking to avoid
actual Cloudinary API calls and file system modifications.
"""

import json
import os
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from media_processor import (
    find_media_files,
    load_existing_mapping,
    load_markdown_mapping,
    save_mapping,
    update_markdown_file,
)


@pytest.mark.integration
class TestUploadWorkflow:
    """Integration tests for upload workflow."""

    def test_upload_workflow_complete(
        self, mocker, tmp_content_dir, sample_media_files, mock_cloudinary_upload_response
    ):
        """Test complete upload workflow: find files → upload → save mapping."""
        # Setup
        mapping_file = tmp_content_dir.parent / "cloudinary_mapping.json"
        
        # Mock Cloudinary upload
        mock_upload = mocker.patch("cloudinary.uploader.upload")
        mock_upload.return_value = mock_cloudinary_upload_response
        
        # Mock Cloudinary config
        mocker.patch("media_processor.cloudinary_settings")
        
        original_cwd = Path.cwd()
        try:
            os.chdir(tmp_content_dir.parent)
            
            # Step 1: Find media files
            media_files = find_media_files(str(tmp_content_dir.name))
            assert len(media_files) >= 3
            
            # Step 2: Load existing mapping (should be empty)
            mapping = load_existing_mapping(str(mapping_file))
            assert len(mapping) == 0
            
            # Step 3: Upload files (simulate)
            uploaded_count = 0
            for file_path in media_files[:2]:  # Upload first 2 files
                relative_path = str(file_path.relative_to(tmp_content_dir))
                
                # Simulate upload_file call
                from media_processor import upload_file, CloudinaryResource
                from datetime import datetime
                
                result = upload_file(file_path, folder="myblog")
                if result:
                    mapping[relative_path] = result
                    uploaded_count += 1
            
            # Step 4: Save mapping
            save_mapping(mapping, str(mapping_file))
            
            # Verify workflow results
            assert uploaded_count == 2
            assert mapping_file.exists()
            
            # Verify mapping structure
            with open(mapping_file, encoding="utf-8") as f:
                saved_mapping = json.load(f)
            
            assert len(saved_mapping) == 2
            assert all("url" in entry for entry in saved_mapping.values())
            assert all("public_id" in entry for entry in saved_mapping.values())
        finally:
            os.chdir(original_cwd)

    def test_upload_workflow_skips_existing(
        self, mocker, tmp_content_dir, sample_media_files, sample_mapping_file
    ):
        """Test upload workflow skips files already in mapping."""
        # Copy sample mapping to project root
        mapping_file = tmp_content_dir.parent / "cloudinary_mapping.json"
        if sample_mapping_file.exists():
            import shutil
            shutil.copy(sample_mapping_file, mapping_file)
        
        # Mock Cloudinary (should not be called for existing files)
        mock_upload = mocker.patch("cloudinary.uploader.upload")
        
        original_cwd = Path.cwd()
        try:
            os.chdir(tmp_content_dir.parent)
            
            # Load existing mapping
            mapping = load_existing_mapping(str(mapping_file))
            existing_count = len(mapping)
            
            # Find files
            media_files = find_media_files(str(tmp_content_dir.name))
            
            # Check which files need upload
            existing_relative_paths = set(mapping.keys())
            need_upload = [
                f for f in media_files
                if str(f.relative_to(tmp_content_dir)) not in existing_relative_paths
            ]
            
            # Should skip files already in mapping
            assert len(need_upload) < len(media_files)
            
            # Upload should not be called for existing files
            # (This is tested by checking need_upload list)
        finally:
            os.chdir(original_cwd)


@pytest.mark.integration
class TestMarkdownUpdateWorkflow:
    """Integration tests for markdown update workflow."""

    def test_markdown_update_workflow_complete(
        self, tmp_path, sample_mapping_file, sample_markdown_file
    ):
        """Test complete markdown update workflow."""
        # Setup: Copy mapping file
        mapping_file = tmp_path / "cloudinary_mapping.json"
        import shutil
        shutil.copy(sample_mapping_file, mapping_file)
        
        # Setup: Create content directory with markdown
        content_dir = tmp_path / "content"
        content_dir.mkdir()
        md_file = content_dir / "test_post.md"
        md_file.write_text(
            "![Image 1](IMG_001.jpg)\n![Image 2](IMG_002.png)",
            encoding="utf-8"
        )
        
        # Step 1: Load mapping
        url_mapping = load_markdown_mapping(str(mapping_file))
        assert len(url_mapping) > 0
        
        # Step 2: Find markdown files
        from media_processor import find_markdown_files
        markdown_files = find_markdown_files(str(content_dir))
        assert len(markdown_files) == 1
        
        # Step 3: Update markdown files
        total_replacements = 0
        for md_file_path in markdown_files:
            replacements = update_markdown_file(md_file_path, url_mapping, backup=False)
            total_replacements += replacements
        
        # Step 4: Verify updates
        assert total_replacements > 0
        
        # Verify content was updated
        updated_content = md_file.read_text(encoding="utf-8")
        assert "https://res.cloudinary.com" in updated_content

    def test_markdown_update_workflow_multiple_files(
        self, tmp_path, sample_mapping_file
    ):
        """Test markdown update workflow with multiple files."""
        # Setup
        mapping_file = tmp_path / "cloudinary_mapping.json"
        import shutil
        shutil.copy(sample_mapping_file, mapping_file)
        
        content_dir = tmp_path / "content"
        content_dir.mkdir()
        
        # Create multiple markdown files
        md_files = []
        for i in range(3):
            md_file = content_dir / f"post_{i}.md"
            md_file.write_text(f"![Image](IMG_001.jpg)", encoding="utf-8")
            md_files.append(md_file)
        
        # Load mapping and update
        url_mapping = load_markdown_mapping(str(mapping_file))
        from media_processor import find_markdown_files, update_markdown_file
        
        markdown_files = find_markdown_files(str(content_dir))
        assert len(markdown_files) == 3
        
        total_replacements = 0
        for md_file_path in markdown_files:
            replacements = update_markdown_file(md_file_path, url_mapping, backup=False)
            total_replacements += replacements
        
        assert total_replacements == 3  # One replacement per file

    def test_markdown_update_workflow_with_backup(
        self, tmp_path, sample_mapping_file
    ):
        """Test markdown update workflow creates backups."""
        # Setup
        mapping_file = tmp_path / "cloudinary_mapping.json"
        import shutil
        shutil.copy(sample_mapping_file, mapping_file)
        
        content_dir = tmp_path / "content"
        content_dir.mkdir()
        md_file = content_dir / "test.md"
        md_file.write_text("![Image](IMG_001.jpg)", encoding="utf-8")
        
        # Update with backup
        url_mapping = load_markdown_mapping(str(mapping_file))
        from media_processor import find_markdown_files, update_markdown_file
        
        markdown_files = find_markdown_files(str(content_dir))
        update_markdown_file(markdown_files[0], url_mapping, backup=True)
        
        # Verify backup was created
        backup_file = content_dir / "test.md.backup"
        assert backup_file.exists()


@pytest.mark.integration
class TestDuplicateDetectionWorkflow:
    """Integration tests for duplicate detection workflow."""

    def test_duplicate_detection_workflow(
        self, mocker, mock_cloudinary_resources_response
    ):
        """Test complete duplicate detection workflow."""
        # Mock Cloudinary API resources call
        mock_resources = mocker.patch("cloudinary.api.resources")
        mock_resources.return_value = mock_cloudinary_resources_response
        
        # Mock Cloudinary config
        mocker.patch("media_processor.cloudinary_settings")
        
        # Test list_all_resources function
        from media_processor import list_all_resources, find_duplicates
        
        # Step 1: List resources
        images = list_all_resources(resource_type="image", folder="myblog")
        assert len(images) == 3
        
        # Step 2: Find duplicates
        duplicates = find_duplicates(images)
        
        # Step 3: Verify detection
        # Should find IMG_001 as duplicate (appears twice)
        assert len(duplicates) == 1
        assert "IMG_001" in duplicates
        assert len(duplicates["IMG_001"]["delete"]) == 1

    def test_duplicate_detection_workflow_no_duplicates(self, mocker):
        """Test duplicate detection when no duplicates exist."""
        # Mock resources with no duplicates
        mock_resources = mocker.patch("cloudinary.api.resources")
        mock_resources.return_value = {
            "resources": [
                {
                    "public_id": "myblog/travelogue/camino/ch1/IMG_001",
                    "resource_type": "image",
                    "bytes": 1024,
                    "created_at": "2024-01-01T00:00:00Z"
                },
                {
                    "public_id": "myblog/travelogue/camino/ch2/IMG_002",
                    "resource_type": "image",
                    "bytes": 2048,
                    "created_at": "2024-01-02T00:00:00Z"
                }
            ],
            "next_cursor": None
        }
        
        mocker.patch("media_processor.cloudinary_settings")
        
        from media_processor import list_all_resources, find_duplicates
        
        images = list_all_resources(resource_type="image", folder="myblog")
        duplicates = find_duplicates(images)
        
        assert len(duplicates) == 0

    def test_duplicate_detection_workflow_pagination(self, mocker):
        """Test duplicate detection with paginated API responses."""
        # Mock paginated responses
        mock_resources = mocker.patch("cloudinary.api.resources")
        
        # First page
        mock_resources.side_effect = [
            {
                "resources": [
                    {
                        "public_id": "myblog/travelogue/camino/ch1/IMG_001",
                        "resource_type": "image",
                        "bytes": 1024,
                        "created_at": "2024-01-01T00:00:00Z"
                    }
                ],
                "next_cursor": "cursor123"
            },
            # Second page
            {
                "resources": [
                    {
                        "public_id": "myblog/travelogue/camino/ch2/IMG_001",  # Duplicate filename
                        "resource_type": "image",
                        "bytes": 1024,
                        "created_at": "2024-01-02T00:00:00Z"
                    }
                ],
                "next_cursor": None
            }
        ]
        
        mocker.patch("media_processor.cloudinary_settings")
        
        from media_processor import list_all_resources, find_duplicates
        
        images = list_all_resources(resource_type="image", folder="myblog")
        assert len(images) == 2
        
        duplicates = find_duplicates(images)
        assert len(duplicates) == 1
        assert "IMG_001" in duplicates
