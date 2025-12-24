"""
ChatGPT Service
Call OpenAI API to generate test cases from BRD content
Focus on UI/UX testing with 3-batch strategy for 90 test cases
"""
import os
import json
from typing import List, Dict, Optional, Tuple
from openai import OpenAI
from dotenv import load_dotenv
import re

load_dotenv()


class ChatGPTService:
    """Service to interact with OpenAI ChatGPT API"""

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        """
        Initialize ChatGPT service
        Supports both Azure OpenAI and standard OpenAI

        Args:
            api_key: OpenAI API key (if None, loads from environment)
            model: Model to use (if None, loads from environment)
        """
        # Check using Azure OpenAI
        self.azure_endpoint = os.getenv('AZURE_OPENAI_ENDPOINT')
        self.azure_api_key = os.getenv('AZURE_OPENAI_API_KEY')
        self.azure_deployment = os.getenv('AZURE_OPENAI_DEPLOYMENT')
        self.azure_api_version = os.getenv('AZURE_OPENAI_API_VERSION', '2024-12-01-preview')

        if self.azure_endpoint and self.azure_api_key:
            # Use Azure OpenAI
            print(" Using Azure OpenAI Service")
            print(f"  - Endpoint: {self.azure_endpoint}")
            print(f"  - Deployment: {self.azure_deployment}")

            from openai import AzureOpenAI
            self.client = AzureOpenAI(
                api_key=self.azure_api_key,
                api_version=self.azure_api_version,
                azure_endpoint=self.azure_endpoint
            )
            self.model = self.azure_deployment
            self.is_azure = True
        else:
            #
            print(" Using standard OpenAI API")
            self.api_key = api_key or os.getenv('OPENAI_API_KEY')
            self.model = model or os.getenv('OPENAI_MODEL', 'gpt-4-turbo-preview')

            if not self.api_key:
                raise ValueError("OpenAI API key not found. Set OPENAI_API_KEY or Azure config in .env file")

            from openai import OpenAI
            self.client = OpenAI(api_key=self.api_key)
            self.is_azure = False

    def estimate_required_test_cases(self, brd_content: str, generated_count: int) -> int:
        """
        Estimate TOTAL test cases needed to fully cover BRD (including UI details)

        Args:
            brd_content: Full BRD text
            generated_count: Number of test cases already generated

        Returns:
            Estimated total test cases needed for full coverage
        """
        content_sample = brd_content[:6000] if len(brd_content) > 6000 else brd_content

        prompt = f"""You are a QA Test Manager. Analyze this BRD and estimate the TOTAL number of UI/UX test cases needed for COMPREHENSIVE coverage.

    BRD Content:
    {content_sample}

    Consider:
    1. Number of screens/pages
    2. Number of UI elements per screen (buttons, fields, dropdowns, etc.)
    3. Number of user interactions (click, type, select, navigate)
    4. Validation scenarios (required fields, format checks)
    5. Edge cases (empty states, max length, special characters)
    6. Responsive design testing (mobile, tablet, desktop)
    7. Different user flows and paths

    For example:
    - Simple login page: 15-20 test cases
    - Complex form with 10 fields: 40-50 test cases
    - Multi-step wizard: 60-80 test cases
    - Full insurance application: 80-120 test cases

    Currently generated: {generated_count} test cases

    Return ONLY a single number representing the TOTAL test cases needed for full UI/UX coverage:"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system",
                     "content": "You are an expert QA manager who estimates test coverage needs accurately."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=50
            )

            result = response.choices[0].message.content.strip()
            numbers = re.findall(r'\d+', result)

            if numbers:
                estimated = int(numbers[0])
                # Ensure estimate is at least equal to what we generated
                estimated = max(estimated, generated_count)
                print(f"  ✓ AI estimated: {estimated} test cases needed for full coverage")
                return estimated
            else:
                return self._estimate_by_heuristic(brd_content, generated_count)

        except Exception as e:
            print(f"   AI estimation failed: {str(e)}")
            return self._estimate_by_heuristic(brd_content, generated_count)

    def _estimate_by_heuristic(self, brd_content: str, generated_count: int) -> int:
        """
        Fallback: estimate based on BRD length and complexity

        Args:
            brd_content: Full BRD text
            generated_count: Number of test cases generated

        Returns:
            Estimated total test cases needed
        """
        # Heuristics based on BRD characteristics
        brd_length = len(brd_content)

        # Count UI elements mentioned
        ui_keywords = [
            'button', 'field', 'form', 'input', 'dropdown', 'checkbox',
            'radio', 'select', 'menu', 'tab', 'modal', 'dialog',
            'nút', 'trường', 'biểu mẫu', 'nhập', 'chọn'
        ]

        ui_element_count = sum(brd_content.lower().count(keyword) for keyword in ui_keywords)

        # Base estimate on length
        if brd_length < 5000:
            base_estimate = 30  # Simple BRD
        elif brd_length < 15000:
            base_estimate = 60  # Medium BRD
        else:
            base_estimate = 100  # Complex BRD

        # Adjust based on UI complexity
        ui_factor = min(ui_element_count / 20, 2.0)  # Up to 2x multiplier

        estimate = int(base_estimate * (1 + ui_factor * 0.5))

        # Ensure estimate is reasonable relative to generated count
        # If we generated 20, estimate should be at least 40 (assuming 50% coverage)
        min_estimate = int(generated_count * 1.5)
        estimate = max(estimate, min_estimate)

        print(
            f"  ✓ Heuristic estimate: {estimate} test cases (based on BRD length: {brd_length} chars, UI elements: {ui_element_count})")

        return estimate

    def _create_prompt_ui_happy_path(self, brd_content: str, count: int = 30) -> str:
        """Create prompt for generating UI Happy Path test cases"""
        prompt = f"""You are an expert QA UI/UX Test Engineer for an insurance company.

Analyze the following BRD (Business Requirements Document) and generate EXACTLY {count} test cases focusing on UI/UX HAPPY PATH scenarios.

BRD CONTENT:
{brd_content}

FOCUS AREAS FOR THIS BATCH:
1. Main user flows working correctly (navigation, form submission)
2. UI elements displaying properly (buttons, fields, labels, images)
3. Successful scenarios (user completes tasks without errors)
4. Page transitions and navigation between screens
5. Data display and presentation on UI

TEST CASE REQUIREMENTS:
- Focus ONLY on UI/UX testing (NOT backend/API/database)
- Test user interface elements: buttons, forms, fields, dropdowns, checkboxes, etc.
- Test visual elements: layout, alignment, colors, fonts, spacing
- Test user interactions: click, type, select, navigate
- Describe WHAT USER SEES and WHAT USER DOES on the UI
- Each test case MUST include:
  * description: Clear UI-focused description
  * steps: Detailed UI interaction steps (use \\n for line breaks)
  * expected_result: What user sees on screen (UI feedback)
  * priority: "High" for critical UI flows, "Medium" for secondary

OUTPUT FORMAT - MUST be valid JSON array ONLY:
[
  {{
    "description": "Verify health insurance selection button displays and is clickable",
    "steps": "1. Open the insurance selection page\\n2. Locate the 'Health Insurance' button\\n3. Verify button is visible and enabled\\n4. Click on the button",
    "expected_result": "Button changes color on hover, page navigates to health insurance form, form fields are displayed correctly",
    "priority": "High"
  }},
  ...
]

IMPORTANT:
- Output ONLY the JSON array, no markdown, no explanations
- Generate EXACTLY {count} test cases
- Use Vietnamese if BRD is in Vietnamese
- Focus on UI elements, user interactions, visual verification
- NO technical/backend testing (no API, database, server tests)
"""
        return prompt

    def _create_prompt_ui_validation(self, brd_content: str, count: int = 30) -> str:
        """Create prompt for generating UI Validation & Interaction test cases"""
        prompt = f"""You are an expert QA UI/UX Test Engineer for an insurance company.

Analyze the following BRD (Business Requirements Document) and generate EXACTLY {count} test cases focusing on UI VALIDATION & USER INTERACTIONS.

BRD CONTENT:
{brd_content}

FOCUS AREAS FOR THIS BATCH:
1. Form field validation (required fields, format validation, length limits)
2. Input field behaviors (placeholder text, error messages, success indicators)
3. Button states (enabled/disabled/loading states)
4. Dropdown/select behaviors (options display, selection feedback)
5. Checkbox/radio button interactions
6. Error message display and formatting
7. Tooltip and help text display
8. User input feedback (typing indicators, character counters)

TEST CASE REQUIREMENTS:
- Focus on UI VALIDATION and USER INTERACTION feedback
- Test what happens when user enters invalid/valid data
- Test UI response to user actions
- Verify error messages, validation messages display correctly on UI
- Test field-level interactions (focus, blur, typing, selecting)
- Each test case MUST include:
  * description: Clear UI validation scenario
  * steps: Detailed interaction steps on UI
  * expected_result: UI feedback user sees (error messages, visual indicators)
  * priority: "Medium" for most validation tests

OUTPUT FORMAT - MUST be valid JSON array ONLY:
[
  {{
    "description": "Verify error message displays when required field is left empty",
    "steps": "1. Open insurance application form\\n2. Leave 'Full Name' field empty\\n3. Click Submit button\\n4. Observe error message",
    "expected_result": "Red error message appears below field stating 'Full Name is required', field border turns red, submit button remains enabled",
    "priority": "Medium"
  }},
  ...
]

IMPORTANT:
- Output ONLY the JSON array, no markdown, no explanations
- Generate EXACTLY {count} test cases
- Use Vietnamese if BRD is in Vietnamese
- Focus on UI validation feedback, not backend validation
- Test visual feedback user sees on screen
"""
        return prompt

    def _create_prompt_ui_edge_cases(self, brd_content: str, count: int = 30) -> str:
        """Create prompt for generating UI Edge Cases & Responsive test cases"""
        prompt = f"""You are an expert QA UI/UX Test Engineer for an insurance company.

Analyze the following BRD (Business Requirements Document) and generate EXACTLY {count} test cases focusing on UI EDGE CASES, RESPONSIVE DESIGN, and CROSS-BROWSER testing.

BRD CONTENT:
{brd_content}

FOCUS AREAS FOR THIS BATCH:
1. Boundary testing (max length inputs, special characters, very long text)
2. Responsive design (mobile, tablet, desktop views)
3. Browser compatibility (Chrome, Safari, Firefox, Edge)
4. UI edge cases (window resize, zoom in/out, orientation change)
5. Accessibility (keyboard navigation, tab order, screen reader support)
6. Visual regression (layout breaks, overlapping elements, cut-off text)
7. Empty states and loading states
8. Performance UI feedback (slow loading, large data sets)

TEST CASE REQUIREMENTS:
- Focus on EDGE CASES and CROSS-DEVICE testing
- Test UI behavior in unusual but valid scenarios
- Test responsive design across different screen sizes
- Test accessibility features
- Verify UI doesn't break under edge conditions
- Each test case MUST include:
  * description: Clear edge case or responsive scenario
  * steps: Detailed steps including device/browser context
  * expected_result: UI behavior and layout expectations
  * priority: "Medium" or "Low" based on criticality

OUTPUT FORMAT - MUST be valid JSON array ONLY:
[
  {{
    "description": "Verify form layout remains intact when browser window is resized to tablet width (768px)",
    "steps": "1. Open insurance form on desktop browser\\n2. Resize browser window to 768px width\\n3. Observe form layout and field alignment\\n4. Try filling and submitting form",
    "expected_result": "Form fields stack vertically, buttons remain visible and clickable, no horizontal scrolling, all text remains readable, no overlapping elements",
    "priority": "Medium"
  }},
  ...
]

IMPORTANT:
- Output ONLY the JSON array, no markdown, no explanations
- Generate EXACTLY {count} test cases
- Use Vietnamese if BRD is in Vietnamese
- Focus on UI edge cases, responsive behavior, visual consistency
- Test cross-device and cross-browser UI rendering
"""
        return prompt

    def _call_chatgpt(self, prompt: str, max_tokens: int = 12000) -> Tuple[bool, str, Optional[str]]:
        """Call ChatGPT API"""
        try:
            print(f" Calling ChatGPT API ({self.model})...")

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert QA UI/UX Test Engineer specializing in generating comprehensive UI/UX test cases. Always output valid JSON only. Focus on user interface testing, not backend or technical testing."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=max_tokens,
                temperature=0.7
            )

            response_text = response.choices[0].message.content

            # Log token usage
            print(f"✓ API call successful")
            print(f"  - Input tokens: {response.usage.prompt_tokens}")
            print(f"  - Output tokens: {response.usage.completion_tokens}")
            print(f"  - Total tokens: {response.usage.total_tokens}")

            return True, response_text, None

        except Exception as e:
            error_msg = f"ChatGPT API error: {str(e)}"
            print(f"✗ {error_msg}")
            return False, "", error_msg

    def _parse_test_cases(self, response_text: str) -> Tuple[bool, List[Dict], Optional[str]]:
        """Parse test cases from ChatGPT response"""
        try:
            # Remove markdown code blocks
            cleaned_text = response_text.strip()

            if cleaned_text.startswith('```'):
                lines = cleaned_text.split('\n')
                lines = lines[1:]
                cleaned_text = '\n'.join(lines)

            if cleaned_text.endswith('```'):
                cleaned_text = cleaned_text.rsplit('```', 1)[0]

            cleaned_text = cleaned_text.strip()

            # Find JSON array
            first_bracket = cleaned_text.find('[')
            last_bracket = cleaned_text.rfind(']')

            if first_bracket == -1 or last_bracket == -1:
                return False, [], "No JSON array found in response"

            if first_bracket != -1:
                cleaned_text = cleaned_text[first_bracket:]
            if last_bracket != -1:
                cleaned_text = cleaned_text[:last_bracket + 1]

            # Parse JSON
            test_cases = json.loads(cleaned_text)

            if not isinstance(test_cases, list):
                return False, [], "Response is not a JSON array"

            # Validate fields
            required_fields = ['description', 'steps', 'expected_result', 'priority']
            valid_test_cases = []

            for i, tc in enumerate(test_cases):
                missing_fields = [field for field in required_fields if field not in tc]

                if missing_fields:
                    print(f"  Test case {i + 1} missing fields: {missing_fields}, skipping...")
                    continue

                tc['description'] = str(tc['description']).strip()
                tc['steps'] = str(tc['steps']).strip()
                tc['expected_result'] = str(tc['expected_result']).strip()
                tc['priority'] = str(tc['priority']).strip().capitalize()

                valid_test_cases.append(tc)

            if not valid_test_cases:
                return False, [], "No valid test cases found after parsing"

            print(f"✓ Successfully parsed {len(valid_test_cases)} test cases")

            if len(valid_test_cases) < len(test_cases):
                print(f"  Skipped {len(test_cases) - len(valid_test_cases)} invalid test cases")

            return True, valid_test_cases, None

        except json.JSONDecodeError as e:
            error_msg = f"Failed to parse JSON: {str(e)}"
            print(f"✗ {error_msg}")
            return False, [], error_msg

        except Exception as e:
            error_msg = f"Parsing error: {str(e)}"
            print(f"✗ {error_msg}")
            return False, [], error_msg

    def generate_test_cases(
        self,
        brd_content: str,
        target_count: int = 90,
        batch_mode: bool = True
    ) -> Tuple[bool, List[Dict], Optional[str]]:
        """
        Generate UI/UX test cases from BRD content using 3-batch strategy

        Args:
            brd_content: BRD document text content
            target_count: Target number of test cases (default: 90)
            batch_mode: If True, generates in 3 batches

        Returns:
            Tuple of (success, test_cases_list, error_message, batch_breakdown)
        """
        all_test_cases = []
        batch_breakdown = None  # 🆕 Batch statistics tracking

        if batch_mode and target_count >= 70:
            # 3-BATCH STRATEGY
            batch1_count = 30
            batch2_count = 30
            batch3_count = target_count - 60

            print(f"\n{'='*70}")
            print(f"UI/UX TEST GENERATION STRATEGY - {target_count} test cases")
            print(f"{'='*70}")
            print(f"  Batch 1: {batch1_count} UI Happy Path test cases")
            print(f"  Batch 2: {batch2_count} UI Validation test cases")
            print(f"  Batch 3: {batch3_count} UI Edge Cases test cases")
            print(f"{'='*70}\n")

            # BATCH 1
            print(f"\n{'='*70}")
            print(f"BATCH 1: Generating {batch1_count} UI HAPPY PATH test cases")
            print(f"{'='*70}")

            prompt1 = self._create_prompt_ui_happy_path(brd_content, batch1_count)
            success1, response1, error1 = self._call_chatgpt(prompt1)

            if not success1:
                return False, [], error1, None  # 🆕 Return None for breakdown

            success_parse1, happy_cases, parse_error1 = self._parse_test_cases(response1)
            if not success_parse1:
                return False, [], parse_error1, None  # 🆕 Return None for breakdown

            all_test_cases.extend(happy_cases)
            batch1_actual = len(happy_cases)  # 🆕 Track batch 1 count
            print(f"✓ Batch 1 completed: {len(happy_cases)} test cases")

            # BATCH 2
            print(f"\n{'='*70}")
            print(f"BATCH 2: Generating {batch2_count} UI VALIDATION test cases")
            print(f"{'='*70}")

            prompt2 = self._create_prompt_ui_validation(brd_content, batch2_count)
            success2, response2, error2 = self._call_chatgpt(prompt2)

            batch2_actual = 0  # 🆕 Track batch 2 count
            if not success2:
                print(f"Batch 2 failed, returning {len(all_test_cases)} test cases from Batch 1")
                # 🆕 Create breakdown with only batch 1
                batch_breakdown = {
                    'batch1_happy_path': {'name': 'UI Happy Path (MainFlow)', 'count': batch1_actual, 'percentage': 100.0},
                    'batch2_validation': {'name': 'UI Validation', 'count': 0, 'percentage': 0.0},
                    'batch3_edge_cases': {'name': 'UI Boundary (Edge Cases)', 'count': 0, 'percentage': 0.0}
                }
                return True, all_test_cases, "Batch 2 failed but Batch 1 succeeded", batch_breakdown

            success_parse2, validation_cases, parse_error2 = self._parse_test_cases(response2)
            if not success_parse2:
                print(f"Batch 2 parsing failed, returning {len(all_test_cases)} test cases from Batch 1")
                # 🆕 Create breakdown with only batch 1
                batch_breakdown = {
                    'batch1_happy_path': {'name': 'UI Happy Path (MainFlow)', 'count': batch1_actual, 'percentage': 100.0},
                    'batch2_validation': {'name': 'UI Validation', 'count': 0, 'percentage': 0.0},
                    'batch3_edge_cases': {'name': 'UI Boundary (Edge Cases)', 'count': 0, 'percentage': 0.0}
                }
                return True, all_test_cases, "Batch 2 parsing failed but Batch 1 succeeded", batch_breakdown

            all_test_cases.extend(validation_cases)
            batch2_actual = len(validation_cases)  # 🆕 Track batch 2 count
            print(f"✓ Batch 2 completed: {len(validation_cases)} test cases")

            # BATCH 3
            print(f"\n{'='*70}")
            print(f"BATCH 3: Generating {batch3_count} UI EDGE CASES test cases")
            print(f"{'='*70}")

            prompt3 = self._create_prompt_ui_edge_cases(brd_content, batch3_count)
            success3, response3, error3 = self._call_chatgpt(prompt3, max_tokens=12000)

            batch3_actual = 0  # 🆕 Track batch 3 count
            if not success3:
                print(f"Batch 3 failed, returning {len(all_test_cases)} test cases from Batch 1+2")
                # 🆕 Create breakdown with batch 1+2 only
                total = batch1_actual + batch2_actual
                batch_breakdown = {
                    'batch1_happy_path': {'name': 'UI Happy Path (MainFlow)', 'count': batch1_actual, 'percentage': round((batch1_actual/total)*100, 1) if total > 0 else 0},
                    'batch2_validation': {'name': 'UI Validation', 'count': batch2_actual, 'percentage': round((batch2_actual/total)*100, 1) if total > 0 else 0},
                    'batch3_edge_cases': {'name': 'UI Boundary (Edge Cases)', 'count': 0, 'percentage': 0.0}
                }
                return True, all_test_cases, "Batch 3 failed but Batch 1+2 succeeded", batch_breakdown

            success_parse3, edge_cases, parse_error3 = self._parse_test_cases(response3)
            if not success_parse3:
                print(f"Batch 3 parsing failed, returning {len(all_test_cases)} test cases from Batch 1+2")
                # 🆕 Create breakdown with batch 1+2 only
                total = batch1_actual + batch2_actual
                batch_breakdown = {
                    'batch1_happy_path': {'name': 'UI Happy Path (MainFlow)', 'count': batch1_actual, 'percentage': round((batch1_actual/total)*100, 1) if total > 0 else 0},
                    'batch2_validation': {'name': 'UI Validation', 'count': batch2_actual, 'percentage': round((batch2_actual/total)*100, 1) if total > 0 else 0},
                    'batch3_edge_cases': {'name': 'UI Boundary (Edge Cases)', 'count': 0, 'percentage': 0.0}
                }
                return True, all_test_cases, "Batch 3 parsing failed but Batch 1+2 succeeded", batch_breakdown

            all_test_cases.extend(edge_cases)
            batch3_actual = len(edge_cases)  # 🆕 Track batch 3 count
            print(f"✓ Batch 3 completed: {len(edge_cases)} test cases")

            # 🆕 Calculate final breakdown for all 3 batches
            total_generated = batch1_actual + batch2_actual + batch3_actual
            batch_breakdown = {
                'batch1_happy_path': {
                    'name': 'UI Happy Path (MainFlow)',
                    'count': batch1_actual,
                    'percentage': round((batch1_actual / total_generated) * 100, 1) if total_generated > 0 else 0
                },
                'batch2_validation': {
                    'name': 'UI Validation',
                    'count': batch2_actual,
                    'percentage': round((batch2_actual / total_generated) * 100, 1) if total_generated > 0 else 0
                },
                'batch3_edge_cases': {
                    'name': 'UI Boundary (Edge Cases)',
                    'count': batch3_actual,
                    'percentage': round((batch3_actual / total_generated) * 100, 1) if total_generated > 0 else 0
                }
            }

        else:
            # Single batch mode
            print(f"\n{'='*70}")
            print(f"Generating {target_count} test cases (single batch mode)")
            print(f"{'='*70}")

            prompt = self._create_prompt_ui_happy_path(brd_content, target_count)
            success, response, error = self._call_chatgpt(prompt, max_tokens=12000)

            if not success:
                return False, [], error, None  # 🆕 Return None for breakdown

            success_parse, test_cases, parse_error = self._parse_test_cases(response)
            if not success_parse:
                return False, [], parse_error, None  # 🆕 Return None for breakdown

            all_test_cases = test_cases

            # 🆕 Create breakdown for single batch mode
            batch_breakdown = {
                'batch1_happy_path': {
                    'name': 'All Test Cases (Single Batch)',
                    'count': len(test_cases),
                    'percentage': 100.0
                },
                'batch2_validation': {'name': 'N/A', 'count': 0, 'percentage': 0.0},
                'batch3_edge_cases': {'name': 'N/A', 'count': 0, 'percentage': 0.0}
            }

        print(f"\n{'='*70}")
        print(f"TOTAL GENERATED: {len(all_test_cases)} UI/UX test cases")
        # 🆕 Print breakdown if available
        if batch_breakdown:
            print(f"\n📊 Batch Breakdown:")
            for key, data in batch_breakdown.items():
                if data['count'] > 0:
                    print(f"  • {data['name']}: {data['count']} test cases ({data['percentage']}%)")
        print(f"{'='*70}\n")

        return True, all_test_cases, None, batch_breakdown  # 🆕 Return breakdown


# Convenience function
def generate_testcases_from_brd(brd_content: str, target_count: int = 90) -> Tuple[bool, List[Dict], Optional[str]]:
    """
    Quick function to generate UI/UX test cases from BRD

    Args:
        brd_content: BRD text content
        target_count: Target number of test cases (recommended: 70-90)

    Returns:
        Tuple of (success, test_cases_list, error_message)
    """
    service = ChatGPTService()
    return service.generate_test_cases(brd_content, target_count)

    def continue_test_case_generation(
            self,
            brd_content: str,
            already_generated: int,
            remaining_count: int,
            existing_breakdown: dict
    ) -> Tuple[bool, List[Dict], Optional[str], Optional[Dict]]:
        """
        Generate additional test cases to complete coverage

        Returns updated breakdown combining old + new batches

        attention language is VietNamese
        """
        pass