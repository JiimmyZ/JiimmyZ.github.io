# Legacy Context

歷史記錄和已完成的工作。

## Completed Session Logs

### Session Log 2026-07-25 - Remove external fonts (perf ADR)

**Summary**: Confirmed CDN web fonts were the main cause of slow first paint / jank. Removed all external font loading; site uses PaperMod system stack only.

**Timeline / findings**:
1. Site used Google Fonts (Literata) + jsDelivr `lxgw-wenkai-webfont@1.7.0/style.css`
2. Package `style.css` imported **6** families (regular/light/bold + mono variants); each regular alone has ~97 unicode-range `.woff2` subsets → large CSS parse + many font requests on CJK pages
3. Interim trim: load only `lxgwwenkai-regular.css` (helped somewhat)
4. User confirmed fonts were still the bottleneck → **remove all external fonts**

**Decision (ADR)**:
- **Do not** load Google Fonts, jsDelivr webfonts, or a local `fonts.css` override
- Rely on PaperMod `reset.css` system stack (`-apple-system`, `BlinkMacSystemFont`, `Segoe UI`, etc.)
- Prefer perceived speed over custom typography for this solo blog

**Files**:
- `layouts/partials/extend_head.html` — font `<link>` / preconnect removed
- `static/css/fonts.css` — deleted
- `README.md` / `context.md` — stack documented as system fonts

**Supersedes**: Session Log 2026-07-25 - Site font unification (LXGW WenKai + Literata) below (historical only; stack no longer in use).

**Status**: **COMPLETED** — reload felt much faster after removal.

### Session Log 2026-07-25 - README rewrite (solo + agent)

**Summary**: Rewrote `README.md` for single-maintainer + future AI agents (not contributor onboarding).

**Done**:
- Quick-start flows (text-only / with media / large video)
- Source-of-truth table (`hugo.toml` / `context.md` / `LEGACY.md` / `media_processor.py`)
- One media section; historical Cloudinary migration stats deferred to LEGACY
- Removed 貢獻／授權；deleted dead links to non-existent `GISCUS_SETUP.md` / `CLOUDINARY_SETUP.md` / `SEO_GUIDELINES.md`
- FAQ: `python media_processor.py update-markdown`; clone URL = `JiimmyZ/JiimmyZ.github.io`

**Status**: **COMPLETED**

### Session Log 2026-07-25 - Giscus theme & login options (no change)

**Summary**: Reviewed whether Giscus comment UI colors and login providers can be customized. Decided to leave the current setup unchanged.

**Theme / colors**:
- Giscus runs in a cross-origin iframe; site CSS cannot style the widget directly
- Colors are controlled via `params.comments.giscus.theme` in `hugo.toml` (currently `preferred_color_scheme`)
- Possible approaches (not applied): built-in themes (e.g. `transparent_dark`), custom CSS URL as `data-theme`, or `postMessage` sync with site light/dark toggle
- **Decision**: Do not change theme for now

**Login options**:
- Giscus only supports GitHub OAuth (comments are GitHub Discussions)
- Other providers (Google, etc.) are not available without replacing or dual-running another comment system (Disqus, Cusdis, self-hosted + Auth)
- Dual systems conflict with the site’s minimal design; keep Giscus-only
- **Decision**: Keep GitHub-only login

**Config reference** (`hugo.toml` → `[params.comments.giscus]`):
- `theme = "preferred_color_scheme"`
- Partial: `layouts/partials/comments.html` (`data-theme` from config)

**Status**: **NO CHANGE** — documented for future reference; Giscus remains sole comment system with GitHub login only.

### Session Log 2026-07-25 - Dim Buy JZ Coffee button

**Summary**: Softened the inline donation button from a solid primary fill to a quiet outline style so it blends with surrounding article content.

**CSS** (`layouts/partials/donation_section.html`):
- Text: `var(--secondary)`
- Background: transparent
- Border: `1px solid var(--border)`
- Hover: text → `var(--primary)`, border → `var(--tertiary)`
- Focus outline: `var(--secondary)`

**Status**: **COMPLETED**

### Session Log 2026-07-25 - Site font unification (LXGW WenKai + Literata)

**Summary**: Unified site-wide fonts to 霞鹜文楷 (LXGW WenKai) for CJK and Literata for Latin/numbers via CDN; code blocks use system monospace (Consolas stack).

**Why not `assets/css/extended`**: Hugo’s CSS minify strips quotes from multi-word `font-family` names (e.g. `"LXGW WenKai"` → broken). Font rules therefore live in `static/css/fonts.css` and are linked from `extend_head.html`.

**Stack**:
- Chinese / body: `"LXGW WenKai", "Literata", "Noto Serif TC", serif`
- Code: `ui-monospace, Consolas, "Cascadia Code", "Courier New", monospace`
- CDN: Google Fonts (Literata) + jsDelivr `lxgw-wenkai-webfont@1.7.0`

**Files**:
- `layouts/partials/extend_head.html` — preconnect + font stylesheets + local `css/fonts.css`
- `static/css/fonts.css` — `body` / code `font-family`
- `README.md` / `context.md` — documentation

**Known limitation**: Giscus comments/reactions run in a cross-origin iframe and do **not** inherit site fonts. Unifying Giscus requires a custom `data-theme` CSS URL (not done in this session).

**Status**: **SUPERSEDED** — external fonts removed the same day for performance (see “Remove external fonts” above). Kept here as history of why CDN CJK fonts were tried and why `static/css/fonts.css` existed.

### Session Log 2026-07-25 - Busuanzi visitor stats on About page

**Summary**: Added [不蒜子](https://www.busuanzi.cc/) for site-wide visit counting; UI only on the About page.

**Design**:
- Script loads site-wide (so all page views count toward `site_uv`)
- Visible stats only when `showSiteStats = true` (currently `content/about.md`)
- Displays: total unique visitors (`busuanzi_site_uv`) + operating days from `params.busuanzi.siteStartDate` (`2025-07-26`)
- No API key / registration required

**Files**:
- `hugo.toml` — `[params.busuanzi]` (`enabled`, `siteStartDate`)
- `layouts/partials/extend_footer.html` — Busuanzi script
- `layouts/partials/about_stats.html` — About-page UI
- `layouts/_default/single.html` — render `about_stats`
- `content/about.md` — `showSiteStats = true`
- `README.md` / `context.md` — documentation

**Known limitation**: On localhost, Busuanzi may show「域名/IP已被禁用」; production domain should work after deploy.

**Status**: **COMPLETED**

### Session Log 2026-02-01 (Evening) - Pydantic Integration Implementation

**Summary**: Implemented comprehensive Pydantic integration across Python scripts to improve type safety, data validation, and configuration management. Completed Phase 1 (Foundation Setup), Phase 2 (Ebook Generator Configuration), and Phase 3 (Cloudinary Data Models).

**Phase 1: Foundation Setup**
- Added Pydantic dependencies (`pydantic>=2.0.0`, `pydantic-settings>=2.0.0`)
- Created `CloudinarySettings` class for environment variable validation
- Scripts now fail fast with clear error messages for missing configuration
- Removed redundant credential checks

**Phase 2: Ebook Generator Configuration**
- Rewrote `ebook-generator/config.py` using Pydantic models
- Created `EbookConfig` and `EpubMetadata` models
- Added type hints and validation for all configuration values
- Maintained backward compatibility with old constant names
- *(2026-07-25: `ebook-generator/` moved out of this repo.)*

**Phase 3: Cloudinary Data Models**
- Created `CloudinaryResource` model with validated fields
- Updated all mapping functions to use Pydantic models
- Updated upload functions to return `CloudinaryResource` instances
- Maintained backward compatibility with existing JSON format

**Files Modified**:
- `requirements.txt` - Added Pydantic dependencies
- `media_processor.py` - Added models and updated all functions
- `ebook-generator/config.py` - Complete rewrite using Pydantic

> **Note (2026-07-25)**: `ebook-generator/` was moved out of this repo; see that separate project for the config rewrite.

**Status**: **COMPLETED** - All high and medium priority phases implemented.

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

**Status**: **COMPLETED** - Giscus comments system successfully integrated and configured.

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

**Status**: **COMPLETED**

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

**Status**: **COMPLETED**

### Session Log 2026-01-31 (Evening) - Donation Feature Implementation & Suspension

**Summary**: Implemented donation feature (QR Code transfer) following the plan document, then suspended development by commenting out all related code.

**Features Implemented**:
- Created `layouts/partials/donation.html` - Donation partial template with HTML, CSS, and JavaScript
- Modified `layouts/_default/single.html` - Added donation section between footer and comments
- Updated `hugo.toml` - Added donation configuration parameters
- Created `static/donation/` directory for QR Code images
- Added `static/donation/README.md` - Instructions for QR Code image preparation

**Configuration**:
- Donation section displayed at article bottom (between share buttons and comments)
- Four fixed amount buttons: 50, 100, 200, 500 NTD
- Support for multiple payment methods (bank transfer, Line Pay, JKO Pay)
- Responsive design for mobile and desktop
- Dark/light theme auto-adaptation

**Status**: **SUSPENDED** - All donation-related code has been commented out
- `hugo.toml`: Donation configuration section commented out
- `layouts/_default/single.html`: Donation partial reference commented out
- `layouts/partials/donation.html`: File retained but not called

**Files Created**:
- `layouts/partials/donation.html` - Donation partial template (359 lines)
- `static/donation/README.md` - QR Code image preparation guide
- `static/donation/Receive.jpg` - User-provided QR Code image

**Files Modified**:
- `hugo.toml` - Added (then commented out) donation configuration
- `layouts/_default/single.html` - Added (then commented out) donation section

**To Re-enable**:
1. Uncomment `[params.donation]` section in `hugo.toml`
2. Uncomment donation partial reference in `layouts/_default/single.html`

**Note**: Feature was tested but QR Code display functionality had issues. Development suspended for future refinement.

### Session Log 2026-02-01 (Evening) - Comprehensive SEO Optimization Implementation

**Summary**: Implemented comprehensive SEO optimization across all phases including enhanced meta tags, structured data, image optimization, technical SEO enhancements, content guidelines, and performance verification.

**Files Created**:
- `layouts/partials/seo_meta.html` - Enhanced SEO meta tags partial
- `layouts/partials/schema_article.html` - Enhanced Article schema for structured data
- `SEO_GUIDELINES.md` - Comprehensive SEO best practices documentation

**Files Modified**:
- `hugo.toml` - Added SEO params and sitemap configuration
- `layouts/partials/extend_head.html` - Integrated SEO meta and schema partials
- `layouts/_default/_markup/render-image.html` - Enhanced alt text handling
- `static/robots.txt` - Added draft/backup file exclusions
- `README.md` - Added SEO optimization section and guidelines reference

### Session Log 2026-02-01 (Evening) - Fix Ch6 Cloudinary Path Duplication

**Summary**: Fixed duplicate path segments in ch6 Cloudinary files (same issue as ch7/ch8). Renamed 98 files (96 images + 2 videos) to correct paths using Cloudinary API.

### Session Log 2026-01-31 (Late Evening) - Fix Ch7 Cloudinary Path Duplication

**Summary**: Fixed duplicate path segments in ch7 Cloudinary files (same issue as ch8). Renamed 255 files (250 images + 5 videos) to correct paths using Cloudinary API.

### Session Log 2026-01-31 (Evening) - Fix Image Rendering & Cloudinary Path Issues

**Summary**: 
- Fixed template `render-image.html` to handle Cloudinary absolute URLs correctly
- Fixed ch8 Cloudinary path duplication (renamed 291 files)
- Updated all URLs to use `v1` version (637 URLs across 6 markdown files)

### Session Log 2026-01-31 (Evening) - Git Repository Cleanup & Push Success

**Summary**: Cleaned Git object database and removed large media files from history. Repository size reduced from 4+ GiB to ~1 GiB (74% reduction). Successfully pushed to remote.

### Session Log 2026-02-01 (Afternoon) - URL Normalization Fix

**Summary**: Fixed duplicate path segments in all Cloudinary URLs (1,294 URLs fixed). Enhanced `upload_to_cloudinary.py` with automatic URL normalization to prevent future issues.

### Session Log 2026-02-01 (Morning) - Large Video Compression

**Summary**: Compressed large video file (115.63 MB → 29.46 MB) and uploaded to Cloudinary. Enhanced compression script with aggressive settings.

### Session Log 2026-01-31 - Initial Cloudinary Migration

**Summary**: Migrated 659 media files to Cloudinary CDN. Created automation scripts for upload and markdown link replacement. Fixed encoding issues and Windows compatibility problems. All files uploaded and markdown files updated with Cloudinary URLs.

## Completed Features ✅

1. **Cloudinary Integration Setup**
   - ✅ Created upload script with progress tracking
   - ✅ Created markdown update script
   - ✅ Created duplicate detection and removal script
   - ✅ Created status checking utilities
   - ✅ Environment variable configuration (`.env`)

2. **Media Migration**
   - ✅ **659 files uploaded** (646 images + 13 videos)
   - ✅ All files successfully migrated to Cloudinary
   - ✅ **6 markdown files updated** with Cloudinary URLs
   - ✅ **633 image/video links replaced** with CDN URLs
   - ✅ **3 duplicate files removed** from Cloudinary

3. **Scripts Created**
   - ✅ `upload_to_cloudinary.py` - Automated media upload with deduplication
   - ✅ `update_markdown.py` - Batch markdown link replacement
   - ✅ `check_duplicates.py` - Cloudinary duplicate detection and cleanup
   - ✅ `check_status.py` - Upload status verification
   - ✅ `compress_video.py` - Video compression utility (for files >100MB)

4. **Optimizations**
   - ✅ Fixed duplicate file detection (Windows case-insensitivity issue)
   - ✅ Optimized upload flow (only process files needing upload)
   - ✅ Added progress counters for better UX
   - ✅ Handled large video files (>50MB) without format conversion

## Migration Statistics
- **Total files processed**: 660
- **Successfully uploaded**: 660 (646 images + 14 videos)
- **Markdown files updated**: 6
- **Total link replacements**: 634
- **Large videos compressed**: 1 (115.63 MB → 29.46 MB, 74.5% reduction)
- **URL fixes applied**: 1,294 (634 in markdown + 660 in mapping file)

## Architecture Decision Records (ADR)

### ADR-001 - External CDN for Media Storage
**Decision**: Migrate all media files to Cloudinary CDN instead of Git LFS or keeping files in repository.

**Rationale**: Repository contained 659 media files totaling ~500MB+, causing slow git operations. Cloudinary provides 25GB free storage, automatic optimization, and CDN delivery.

### ADR-002 - Mapping File Strategy for Incremental Updates
**Decision**: Use JSON mapping file (`cloudinary_mapping.json`) with local relative path as key, storing Cloudinary URL and metadata.

**Rationale**: Simple, version-controllable, fast local lookups (O(1) dictionary access), enables incremental updates.

### ADR-003 - Deduplication Before Upload
**Decision**: Implement pre-upload duplicate detection script that queries Cloudinary API, identifies duplicates by filename, and removes redundant copies (keeping oldest).

### ADR-004 - Large Video Handling Strategy
**Decision**: 
- Files 20-50MB: Use `upload_large()` method for reliability
- Files >50MB: Upload without format conversion to avoid sync processing
- Files >100MB: Require compression before upload (FFmpeg)

### ADR-005 - Set-Based File Discovery for Windows Compatibility
**Decision**: Change `find_media_files()` to use Python `set()` instead of `list()` for automatic deduplication, ensuring each file path is processed exactly once.

### ADR-006 - URL Normalization in Upload Script
**Decision**: Integrate URL normalization directly into `upload_to_cloudinary.py` instead of using separate fix scripts.

**Rationale**: Prevents URL issues at source, automatic normalization for all future uploads, cleaner codebase.

### ADR-007 - Cloudinary URL Version Strategy
**Decision**: Update all Cloudinary URLs in markdown files to use `v1` version instead of specific version numbers.

**Rationale**: Simple solution, works reliably, Cloudinary serves latest version with v1.

### ADR-008 - Cloudinary Path Duplication Fix Strategy
**Decision**: Use Cloudinary API `rename()` method to move all files from duplicate paths to correct paths, rather than re-uploading.

**Rationale**: Preserves all existing files, no data loss, fast operation.

### ADR-009 - Comprehensive SEO Optimization Strategy
**Decision**: Implement comprehensive SEO optimization across six phases: enhanced meta tags, structured data, image SEO, technical SEO, content guidelines, and performance verification.

**Rationale**: Full control, no dependencies, integrates with existing theme, comprehensive documentation for content creators.

## Resolved Issues ✅

- ~~Image Rendering Template Issue~~ - Fixed template to handle Cloudinary absolute URLs
- ~~Cloudinary Path Duplication~~ - Fixed ch6/ch7/ch8 paths (644 files total)
- ~~Cloudinary URL Version Numbers~~ - Updated all URLs to use `v1` version
- ~~Large Video File Limit~~ - Compression pipeline operational
- ~~Duplicate Path Segments in URLs~~ - Enhanced upload script with automatic normalization
- ~~Git Push Failure~~ - Repository size reduced, push successful
- ~~FFmpeg Installation~~ - Installed and operational
- ~~Repository Cleanup~~ - Removed temporary scripts and backup files

## One-Time Migration (Completed)
1. ✅ Checked for duplicates in Cloudinary
2. ✅ Removed 3 duplicate files
3. ✅ Uploaded all 660 media files (646 images + 14 videos)
4. ✅ Updated 6 markdown files with Cloudinary URLs
5. ✅ Handled large video file (>100MB) - compressed and uploaded
6. ✅ Fixed duplicate path segments in all URLs (1,294 URLs corrected)
7. ✅ Improved upload script to prevent future URL issues
8. ✅ Cleaned Git object database (reduced from 4.06 GiB to 1.05 GiB)
9. ✅ Removed large media files from Git history (84% reduction in blob size)
10. ✅ Successfully pushed all changes to remote main branch
11. ✅ Cleaned root directory (removed temporary files, backups, and scripts - freed ~3.16 GB)
