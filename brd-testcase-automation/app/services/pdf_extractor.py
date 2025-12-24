"""
PDF Extraction Service
Extract text content from PDF BRD documents
"""
import PyPDF2
import pdfplumber
from typing import Optional, Tuple
import os


class PDFExtractor:
    """Extract text content from PDF files"""

    def __init__(self):
        """Initialize PDF extractor"""
        pass

    def extract_text_pypdf2(self, pdf_path: str) -> str:
        """
        Extract text using PyPDF2 library
        Args:
            pdf_path: Path to PDF file
        Returns:
            Extracted text content
        """
        text = ""
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                num_pages = len(pdf_reader.pages)

                for page_num in range(num_pages):
                    page = pdf_reader.pages[page_num]
                    text += page.extract_text() + "\n\n"

            return text.strip()

        except Exception as e:
            print(f"PyPDF2 extraction failed: {str(e)}")
            return ""

    def extract_text_pdfplumber(self, pdf_path: str) -> str:
        """
        Extract text using pdfplumber library (more accurate)
        Args:
            pdf_path: Path to PDF file
        Returns:
            Extracted text content
        """
        text = ""
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n\n"

            return text.strip()

        except Exception as e:
            print(f"pdfplumber extraction failed: {str(e)}")
            return ""

    def extract_text(self, pdf_path: str, method: str = "auto") -> Tuple[bool, str, Optional[str]]:
        """
        Extract text from PDF using best available method

        Args:
            pdf_path: Path to PDF file
            method: Extraction method ('auto', 'pypdf2', 'pdfplumber')

        Returns:
            Tuple of (success, extracted_text, error_message)
        """
        # Validate file exists
        if not os.path.exists(pdf_path):
            return False, "", f"File not found: {pdf_path}"

        # Validate file is PDF
        if not pdf_path.lower().endswith('.pdf'):
            return False, "", "File is not a PDF"

        extracted_text = ""

        # Try extraction based on method
        if method == "auto":
            # Try pdfplumber first (more accurate)
            print(f"Extracting text from: {os.path.basename(pdf_path)}")
            print("   Method: pdfplumber (primary)")
            extracted_text = self.extract_text_pdfplumber(pdf_path)

            # Fallback to PyPDF2 if pdfplumber fails
            if not extracted_text or len(extracted_text.strip()) < 100:
                print("   Method: PyPDF2 (fallback)")
                extracted_text = self.extract_text_pypdf2(pdf_path)

        elif method == "pypdf2":
            extracted_text = self.extract_text_pypdf2(pdf_path)

        elif method == "pdfplumber":
            extracted_text = self.extract_text_pdfplumber(pdf_path)

        else:
            return False, "", f"Unknown extraction method: {method}"

        # Validate extracted content
        if not extracted_text or len(extracted_text.strip()) < 100:
            return False, "", "Failed to extract sufficient text from PDF. File may be scanned image or corrupted."

        # Clean up extracted text
        extracted_text = self._clean_text(extracted_text)

        print(f"✓ Successfully extracted {len(extracted_text)} characters")
        print(f"✓ Extracted {extracted_text.count(chr(10)) + 1} lines")

        return True, extracted_text, None

    def _clean_text(self, text: str) -> str:
        """
        Clean extracted text (remove excessive whitespace, etc.)

        Args:
            text: Raw extracted text

        Returns:
            Cleaned text
        """
        # loại bỏ dòng trắng dư
        lines = text.split('\n')
        cleaned_lines = []
        blank_count = 0

        for line in lines:
            if line.strip() == '':
                blank_count += 1
                if blank_count <= 2:
                    cleaned_lines.append(line)
            else:
                blank_count = 0
                cleaned_lines.append(line)

        text = '\n'.join(cleaned_lines)

        # Xóa khoảng trắng thừa giữa các từ
        text = ' '.join(text.split())

        # Thêm ngắt dòng sau dấu chấm câu để câu rõ ràng
        text = text.replace('. ', '.\n')

        return text.strip()

    def get_pdf_info(self, pdf_path: str) -> dict:
        """
        Get PDF metadata and info

        Args:
            pdf_path: Path to PDF file

        Returns:
            Dictionary with PDF info
        """
        info = {
            'file_name': os.path.basename(pdf_path),
            'file_size_mb': 0,
            'num_pages': 0,
            'has_text': False
        }

        try:
            # Get file size
            file_size = os.path.getsize(pdf_path)
            info['file_size_mb'] = round(file_size / (1024 * 1024), 2)

            # Get page count and check for text
            with pdfplumber.open(pdf_path) as pdf:
                info['num_pages'] = len(pdf.pages)

                # Check if first page has text
                if pdf.pages:
                    first_page_text = pdf.pages[0].extract_text()
                    info['has_text'] = bool(first_page_text and len(first_page_text.strip()) > 10)

        except Exception as e:
            print(f"Error getting PDF info: {str(e)}")

        return info


# Convenience function for quick usage
def extract_pdf_text(pdf_path: str) -> Tuple[bool, str, Optional[str]]:
    """
    Quick function to extract text from PDF

    Args:
        pdf_path: Path to PDF file

    Returns:
        Tuple of (success, extracted_text, error_message)
    """
    extractor = PDFExtractor()
    return extractor.extract_text(pdf_path)