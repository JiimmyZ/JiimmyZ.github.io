# Project Context

## Session Log

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

## Cumulative Decision Log (ADR - Architecture Decision Records)

### 2026-02-01: ADR-006 - URL Normalization in Upload Script

**Context**:
After initial migration, discovered all 634 Cloudinary URLs contained duplicated path segments (e.g., `/myblog/path/myblog/path/file.jpg`), causing 404 errors. Root cause: `upload_to_cloudinary.py` was setting both `folder` parameter and `public_id` with full path, causing Cloudinary to duplicate paths.

**Decision**:
Integrate URL normalization directly into `upload_to_cloudinary.py` instead of using separate fix scripts.

**Alternatives Considered**:
1. **Separate Fix Scripts**: Quick fix but adds technical debt
2. **Fix in Upload Script**: Chosen - prevents issues at source, cleaner codebase
3. **Post-Processing Script**: More complex, requires running after every upload

**Consequences**:
- ✅ **Pros**:
  - Prevents URL issues at source
  - Automatic normalization for all future uploads
  - Cleaner codebase (no temporary fix scripts)
  - Self-healing: `save_mapping()` normalizes existing URLs
- ⚠️ **Trade-offs**:
  - Slight performance overhead (minimal, URL processing is fast)
  - More complex upload function (acceptable for correctness)

**Implementation**:
- Added `normalize_url()` function to `upload_to_cloudinary.py`
- Removed conflicting upload parameters (`folder`, `use_filename`)
- Added normalization in `save_mapping()` to fix existing URLs

### 2026-01-31: ADR-001 - External CDN for Media Storage

**Context**: 
Repository contained 659 media files (646 images, 13 videos) totaling ~500MB+, causing:
- Git push operations taking 10+ minutes
- Repository size bloating to hundreds of MB
- Poor clone performance
- Git's inefficiency with binary files

**Decision**: 
Migrate all media files to Cloudinary CDN instead of Git LFS or keeping files in repository.

**Alternatives Considered**:
1. **Git LFS**: Would keep files in git but requires LFS server, limited free tier (1GB)
2. **External CDN (Cloudinary)**: Chosen - 25GB free storage, automatic optimization, CDN delivery
3. **Separate Media Repository**: More complex, submodule management overhead
4. **Optimize Before Commit**: Quick win but doesn't solve root problem

**Consequences**:
- ✅ **Pros**: 
  - Fast CDN delivery (global edge locations)
  - Automatic image optimization (WebP, quality adjustment)
  - Reduced repository size by ~500MB
  - Better scalability (no git performance degradation)
  - Free tier sufficient for current needs (25GB storage, 25GB bandwidth/month)
- ⚠️ **Trade-offs**:
  - External dependency (Cloudinary service availability)
  - File size limit: 100MB on free tier (requires compression for larger videos)
  - Additional setup complexity (API keys, environment variables)
  - Migration effort required (one-time)

**CAP/PACELC Considerations**:
- **Consistency**: Eventual (CDN propagation delay ~1-2 seconds)
- **Availability**: High (Cloudinary SLA 99.9%)
- **Partition Tolerance**: Handled by CDN edge locations
- **Latency**: Optimized (CDN edge caching)
- **Consistency**: Acceptable trade-off for static media (read-heavy workload)

### 2026-01-31: ADR-002 - Mapping File Strategy for Incremental Updates

**Context**:
Need to prevent duplicate uploads when re-running upload script. Required mechanism to track which files have already been uploaded to Cloudinary.

**Decision**:
Use JSON mapping file (`cloudinary_mapping.json`) with local relative path as key, storing Cloudinary URL and metadata.

**Alternatives Considered**:
1. **Database**: Overkill for simple key-value mapping
2. **Cloudinary API queries**: Slow, rate-limited, unnecessary API calls
3. **JSON file**: Chosen - Simple, version-controllable, fast local lookups

**Consequences**:
- ✅ **Pros**:
  - Fast lookups (O(1) dictionary access)
  - Version controllable (can track changes in git)
  - Human-readable format
  - Enables incremental updates (only upload new files)
- ⚠️ **Trade-offs**:
  - File grows with each upload (currently 659 entries, ~150KB)
  - Manual cleanup may be needed if file becomes too large
  - Requires file I/O operations (negligible performance impact)

### 2026-01-31: ADR-003 - Deduplication Before Upload

**Context**:
Initial uploads created duplicate entries in Cloudinary due to path construction issues. Need to identify and remove duplicates to prevent storage waste.

**Decision**:
Implement pre-upload duplicate detection script that queries Cloudinary API, identifies duplicates by filename, and removes redundant copies (keeping oldest).

**Consequences**:
- ✅ **Pros**:
  - Prevents storage waste
  - Cleaner Cloudinary dashboard
  - Reduces confusion
  - One-time cleanup operation
- ⚠️ **Trade-offs**:
  - Additional API calls (minimal impact)
  - Requires manual execution or integration into workflow

### 2026-01-31: ADR-004 - Large Video Handling Strategy

**Context**:
Videos >50MB failed to upload with error "Video is too large to process synchronously". Cloudinary free tier has 100MB file size limit.

**Decision**:
- Files 20-50MB: Use `upload_large()` method for reliability
- Files >50MB: Upload without format conversion to avoid sync processing
- Files >100MB: Require compression before upload (FFmpeg)

**Consequences**:
- ✅ **Pros**:
  - Handles edge cases gracefully
  - Avoids processing errors
  - Maintains file quality for smaller videos
- ⚠️ **Trade-offs**:
  - Files >100MB require external tool (FFmpeg)
  - Compression adds processing time
  - May require admin privileges for FFmpeg installation

### 2026-01-31: ADR-005 - Set-Based File Discovery for Windows Compatibility

**Context**:
Upload script was processing each file twice, causing duplicate upload warnings. Root cause: Windows file system case-insensitivity combined with searching both `.jpg` and `.JPG` extensions.

**Decision**:
Change `find_media_files()` to use Python `set()` instead of `list()` for automatic deduplication, ensuring each file path is processed exactly once.

**Consequences**:
- ✅ **Pros**:
  - Eliminates duplicate processing
  - Works correctly on Windows (case-insensitive) and Linux (case-sensitive)
  - Minimal code change (1 line)
- ⚠️ **Trade-offs**:
  - Slight memory overhead (negligible for 659 files)
  - Requires sorting before return (O(n log n) vs O(n))

### 2026-01-31: ADR-007 - Cloudinary URL Version Strategy

**Context**:
After fixing Cloudinary path duplication, discovered that URLs with specific version numbers (e.g., `v1769773744`) returned 404 errors, while URLs with `v1` worked correctly. Cloudinary API returns specific version numbers, but these don't work for direct HTTP access.

**Decision**:
Update all Cloudinary URLs in markdown files to use `v1` version instead of specific version numbers.

**Alternatives Considered**:
1. **Keep Specific Versions**: Would require fetching current version for each file from Cloudinary API - complex and slow
2. **Remove Version Numbers**: Cloudinary may require version numbers for some features
3. **Use v1**: Chosen - Simple, works reliably, Cloudinary automatically serves latest version with v1

**Consequences**:
- ✅ **Pros**:
  - Simple solution (regex replace)
  - Works reliably (v1 always accessible)
  - No API calls needed
  - Cloudinary serves latest version with v1
- ⚠️ **Trade-offs**:
  - Loses version-specific caching benefits (minimal impact for static media)
  - If file is updated in Cloudinary, v1 will serve new version (acceptable for read-only media)

**Implementation**:
- Updated 637 URLs across 6 markdown files to use `v1` version

### 2026-01-31: ADR-008 - Cloudinary Path Duplication Fix Strategy

**Context**:
Discovered that all Cloudinary files had duplicate path segments, causing 404 errors. Root cause was initial upload script creating incorrect paths.

**Decision**:
Use Cloudinary API `rename()` method to move all files from duplicate paths to correct paths, rather than re-uploading (local files no longer available).

**Alternatives Considered**:
1. **Re-upload Files**: Not possible - local files were removed to save space
2. **Delete and Re-upload**: Would lose files permanently
3. **Rename via API**: Chosen - Preserves files, corrects paths, no data loss

**Consequences**:
- ✅ **Pros**:
  - Preserves all existing files
  - No data loss
  - Fast operation (API rename is quick)
  - Maintains file metadata
- ⚠️ **Trade-offs**:
  - Requires Cloudinary API access
  - One-time operation (acceptable)

**Implementation**:
- Fixed 644 files total (ch6: 98, ch7: 255, ch8: 291) using `cloudinary.uploader.rename()` method

## Project Overview & Tech Stack

### Project Type
Hugo static site blog with extensive media content (travelogue with photos and videos)

### Technology Stack
- **Static Site Generator**: Hugo
- **Theme**: PaperMod
- **Media Storage**: Cloudinary (CDN)
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
├── upload_to_cloudinary.py    # Media upload automation
├── update_markdown.py         # Markdown link replacement
├── check_duplicates.py        # Cloudinary duplicate detection
├── check_status.py             # Upload status checker
└── cloudinary_mapping.json    # Local file → Cloudinary URL mapping
```

## Architectural Decisions

### Why Cloudinary?
**Problem**: Repository contained 659 media files (646 images + 13 videos) totaling hundreds of MB, causing:
- Extremely slow git push operations (minutes to hours)
- Large repository size
- Poor clone performance
- Git not optimized for binary files

**Solution**: Migrate all media to Cloudinary CDN
- **Benefits**:
  - Fast CDN delivery for better page load times
  - Automatic image optimization (WebP conversion, quality adjustment)
  - Reduced repository size (media files removed from git)
  - Better scalability
  - Free tier: 25GB storage, 25GB bandwidth/month

### Design Decisions

1. **Mapping File Strategy**
   - Created `cloudinary_mapping.json` to track local → Cloudinary URL mappings
   - Prevents duplicate uploads on script re-runs
   - Enables incremental updates

2. **Deduplication Before Upload**
   - Implemented `check_duplicates.py` to identify and remove duplicate files in Cloudinary
   - Prevents storage waste and confusion

3. **Progress Tracking**
   - Added counter display (`[1/659]`, `[2/659]`) for upload progress
   - Only processes files that need upload (skips already uploaded)

4. **Large Video Handling**
   - Files >20MB use `upload_large()` method for reliability
   - Files >50MB uploaded without format conversion to avoid sync processing errors
   - Files >100MB require compression (Cloudinary free tier limit)

5. **Backup Strategy**
   - Markdown files backed up with `.backup` extension before modification
   - Allows rollback if needed

## Current Progress

### Completed Features ✅

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
   - ✅ `analyze_upload_time.py` - Upload time estimation

4. **Optimizations**
   - ✅ Fixed duplicate file detection (Windows case-insensitivity issue)
   - ✅ Optimized upload flow (only process files needing upload)
   - ✅ Added progress counters for better UX
   - ✅ Handled large video files (>50MB) without format conversion

### Migration Statistics
- **Total files processed**: 660
- **Successfully uploaded**: 660 (646 images + 14 videos)
- **Markdown files updated**: 6
- **Total link replacements**: 634
- **Backup files created**: 30
- **Large videos compressed**: 1 (115.63 MB → 29.46 MB, 74.5% reduction)
- **URL fixes applied**: 1,294 (634 in markdown + 660 in mapping file)

## Updated Roadmap

### Immediate Next Steps (Priority Order)

1. ~~**Complete Large Video Migration**~~ ✅ **COMPLETED**
   - ~~**File**: `VID_20250703_100502.mp4` (115.6 MB)~~
   - **Status**: ✅ Compressed to 29.46 MB and uploaded successfully
   - **Action Items**:
     - [x] Install FFmpeg (admin PowerShell: `choco install ffmpeg -y`)
     - [x] Verify installation: `ffmpeg -version`
     - [x] Compress video: `python compress_video.py content/travelogue/camino/ch8/VID_20250703_100502.mp4`
     - [x] Verify compressed size <100 MB (29.46 MB)
     - [x] Upload compressed file: `python upload_to_cloudinary.py`
     - [x] Update markdown: `python update_markdown.py`
   - **Actual Time**: ~15 minutes (compression) + 2 minutes (upload)

2. **Testing & Verification** 🟡 Medium Priority
   - **Action Items**:
     - [ ] Start Hugo server: `hugo server`
     - [ ] Verify all 633 Cloudinary URLs load correctly
     - [ ] Test video playback functionality
     - [ ] Measure page load performance (before/after comparison)
     - [ ] Check browser console for 404 errors
     - [ ] Validate responsive image behavior
   - **Success Criteria**: All media displays, no broken links, improved load times

3. **Repository Cleanup** 🟢 Low Priority
   - **Action Items**:
     - [ ] Review `.backup` files (30 files)
     - [ ] Delete backup files after verification: `Get-ChildItem -Recurse -Filter *.backup | Remove-Item`
     - [ ] Optional: Remove local media files from `content/` (659 files, ~500MB)
     - [ ] Update `.gitignore` if removing local media
   - **Note**: Local files can be kept as backup or removed to reduce repo size

4. ~~**Git Commit & Deployment**~~ ✅ **COMPLETED**
   - **Status**: ✅ Successfully pushed to remote main branch
   - **Action Items**:
     - [x] Cleaned Git object database
     - [x] Removed large files from Git history
     - [x] Pushed to remote: `git push origin main --force`
     - [x] Verified remote branch updated
   - **Actual Time**: ~1 hour (including history cleanup)

### Future Enhancements (Backlog)

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

## Known Issues & Technical Debt

### Resolved Issues ✅

- ~~Image Rendering Template Issue~~ - Fixed template to handle Cloudinary absolute URLs
- ~~Cloudinary Path Duplication~~ - Fixed ch6/ch7/ch8 paths (644 files total)
- ~~Cloudinary URL Version Numbers~~ - Updated all URLs to use `v1` version
- ~~Large Video File Limit~~ - Compression pipeline operational
- ~~Duplicate Path Segments in URLs~~ - Enhanced upload script with automatic normalization
- ~~Git Push Failure~~ - Repository size reduced, push successful
- ~~FFmpeg Installation~~ - Installed and operational

### Current Issues

1. **Website Testing** ⏳ **PENDING**
   - Hugo server not accessible for local testing
   - URLs verified in source files, but live website not tested
   - Action Needed: Start Hugo server and verify all images/videos load correctly

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

## Environment Setup

### Required Environment Variables
```env
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret
```

### Python Dependencies
```
cloudinary>=1.36.0
python-dotenv>=1.0.0
```

### External Tools
- **FFmpeg**: Required for video compression (optional, only for files >100MB)
  - Installation: `choco install ffmpeg` (Windows, requires admin)
  - Or download from: https://www.gyan.dev/ffmpeg/builds/

## Workflow Summary

### Typical Workflow
1. Add new media files to `content/` directory
2. Run `python upload_to_cloudinary.py` to upload new files
3. Run `python update_markdown.py` to update markdown links
4. Test locally with `hugo server`
5. Commit and push changes

### One-Time Migration (Completed)
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

## Notes

- All media files are now served via Cloudinary CDN
- Original local files can be safely removed (optional, for repository size reduction)
- Backup files (`.backup`) can be deleted after verification
- Cloudinary free tier provides 25GB storage and 25GB bandwidth/month
- For files >100MB, consider compression or upgrading Cloudinary plan
- **Git History**: Large media files have been removed from Git history to reduce repository size
- **Repository Size**: Reduced from 4+ GiB to ~1 GiB (74% reduction)
- **Push Performance**: Future pushes will be significantly faster due to reduced repository size
- **Cloudinary URLs**: All URLs use `v1` version for reliable access (Cloudinary serves latest version)
- **Template Fix**: `render-image.html` now correctly handles absolute URLs by extracting extension from URL path component
- **Path Fix**: All Cloudinary files moved from duplicate paths to correct paths (644 files total: ch6: 98, ch7: 255, ch8: 291)