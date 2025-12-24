"""
Test URL Manager
"""
from app.automation.url_manager import URLManager

print("\n" + "="*70)
print("🧪 Testing URL Manager")
print("="*70)

manager = URLManager()

# Test get URLs
print("\n1️⃣ Testing get URLs:")
print("-" * 70)

tests = [
    ('contract', 'list'),
    ('contract', 'create'),
    ('contract', 'edit', {'id': '123'}),
    ('lead', 'list'),
    ('product', 'create'),
]

for test in tests:
    if len(test) == 2:
        module, action = test
        url = manager.get(module, action)
    else:
        module, action, kwargs = test
        url = manager.get(module, action, **kwargs)
    
    print(f"✓ {module}.{action}: {url}")

# Test get all URLs for contract
print("\n2️⃣ All URLs for 'contract' module:")
print("-" * 70)

contract_urls = manager.get_all_urls('contract')
for action, url in contract_urls.items():
    print(f"  • {action}: {url}")

print("\n" + "="*70)
print("✅ URL Manager Test Completed!")
print("="*70 + "\n")
