"""
Test Sheet Reader
"""
from app.automation.sheet_reader import SheetReader
from app.config import Config

print("\n" + "="*70)
print("🧪 Testing Sheet Reader")
print("="*70)

# Initialize
Config.init_app()
reader = SheetReader()

# Connect
print("\n1️⃣ Connecting to Google Sheets...")
success, error = reader.connect()

if not success:
    print(f"❌ Connection failed: {error}")
    exit(1)

print("✅ Connected successfully!")

# Test với 1 worksheet
test_worksheet = "BRD_LUONG_KY_HOP_ONG_-_QUAN_LY_HOP_ONG_VER_2_0_20251024_220811"

print(f"\n2️⃣ Reading test cases from: {test_worksheet}")

success, test_cases, error = reader.read_test_cases(test_worksheet)

if not success:
    print(f"❌ Failed to read: {error}")
    exit(1)

print(f"\n✅ Read {len(test_cases)} test cases successfully!")

# Display first 3 test cases
print(f"\n{'='*70}")
print("📋 First 3 Test Cases:")
print(f"{'='*70}")

for i, tc in enumerate(test_cases[:3], 1):
    print(f"\n{i}. {tc['test_id']}: {tc['description']}")
    print(f"   Priority: {tc['priority']}")
    print(f"   Steps: {tc['steps'][:100]}...")
    print(f"   Expected: {tc['expected_result'][:100]}...")

print(f"\n{'='*70}")
print("✅ Sheet Reader Test Completed!")
print(f"{'='*70}\n")
