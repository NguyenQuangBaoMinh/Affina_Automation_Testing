"""
Test Result Reporter with Screenshot Embedding
"""
from app.automation.result_reporter import ResultReporter
from app.config import Config
import os

print("\n" + "="*70)
print("🧪 Testing Result Reporter (Embed Screenshot)")
print("="*70)

Config.init_app()

# Initialize
reporter = ResultReporter()

# Find a screenshot
screenshot_files = [f for f in os.listdir('screenshots/failures') if f.endswith('.png')]

if not screenshot_files:
    print("❌ No screenshots found!")
    print("Please run a failing test first to generate a screenshot")
    exit(1)

screenshot_path = f"screenshots/failures/{screenshot_files[0]}"
print(f"Using screenshot: {screenshot_path}")

# Mock test case with FAIL + screenshot
test_case = {
    'test_id': 'TC002',
    'row_number': 5,  # Row 5 in sheet (TC002)
    'description': 'Test với screenshot'
}

result = {
    'status': 'FAIL',
    'error_message': 'Test timeout after 30 seconds',
    'screenshot_path': screenshot_path,
    'execution_time': 32.5
}

worksheet_name = "BRD_LUONG_KY_HOP_ONG_-_QUAN_LY_HOP_ONG_VER_2_0_20251024_220811"

# Report result
print("\n📝 Reporting FAIL result with screenshot...")
success = reporter.report_result(worksheet_name, test_case, result)

if success:
    print("\n✅ SUCCESS!")
    print("\n📋 Check Google Sheet:")
    print(f"  Row 5 (TC002): Should show FAIL with error and screenshot reference")
else:
    print("\n❌ FAILED!")

print("\n" + "="*70)
