"""
API Routes for BRD Test Case Generation
Endpoints for uploading BRD and generating test cases
"""
from flask import Blueprint, request, jsonify, render_template
from werkzeug.utils import secure_filename
import os
from datetime import datetime

from app.services.pdf_extractor import PDFExtractor
from app.services.chatgpt_service import ChatGPTService
from app.services.gsheet_service import GoogleSheetService
from app.utils.validators import validate_file_upload, validate_brd_content
from app.utils.helpers import (
    generate_worksheet_name,
    cleanup_upload_file,
    format_file_size,
    estimate_processing_time
)
from app.config import Config

# Create Blueprint
brd_bp = Blueprint('brd', __name__)


@brd_bp.route('/')
def index():
    """Render main page"""
    return render_template('index.html')


@brd_bp.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'BRD Test Case Automation',
        'timestamp': datetime.now().isoformat()
    }), 200


@brd_bp.route('/api/generate-testcases', methods=['POST'])
def generate_testcases():
    """
    Main endpoint to generate test cases from BRD PDF

    Expected request:
        - multipart/form-data
        - field: 'files' (one or more PDF files)
        - optional field: 'target_count' (number of test cases, default: 55)

    Returns:
        JSON with test cases results and Google Sheets URL
    """
    try:
        # Step 1: Validate request
        if 'files' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No files provided in request'
            }), 400

        files = request.files.getlist('files')

        if not files or files[0].filename == '':
            return jsonify({
                'success': False,
                'error': 'No files selected'
            }), 400

        # Get optional parameters
        target_count = int(request.form.get('target_count', 55))

        # Initialize services
        pdf_extractor = PDFExtractor()
        chatgpt_service = ChatGPTService()
        gsheet_service = GoogleSheetService()

        results = []
        all_success = True

        # Step 2: Process each file
        for file in files:
            try:
                print(f"\n{'=' * 70}")
                print(f"Processing file: {file.filename}")
                print(f"{'=' * 70}\n")

                # Validate file
                is_valid, error_msg = validate_file_upload(
                    file,
                    Config.ALLOWED_EXTENSIONS,
                    max_size_mb=16
                )

                if not is_valid:
                    results.append({
                        'filename': file.filename,
                        'success': False,
                        'error': error_msg
                    })
                    all_success = False
                    continue

                # Save file temporarily
                filename = secure_filename(file.filename)
                filepath = os.path.join(Config.UPLOAD_FOLDER, filename)
                file.save(filepath)

                file_size_mb = os.path.getsize(filepath) / (1024 * 1024)
                print(f"✓ File saved: {filename} ({format_file_size(os.path.getsize(filepath))})")
                print(f"  Estimated processing time: ~{estimate_processing_time(file_size_mb)} seconds")
                print()

                # Step 3: Extract text from PDF
                print("Step 1/4: Extracting text from PDF...")
                success, brd_content, error = pdf_extractor.extract_text(filepath)

                if not success:
                    cleanup_upload_file(filepath)
                    results.append({
                        'filename': filename,
                        'success': False,
                        'error': f"PDF extraction failed: {error}"
                    })
                    all_success = False
                    continue

                # Validate BRD content
                is_valid, error_msg = validate_brd_content(brd_content, min_length=100)
                if not is_valid:
                    cleanup_upload_file(filepath)
                    results.append({
                        'filename': filename,
                        'success': False,
                        'error': error_msg
                    })
                    all_success = False
                    continue

                print()

                # Step 4: Generate test cases using ChatGPT
                print("Step 2/4: Generating test cases with ChatGPT...")
                success, test_cases, error, batch_breakdown = chatgpt_service.generate_test_cases(  # 🆕 Added batch_breakdown
                    brd_content,
                    target_count=target_count,
                    batch_mode=True
                )

                if not success:
                    cleanup_upload_file(filepath)
                    results.append({
                        'filename': filename,
                        'success': False,
                        'error': f"Test case generation failed: {error}"
                    })
                    all_success = False
                    continue

                print()

                # Step 5: Estimate total test cases needed and calculate coverage
                print("Step 3/4: Calculating test coverage...")
                total_tests_needed = chatgpt_service.estimate_required_test_cases(
                    brd_content,
                    len(test_cases)
                )

                if total_tests_needed > 0:
                    coverage_percentage = (len(test_cases) / total_tests_needed) * 100
                    coverage_percentage = round(min(100, coverage_percentage), 1)
                else:
                    coverage_percentage = 100 if len(test_cases) > 0 else 0

                print(f"📊 Coverage Analysis:")
                print(f"   Generated: {len(test_cases)} test cases")
                print(f"   Estimated needed: {total_tests_needed} test cases")
                print(f"   Coverage: {coverage_percentage}%")
                print()

                # Step 6: Write to Google Sheets
                print("Step 4/4: Writing to Google Sheets...")
                worksheet_name = generate_worksheet_name(filename)

                success, sheet_url, error = gsheet_service.write_test_cases(
                    test_cases,
                    worksheet_name,
                    brd_filename=filename,
                    test_id_prefix=Config.TEST_CASE_PREFIX
                )

                if not success:
                    cleanup_upload_file(filepath)
                    results.append({
                        'filename': filename,
                        'success': False,
                        'error': f"Google Sheets write failed: {error}"
                    })
                    all_success = False
                    continue

                # Success!
                cleanup_upload_file(filepath)

                # ✅ FIXED: Use correct variable names
                results.append({
                    'filename': filename,
                    'success': True,
                    'worksheet_name': worksheet_name,
                    'total_test_cases': len(test_cases),
                    'target_test_cases': target_count,
                    'estimated_total_needed': total_tests_needed,  # ✅ ĐÚNG
                    'coverage_percentage': coverage_percentage,
                    'batch_breakdown': batch_breakdown,  # 🆕 THÊM BATCH BREAKDOWN
                    'sheet_url': sheet_url
                })

                print(f"\n{'=' * 70}")
                print(f"✓ COMPLETED: {filename}")
                print(f"  Test Cases Generated: {len(test_cases)}")
                print(f"  Estimated Total Needed: {total_tests_needed}")
                print(f"  Coverage: {coverage_percentage}%")
                # 🆕 Print batch breakdown if available
                if batch_breakdown:
                    print(f"  Batch Breakdown:")
                    for key, data in batch_breakdown.items():
                        if data['count'] > 0:
                            print(f"    • {data['name']}: {data['count']} ({data['percentage']}%)")
                print(f"{'=' * 70}\n")

            except Exception as e:
                print(f"✗ Error processing {file.filename}: {str(e)}")
                results.append({
                    'filename': file.filename,
                    'success': False,
                    'error': f"Unexpected error: {str(e)}"
                })
                all_success = False

                # Cleanup if file was saved
                try:
                    filepath = os.path.join(Config.UPLOAD_FOLDER, secure_filename(file.filename))
                    cleanup_upload_file(filepath)
                except:
                    pass

        # Step 7: Return results
        response = {
            'success': all_success,
            'message': 'All files processed successfully' if all_success else 'Some files failed to process',
            'total_files': len(files),
            'successful_files': sum(1 for r in results if r['success']),
            'failed_files': sum(1 for r in results if not r['success']),
            'results': results
        }

        status_code = 200 if all_success else 207  # 207 = Multi-Status
        return jsonify(response), status_code

    except Exception as e:
        print(f"✗ Fatal error in generate_testcases endpoint: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
        }), 500


@brd_bp.route('/api/config', methods=['GET'])
def get_config():
    """Get current configuration (for UI display)"""
    return jsonify({
        'success': True,
        'config': {
            'model': Config.OPENAI_MODEL,
            'coverage_target': Config.COVERAGE_TARGET,
            'test_case_prefix': Config.TEST_CASE_PREFIX,
            'allowed_extensions': list(Config.ALLOWED_EXTENSIONS),
            'max_file_size_mb': Config.MAX_CONTENT_LENGTH / (1024 * 1024),
            'google_sheet_name': Config.GOOGLE_SHEET_NAME
        }
    }), 200


@brd_bp.route('/api/continue-generation', methods=['POST'])
def continue_generation():
    """
    Continue generating test cases to reach coverage target

    Request body:
    {
        "brd_filename": "...",
        "brd_content": "...",
        "current_count": 85,
        "target_total": 320,
        "worksheet_name": "...",
        "existing_breakdown": {...}
    }
    """
    pass

@brd_bp.errorhandler(413)
def request_entity_too_large(error):
    """Handle file too large error"""
    return jsonify({
        'success': False,
        'error': f'File too large. Maximum size: {Config.MAX_CONTENT_LENGTH / (1024 * 1024)}MB'
    }), 413


@brd_bp.errorhandler(500)
def internal_server_error(error):
    """Handle internal server error"""
    return jsonify({
        'success': False,
        'error': 'Internal server error. Please check logs.'
    }), 500