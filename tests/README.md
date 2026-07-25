# Test Suite Documentation

This directory contains the automated test suite for the myblog project.

## Test Structure

```
tests/
├── __init__.py
├── conftest.py              # Shared pytest fixtures
├── test_media_processor.py  # Tests for media_processor.py
├── test_check_status.py     # Tests for check_status.py
└── test_integration.py      # Integration tests for workflows
```

## Running Tests

### Run all tests
```bash
pytest
```

Coverage flags come from `pytest.ini`, so a bare `pytest` already produces
`term-missing`, `htmlcov/`, and `coverage.xml`.

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

## Coverage

The gate lives in `pytest.ini` (`--cov-fail-under`) and is a ratchet set just below
the current total, so a regression fails CI. Coverage scope/omissions are in `.coveragerc`.

| Module | Current | Goal |
|--------|---------|------|
| `media_processor.py` | ~51% | ≥80% |
| `check_status.py` | 0% (module-level script, not imported by tests) | ≥70% |
| **Total gate** | **45%** | raise as coverage improves |

## Test Fixtures

Common fixtures available in `conftest.py`:

- `tmp_content_dir` - Temporary content directory structure
- `sample_media_files` - Sample image and video files
- `sample_mapping_file` - Sample Cloudinary mapping JSON
- `sample_markdown_file` - Sample markdown with media references
- `mock_cloudinary_upload_response` - Mock Cloudinary upload response
- `mock_cloudinary_resources_response` - Mock Cloudinary resources list
- `mock_ffmpeg_success` - Mock successful FFmpeg execution
- `mock_ffmpeg_not_found` - Mock FFmpeg missing from PATH

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
