"""
Playwright Runner Service
Executes generated test code with Playwright browser
"""
import asyncio
import os
import importlib.util
import traceback
from typing import Dict, Tuple, Optional
from datetime import datetime
from playwright.async_api import async_playwright, Browser, BrowserContext, Page
from app.config import Config


class PlaywrightRunner:
    """Execute Playwright tests and capture results"""
    
    def __init__(self):
        """Initialize Playwright runner"""
        self.browser = None
        self.context = None
        self.page = None
        self.playwright = None
        
        # Screenshot settings
        self.screenshot_dir = Config.SCREENSHOT_FOLDER
        if not os.path.exists(self.screenshot_dir):
            os.makedirs(self.screenshot_dir)
        
        print(f"✓ Playwright Runner initialized")
        print(f"  Browser: {Config.BROWSER}")
        print(f"  Headless: {Config.HEADLESS}")
        print(f"  Screenshot folder: {self.screenshot_dir}")
    
    async def start_browser(self) -> Tuple[bool, Optional[str]]:
        """
        Start Playwright browser
        
        Returns:
            Tuple of (success, error_message)
        """
        try:
            print(f"\n{'='*70}")
            print(f"🌐 Starting browser...")
            print(f"{'='*70}")
            
            self.playwright = await async_playwright().start()
            
            # Select browser
            if Config.BROWSER == 'chromium':
                browser_type = self.playwright.chromium
            elif Config.BROWSER == 'firefox':
                browser_type = self.playwright.firefox
            elif Config.BROWSER == 'webkit':
                browser_type = self.playwright.webkit
            else:
                browser_type = self.playwright.chromium
            
            # Launch browser
            self.browser = await browser_type.launch(
                headless=Config.HEADLESS,
                slow_mo=Config.SLOW_MO,
                channel='chrome',
            )
            
            print(f"✓ Browser launched: {Config.BROWSER}")
            
            # Create context
            self.context = await self.browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            )
            
            print(f"✓ Browser context created")
            
            # Create page
            self.page = await self.context.new_page()
            self.page.set_default_timeout(Config.TIMEOUT)
            
            print(f"✓ Page created with timeout: {Config.TIMEOUT}ms")
            
            return True, None
        
        except Exception as e:
            error_msg = f"Failed to start browser: {str(e)}"
            print(f"✗ {error_msg}")
            traceback.print_exc()
            return False, error_msg
    
    async def stop_browser(self):
        """Stop browser and cleanup"""
        try:
            if self.page:
                await self.page.close()
            
            if self.context:
                await self.context.close()
            
            if self.browser:
                await self.browser.close()
            
            if self.playwright:
                await self.playwright.stop()
            
            print(f"✓ Browser stopped and cleaned up")
        
        except Exception as e:
            print(f"  Warning during cleanup: {str(e)}")

    async def login(self) -> Tuple[bool, Optional[str]]:
        """
        Perform login to website

        Returns:
            Tuple of (success, error_message)
        """
        try:
            print(f"\n{'=' * 70}")
            print(f" Logging in...")
            print(f"{'=' * 70}")
            print(f"URL: {Config.TEST_WEBSITE_URL}")
            print(f"Username: {Config.TEST_USERNAME}")

            # Go to website
            await self.page.goto(Config.TEST_WEBSITE_URL, wait_until='networkidle')
            print(f"✓ Navigated to: {Config.TEST_WEBSITE_URL}")

            # Wait for page to load
            await asyncio.sleep(2)

            # Check if already logged in
            current_url = self.page.url
            if 'login' not in current_url.lower():
                print(f"✓ Already logged in (no login page)")
                return True, None

            print(f"✓ Login page detected: {current_url}")

            #  FIX: Fill USERNAME (not email!)
            username_selectors = [
                "input[name='username']",
                "#usernameHook",
                "input[id*='username' i]",
                "input[type='text']",
            ]

            username_filled = False
            for selector in username_selectors:
                try:
                    await self.page.wait_for_selector(selector, timeout=5000)
                    await self.page.fill(selector, Config.TEST_USERNAME)
                    username_filled = True
                    print(f"✓ Filled username using: {selector}")
                    break
                except:
                    continue

            if not username_filled:
                return False, "Could not find username input field"

            # Fill password
            password_selectors = [
                "input[name='password']",
                "input[type='password']",
                "#password",
            ]

            password_filled = False
            for selector in password_selectors:
                try:
                    await self.page.wait_for_selector(selector, timeout=5000)
                    await self.page.fill(selector, Config.TEST_PASSWORD)
                    password_filled = True
                    print(f"✓ Filled password using: {selector}")
                    break
                except:
                    continue

            if not password_filled:
                return False, "Could not find password input field"

            # Click login button
            login_button_selectors = [
                "button:has-text('Đăng nhập')",
                "button[type='submit']",
                "input[type='submit']",
            ]

            login_clicked = False
            for selector in login_button_selectors:
                try:
                    await self.page.wait_for_selector(selector, timeout=5000)
                    await self.page.click(selector)
                    login_clicked = True
                    print(f"✓ Clicked login button using: {selector}")
                    break
                except:
                    continue

            if not login_clicked:
                return False, "Could not find login button"

            # Wait for navigation
            try:
                await self.page.wait_for_load_state('networkidle', timeout=15000)
                await asyncio.sleep(2)

                # Check if login successful
                current_url = self.page.url
                if 'login' in current_url.lower():
                    # Still on login page - failed
                    screenshot_path = await self._capture_screenshot("LOGIN", "still_on_login_page")
                    return False, "Login failed - still on login page"

                print(f"✓ Login successful!")
                print(f"  Current URL: {current_url}")

                return True, None

            except Exception as e:
                return False, f"Login timeout: {str(e)}"

        except Exception as e:
            error_msg = f"Login error: {str(e)}"
            print(f"✗ {error_msg}")
            traceback.print_exc()
            return False, error_msg
    
    async def execute_test_code(self, test_id: str, code_file: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Execute generated test code
        
        Args:
            test_id: Test case ID (e.g., "TC001")
            code_file: Path to generated code file
        
        Returns:
            Tuple of (success, error_message, screenshot_path)
        """
        try:
            print(f"\n{'='*70}")
            print(f" Executing test: {test_id}")
            print(f"{'='*70}")
            print(f"Code file: {code_file}")
            
            # Check file exists
            if not os.path.exists(code_file):
                return False, f"Code file not found: {code_file}", None
            
            # Load module dynamically
            spec = importlib.util.spec_from_file_location(f"test_{test_id.lower()}", code_file)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Get test function
            test_function_name = f"test_{test_id.lower()}"
            if not hasattr(module, test_function_name):
                return False, f"Test function '{test_function_name}' not found in module", None
            
            test_function = getattr(module, test_function_name)
            
            print(f"✓ Test function loaded: {test_function_name}")
            
            # Execute test with timeout
            try:
                # Run test with page
                result = await asyncio.wait_for(
                    test_function(self.page),
                    timeout=120  # 2 minutes timeout per test
                )
                
                if result:
                    print(f" Test PASSED: {test_id}")
                    return True, None, None
                else:
                    print(f" Test FAILED: {test_id}")
                    screenshot_path = await self._capture_screenshot(test_id, "assertion_failed")
                    return False, "Test assertions failed", screenshot_path
            
            except asyncio.TimeoutError:
                print(f"  Test TIMEOUT: {test_id}")
                screenshot_path = await self._capture_screenshot(test_id, "timeout")
                return False, "Test execution timeout (120s)", screenshot_path
            
            except Exception as test_error:
                print(f" Test ERROR: {test_id}")
                print(f"   Error: {str(test_error)}")
                traceback.print_exc()
                screenshot_path = await self._capture_screenshot(test_id, "error")
                return False, str(test_error), screenshot_path
        
        except Exception as e:
            error_msg = f"Failed to execute test: {str(e)}"
            print(f"✗ {error_msg}")
            traceback.print_exc()
            return False, error_msg, None
    
    async def _capture_screenshot(self, test_id: str, reason: str) -> Optional[str]:
        """
        Capture screenshot on failure
        
        Args:
            test_id: Test case ID
            reason: Reason for screenshot (timeout, error, assertion_failed)
        
        Returns:
            Screenshot file path or None
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{test_id}_{reason}_{timestamp}.png"
            filepath = os.path.join(self.screenshot_dir, filename)
            
            await self.page.screenshot(path=filepath, full_page=True)
            
            print(f" Screenshot saved: {filepath}")
            return filepath
        
        except Exception as e:
            print(f"  Failed to capture screenshot: {str(e)}")
            return None
    
    async def run_single_test(self, test_id: str, code_file: str) -> Dict:
        """
        Run a single test with full lifecycle
        
        Args:
            test_id: Test case ID
            code_file: Path to generated code file
        
        Returns:
            Result dictionary with status, error, screenshot
        """
        result = {
            'test_id': test_id,
            'status': 'PENDING',
            'error_message': None,
            'screenshot_path': None,
            'execution_time': 0,
        }
        
        start_time = datetime.now()
        
        try:
            # Start browser if not started
            if not self.browser:
                success, error = await self.start_browser()
                if not success:
                    result['status'] = 'FAIL'
                    result['error_message'] = f"Browser start failed: {error}"
                    return result
                
                # Login
                success, error = await self.login()
                if not success:
                    result['status'] = 'FAIL'
                    result['error_message'] = f"Login failed: {error}"
                    screenshot_path = await self._capture_screenshot(test_id, "login_failed")
                    result['screenshot_path'] = screenshot_path
                    return result
            
            # Execute test
            success, error, screenshot_path = await self.execute_test_code(test_id, code_file)
            
            if success:
                result['status'] = 'PASS'
            else:
                result['status'] = 'FAIL'
                result['error_message'] = error
                result['screenshot_path'] = screenshot_path
        
        except Exception as e:
            result['status'] = 'FAIL'
            result['error_message'] = f"Unexpected error: {str(e)}"
            traceback.print_exc()
        
        finally:
            end_time = datetime.now()
            result['execution_time'] = (end_time - start_time).total_seconds()
        
        return result
