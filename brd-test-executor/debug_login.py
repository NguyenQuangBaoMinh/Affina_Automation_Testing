"""
Debug login process - Manual inspection
"""
import asyncio
from playwright.async_api import async_playwright
from app.config import Config

async def main():
    Config.init_app()
    
    async with async_playwright() as p:
        # Launch browser
        browser = await p.chromium.launch(
            headless=False,
            slow_mo=1000,  # Slow down 1s per action
            channel='chrome'
        )
        
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080}
        )
        
        page = await context.new_page()
        
        print("Navigating to website...")
        await page.goto(Config.TEST_WEBSITE_URL)
        
        print("\n" + "="*70)
        print("🔍 Page Info:")
        print("="*70)
        print(f"URL: {page.url}")
        print(f"Title: {await page.title()}")
        
        # Take screenshot
        await page.screenshot(path='debug_initial_page.png', full_page=True)
        print(f"✓ Screenshot: debug_initial_page.png")
        
        # Wait to see page
        print("\n⏸️  Browser will stay open for 30 seconds for inspection...")
        print("   Check what's on the page!")
        await asyncio.sleep(30)
        
        # Try to find email input
        print("\n🔍 Looking for email input...")
        
        selectors_to_try = [
            "input[name='email']",
            "input[type='email']",
            "input[placeholder*='email' i]",
            "input[placeholder*='Email' i]",
            "#email",
            "[id*='email' i]",
            "[name*='username' i]",
            "input[type='text']",
        ]
        
        for selector in selectors_to_try:
            try:
                element = await page.wait_for_selector(selector, timeout=2000)
                if element:
                    print(f"✓ Found: {selector}")
                    # Get element details
                    attrs = await element.evaluate('''el => ({
                        tag: el.tagName,
                        id: el.id,
                        name: el.name,
                        type: el.type,
                        placeholder: el.placeholder,
                        class: el.className
                    })''')
                    print(f"  Details: {attrs}")
            except:
                print(f"✗ Not found: {selector}")
        
        print("\n⏸️  Pausing... Close browser when done inspecting")
        await asyncio.sleep(60)
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
