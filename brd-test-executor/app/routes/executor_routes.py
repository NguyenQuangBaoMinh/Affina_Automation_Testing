"""
Executor Routes - Phase 2
API endpoints for test execution
"""
from flask import jsonify, request, render_template
from app.routes import executor_bp
from app.services.gsheet_service import GoogleSheetService
from app.config import Config
import traceback


@executor_bp.route('/')
def index():
    """Render main UI page"""
    return render_template('executor.html')


@executor_bp.route('/api/config', methods=['GET'])
def get_config():
    """Get application configuration"""
    return jsonify({
        'success': True,
        'config': {
            'sheet_name': Config.GOOGLE_SHEET_NAME,
            'test_website': Config.TEST_WEBSITE_URL,
            'browser': Config.BROWSER,
            'headless': Config.HEADLESS
        }
    })


@executor_bp.route('/api/worksheets', methods=['GET'])
def get_worksheets():
    """
    Get list of worksheets from Google Sheet
    
    Returns:
        JSON with list of worksheets
    """
    try:
        print("\n📋 Fetching worksheets from Google Sheet...")
        
        # Initialize Google Sheets service
        gsheet_service = GoogleSheetService(
            credentials_file=Config.GOOGLE_CREDENTIALS_FILE,
            sheet_name=Config.GOOGLE_SHEET_NAME
        )
        
        # Get or open spreadsheet
        success, error = gsheet_service._get_or_create_spreadsheet()
        if not success:
            return jsonify({
                'success': False,
                'error': f'Failed to access Google Sheet: {error}'
            }), 500
        
        # Get all worksheets
        worksheets = gsheet_service.spreadsheet.worksheets()

        # Format worksheet data
        worksheet_list = []
        for ws in worksheets:
            # Skip default empty worksheet
            if ws.title == 'Trang tính1' or ws.row_count <= 3:
                continue

            # ĐẾM CHÍNH XÁC: Đọc tất cả giá trị trong cột A (TC ID)
            try:
                # Lấy tất cả giá trị cột A (TC ID column)
                col_a_values = ws.col_values(1)  # Column A

                # Đếm số dòng có TC ID (bắt đầu bằng "TC")
                actual_test_count = sum(1 for val in col_a_values if val and str(val).strip().startswith('TC'))

                # Nếu không có TC nào, skip worksheet này
                if actual_test_count == 0:
                    continue

                worksheet_info = {
                    'name': ws.title,
                    'test_count': actual_test_count,  # ← Số chính xác
                    'row_count': ws.row_count,
                    'url': ws.url
                }

                worksheet_list.append(worksheet_info)

            except Exception as e:
                # Nếu lỗi khi đọc, dùng cách tính cũ
                print(f"⚠️  Warning: Could not read worksheet {ws.title}: {e}")
                test_count = max(0, ws.row_count - 3)

                worksheet_info = {
                    'name': ws.title,
                    'test_count': test_count,
                    'row_count': ws.row_count,
                    'url': ws.url
                }

                worksheet_list.append(worksheet_info)
        
        print(f"✓ Found {len(worksheet_list)} worksheets with test cases")
        
        return jsonify({
            'success': True,
            'sheet_name': Config.GOOGLE_SHEET_NAME,
            'sheet_url': gsheet_service.spreadsheet.url,
            'worksheets': worksheet_list,
            'total': len(worksheet_list)
        })
    
    except Exception as e:
        error_msg = f"Error fetching worksheets: {str(e)}"
        print(f"✗ {error_msg}")
        traceback.print_exc()
        
        return jsonify({
            'success': False,
            'error': error_msg
        }), 500


@executor_bp.route('/api/run-tests', methods=['POST'])
def run_tests():
    """
    Start test execution (placeholder for now)
    
    Request body:
        {
            "worksheet_name": "BRD_Portal_20251023_235959",
            "browser": "chromium",
            "headless": false
        }
    
    Returns:
        JSON with execution ID
    """
    try:
        data = request.get_json()
        
        worksheet_name = data.get('worksheet_name')
        browser = data.get('browser', 'chromium')
        headless = data.get('headless', False)
        
        if not worksheet_name:
            return jsonify({
                'success': False,
                'error': 'worksheet_name is required'
            }), 400
        
        print("\n" + "="*70)
        print("🚀 Test Execution Request")
        print("="*70)
        print(f"Worksheet: {worksheet_name}")
        print(f"Browser: {browser}")
        print(f"Headless: {headless}")
        print("="*70)
        
        # TODO: Implement actual test execution
        # For now, return mock response
        
        import time
        execution_id = f"exec_{int(time.time())}"
        
        return jsonify({
            'success': True,
            'execution_id': execution_id,
            'message': 'Test execution will be implemented next',
            'worksheet_name': worksheet_name,
            'status': 'pending'
        })
    
    except Exception as e:
        error_msg = f"Error starting test execution: {str(e)}"
        print(f"✗ {error_msg}")
        traceback.print_exc()
        
        return jsonify({
            'success': False,
            'error': error_msg
        }), 500
