"""
Result Reporter
Write test execution results back to Google Sheets
"""
from typing import Dict, Optional
from app.services.gsheet_service import GoogleSheetService
from app.config import Config
import os


class ResultReporter:
    """Report test results to Google Sheets"""
    
    def __init__(self):
        """Initialize result reporter"""
        self.gsheet_service = GoogleSheetService(
            credentials_file=Config.GOOGLE_CREDENTIALS_FILE,
            sheet_name=Config.GOOGLE_SHEET_NAME
        )
        
        print("✓ Result Reporter initialized")
    
    def _ensure_result_columns(self, worksheet) -> bool:
        """Ensure columns G and H exist with proper headers"""
        try:
            headers = worksheet.row_values(3)
            current_cols = len(headers)
            updates_needed = []
            
            if current_cols < 7 or (current_cols >= 7 and (not headers[6] or headers[6].strip() == '')):
                updates_needed.append((3, 7, 'Error Message'))
                print("  Adding column G: Error Message")
            
            if current_cols < 8 or (current_cols >= 8 and (not headers[7] or headers[7].strip() == '')):
                updates_needed.append((3, 8, 'Screenshot'))
                print("  Adding column H: Screenshot")
            
            if updates_needed:
                print(f"✓ Adding {len(updates_needed)} missing columns...")
                for row, col, value in updates_needed:
                    worksheet.update_cell(row, col, value)
                print(f"✓ Columns added successfully")
            else:
                print(f"✓ All result columns already exist")
            
            return True
        
        except Exception as e:
            print(f"✗ Error ensuring columns: {str(e)}")
            return False
    
    def _add_screenshot_info(
        self, 
        worksheet,
        row_num: int,
        col_num: int,
        image_path: str
    ) -> bool:
        """
        Add screenshot information to cell
        
        Args:
            worksheet: Worksheet object
            row_num: Row number
            col_num: Column number
            image_path: Path to screenshot
        
        Returns:
            True if successful
        """
        try:
            print(f"📸 Adding screenshot info...")
            
            # Get file info
            filename = os.path.basename(image_path)
            rel_path = os.path.relpath(image_path)
            file_size = os.path.getsize(image_path) / 1024  # KB
            
            # Create text with relative path and size
            screenshot_text = f"{rel_path} ({file_size:.0f} KB)"
            
            # Update cell
            worksheet.update_cell(row_num, col_num, screenshot_text)
            
            print(f"✓ Screenshot info added")
            print(f"  File: {filename}")
            print(f"  Path: {rel_path}")
            print(f"  Size: {file_size:.0f} KB")
            
            return True
        
        except Exception as e:
            print(f"  Error adding screenshot info: {str(e)}")
            # Fallback: Just filename
            try:
                filename = os.path.basename(image_path)
                worksheet.update_cell(row_num, col_num, f"📸 {filename}")
                return True
            except:
                return False
    
    def report_result(
        self,
        worksheet_name: str,
        test_case: Dict,
        result: Dict
    ) -> bool:
        """
        Report test result to Google Sheet
        
        Args:
            worksheet_name: Name of worksheet
            test_case: Test case dict (with row_number)
            result: Result dict from runner
        
        Returns:
            True if successful
        """
        try:
            print(f"\n{'='*70}")
            print(f"📊 Reporting result for: {test_case['test_id']}")
            print(f"{'='*70}")
            
            # Get worksheet
            success, error = self.gsheet_service._get_or_create_spreadsheet()
            if not success:
                print(f"✗ Failed to access sheet: {error}")
                return False
            
            worksheet = self.gsheet_service.spreadsheet.worksheet(worksheet_name)
            
            # Ensure columns G and H exist
            print("Checking result columns...")
            self._ensure_result_columns(worksheet)
            
            # Row number
            row_num = test_case.get('row_number')
            if not row_num:
                print(f"✗ No row number in test case")
                return False
            
            print(f"Updating row: {row_num}")
            
            # Column F: Result (PASS/FAIL)
            status = result.get('status', 'UNKNOWN')
            worksheet.update_cell(row_num, 6, status)
            print(f" Updated Result (F): {status}")
            
            # Column G: Error Message (if FAIL)
            error_msg = result.get('error_message', '')
            if error_msg:
                # Truncate if too long
                if len(error_msg) > 1000:
                    error_msg = error_msg[:1000] + "... (truncated)"
                worksheet.update_cell(row_num, 7, error_msg)
                print(f" Updated Error (G): {error_msg[:50]}...")
            else:
                worksheet.update_cell(row_num, 7, '')
                print(f" Cleared Error (G)")
            
            # Column H: Screenshot path
            screenshot_path = result.get('screenshot_path')
            if screenshot_path and os.path.exists(screenshot_path):
                self._add_screenshot_info(worksheet, row_num, 8, screenshot_path)
            else:
                worksheet.update_cell(row_num, 8, '')
                print(f"✓ No screenshot (test passed)")
            
            print(f"{'='*70}")
            print(f" Result reported successfully!")
            print(f"{'='*70}\n")
            
            return True
        
        except Exception as e:
            print(f" Error reporting result: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def clear_results(self, worksheet_name: str, start_row: int = 4, end_row: int = 100):
        """
        Clear all results from worksheet
        
        Args:
            worksheet_name: Name of worksheet
            start_row: Start row (default 4 - first test case)
            end_row: End row
        """
        try:
            print(f" Clearing results in {worksheet_name}...")
            
            success, error = self.gsheet_service._get_or_create_spreadsheet()
            if not success:
                return False
            
            worksheet = self.gsheet_service.spreadsheet.worksheet(worksheet_name)
            
            # Ensure columns exist
            self._ensure_result_columns(worksheet)
            
            # Clear columns F, G, H
            for row in range(start_row, end_row + 1):
                worksheet.update_cell(row, 6, '')  # Result
                worksheet.update_cell(row, 7, '')  # Error
                worksheet.update_cell(row, 8, '')  # Screenshot
            
            print(f" Results cleared")
            return True
        
        except Exception as e:
            print(f" Error clearing results: {str(e)}")
            return False
    
    def batch_report_results(
        self,
        worksheet_name: str,
        test_results: list
    ) -> tuple:
        """
        Report multiple test results at once
        
        Args:
            worksheet_name: Name of worksheet
            test_results: List of (test_case, result) tuples
        
        Returns:
            Tuple of (success_count, fail_count)
        """
        success_count = 0
        fail_count = 0
        
        print(f"\n{'='*70}")
        print(f" Batch Reporting {len(test_results)} results")
        print(f"{'='*70}")
        
        for test_case, result in test_results:
            success = self.report_result(worksheet_name, test_case, result)
            if success:
                success_count += 1
            else:
                fail_count += 1
        
        print(f"\n{'='*70}")
        print(f" Batch Report Complete")
        print(f"{'='*70}")
        print(f"Success: {success_count}/{len(test_results)}")
        print(f"Failed: {fail_count}/{len(test_results)}")
        
        return success_count, fail_count
