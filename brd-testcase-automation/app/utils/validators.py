"""
Validation functions for file uploads and data
"""
import os
from werkzeug.utils import secure_filename
from typing import Tuple, Optional


def allowed_file(filename: str, allowed_extensions: set) -> bool:
    """
    Check if file extension is allowed

    Args:
        filename: Name of the file
        allowed_extensions: Set of allowed extensions (e.g., {'pdf', 'docx'})

    Returns:
        True if file extension is allowed, False otherwise
    """
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in allowed_extensions


def validate_file_upload(file, allowed_extensions: set, max_size_mb: int = 16) -> Tuple[bool, Optional[str]]:
    """
    Validate uploaded file

    Args:
        file: Uploaded file object from Flask request
        allowed_extensions: Set of allowed extensions
        max_size_mb: Maximum file size in megabytes

    Returns:
        Tuple of (is_valid, error_message)
    """
    # Check if file exists
    if not file:
        return False, "No file provided"

    # Check if file has a filename
    if file.filename == '':
        return False, "No file selected"

    # Check file extension
    if not allowed_file(file.filename, allowed_extensions):
        return False, f"File type not allowed. Allowed types: {', '.join(allowed_extensions)}"

    # Check file size (if file has seek capability)
    try:
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)  # Reset to beginning

        max_size_bytes = max_size_mb * 1024 * 1024
        if file_size > max_size_bytes:
            return False, f"File too large. Maximum size: {max_size_mb}MB"
    except (AttributeError, OSError):
        # If file doesn't support seek, skip size check
        pass

    return True, None


def get_secure_filename(filename: str) -> str:
    """
    Get secure version of filename

    Args:
        filename: Original filename

    Returns:
        Secure filename safe for filesystem
    """
    return secure_filename(filename)


def validate_test_case_data(test_case: dict) -> Tuple[bool, Optional[str]]:
    """
    Validate test case data structure

    Args:
        test_case: Dictionary containing test case data

    Returns:
        Tuple of (is_valid, error_message)
    """
    required_fields = ['description', 'steps', 'expected_result', 'priority']

    # Check if all required fields exist
    for field in required_fields:
        if field not in test_case:
            return False, f"Missing required field: {field}"

        # Check if field is not empty
        if not test_case[field] or str(test_case[field]).strip() == '':
            return False, f"Field '{field}' cannot be empty"

    # Validate priority value
    valid_priorities = ['high', 'medium', 'low']
    priority = str(test_case['priority']).lower()
    if priority not in valid_priorities:
        return False, f"Invalid priority. Must be one of: {', '.join(valid_priorities)}"

    return True, None


def validate_brd_content(content: str, min_length: int = 100) -> Tuple[bool, Optional[str]]:
    """
    Validate BRD content extracted from PDF

    Args:
        content: Extracted text content
        min_length: Minimum required content length

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not content or content.strip() == '':
        return False, "BRD content is empty"

    if len(content.strip()) < min_length:
        return False, f"BRD content too short. Minimum {min_length} characters required"

    # Check if content contains meaningful text (not just special characters)
    alphanumeric_count = sum(c.isalnum() for c in content)
    if alphanumeric_count < min_length * 0.5:
        return False, "BRD content appears to be invalid or corrupted"

    return True, None


def validate_google_sheet_name(sheet_name: str) -> Tuple[bool, Optional[str]]:
    """
    Validate Google Sheet name

    Args:
        sheet_name: Name of the Google Sheet

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not sheet_name or sheet_name.strip() == '':
        return False, "Sheet name cannot be empty"

    # Google Sheets has a 100 character limit for worksheet names
    if len(sheet_name) > 100:
        return False, "Sheet name too long (max 100 characters)"

    # Check for invalid characters (Google Sheets restrictions)
    invalid_chars = ['[', ']', '*', '?', ':', '/', '\\']
    for char in invalid_chars:
        if char in sheet_name:
            return False, f"Sheet name contains invalid character: '{char}'"

    return True, None


def validate_api_key(api_key: Optional[str], service_name: str = "API") -> Tuple[bool, Optional[str]]:
    """
    Validate API key format

    Args:
        api_key: API key string
        service_name: Name of the service (for error message)

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not api_key or api_key.strip() == '':
        return False, f"{service_name} key not configured"

    # Basic validation - check if it looks like a key
    if len(api_key) < 20:
        return False, f"{service_name} key appears to be invalid (too short)"

    if api_key.startswith('your_') or api_key.startswith('sk-xxx'):
        return False, f"{service_name} key is still using placeholder value"

    return True, None


def validate_file_path(file_path: str) -> Tuple[bool, Optional[str]]:
    """
    Validate file path exists

    Args:
        file_path: Path to file

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not file_path:
        return False, "File path is empty"

    if not os.path.exists(file_path):
        return False, f"File not found: {file_path}"

    if not os.path.isfile(file_path):
        return False, f"Path is not a file: {file_path}"

    return True, None