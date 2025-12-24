"""
Code Generator Service
Generates Playwright test code from test cases using Azure OpenAI
"""
from typing import Dict, Optional, Tuple
from openai import AzureOpenAI
from app.config import Config
from app.automation.locator_manager import get_locator_manager
from app.automation.url_manager import get_url_manager
import json


class CodeGenerator:
    """Generate Playwright test code using Azure OpenAI"""
    
    def __init__(self):
        """Initialize code generator with Azure OpenAI client"""
        self.client = AzureOpenAI(
            api_key=Config.AZURE_OPENAI_API_KEY,
            api_version=Config.AZURE_OPENAI_API_VERSION,
            azure_endpoint=Config.AZURE_OPENAI_ENDPOINT
        )
        self.deployment = Config.AZURE_OPENAI_DEPLOYMENT
        self.locator_manager = get_locator_manager()
        self.url_manager = get_url_manager()
        
        print(f"✓ Code Generator initialized")
        print(f"  Azure OpenAI: {Config.AZURE_OPENAI_DEPLOYMENT}")
    
    def _detect_module(self, test_case: Dict) -> str:
        """
        Detect which module/feature this test case belongs to
        
        Args:
            test_case: Test case dictionary
        
        Returns:
            Module name (e.g., 'contract', 'lead', 'product')
        """
        description = test_case.get('description', '').lower()
        steps = test_case.get('steps', '').lower()
        
        # Keyword mapping
        if any(word in description or word in steps for word in ['hợp đồng', 'ctv', 'contract']):
            return 'contract'
        elif any(word in description or word in steps for word in ['lead', 'khách hàng tiềm năng']):
            return 'lead'
        elif any(word in description or word in steps for word in ['sản phẩm', 'product']):
            return 'product'
        elif any(word in description or word in steps for word in ['deeplink', 'link']):
            return 'deeplink'
        elif any(word in description or word in steps for word in ['báo cáo', 'report', 'dashboard']):
            return 'report'
        elif any(word in description or word in steps for word in ['cài đặt', 'setting', 'kpi']):
            return 'settings'
        elif any(word in description or word in steps for word in ['profile', 'hồ sơ', 'tài khoản']):
            return 'profile'
        else:
            return 'contract'  # Default
    
    def _create_prompt(self, test_case: Dict, locators: Dict) -> str:
        """
        Create prompt for Azure OpenAI
        
        Args:
            test_case: Test case dictionary
            locators: Available locators
        
        Returns:
            Prompt string
        """
        # Detect module from test case description or ID
        module = self._detect_module(test_case)
        
        # Get relevant URLs for the module
        module_urls = self.url_manager.get_all_urls(module) if module else {}
        
        prompt = f"""You are an expert Playwright test automation engineer. Generate Python Playwright code for the following test case.

TEST CASE INFORMATION:
- Test ID: {test_case['test_id']}
- Description: {test_case['description']}
- Steps: {test_case['steps']}
- Expected Result: {test_case['expected_result']}
- Priority: {test_case['priority']}

WEBSITE INFORMATION:
- Base URL: {Config.TEST_WEBSITE_URL}
- Login Username: {Config.TEST_USERNAME}
- Login Password: {Config.TEST_PASSWORD}

MODULE DETECTED: {module or 'contract (default)'}

AVAILABLE URLs FOR THIS MODULE:
{json.dumps(module_urls, indent=2, ensure_ascii=False)}

IMPORTANT URL NOTES:
- Use the correct URL path from the mapping above
- For example, contract list page is: /account/contract (NOT /contract/list)
- Always use full URL from the mapping above
- If URL contains {{id}}, replace with actual ID when needed

AVAILABLE ELEMENT LOCATORS (use these when possible):
{json.dumps(locators, indent=2, ensure_ascii=False)}

REQUIREMENTS:
1. Generate ONLY a Python async function named `test_{test_case['test_id'].lower()}`
2. Function signature: `async def test_{test_case['test_id'].lower()}(page: Page):`
3. Use Playwright Page API (page.goto, page.fill, page.click, etc.)
4. Use the provided locators when matching elements
5. Use the CORRECT URLs from the module mapping above
6. Add appropriate waits (page.wait_for_selector, page.wait_for_load_state)
7. Add assertions using expect() from playwright.sync_api
8. Handle popups/alerts if needed
9. Add comments explaining key steps in Vietnamese
10. Include error handling with try-except
11. Return True if test passes, False if fails

IMPORTANT NOTES:
- Use Vietnamese text matching with :has-text() for buttons/links
- Use multiple selector fallbacks from locators config
- Add reasonable timeouts (30 seconds default)
- Take screenshot on failure
- Do NOT include imports or fixture code
- Do NOT include login code (assume already logged in)
- Focus on the specific test case steps
- ALWAYS use correct URL paths from the module mapping provided above
- The page object is already provided, you don't need to create browser or context

CRITICAL: Make sure to use the exact URLs from the "AVAILABLE URLs FOR THIS MODULE" section above!

Generate ONLY the function code, nothing else:"""
        
        return prompt
    
    def generate_code(self, test_case: Dict) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Generate Playwright code for a test case
        
        Args:
            test_case: Test case dictionary from sheet reader
        
        Returns:
            Tuple of (success, generated_code, error_message)
        """
        try:
            print(f"\n{'='*70}")
            print(f"🤖 Generating code for: {test_case['test_id']}")
            print(f"{'='*70}")
            print(f"Description: {test_case['description'][:80]}...")
            
            # Detect module
            module = self._detect_module(test_case)
            print(f"Detected module: {module}")
            
            # Get relevant locators
            locators = {
                'login': self.locator_manager.get_all('login'),
                'contract': self.locator_manager.get_all('contract'),
                'common': self.locator_manager.get_all('common'),
            }
            
            # Add more locators based on detected module
            if module == 'lead':
                locators['lead'] = self.locator_manager.get_all('lead') or {}
            elif module == 'product':
                locators['product'] = self.locator_manager.get_all('product') or {}
            
            # Create prompt
            prompt = self._create_prompt(test_case, locators)
            
            print(f"\n📝 Sending request to Azure OpenAI...")
            
            # Call Azure OpenAI
            response = self.client.chat.completions.create(
                model=self.deployment,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert Playwright test automation engineer. Generate clean, efficient, and reliable test code. Always use the correct URLs provided in the prompt."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.4,
                max_tokens=12000,
            )
            
            # Extract generated code
            generated_code = response.choices[0].message.content.strip()
            
            # Clean up code (remove markdown if present)
            if generated_code.startswith('```python'):
                generated_code = generated_code[len('```python'):].strip()
            if generated_code.startswith('```'):
                generated_code = generated_code[3:].strip()
            if generated_code.endswith('```'):
                generated_code = generated_code[:-3].strip()
            
            print(f"✓ Code generated successfully!")
            print(f"  Length: {len(generated_code)} characters")
            print(f"  Lines: {len(generated_code.split(chr(10)))} lines")
            
            # Show preview
            print(f"\n📄 Code Preview (first 15 lines):")
            print("-" * 70)
            lines = generated_code.split('\n')
            for i, line in enumerate(lines[:15], 1):
                print(f"{i:2d} | {line}")
            if len(lines) > 15:
                print(f"... ({len(lines) - 15} more lines)")
            print("-" * 70)
            
            return True, generated_code, None
        
        except Exception as e:
            import traceback
            error_msg = f"Error generating code: {str(e)}"
            print(f"\n✗ {error_msg}")
            traceback.print_exc()
            return False, None, error_msg
    
    def generate_batch(self, test_cases: list, max_count: int = 5) -> Tuple[int, list]:
        """
        Generate code for multiple test cases
        
        Args:
            test_cases: List of test case dictionaries
            max_count: Maximum number to generate
        
        Returns:
            Tuple of (success_count, results_list)
        """
        print(f"\n{'='*70}")
        print(f" Batch Code Generation")
        print(f"{'='*70}")
        print(f"Generating code for {min(len(test_cases), max_count)} test cases...")
        
        results = []
        success_count = 0
        
        for i, test_case in enumerate(test_cases[:max_count], 1):
            print(f"\n[{i}/{min(len(test_cases), max_count)}] Processing {test_case['test_id']}...")
            
            success, code, error = self.generate_code(test_case)
            
            result = {
                'test_case': test_case,
                'success': success,
                'code': code,
                'error': error
            }
            
            results.append(result)
            
            if success:
                success_count += 1
        
        print(f"\n{'='*70}")
        print(f" Batch Generation Complete")
        print(f"{'='*70}")
        print(f"Success: {success_count}/{min(len(test_cases), max_count)}")
        print(f"Failed: {min(len(test_cases), max_count) - success_count}")
        
        return success_count, results
    
    def save_generated_code(self, test_id: str, code: str, output_dir: str = "tests/generated") -> bool:
        """
        Save generated code to file
        
        Args:
            test_id: Test case ID
            code: Generated code
            output_dir: Output directory
        
        Returns:
            True if successful
        """
        try:
            import os
            
            # Create output directory
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            
            # Create filename
            filename = f"{output_dir}/test_{test_id.lower()}.py"
            
            # Add imports at the top
            full_code = f'''"""
Auto-generated test for {test_id}
Generated by BRD Test Executor
"""
from playwright.async_api import Page, expect
import asyncio

{code}

# Run the test
if __name__ == "__main__":
    from playwright.async_api import async_playwright
    
    async def main():
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False, channel='chrome')
            context = await browser.new_context()
            page = await context.new_page()
            
            try:
                result = await test_{test_id.lower()}(page)
                print(f"Test result: {{'PASS' if result else 'FAIL'}}")
            except Exception as e:
                print(f"Test failed with error: {{e}}")
            finally:
                await browser.close()
    
    asyncio.run(main())
'''
            
            # Write to file
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(full_code)
            
            print(f"✓ Code saved to: {filename}")
            return True
        
        except Exception as e:
            print(f"✗ Error saving code: {str(e)}")
            return False
