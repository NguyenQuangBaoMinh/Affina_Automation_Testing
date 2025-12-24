"""
Test Locator Manager
"""
from app.automation.locator_manager import LocatorManager

print("\n" + "="*70)
print("🧪 Testing Locator Manager")
print("="*70)

# Initialize
manager = LocatorManager()

# Test get specific locators
print("\n1️⃣ Testing specific locators:")
print("-" * 70)

tests = [
    ('login', 'email_input'),
    ('login', 'password_input'),
    ('login', 'login_button'),
    ('contract', 'create_new_button'),
    ('contract', 'search_input'),
    ('common', 'success_toast'),
]

for category, element in tests:
    locator = manager.get(category, element)
    status = "✓" if locator else "✗"
    print(f"{status} {category}.{element}")
    if locator:
        print(f"   → {locator[:80]}...")

# Test get all locators in category
print("\n2️⃣ Testing category 'login':")
print("-" * 70)

login_locators = manager.get_all('login')
print(f"Found {len(login_locators)} locators:")
for name, selector in login_locators.items():
    print(f"  • {name}: {selector[:60]}...")

# Test has method
print("\n3️⃣ Testing existence check:")
print("-" * 70)

checks = [
    ('login', 'email_input', True),
    ('login', 'nonexistent', False),
    ('contract', 'save_button', True),
]

for category, element, expected in checks:
    exists = manager.has(category, element)
    status = "✓" if exists == expected else "✗"
    print(f"{status} {category}.{element} exists: {exists} (expected: {expected})")

print("\n" + "="*70)
print("✅ Locator Manager Test Completed!")
print("="*70 + "\n")
