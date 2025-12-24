"""
Test Google Sheets connection
"""
from app.services.gsheet_service import GoogleSheetService
from app.config import Config

print("\n" + "="*70)
print("🧪 Testing Google Sheets Connection")
print("="*70)

# Initialize config
Config.init_app()

# Create service
print("\nInitializing Google Sheets service...")
gsheet = GoogleSheetService(
    credentials_file=Config.GOOGLE_CREDENTIALS_FILE,
    sheet_name=Config.GOOGLE_SHEET_NAME
)

# Get spreadsheet
print(f"\nOpening spreadsheet: {Config.GOOGLE_SHEET_NAME}")
success, error = gsheet._get_or_create_spreadsheet()

if not success:
    print(f"❌ Error: {error}")
    exit(1)

print("✓ Spreadsheet opened successfully!")

# List worksheets
print("\n" + "="*70)
print("📋 Available Worksheets:")
print("="*70)

worksheets = gsheet.spreadsheet.worksheets()

for i, ws in enumerate(worksheets, 1):
    print(f"{i}. {ws.title}")
    print(f"   Rows: {ws.row_count}")
    print(f"   Cols: {ws.col_count}")
    print(f"   URL: {ws.url}")
    print()

print("="*70)
print(f"✅ Found {len(worksheets)} worksheets")
print("="*70)