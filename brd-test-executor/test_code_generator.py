"""
Test Code Generator
"""
from app.automation.sheet_reader import SheetReader
from app.automation.code_generator import CodeGenerator
from app.config import Config

print("\n" + "="*70)
print("🧪 Testing Code Generator")
print("="*70)

# Initialize
Config.init_app()

# Step 1: Read test cases
print("\n1️⃣ Reading test cases...")
reader = SheetReader()
worksheet_name = "BRD_LUONG_KY_HOP_ONG_-_QUAN_LY_HOP_ONG_VER_2_0_20251024_220811"

success, test_cases, error = reader.read_test_cases(worksheet_name)

if not success:
    print(f"❌ Failed to read test cases: {error}")
    exit(1)

print(f"✅ Read {len(test_cases)} test cases")

# Step 2: Generate code for first test case
print("\n2️⃣ Generating code for first test case...")

generator = CodeGenerator()

test_case = test_cases[0]  # First test case
success, code, error = generator.generate_code(test_case)

if not success:
    print(f"❌ Code generation failed: {error}")
    exit(1)

print(f"\n✅ Code generated successfully!")

# Step 3: Save generated code
print("\n3️⃣ Saving generated code...")
generator.save_generated_code(test_case['test_id'], code)

print("\n" + "="*70)
print("✅ Code Generator Test Completed!")
print("="*70)
print("\n📁 Check: tests/generated/test_tc001.py")
print("="*70 + "\n")
