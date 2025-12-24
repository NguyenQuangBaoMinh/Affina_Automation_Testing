"""
Test Google Drive upload
"""
from app.services.drive_service import GoogleDriveService
from app.config import Config

print("\n" + "="*70)
print("🧪 Testing Google Drive Upload")
print("="*70)

Config.init_app()

# Initialize
drive = GoogleDriveService()

# Create folder
folder_id = drive.get_or_create_folder("BRD_Test_Screenshots")

# Upload test screenshot (nếu có)
import os
screenshot_files = [f for f in os.listdir('screenshots/failures') if f.endswith('.png')]

if screenshot_files:
    test_file = f"screenshots/failures/{screenshot_files[0]}"
    print(f"\nUploading: {test_file}")
    
    file_id, image_url = drive.upload_file(test_file)
    
    if image_url:
        print(f"\n✅ Upload successful!")
        print(f"Image URL: {image_url}")
        print(f"\nUse in Sheet: =IMAGE(\"{image_url}\")")
    else:
        print("❌ Upload failed")
else:
    print("⚠️  No screenshots found in screenshots/failures/")

print("\n" + "="*70)
