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
1. **Automated Testing** - No unit/integration tests exist
2. **Error Handling** - Basic error handling, needs structured logging and retry mechanisms
3. **CI/CD Testing** - GitHub Actions lacks test steps before deployment

**Medium Priority (Short-term)**:
4. **Dependency Locking** - Versions use `>=` ranges, need pinning
5. **Code Formatting** - No linting/formatting tools (ruff recommended)
6. **Documentation** - Missing developer docs (CONTRIBUTING.md, DEVELOPMENT.md)

**Low Priority (Long-term)**:
7. **Performance Monitoring** - No metrics for upload/processing times
8. **Security Scanning** - No dependency vulnerability scanning
9. **Build Validation** - No HTML validation or broken links checking

### Key Improvements Identified

- **Testing**: Add pytest for `media_processor.py` unit/integration tests
- **Linting**: Integrate ruff for code formatting and style checking
- **Error Handling**: Replace print statements with structured logging (logging module)
- **CI/CD**: Add test steps and build validation to GitHub Actions workflow
- **Dependencies**: Lock versions in requirements.txt, add requirements-dev.txt
- **Documentation**: Create CONTRIBUTING.md and DEVELOPMENT.md guides

**Full details**: See plan document for complete analysis and implementation recommendations.

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
- 已完成的 Session Logs（Giscus 整合、根目錄清理、捐贈功能暫停、SEO 優化、路徑修復、遷移等）
- 已完成的 Features 和 Migration Statistics
- Architecture Decision Records (ADR)
- 已解決的問題和一次性遷移記錄
