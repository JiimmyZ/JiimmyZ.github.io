"""
Check the actual URL format for a Cloudinary file after rename.
"""

import os
import cloudinary
import cloudinary.api
from dotenv import load_dotenv

load_dotenv()

cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
    secure=True
)

# Check one specific file
public_id = "myblog/travelogue/camino/ch8/IMG_20250703_074525"
try:
    result = cloudinary.api.resource(
        public_id,
        resource_type="image"
    )
    print(f"Public ID: {result.get('public_id')}")
    print(f"Version: {result.get('version')}")
    print(f"URL: {result.get('secure_url')}")
    print(f"Format: {result.get('format')}")
    
    # Also try to generate URL manually
    from cloudinary.utils import cloudinary_url
    url, options = cloudinary_url(public_id, resource_type="image", format="jpg")
    print(f"\nGenerated URL: {url}")
    
    # Test if URL is accessible
    import requests
    response = requests.head(url, timeout=10, allow_redirects=True)
    print(f"HTTP Status: {response.status_code}")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
