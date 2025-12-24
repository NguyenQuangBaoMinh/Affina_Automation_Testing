"""
Helper functions for BRD Test Case Automation
Utility functions for file handling, ID generation, timestamps, etc.
"""
import os
import re
from datetime import datetime
from typing import Optional


def generate_test_id(index: int, prefix: str = "TC") -> str:
    """
    Generate test case ID with prefix and zero-padded number

    Args:
        index: Test case number (1, 2, 3...)
        prefix: Prefix for test ID (default: TC)

    Returns:
        Formatted test ID (e.g., TC001, TC002, TC003)
    """
    return f"{prefix}{index:03d}"


def get_timestamp(format: str = "%Y%m%d_%H%M%S") -> str:
    """
    Get current timestamp as formatted string

    Args:
        format: Datetime format string

    Returns:
        Formatted timestamp string
    """
    return datetime.now().strftime(format)


def sanitize_filename(filename: str) -> str:
    """
    Remove special characters from filename for safe usage

    Args:
        filename: Original filename

    Returns:
        Sanitized filename
    """
    # Remove file extension
    name_without_ext = os.path.splitext(filename)[0]

    # Replace spaces and special characters with underscore
    sanitized = re.sub(r'[^a-zA-Z0-9_-]', '_', name_without_ext)

    # Remove multiple consecutive underscores
    sanitized = re.sub(r'_+', '_', sanitized)

    # Remove leading/trailing underscores
    sanitized = sanitized.strip('_')

    return sanitized


def generate_worksheet_name(brd_filename: str, max_length: int = 100) -> str:
    """
    Generate unique worksheet (tab) name for Google Sheets
    Format: {sanitized_filename}_{timestamp}

    Args:
        brd_filename: Original BRD filename
        max_length: Maximum length for worksheet name (Google Sheets limit is 100)

    Returns:
        Unique worksheet name
    """
    sanitized = sanitize_filename(brd_filename)
    timestamp = get_timestamp("%Y%m%d_%H%M%S")

    worksheet_name = f"{sanitized}_{timestamp}"

    # Truncate if too long (Google Sheets has 100 char limit)
    if len(worksheet_name) > max_length:
        # Keep timestamp, truncate filename part
        max_filename_length = max_length - len(timestamp) - 1  # -1 for underscore
        sanitized = sanitized[:max_filename_length]
        worksheet_name = f"{sanitized}_{timestamp}"

    return worksheet_name


def cleanup_upload_file(filepath: str) -> bool:
    """
    Delete uploaded file after processing

    Args:
        filepath: Path to file to delete

    Returns:
        True if successful, False otherwise
    """
    try:
        if os.path.exists(filepath):
            os.remove(filepath)
            print(f"✓ Cleaned up file: {filepath}")
            return True
        return False
    except Exception as e:
        print(f"  Error cleaning up file {filepath}: {str(e)}")
        return False


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format

    Args:
        size_bytes: File size in bytes

    Returns:
        Formatted string (e.g., "1.5 MB", "250 KB")
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"


def parse_test_cases_from_response(response_text: str) -> list:
    """
    Parse test cases from ChatGPT response
    Expects JSON format or structured text

    Args:
        response_text: Response from ChatGPT

    Returns:
        List of test case dictionaries
    """
    import json

    try:
        # Try to parse as JSON first
        data = json.loads(response_text)

        # If it's a dict with 'test_cases' key
        if isinstance(data, dict) and 'test_cases' in data:
            return data['test_cases']

        # If it's already a list
        if isinstance(data, list):
            return data

        return []

    except json.JSONDecodeError:
        # If not JSON, try to parse structured text
        # This is a fallback - we'll handle this in chatgpt_service.py
        return []


def validate_test_case_structure(test_case: dict) -> bool:
    """
    Validate that a test case has all required fields

    Args:
        test_case: Test case dictionary

    Returns:
        True if valid, False otherwise
    """
    required_fields = ['description', 'steps', 'expected_result', 'priority']

    for field in required_fields:
        if field not in test_case or not test_case[field]:
            return False

    return True


def get_priority_order(priority: str) -> int:
    """
    Get numeric order for priority sorting

    Args:
        priority: Priority string (High, Medium, Low)

    Returns:
        Numeric value for sorting
    """
    priority_map = {
        'high': 1,
        'medium': 2,
        'low': 3
    }
    return priority_map.get(priority.lower(), 999)


def estimate_processing_time(file_size_mb: float) -> int:
    """
    Estimate processing time based on file size

    Args:
        file_size_mb: File size in megabytes

    Returns:
        Estimated time in seconds
    """
    # Rough estimate: 5 seconds per MB + base time
    base_time = 10  # Base processing time
    per_mb_time = 5

    estimated = base_time + (file_size_mb * per_mb_time)
    return int(estimated)