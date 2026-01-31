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

### Session Log 2026-02-01 (Evening) - Final Root Directory Cleanup & Legacy Separation

**Summary**: Final cleanup of root directory by removing legacy scripts that have been fully integrated into `media_processor.py`. Separated Legacy Context into independent `LEGACY.md` file to reduce token consumption.

**Files Deleted**:
- **Legacy Scripts** (4 files):
  - `upload_to_cloudinary.py` - Integrated into `media_processor.py upload`
  - `update_markdown.py` - Integrated into `media_processor.py update-markdown`
  - `check_duplicates.py` - Integrated into `media_processor.py check-duplicates`
  - `compress_video.py` - Integrated into `media_processor.py compress`
- **Python Cache**: `__pycache__/` directory

**Files Created**:
- `LEGACY.md` - Separated legacy context to reduce token consumption (~46% savings)

**Files Retained**:
- `media_processor.py` - Unified media processing tool (all-in-one)
- `check_status.py` - Status verification (functionality not integrated)

**Documentation Updates**:
- Updated `context.md` - Removed legacy script references, added LEGACY.md link
- Updated `README.md` - Removed all legacy script usage examples, simplified to use `media_processor.py` only

**Impact**:
- Cleaner root directory (only 2 Python scripts remaining)
- Reduced token consumption (~46% when reading context.md)
- Simplified workflow (single unified tool)
- Better maintainability (one source of truth)

### Session Log 2026-02-01 (Evening) - Root Directory Cleanup

**Summary**: Cleaned up root directory by removing temporary scripts and backup files that are no longer needed after Cloudinary migration completion.

**Files Deleted**:
- **Temporary Check/Fix Scripts** (10 files): All one-time fix scripts for Cloudinary migration issues
- **Backup Files** (60+ files): All `.backup` files in `content/` and `public/` directories
- **Python Cache**: `__pycache__/` directory

**Files Retained** (Essential Scripts):
- `upload_to_cloudinary.py` - Main upload script
- `update_markdown.py` - Markdown link replacement
- `check_duplicates.py` - Duplicate detection
- `check_status.py` - Status verification
- `compress_video.py` - Video compression utility

### Session Log 2026-02-01 (Evening) - Giscus Comments System Integration

**Summary**: Integrated giscus comments system into Hugo blog. Configured GitHub Discussions-based commenting with full setup documentation.

**Configuration Values**:
- `repo`: `JiimmyZ/JiimmyZ.github.io`
- `repoId`: `R_kgDOPTd04Q`
- `categoryId`: `DIC_kwDOPTd04c4C0EQR`
- `mapping`: `pathname` (uses URL pathname to match discussions)
- `inputPosition`: `top` (comment box at top)
- `theme`: `preferred_color_scheme` (auto-follows system theme)
- `lang`: `zh-TW` (Traditional Chinese)

**Next Steps**:
- [ ] Test giscus functionality on live site
- [ ] Verify comments appear correctly on article pages
- [ ] Test GitHub OAuth flow for visitor comments
- [ ] Monitor GitHub Discussions for comment management

## Current Issues & Improvements Needed

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

2. **Configuration Management**
   - Cloudinary credentials stored in `.env` (good)
   - Consider adding validation for required environment variables

3. **Script Organization**
   - Multiple utility scripts could be organized into a package
   - Consider adding CLI argument parsing for better usability

4. **Documentation**
   - Scripts have basic docstrings but could use more detailed usage examples
   - Consider adding a README for the upload workflow

5. **Testing**
   - No automated tests for upload/update scripts
   - Manual testing only

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
- 已完成的 Session Logs（SEO 優化、路徑修復、遷移等）
- 已完成的 Features 和 Migration Statistics
- Architecture Decision Records (ADR)
- 已解決的問題和一次性遷移記錄
