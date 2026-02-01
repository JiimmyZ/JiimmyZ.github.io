# Test Suite Documentation

This directory contains the automated test suite for the myblog project.

## Test Structure

```
tests/
├── __init__.py
├── conftest.py              # Shared pytest fixtures
├── test_media_processor.py  # Tests for media_processor.py
├── test_check_status.py     # Tests for check_status.py
├── test_integration.py       # Integration tests for workflows
├── ebook_generator/
│   ├── __init__.py
│   └── test_config.py       # Tests for ebook-generator/config.py
├── fixtures/
│   ├── sample_mapping.json  # Sample Cloudinary mapping file
│   └── sample_markdown.md   # Sample markdown file
└── utils.py                 # Test utility functions
```

## Running Tests

### Run all tests
```bash
pytest
```

### Run with coverage report
```bash
pytest --cov=. --cov-report=html
```

### Run specific test file
```bash
pytest tests/test_media_processor.py
```

### Run specific test class
```bash
pytest tests/test_media_processor.py::TestFindMediaFiles
```

### Run tests with markers
```bash
pytest -m unit          # Run only unit tests
pytest -m integration   # Run only integration tests
pytest -m cloudinary    # Run Cloudinary-related tests
```

## Test Markers

- `@pytest.mark.unit` - Unit tests (fast, isolated)
- `@pytest.mark.integration` - Integration tests (may involve multiple components)
- `@pytest.mark.cloudinary` - Tests that mock Cloudinary API
- `@pytest.mark.ffmpeg` - Tests that mock FFmpeg subprocess

## Coverage Goals

- Core functions (`media_processor.py`): ≥80% coverage
- Utility scripts (`check_status.py`): ≥70% coverage
- Configuration (`config.py`): ≥90% coverage

## Test Fixtures

Common fixtures available in `conftest.py`:

- `tmp_content_dir` - Temporary content directory structure
- `sample_media_files` - Sample image and video files
- `sample_mapping_file` - Sample Cloudinary mapping JSON
- `sample_markdown_file` - Sample markdown with media references
- `mock_cloudinary_upload_response` - Mock Cloudinary upload response
- `mock_cloudinary_resources_response` - Mock Cloudinary resources list
- `mock_ffmpeg_success` - Mock successful FFmpeg execution
- `mock_env_vars` - Mock environment variables

## CI/CD Integration

Tests run automatically in GitHub Actions on every push. The test job:

1. Installs dependencies from `requirements.txt` and `requirements-dev.txt`
2. Runs pytest with coverage reporting
3. Uploads coverage reports as artifacts

Test failures block the deployment pipeline.

## Notes

- All external dependencies (Cloudinary API, FFmpeg) are mocked in tests
- Tests use temporary directories to avoid modifying actual project files
- Integration tests use extensive mocking to avoid actual API calls
