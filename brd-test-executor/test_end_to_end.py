"""
End-to-End Test
Complete flow: Read → Generate → Execute → Report
"""
from app.config import Config
from app.automation.code_generator import CodeGenerator
from app.automation.playwright_runner import PlaywrightRunner
from app.automation.result_reporter import ResultReporter

print("\n" + "="*70)
print("🚀 END-TO-END TEST - Complete Flow")
print("="*70)

# Initialize
Config.init_app()

# Step 1: Read test cases (sử dụng code từ test_code_generator.py)
print("\n📖 STEP 1: Reading test cases from Google Sheet...")

# Import và đọc test cases
import sys
sys.path.append('.')

# Read từ test_code_generator logic
from app.services.gsheet_service import GoogleSheetService

gsheet = GoogleSheetService(
    credentials_file=Config.GOOGLE_CREDENTIALS_FILE,
    sheet_name=Config.GOOGLE_SHEET_NAME
)

worksheet_name = "BRD_LUONG_KY_HOP_ONG_-_QUAN_LY_HOP_ONG_VER_2_0_20251024_220811"

# Connect và read
success, error = gsheet._get_or_create_spreadsheet()
if not success:
    print(f"❌ Failed to connect: {error}")
    exit(1)

worksheet = gsheet.spreadsheet.worksheet(worksheet_name)

# Get headers
headers = worksheet.row_values(3)
print(f"✓ Headers: {headers}")

# Get all rows
all_rows = worksheet.get_all_values()[3:]  # Skip header rows

# Parse test cases
test_cases = []
for i, row in enumerate(all_rows, start=4):
    if len(row) >= 6 and row[0]:  # Has Test ID
        test_case = {
            'test_id': row[0],
            'description': row[1],
            'steps': row[2],
            'expected_result': row[3],
            'priority': row[4],
            'row_number': i
        }
        test_cases.append(test_case)

if not test_cases:
    print("❌ No test cases found!")
    exit(1)

print(f"✓ Found {len(test_cases)} test cases")

# Select TC001
tc001 = next((tc for tc in test_cases if tc['test_id'] == 'TC001'), None)

if not tc001:
    print("❌ TC001 not found!")
    exit(1)

print(f"\n🎯 Selected: {tc001['test_id']}")
print(f"   Description: {tc001['description'][:60]}...")
print(f"   Row number: {tc001['row_number']}")

# Step 2: Generate code
print("\n🤖 STEP 2: Generating Playwright code...")
generator = CodeGenerator()
success, code, error = generator.generate_code(tc001)

if not success:
    print(f"❌ Code generation failed: {error}")
    exit(1)

print("✓ Code generated successfully")

# Save code
generator.save_generated_code(tc001['test_id'], code)
print(f"✓ Code saved to: tests/generated/test_{tc001['test_id'].lower()}.py")

# Step 3: Execute test
print("\n🧪 STEP 3: Executing test with Playwright...")
runner = PlaywrightRunner()
result = runner.run_single_test(tc001['test_id'])

print(f"\n📊 Test Result:")
print(f"   Status: {result['status']}")
print(f"   Time: {result['execution_time']:.1f}s")
if result['error_message']:
    print(f"   Error: {result['error_message'][:100]}...")
if result['screenshot_path']:
    print(f"   Screenshot: {result['screenshot_path']}")

# Step 4: Report to Sheet
print("\n📝 STEP 4: Reporting result to Google Sheet...")
reporter = ResultReporter()

report_success = reporter.report_result(worksheet_name, tc001, result)

if report_success:
    print("✓ Result reported to Sheet successfully!")
else:
    print("❌ Failed to report result")

# Summary
print("\n" + "="*70)
print("📊 END-TO-END TEST SUMMARY")
print("="*70)
print(f"Test Case: {tc001['test_id']}")
print(f"Test Result: {result['status']}")
print(f"Execution Time: {result['execution_time']:.1f}s")
print(f"Report Status: {'SUCCESS' if report_success else 'FAILED'}")
print("\n✅ Check Google Sheet to verify the result!")
print("="*70 + "\n")
