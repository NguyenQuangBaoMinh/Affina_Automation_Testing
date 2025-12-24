"""
Sheet Reader Service
Reads test cases from Google Sheets worksheet
"""
from typing import List, Dict, Tuple, Optional
from app.services.gsheet_service import GoogleSheetService
from app.config import Config


class SheetReader:
    """Read and parse test cases from Google Sheets"""
    
    def __init__(self):
        """Initialize sheet reader"""
        self.gsheet_service = GoogleSheetService(
            credentials_file=Config.GOOGLE_CREDENTIALS_FILE,
            sheet_name=Config.GOOGLE_SHEET_NAME
        )
        self.spreadsheet = None
    
    def connect(self) -> Tuple[bool, Optional[str]]:
        """
        Connect to Google Sheets
        
        Returns:
            Tuple of (success, error_message)
        """
        try:
            success, error = self.gsheet_service._get_or_create_spreadsheet()
            if success:
                self.spreadsheet = self.gsheet_service.spreadsheet
                print(f"✓ Connected to spreadsheet: {Config.GOOGLE_SHEET_NAME}")
                return True, None
            else:
                return False, error
        except Exception as e:
            return False, str(e)
    
    def read_test_cases(self, worksheet_name: str) -> Tuple[bool, List[Dict], Optional[str]]:
        """
        Read all test cases from a worksheet
        
        Args:
            worksheet_name: Name of worksheet to read
        
        Returns:
            Tuple of (success, list_of_test_cases, error_message)
        """
        try:
            print(f"\n{'='*70}")
            print(f"📖 Reading test cases from: {worksheet_name}")
            print(f"{'='*70}")
            
            # Connect if not already connected
            if not self.spreadsheet:
                success, error = self.connect()
                if not success:
                    return False, [], f"Failed to connect: {error}"
            
            # Get worksheet
            try:
                worksheet = self.spreadsheet.worksheet(worksheet_name)
            except Exception as e:
                return False, [], f"Worksheet not found: {worksheet_name}"
            
            print(f"✓ Worksheet opened: {worksheet.title}")
            print(f"  Total rows: {worksheet.row_count}")
            
            # Get all values (from row 1 to end)
            all_values = worksheet.get_all_values()
            
            if len(all_values) < 4:
                return False, [], "Worksheet has insufficient data (need at least 4 rows)"
            
            # Row 1: BRD filename (skip)
            # Row 2: Empty (skip)
            # Row 3: Headers
            headers = all_values[2]  # Index 2 = Row 3
            
            print(f"✓ Headers found: {headers}")
            
            # Validate headers
            expected_headers = ['Test ID', 'Description', 'Steps', 'Expected Result', 'Priority']
            for i, expected in enumerate(expected_headers):
                if i >= len(headers) or expected.lower() not in headers[i].lower():
                    print(f"  Warning: Expected header '{expected}' at column {i+1}, found '{headers[i] if i < len(headers) else 'N/A'}'")
            
            # Parse test cases (from row 4 onwards)
            test_cases = []
            
            for row_idx in range(3, len(all_values)):  # Start from row 4 (index 3)
                row = all_values[row_idx]
                
                # Skip empty rows
                if not row or not row[0] or not row[0].strip():
                    continue
                
                # Extract test case data
                test_id = row[0].strip() if len(row) > 0 else ""
                description = row[1].strip() if len(row) > 1 else ""
                steps = row[2].strip() if len(row) > 2 else ""
                expected_result = row[3].strip() if len(row) > 3 else ""
                priority = row[4].strip() if len(row) > 4 else "Medium"
                
                # Skip if test ID doesn't start with TC
                if not test_id.startswith('TC'):
                    continue
                
                # Create test case dict
                test_case = {
                    'test_id': test_id,
                    'description': description,
                    'steps': steps,
                    'expected_result': expected_result,
                    'priority': priority,
                    'row_number': row_idx + 1,  # +1 because row_idx is 0-based
                    'status': '',  # Will be filled after execution
                    'error_message': '',
                    'screenshot_url': ''
                }
                
                test_cases.append(test_case)
            
            print(f"\n✓ Successfully read {len(test_cases)} test cases")
            
            # Print summary
            if test_cases:
                print(f"\n📋 Test Cases Summary:")
                print(f"  First TC: {test_cases[0]['test_id']} - {test_cases[0]['description'][:50]}...")
                print(f"  Last TC:  {test_cases[-1]['test_id']} - {test_cases[-1]['description'][:50]}...")
                
                # Priority breakdown
                priority_count = {}
                for tc in test_cases:
                    priority = tc['priority']
                    priority_count[priority] = priority_count.get(priority, 0) + 1
                
                print(f"\n  Priority Breakdown:")
                for priority, count in sorted(priority_count.items()):
                    print(f"    {priority}: {count} test cases")
            
            print(f"{'='*70}\n")
            
            return True, test_cases, None
        
        except Exception as e:
            import traceback
            error_msg = f"Error reading test cases: {str(e)}"
            print(f"✗ {error_msg}")
            traceback.print_exc()
            return False, [], error_msg
    
    def get_test_case_by_id(self, test_cases: List[Dict], test_id: str) -> Optional[Dict]:
        """
        Get a specific test case by ID
        
        Args:
            test_cases: List of test cases
            test_id: Test case ID (e.g., "TC001")
        
        Returns:
            Test case dict or None
        """
        for tc in test_cases:
            if tc['test_id'] == test_id:
                return tc
        return None
    
    def filter_by_priority(self, test_cases: List[Dict], priority: str) -> List[Dict]:
        """
        Filter test cases by priority
        
        Args:
            test_cases: List of test cases
            priority: Priority level (High, Medium, Low)
        
        Returns:
            Filtered list of test cases
        """
        return [tc for tc in test_cases if tc['priority'].lower() == priority.lower()]


# Convenience function
def read_test_cases_from_worksheet(worksheet_name: str) -> Tuple[bool, List[Dict], Optional[str]]:
    """
    Convenience function to read test cases
    
    Args:
        worksheet_name: Name of worksheet
    
    Returns:
        Tuple of (success, test_cases, error)
    """
    reader = SheetReader()
    return reader.read_test_cases(worksheet_name)
