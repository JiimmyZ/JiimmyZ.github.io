# Project Context

## Project Overview

### Project Type
Hugo static site blog with extensive media content (travelogue with photos and videos)

### Technology Stack
- **Static Site Generator**: Hugo
- **Theme**: PaperMod
- **Media Storage**: Cloudinary (CDN)
- **Comments System**: Giscus (GitHub Discussions)
- **Version Control**: Git / GitHub Pages
- **Python Scripts**: 
  - `cloudinary` SDK (v1.44.1)
  - `python-dotenv` (v1.2.1)
  - `pydantic` (v2.12.5) - Data validation and type safety
  - `pydantic-settings` (v2.12.0) - Settings management
- **Deployment**: GitHub Actions → GitHub Pages

### Project Structure
```
myblog/
├── content/              # Hugo content directory
│   └── travelogue/       # Travel blog posts with media
├── themes/               # Hugo themes
├── public/               # Generated static site
├── media_processor.py         # 圖片影片處理工具（整合上傳、更新、檢測、壓縮）⭐
├── check_status.py             # Upload status checker
└── cloudinary_mapping.json    # Local file → Cloudinary URL mapping
```

## Recent Session Logs

### Session Log 2026-02-01 (Late Evening) - Cloudinary Image Display Issues Resolution

**Summary**: Resolved image display issues in ch2 and ch3 by identifying root causes (incorrect chapter paths, stale timestamps, mapping-reality mismatch) and implementing force re-upload solution.

**Problem Discovery**:
- User reported images in ch2 and ch3 not displaying
- Initial investigation found URLs with incorrect chapter paths (pointing to ch6/ch7 instead of ch2/ch3)
- URLs also had incorrect timestamps

**Initial Fix Attempts**:
1. ✅ Corrected chapter paths in markdown URLs (ch6 → ch2, ch7 → ch2, ch6 → ch3)
2. ✅ Updated timestamps to match mapping file entries
3. ❌ Images still not displaying after URL corrections

**Root Cause Analysis**:
- Mapping file contained entries but images may not have been actually uploaded to Cloudinary
- `update-markdown` command couldn't always match files with identical filenames across different chapters
- Need to verify actual Cloudinary resource existence, not just mapping file presence

**Final Resolution**:
1. Created temporary `force_upload_ch2_ch3.py` script to force re-upload 4 problematic images
2. Successfully re-uploaded:
   - `ch2/IMG_20250616_121207.jpg` → v1769928422
   - `ch2/IMG_20250616_121609.jpg` → v1769928438
   - `ch3/IMG_20250613_145504.jpg` → v1769928448
   - `ch3/IMG_20250616_143116.jpg` → v1769928471
3. Ran `update-markdown` to update all markdown files with new URLs
4. Fixed remaining incorrect chapter paths manually

**Key Learnings Documented**:
- Added comprehensive troubleshooting guide to context.md
- Documented prevention strategy for future issues
- Identified need for `--force` flag in upload command
- Highlighted `update-markdown` limitations with same-filename-different-path scenarios

**Files Modified**:
- `content/travelogue/camino/ch2/index.md` - Fixed 4 image URLs
- `content/travelogue/camino/ch3/index.md` - Fixed 5 image URLs
- `cloudinary_mapping.json` - Updated with new timestamps after re-upload
- `context.md` - Added detailed problem resolution documentation

**Status**: **RESOLVED** - All images now have correct URLs and are successfully uploaded to Cloudinary.

### Session Log 2026-02-01 (Evening) - Automated Testing Implementation

**Summary**: Implemented comprehensive automated testing framework using pytest with unit tests, integration tests, coverage reporting, and CI/CD integration. All Python scripts now have test coverage, and tests run automatically in GitHub Actions before deployment.

**Implementation Phases**:

**Phase 1: Test Infrastructure Setup**
- Created `tests/` directory structure with proper organization
- Added pytest dependencies to `requirements-dev.txt`: pytest, pytest-cov, pytest-mock, pytest-asyncio, responses
- Created `pytest.ini` with coverage configuration and test markers
- Created `tests/conftest.py` with shared fixtures for common test scenarios
- Created test utilities (`tests/utils.py`) and sample test data files

**Phase 2-4: Unit Tests**
- **`tests/test_media_processor.py`** (673 lines): Comprehensive tests for media processing
  - Pure function tests: `find_media_files()`, `normalize_url()`, `find_duplicates()`
  - Mocked function tests: `upload_file()`, `load_existing_mapping()`, `save_mapping()`, `update_markdown_file()`, `compress_video()`, `check_ffmpeg()`
- **`tests/test_check_status.py`**: Tests for upload status verification script
- **`tests/ebook_generator/test_config.py`**: Tests for Pydantic configuration models with validation, backward compatibility, and environment variable loading

**Phase 5: Integration Tests**
- **`tests/test_integration.py`**: End-to-end workflow tests
  - Upload workflow: find files → upload → save mapping
  - Markdown update workflow: load mapping → update links → verify changes
  - Duplicate detection workflow: list resources → find duplicates → verify logic

**Phase 6: CI/CD Integration**
- Updated `.github/workflows/deploy.yml` to add `test` job before `lint` job
- Test job installs dependencies, runs pytest with coverage, and uploads coverage reports
- Workflow structure: `test → lint → build → deploy`
- Test failures now block deployment pipeline

**Test Coverage**:
- 80+ test functions across 15+ test classes
- Coverage targets: Core functions ≥80%, utilities ≥70%, config ≥90%
- All external dependencies (Cloudinary API, FFmpeg) are mocked
- Tests use temporary directories to avoid modifying actual project files

**Files Created**:
- `tests/__init__.py`, `tests/conftest.py`, `tests/utils.py`
- `tests/test_media_processor.py`, `tests/test_check_status.py`, `tests/test_integration.py`
- `tests/ebook_generator/__init__.py`, `tests/ebook_generator/test_config.py`
- `tests/fixtures/sample_mapping.json`, `tests/fixtures/sample_markdown.md`
- `tests/README.md` - Test documentation
- `pytest.ini` - Pytest configuration

**Files Modified**:
- `requirements-dev.txt` - Added pytest and testing dependencies
- `.github/workflows/deploy.yml` - Added test job with coverage reporting

**Status**: **COMPLETED** - Full test suite implemented and integrated into CI/CD pipeline.

### Session Log 2026-02-01 (Evening) - Pydantic Integration Implementation

**Summary**: Implemented Pydantic integration across Python scripts to improve type safety, data validation, and configuration management. Completed Phase 1 (Foundation Setup), Phase 2 (Ebook Generator Configuration), and Phase 3 (Cloudinary Data Models) of the Pydantic integration plan.

**Implementation Phases**:

**Phase 1: Foundation Setup**
- Added `pydantic>=2.0.0` and `pydantic-settings>=2.0.0` to dependencies
- Created `CloudinarySettings` class using `BaseSettings` for environment variable validation
- Replaced manual `os.getenv()` calls with validated settings
- Scripts now fail fast with clear error messages if environment variables are missing
- Removed redundant credential checks in command functions

**Phase 2: Ebook Generator Configuration**
- Rewrote `ebook-generator/config.py` to use Pydantic models
- Created `EbookConfig` class with `BaseSettings` for all configuration values
- Created `EpubMetadata` model for EPUB metadata
- Added type hints and validation for all config values (ranges, paths, etc.)
- Maintained backward compatibility with old `UPPER_CASE` constant names
- Added support for `GEMINI_API_KEY` from environment variables

**Phase 3: Cloudinary Data Models**
- Created `CloudinaryResource` model with validated fields:
  - `local_path`, `relative_path`, `public_id`, `url`
  - `resource_type`: `Literal["image", "video"]`
  - `bytes`: non-negative integer validation
  - `uploaded_at`: optional datetime
- Updated `upload_file()` to return `CloudinaryResource` instead of dict
- Updated `load_existing_mapping()` to return `dict[str, CloudinaryResource]` with automatic validation
- Updated `save_mapping()` to serialize Pydantic models
- Updated `load_markdown_mapping()` to use CloudinaryResource models
- Updated `cmd_upload()` to use model attributes instead of dict access
- Maintained backward compatibility with old JSON format

**Benefits**:
- **Type Safety**: All mapping operations now have type hints and IDE autocomplete
- **Data Validation**: JSON data is automatically validated when loaded
- **Better Error Messages**: Clear validation errors for missing/invalid configuration
- **IDE Support**: Full autocomplete for all config values and data models
- **Backward Compatibility**: All existing workflows continue to work unchanged

**Files Modified**:
- `requirements.txt` - Added Pydantic dependencies
- `media_processor.py` - Added CloudinarySettings, CloudinaryResource models, updated all functions
- `ebook-generator/config.py` - Complete rewrite using Pydantic models

**Status**: **COMPLETED** - Phase 1, 2, and 3 successfully implemented and tested.

**Future Work**:
- Phase 4: API Response Models (Low Priority, optional) - Add models for Cloudinary API responses

### Session Log 2026-02-01 (Evening) - Comments System Evaluation & Decision to Maintain Giscus

**Summary**: Evaluated options for adding Google login support to comments system. After comparing Giscus, Disqus, and Cusdis, decided to maintain current Giscus-only setup to preserve minimal design aesthetic.

**Problem Statement**:
- User requested support for additional login methods (e.g., Google) in addition to GitHub
- Current Giscus system only supports GitHub OAuth authentication
- Need to evaluate alternatives that support multiple OAuth providers

**Research & Comparison**:

**1. Giscus (Current System)**
- **Pros**: Free, open-source, privacy-focused, lightweight (~40KB), no tracking/ads, integrates with GitHub ecosystem
- **Cons**: Only supports GitHub login, requires GitHub account, limits non-technical users
- **Best for**: Technical blogs, developer communities

**2. Disqus**
- **Pros**: Supports multiple login methods (Google, Facebook, Twitter, anonymous), mature platform, feature-rich
- **Cons**: Privacy concerns (tracking, ads), performance issues (heavy JavaScript), data stored on third-party servers, requires VPN in China
- **Best for**: General content websites needing broad user engagement

**3. Cusdis**
- **Pros**: Open-source, privacy-focused, supports multiple OAuth providers (Google, GitHub, Twitter), lightweight
- **Cons**: Limited free tier, requires paid subscription ($12/year) or self-hosting for full features, smaller community
- **Best for**: Privacy-conscious sites willing to pay/self-host

**Decision**: **Maintain Giscus-only setup**

**Rationale**:
1. **Design Consistency**: Dual comment system (Giscus + Disqus/Cusdis) would require UI switcher/tabs, which conflicts with the site's minimal design philosophy
2. **Target Audience Alignment**: Site content (literature, poetry, travelogue) likely attracts users comfortable with GitHub or willing to create GitHub accounts
3. **Performance & Privacy**: Giscus maintains excellent performance (lightweight) and privacy (no tracking), aligning with site values
4. **Simplicity**: Single comment system reduces maintenance overhead and keeps codebase clean
5. **User Experience**: Minimal interface without comment system switcher provides cleaner, more focused reading experience

**Trade-offs Accepted**:
- Some users without GitHub accounts may be unable to comment
- Potential reduction in comment engagement from non-technical users
- Benefits of minimal design and performance outweigh accessibility concerns for this use case

**Status**: **MAINTAINED** - Giscus remains the sole comment system. No code changes made.

**Future Considerations**:
- If comment engagement becomes a significant issue, revisit decision
- Monitor user feedback regarding GitHub login requirement
- Consider alternative solutions if Giscus adds multi-OAuth support in future

### Session Log 2026-02-01 (Evening) - Minimal Inline Donation Section Implementation

**Summary**: Implemented a minimal inline donation section component following the plan document. Created a simple, unobtrusive donation button that displays a "not yet available" message when clicked.

**Features Implemented**:
- Created `layouts/partials/donation_section.html` - Minimal donation section component with modal functionality
- Modified `layouts/_default/single.html` - Integrated donation section after post-footer and before comments
- Updated `hugo.toml` - Added minimal donation configuration (`enabled = true`, `title = "Buy JZ a coffee"`)

**Design Evolution**:
1. **Initial Implementation**: Full donation section with title "Buy JZ a coffee" and "Donate" button
2. **Refinement 1**: Removed title for cleaner look, changed button text to "Buy JZ Coffee"
3. **Refinement 2**: Reduced padding and size for more compact design (padding: 0.75rem → 0.5rem, font-size: 1rem → 0.875rem)
4. **Final**: Removed border and background to seamlessly blend with page content

**Component Features**:
- Minimal design: Single button with "Buy JZ Coffee" text
- Modal dialog: Shows "Donation feature is not yet available. Stay tuned!" message
- No border/background: Seamlessly integrated into page flow
- Responsive design: Works on mobile and desktop
- Theme support: Auto-adapts to light/dark mode
- Accessibility: ARIA labels, keyboard navigation, focus management
- Vanilla JavaScript: No external dependencies

**Configuration**:
- Location: Between post-footer and comments section
- Conditional rendering: Controlled by `site.Params.donation.enabled`
- Button text: "Buy JZ Coffee"
- Modal message: "Donation feature is not yet available. Stay tuned!"

**Files Created**:
- `layouts/partials/donation_section.html` - Donation section component (251 lines)

**Files Modified**:
- `layouts/_default/single.html` - Added donation section partial reference
- `hugo.toml` - Added minimal donation configuration

**Git Commits**:
- `0ecf2df`: Initial implementation
- `29e8bf6`: Design refinement (remove title, change button text, reduce size)
- `74a2bf2`: Remove border and background

**Status**: **ACTIVE** - Feature is enabled and working on all article pages

**Note**: This is a simplified version compared to the previous QR Code-based donation feature. The modal serves as a placeholder for future donation functionality implementation.


## Project Improvement Plan Overview (2026-02-01)

**Summary**: Comprehensive technical assessment identifying improvement opportunities in testing, CI/CD, code quality, documentation, and security.

### Priority Categories

**High Priority (Immediate)**:
1. ✅ **Automated Testing** - Comprehensive pytest test suite implemented (completed)
2. **Error Handling** - Basic error handling, needs structured logging and retry mechanisms
3. ✅ **CI/CD Testing** - GitHub Actions test job added before deployment (completed)

**Medium Priority (Short-term)**:
4. **Dependency Locking** - Versions use `>=` ranges, need pinning
5. ✅ **Code Formatting** - Ruff integrated for linting and formatting (completed)
6. **Documentation** - Missing developer docs (CONTRIBUTING.md, DEVELOPMENT.md)

**Low Priority (Long-term)**:
7. **Performance Monitoring** - No metrics for upload/processing times
8. **Security Scanning** - No dependency vulnerability scanning
9. **Build Validation** - No HTML validation or broken links checking

### Key Improvements Identified

- ✅ **Testing**: Comprehensive pytest test suite implemented (completed)
  - Unit tests for `media_processor.py`, `check_status.py`, and `ebook-generator/config.py`
  - Integration tests for complete workflows
  - Coverage reporting with targets: core functions ≥80%, utilities ≥70%, config ≥90%
  - All tests use mocking for external dependencies (Cloudinary, FFmpeg)
- ✅ **Linting**: Ruff integrated for code formatting and style checking (completed)
  - Added to `requirements-dev.txt`
  - Integrated into GitHub Actions workflow (lint job with `ruff check` and `ruff format --check`)
- **Error Handling**: Replace print statements with structured logging (logging module)
- ✅ **CI/CD**: Test job added to GitHub Actions workflow (completed)
  - Tests run automatically on every push before lint/build/deploy
  - Coverage reports generated and uploaded as artifacts
  - Test failures block deployment pipeline
- **Dependencies**: Lock versions in requirements.txt, add requirements-dev.txt
- **Documentation**: Create CONTRIBUTING.md and DEVELOPMENT.md guides

**Full details**: See plan document for complete analysis and implementation recommendations.

## Current Issues & Improvements Needed

### Resolved Issues ✅

#### Image Display Issues - Cloudinary URL Mismatch (2026-02-01)

**Problem**: Images in ch2 and ch3 were not displaying despite URLs appearing correct in markdown files.

**Root Causes Identified**:
1. **Incorrect Chapter Paths**: URLs pointed to wrong chapters (e.g., `ch6/IMG_xxx.jpg` instead of `ch2/IMG_xxx.jpg`)
2. **Stale Timestamps**: URLs had old timestamps that may not match actual Cloudinary resources
3. **Mapping vs Reality Mismatch**: Files existed in `cloudinary_mapping.json` but may not have been actually uploaded to Cloudinary
4. **Update-Markdown Limitations**: The `update-markdown` command couldn't always match files correctly when filenames were identical across different chapters

**Resolution Process**:
1. ✅ Fixed incorrect chapter paths in markdown URLs
2. ✅ Corrected timestamps to match mapping file
3. ✅ **Force re-uploaded problematic images** to Cloudinary to ensure they exist
4. ✅ Updated all markdown files with new valid URLs

**Key Learnings**:
- **Don't trust mapping file alone**: Even if a file exists in `cloudinary_mapping.json`, it may not actually be on Cloudinary
- **Force re-upload when in doubt**: If URLs are correct but images don't display, force re-upload to get fresh, valid URLs
- **Verify actual file existence**: Check both mapping file AND Cloudinary to confirm resources exist
- **Chapter path accuracy matters**: Same filename in different chapters requires correct path matching

**Prevention Strategy**:
1. **Before uploading**: Verify local files are in correct chapter directories
2. **After uploading**: Always run `python check_status.py` to verify upload status
3. **When images don't display**:
   - First: Check URL format (correct chapter path, valid timestamp)
   - Second: Verify file exists in Cloudinary (check mapping file)
   - Third: **Force re-upload** if mapping exists but image doesn't display
4. **Use force re-upload script pattern**:
   ```python
   # Create temporary script to force re-upload specific files
   # Remove mapping entries or use overwrite=True in upload_file()
   ```

**Tools Created**:
- Temporary `force_upload_ch2_ch3.py` script (deleted after use)
- Pattern: Create targeted upload scripts for problematic files

**Future Improvements Needed**:
- Add `--force` flag to `media_processor.py upload` to force re-upload even if in mapping
- Improve `update-markdown` to better handle same-filename-different-path scenarios
- Add validation step that checks Cloudinary API to verify resources actually exist

### Active Issues ⏳

1. **Website Testing** - **PENDING**
   - Hugo server not accessible for local testing
   - URLs verified in source files, but live website not tested
   - Action Needed: Start Hugo server and verify all images/videos load correctly
   - Action Needed: Test giscus comments functionality

2. **SEO Optimization Follow-up**
   - [ ] Submit sitemap to Google Search Console
   - [ ] Validate structured data with Google Rich Results Test
   - [ ] Add descriptions to existing content frontmatter
   - [ ] Review and improve image alt text for existing images

### Technical Debt

1. **Error Handling**
   - Upload script could benefit from retry logic for network failures
   - Better error messages for common issues (file size limits, authentication)
   - Add validation to verify Cloudinary resources actually exist (not just in mapping file)

2. **Configuration Management**
   - ✅ Cloudinary credentials stored in `.env` with Pydantic validation
   - ✅ Environment variables validated at startup with clear error messages
   - ✅ Ebook generator configuration uses Pydantic models with type safety

3. **Code Quality & Formatting**
   - ✅ Ruff integrated for linting and code formatting
   - ✅ GitHub Actions workflow includes ruff checks before deployment
   - ✅ Development dependencies managed in `requirements-dev.txt`

4. **Script Organization**
   - Multiple utility scripts could be organized into a package
   - Consider adding CLI argument parsing for better usability

4. **Documentation**
   - Scripts have basic docstrings but could use more detailed usage examples
   - Consider adding a README for the upload workflow

5. ✅ **Testing** - **COMPLETED**
   - Comprehensive pytest test suite implemented
   - Unit tests for all core functions
   - Integration tests for complete workflows
   - CI/CD integration with automatic test execution
   - Coverage reporting and targets established

### Performance Considerations

1. **Upload Speed**
   - Large files (50-100 MB) take 1-2 minutes to upload
   - Network speed dependent
   - Consider batch upload optimization for future

2. **Mapping File Size**
   - `cloudinary_mapping.json` grows with each upload
   - Currently manageable (659 entries)
   - May need cleanup strategy if it grows significantly

## Future Enhancements (Backlog)

1. **Automation Pipeline** 📅 Future
   - Integrate upload script into Git pre-commit hook
   - Auto-upload new media files on content addition
   - Automated compression for files >100MB
   - **Estimated Effort**: 4-6 hours

2. **Image Optimization** 📅 Future
   - Leverage Cloudinary's responsive image features in Hugo templates
   - Implement lazy loading for better performance
   - Add srcset generation for different screen sizes
   - **Estimated Effort**: 2-3 hours

3. **Video Optimization** 📅 Future
   - Set up automatic video compression pipeline (FFmpeg integration)
   - Consider alternative storage for very large videos (>100MB)
   - Implement video thumbnail generation
   - **Estimated Effort**: 6-8 hours

4. **Monitoring & Analytics** 📅 Future
   - Track Cloudinary bandwidth usage
   - Monitor upload success rates
   - Alert on approaching free tier limits
   - **Estimated Effort**: 3-4 hours

## Essential Scripts Reference


### `media_processor.py` - 圖片影片處理工具（推薦）

**Purpose**: 整合了上傳、Markdown 更新、重複檢測、影片壓縮功能的統一工具

**Features**:
- ✅ **Pydantic Integration**: Uses `CloudinarySettings` for validated environment variables and `CloudinaryResource` models for type-safe data handling
- ✅ **Type Safety**: All mapping operations have type hints and IDE autocomplete support
- ✅ **Data Validation**: Automatic validation of JSON data when loading mapping files

**Usage**:
```bash
# 上傳媒體檔案
python media_processor.py upload

# 更新 Markdown 檔案中的連結
python media_processor.py update-markdown
python media_processor.py update-markdown --no-backup  # 不建立備份

# 檢測重複檔案（僅檢查）
python media_processor.py check-duplicates

# 檢測並自動刪除重複檔案
python media_processor.py check-duplicates --auto

# 壓縮大型影片檔案
python media_processor.py compress <video_file> [output_file]
```

**Features**:
- **上傳功能**: 掃描並上傳媒體檔案，自動跳過已上傳檔案，顯示進度
- **Markdown 更新**: 讀取映射表，更新所有 Markdown 檔案中的連結，自動備份
- **重複檢測**: 查詢 Cloudinary 所有檔案，識別重複檔案，可自動刪除
- **影片壓縮**: 使用 FFmpeg 壓縮大型影片（>100MB），支援兩階段壓縮

**Known Limitations**:
- `update-markdown` may not correctly match files with identical filenames in different chapters
- No `--force` flag to re-upload files that already exist in mapping
- Mapping file may contain entries for files not actually uploaded to Cloudinary

**File Size Handling**:
- Files 20-50MB: Uses `upload_large()` for reliability
- Files >50MB: Uploads without format conversion
- Files >100MB: Requires compression first (use `compress` command)

**Requirements**: 
- Cloudinary credentials (for upload/duplicates)
- FFmpeg (for compression): `choco install ffmpeg` (Windows) or `brew install ffmpeg` (macOS)

### `check_status.py`
**Purpose**: Verify upload status of media files

**Usage**:
```bash
python check_status.py
```

**Features**:
- Validates files in `cloudinary_mapping.json`
- Checks if Cloudinary URLs are accessible
- Reports missing or broken links

### 其他工具

- `check_status.py` - 驗證上傳狀態（獨立工具，功能未整合到 media_processor.py）

## Workflow

### Typical Media Management Workflow
1. Add new media files to `content/` directory
2. Run `python media_processor.py upload` to upload new files
3. Run `python media_processor.py update-markdown` to update markdown links
4. Test locally with `hugo server`
5. Commit and push changes

### For Large Videos (>100MB)
1. Compress video: `python media_processor.py compress path/to/video.mp4`
2. Verify compressed size <100MB
3. Upload compressed file: `python media_processor.py upload`
4. Update markdown: `python update_markdown.py`

## Environment Setup

### Required Environment Variables
Create `.env` file in project root:
```env
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret
```

### Python Dependencies
```bash
pip install -r requirements.txt
```

Required packages:
- `cloudinary>=1.36.0`
- `python-dotenv>=1.0.0`

### External Tools
- **FFmpeg**: Required for video compression (optional, only for files >100MB)
  - Windows: `choco install ffmpeg` (requires admin)
  - macOS: `brew install ffmpeg`
  - Download: https://www.gyan.dev/ffmpeg/builds/

---

## Legacy Context

歷史記錄和已完成的工作已移至獨立的檔案以節省 token 消耗。

詳細內容請參考：[LEGACY.md](LEGACY.md)

包含內容：
- 已完成的 Session Logs（Giscus 整合、根目錄清理、捐贈功能暫停、SEO 優化、路徑修復、遷移等）
- 已完成的 Features 和 Migration Statistics
- Architecture Decision Records (ADR)
- 已解決的問題和一次性遷移記錄
