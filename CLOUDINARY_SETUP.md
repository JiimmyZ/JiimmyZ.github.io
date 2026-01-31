# Cloudinary Setup Guide

This guide will help you set up Cloudinary for your Hugo blog to host images and videos externally.

## Step 1: Create Cloudinary Account

1. Go to [https://cloudinary.com/users/register/free](https://cloudinary.com/users/register/free)
2. Sign up for a free account (no credit card required)
3. Free tier includes:
   - 25GB storage
   - 25GB bandwidth/month
   - Image and video transformations
   - Automatic optimization

## Step 2: Get Your Cloudinary Credentials

1. After signing up, you'll be taken to your dashboard
2. On the dashboard, you'll see your credentials:
   - **Cloud Name** (e.g., `dxyz123abc`)
   - **API Key** (e.g., `123456789012345`)
   - **API Secret** (e.g., `abcdefghijklmnopqrstuvwxyz123456`)

## Step 3: Install Python Dependencies

```bash
pip install -r requirements.txt
```

Or if you prefer using a virtual environment:

```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

pip install -r requirements.txt
```

## Step 4: Configure Cloudinary Credentials

Create a `.env` file in the project root (same directory as `upload_to_cloudinary.py`):

```env
CLOUDINARY_CLOUD_NAME=your_cloud_name_here
CLOUDINARY_API_KEY=your_api_key_here
CLOUDINARY_API_SECRET=your_api_secret_here
```

**Important:** Add `.env` to your `.gitignore` to keep credentials private!

## Step 5: Upload Media Files

Run the upload script:

```bash
python upload_to_cloudinary.py
```

This will:
- Scan all media files in the `content/` directory
- Upload them to Cloudinary
- Create a `cloudinary_mapping.json` file with local paths → Cloudinary URLs
- Skip files that are already uploaded (based on the mapping file)

**Note:** The first upload may take a while depending on:
- Number of files
- File sizes
- Your internet connection speed

## Step 6: Update Markdown Files

After uploading, update your markdown files to use Cloudinary URLs:

```bash
python update_markdown.py
```

This will:
- Replace local image/video references with Cloudinary URLs
- Create `.backup` files of your original markdown files
- Show you how many replacements were made

## Step 7: Review and Commit

1. Review the changes in your markdown files
2. Test your Hugo site locally: `hugo server`
3. If everything looks good, you can:
   - Delete the `.backup` files
   - Remove the original media files from `content/` (they're now on Cloudinary)
   - Commit the updated markdown files to git

## Optional: Remove Local Media Files

After confirming everything works, you can remove local media files to reduce repository size:

```bash
# Be careful! Make sure Cloudinary URLs work first!
# This will delete all images and videos from content directory
# You can restore from git if needed

# Windows PowerShell:
Get-ChildItem -Path content -Recurse -Include *.jpg,*.jpeg,*.png,*.mp4,*.webm | Remove-Item
```

## Troubleshooting

### "Cloudinary credentials not found"
- Make sure `.env` file exists in the project root
- Check that all three variables are set correctly
- Ensure `.env` file doesn't have extra spaces or quotes

### "Upload failed" or timeout errors
- Check your internet connection
- Large files may take time - the script will show progress
- You can re-run the script - it will skip already uploaded files

### Images not showing after update
- Check that `cloudinary_mapping.json` was created correctly
- Verify URLs in the mapping file work in a browser
- Make sure markdown files were updated (check for `.backup` files)

### Want to upload only specific files
- You can modify `find_media_files()` in `upload_to_cloudinary.py`
- Or manually edit `cloudinary_mapping.json` and run `update_markdown.py`

## Benefits

✅ **Faster git operations** - No more slow pushes with large media files  
✅ **Better performance** - CDN delivery for faster page loads  
✅ **Automatic optimization** - Cloudinary optimizes images automatically  
✅ **Responsive images** - Cloudinary can generate different sizes on demand  
✅ **Smaller repository** - Your git repo stays lean and fast  

## Next Steps

- Consider using Cloudinary's image transformations in your Hugo templates
- Set up automatic image optimization in your Hugo config
- Monitor your Cloudinary usage in the dashboard
