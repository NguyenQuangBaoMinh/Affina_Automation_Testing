"""
Google Sheets Service
Write test cases to Google Sheets with multiple worksheet support
"""
import gspread
from google.oauth2.service_account import Credentials
from typing import List, Dict, Optional, Tuple
import os
from datetime import datetime


class GoogleSheetService:
    """Service to write test cases to Google Sheets"""

    def __init__(self, credentials_file: Optional[str] = None, sheet_name: Optional[str] = None):
        """
        Initialize Google Sheets service

        Args:
            credentials_file: Path to service account JSON file
            sheet_name: Name of the Google Sheet
        """
        self.credentials_file = credentials_file or os.getenv('GOOGLE_CREDENTIALS_FILE', 'credentials/service-account.json')
        self.sheet_name = sheet_name or os.getenv('GOOGLE_SHEET_NAME', 'BRD_TestCases_Output')

        # Validate credentials file exists
        if not os.path.exists(self.credentials_file):
            raise FileNotFoundError(f"Google credentials file not found: {self.credentials_file}")

        # Initialize Google Sheets client
        self.client = None
        self.spreadsheet = None
        self._initialize_client()

    def _initialize_client(self):
        """Initialize Google Sheets API client"""
        try:
            # Define the required scopes
            scopes = [
                'https://www.googleapis.com/auth/spreadsheets',
                'https://www.googleapis.com/auth/drive'
            ]

            # Load credentials
            creds = Credentials.from_service_account_file(
                self.credentials_file,
                scopes=scopes
            )

            # Create client
            self.client = gspread.authorize(creds)

            print(f"✓ Google Sheets client initialized")

        except Exception as e:
            raise Exception(f"Failed to initialize Google Sheets client: {str(e)}")

    def _get_or_create_spreadsheet(self) -> Tuple[bool, Optional[str]]:
        """
        Get existing spreadsheet or create new one

        Returns:
            Tuple of (success, error_message)
        """
        try:
            # Try to open existing spreadsheet
            self.spreadsheet = self.client.open(self.sheet_name)
            print(f"✓ Opened existing spreadsheet: {self.sheet_name}")
            return True, None

        except gspread.SpreadsheetNotFound:
            # Create new spreadsheet
            try:
                self.spreadsheet = self.client.create(self.sheet_name)
                print(f"✓ Created new spreadsheet: {self.sheet_name}")
                return True, None
            except Exception as e:
                return False, f"Failed to create spreadsheet: {str(e)}"

        except Exception as e:
            return False, f"Error accessing spreadsheet: {str(e)}"

    def _create_worksheet(self, worksheet_name: str) -> Tuple[bool, Optional[any], Optional[str]]:
        """
        Create new worksheet (tab) in spreadsheet

        Args:
            worksheet_name: Name for the new worksheet

        Returns:
            Tuple of (success, worksheet_object, error_message)
        """
        try:
            # Check if worksheet already exists
            try:
                worksheet = self.spreadsheet.worksheet(worksheet_name)
                print(f"Worksheet '{worksheet_name}' already exists, will overwrite")
                # Clear existing data
                worksheet.clear()
                return True, worksheet, None
            except gspread.WorksheetNotFound:
                pass

            # Create new worksheet
            worksheet = self.spreadsheet.add_worksheet(
                title=worksheet_name,
                rows=150,  # Increased for more test cases
                cols=10
            )

            print(f"✓ Created new worksheet: {worksheet_name}")
            return True, worksheet, None

        except Exception as e:
            return False, None, f"Failed to create worksheet: {str(e)}"

    def _format_test_cases_for_sheet(
        self,
        test_cases: List[Dict],
        brd_filename: str,
        test_id_prefix: str = "TC"
    ) -> List[List[str]]:
        """
        Format test cases into rows for Google Sheets with BRD filename as title

        Args:
            test_cases: List of test case dictionaries
            brd_filename: Original BRD filename to display as title
            test_id_prefix: Prefix for test IDs

        Returns:
            List of rows (each row is a list of cell values)
        """
        # Row 1: BRD filename as title (will be merged across columns)
        title_row = [f"📋 {brd_filename}", "", "", "", "", ""]

        # Row 2: Empty row for spacing
        empty_row = ["", "", "", "", "", ""]

        # Row 3: Header row
        headers = ["Test ID", "Description", "Steps", "Expected Result", "Priority", "Result"]

        # Start with title, empty row, and headers
        rows = [title_row, empty_row, headers]

        # Data rows - test cases
        for i, tc in enumerate(test_cases, 1):
            test_id = f"{test_id_prefix}{i:03d}"  # TC001, TC002, etc.

            row = [
                test_id,
                tc.get('description', ''),
                tc.get('steps', ''),
                tc.get('expected_result', ''),
                tc.get('priority', 'Medium').capitalize(),
                ''  # Result column empty initially
            ]
            rows.append(row)

        return rows

    def _apply_formatting(self, worksheet, brd_filename: str):
        """
        Apply formatting to worksheet (title, headers, colors, etc.)

        Args:
            worksheet: Worksheet object to format
            brd_filename: BRD filename for title
        """
        try:
            # Format Row 1: BRD Title (merged, large, centered, bold)
            worksheet.merge_cells('A1:F1')
            worksheet.format('A1:F1', {
                'backgroundColor': {'red': 0.4, 'green': 0.2, 'blue': 0.8},  # Purple
                'textFormat': {
                    'bold': True,
                    'fontSize': 14,
                    'foregroundColor': {'red': 1.0, 'green': 1.0, 'blue': 1.0}  # White text
                },
                'horizontalAlignment': 'CENTER',
                'verticalAlignment': 'MIDDLE'
            })

            # Set row height for title
            worksheet.set_row_height(1, 50)

            # Format Row 3: Header row (bold, blue background)
            worksheet.format('A3:F3', {
                'backgroundColor': {'red': 0.2, 'green': 0.4, 'blue': 0.8},  # Blue
                'textFormat': {
                    'bold': True,
                    'foregroundColor': {'red': 1.0, 'green': 1.0, 'blue': 1.0}
                },
                'horizontalAlignment': 'CENTER',
                'verticalAlignment': 'MIDDLE'
            })

            # Freeze first 3 rows (title + empty + header)
            worksheet.freeze(rows=3)

            print(f"✓ Applied formatting to worksheet")

        except Exception as e:
            print(f"Warning: Could not apply formatting: {str(e)}")

    def write_test_cases(
        self,
        test_cases: List[Dict],
        worksheet_name: str,
        brd_filename: str = "",
        test_id_prefix: str = "TC"
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Write test cases to Google Sheets with BRD filename as title

        Args:
            test_cases: List of test case dictionaries
            worksheet_name: Name for the worksheet (tab)
            brd_filename: Original BRD filename to display as title
            test_id_prefix: Prefix for test IDs (default: TC)

        Returns:
            Tuple of (success, sheet_url, error_message)
        """
        try:
            print(f"\n{'='*60}")
            print(f"Writing {len(test_cases)} test cases to Google Sheets")
            print(f"BRD: {brd_filename}")
            print(f"{'='*60}\n")

            # Step 1: Get or create spreadsheet
            success, error = self._get_or_create_spreadsheet()
            if not success:
                return False, None, error

            # Step 2: Create worksheet
            success, worksheet, error = self._create_worksheet(worksheet_name)
            if not success:
                return False, None, error

            # Step 3: Format test cases into rows (with BRD filename as title)
            rows = self._format_test_cases_for_sheet(
                test_cases,
                brd_filename or worksheet_name,
                test_id_prefix
            )

            # Step 4: Write data to worksheet
            print(f"Writing {len(rows)} rows to worksheet...")
            worksheet.update('A1', rows)
            print(f"✓ Data written successfully")

            # Step 5: Apply formatting
            self._apply_formatting(worksheet, brd_filename or worksheet_name)

            # Get sheet URL
            sheet_url = self.spreadsheet.url

            print(f"\n{'='*60}")
            print(f"✓ SUCCESS!")
            print(f"  - Spreadsheet: {self.sheet_name}")
            print(f"  - Worksheet: {worksheet_name}")
            print(f"  - BRD: {brd_filename}")
            print(f"  - Test cases: {len(test_cases)}")
            print(f"  - URL: {sheet_url}")
            print(f"{'='*60}\n")

            return True, sheet_url, None

        except Exception as e:
            error_msg = f"Failed to write to Google Sheets: {str(e)}"
            print(f"✗ {error_msg}")
            return False, None, error_msg

    def get_spreadsheet_url(self) -> Optional[str]:
        """Get URL of the current spreadsheet"""
        if self.spreadsheet:
            return self.spreadsheet.url
        return None


# Convenience function
def write_testcases_to_sheet(
    test_cases: List[Dict],
    worksheet_name: str,
    brd_filename: str = "",
    credentials_file: Optional[str] = None,
    sheet_name: Optional[str] = None
) -> Tuple[bool, Optional[str], Optional[str]]:
    """
    Quick function to write test cases to Google Sheets

    Args:
        test_cases: List of test case dictionaries
        worksheet_name: Name for the worksheet
        brd_filename: Original BRD filename for title
        credentials_file: Path to credentials file (optional)
        sheet_name: Name of spreadsheet (optional)

    Returns:
        Tuple of (success, sheet_url, error_message)
    """
    service = GoogleSheetService(credentials_file, sheet_name)
    return service.write_test_cases(test_cases, worksheet_name, brd_filename)