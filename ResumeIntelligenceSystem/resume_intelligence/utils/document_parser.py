"""
Document Parser for Resume Intelligence System

This module provides functionality to parse PDF, DOCX, and TXT documents
using PyMuPDF, python-docx libraries, and built-in file operations.
"""

import os
from pathlib import Path

import fitz  # PyMuPDF
import docx


class DocumentParser:
    
    def __init__(self):
        self.supported_extensions = {
            '.pdf': self._parse_pdf,
            '.docx': self._parse_docx,
            '.txt': self._parse_txt
        }
    
    def parse(self, file_path):

        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        file_ext = file_path.suffix.lower()
        if file_ext not in self.supported_extensions:
            raise ValueError(
                f"Unsupported file format: {file_ext}. "
                f"Supported formats: {', '.join(self.supported_extensions.keys())}"
            )
        
        # Call the appropriate parser based on file extension
        return self.supported_extensions[file_ext](file_path)
    
    def _parse_pdf(self, file_path):

        text = ""
        try:
            with fitz.open(file_path) as doc:
                for page in doc:
                    text += page.get_text()
        except Exception as e:
            raise RuntimeError(f"Error parsing PDF: {e}")
        
        return text
    
    def _parse_docx(self, file_path):

        text = ""
        try:
            doc = docx.Document(file_path)
            for para in doc.paragraphs:
                text += para.text + "\n"
        except Exception as e:
            raise RuntimeError(f"Error parsing DOCX: {e}")
        
        return text
    
    def _parse_txt(self, file_path):

        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                text = file.read()
        except UnicodeDecodeError:
            # Try with a different encoding if UTF-8 fails
            try:
                with open(file_path, 'r', encoding='latin-1') as file:
                    text = file.read()
            except Exception as e:
                raise RuntimeError(f"Error parsing TXT file: {e}")
        except Exception as e:
            raise RuntimeError(f"Error parsing TXT file: {e}")
        
        return text