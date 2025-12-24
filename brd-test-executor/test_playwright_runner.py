"""
Test Playwright Runner
Run a single generated test
"""
import asyncio
from app.automation.playwright_runner import PlaywrightRunner
from app.config import Config

async def main():
    print("\n" + "="*70)
    print("🧪 Testing Playwright Runner")
    print("="*70)
    
    # Initialize
    Config.init_app()
    
    runner = PlaywrightRunner()
    
    # Test file
    test_id = "TC001"
    code_file = "tests/generated/test_tc001.py"
    
    try:
        # Run test
        print(f"\n🚀 Running test: {test_id}")
        print("="*70)
        
        result = await runner.run_single_test(test_id, code_file)
        
        # Display results
        print(f"\n{'='*70}")
        print(f"📊 Test Results")
        print(f"{'='*70}")
        print(f"Test ID: {result['test_id']}")
        print(f"Status: {result['status']}")
        print(f"Execution Time: {result['execution_time']:.2f}s")
        
        if result['error_message']:
            print(f"Error: {result['error_message']}")
        
        if result['screenshot_path']:
            print(f"Screenshot: {result['screenshot_path']}")
        
        print(f"{'='*70}\n")
    
    finally:
        # Cleanup
        await runner.stop_browser()
        print("\n✅ Playwright Runner Test Completed!")

if __name__ == "__main__":
    asyncio.run(main())
