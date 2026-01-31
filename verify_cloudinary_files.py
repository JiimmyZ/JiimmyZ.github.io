"""
Verify that files exist in Cloudinary by checking a few sample URLs.
"""

import json
import os
import requests
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Load mapping
if os.path.exists("cloudinary_mapping.json"):
    with open("cloudinary_mapping.json", "r", encoding="utf-8") as f:
        mapping = json.load(f)
    
    print(f"Total files in mapping: {len(mapping)}")
    
    # Check a sample of files from ch8
    ch8_files = {k: v for k, v in mapping.items() if "ch8" in k}
    print(f"\nFiles in ch8: {len(ch8_files)}")
    
    # Check first 5 files
    print("\nChecking first 5 ch8 files...")
    checked = 0
    failed = 0
    
    for key, value in list(ch8_files.items())[:5]:
        if isinstance(value, dict) and "url" in value:
            url = value["url"]
            try:
                response = requests.head(url, timeout=10, allow_redirects=True)
                status = "OK" if response.status_code == 200 else f"FAIL ({response.status_code})"
                print(f"  {status} {Path(key).name}")
                if response.status_code != 200:
                    failed += 1
                checked += 1
            except Exception as e:
                print(f"  ERROR: {Path(key).name} - {str(e)}")
                failed += 1
                checked += 1
    
    print(f"\nChecked: {checked}, Failed: {failed}")
    
    if failed > 0:
        print("\nWARNING: Some files are missing from Cloudinary!")
        print("   You may need to re-upload the files.")
    else:
        print("\nOK: All checked files exist in Cloudinary")
else:
    print("No mapping file found!")
