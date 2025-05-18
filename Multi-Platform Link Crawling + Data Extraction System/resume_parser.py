import re
from typing import List, Dict, Any
import PyPDF2
from docx import Document
import os

class ResumeParser:
    def __init__(self):
        # Match URLs with or without protocol
        self.url_pattern = re.compile(r'(?:https?://)?(?:www\.)?(github\.com|linkedin\.com|figma\.com|leetcode\.com)(/[\w\-./?=&%]*)?')

    def extract_urls_from_text(self, text: str) -> List[str]:
        """Extract only GitHub, LinkedIn, Figma, and LeetCode URLs from text using regex and add https:// prefix if missing."""
        matches = re.finditer(r'(?:https?://)?(?:www\.)?(github\.com|linkedin\.com|figma\.com|leetcode\.com)(/[\w\-./?=&%]*)?', text)
        urls = []
        for match in matches:
            domain = match.group(1)
            path = match.group(2) if match.group(2) else ''
            url = f"{domain}{path}"
            if not url.startswith(('http://', 'https://')):
                url = f"https://{url}"
            urls.append(url)
        return list(set(urls))

    def parse_pdf(self, file_path: str) -> Dict[str, Any]:
        """Parse PDF file and extract text and URLs."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        urls = []
        text = ""

        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                page_text = page.extract_text()
                text += page_text
                urls.extend(self.extract_urls_from_text(page_text))

        return {
            "text": text,
            "urls": list(set(urls)),  # Remove duplicates
            "format_issues": self._check_format_issues(text)
        }

    def parse_doc(self, file_path: str) -> Dict[str, Any]:
        """Parse DOC file and extract text and URLs."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        doc = Document(file_path)
        text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        urls = self.extract_urls_from_text(text)

        return {
            "text": text,
            "urls": list(set(urls)),  # Remove duplicates
            "format_issues": self._check_format_issues(text)
        }

    def _check_format_issues(self, text: str) -> List[str]:
        """Check for common resume formatting issues."""
        issues = []
        
        # Check for inconsistent line spacing
        if len(re.findall(r'\n{3,}', text)) > 0:
            issues.append("Inconsistent line spacing detected")
        
        # Check for very long paragraphs
        paragraphs = text.split('\n\n')
        for para in paragraphs:
            if len(para.split()) > 100:  # Arbitrary threshold
                issues.append("Very long paragraph detected")
                break
        
        # Check for bullet point consistency
        bullet_points = re.findall(r'[•\-\*]\s', text)
        if len(set(bullet_points)) > 1:
            issues.append("Inconsistent bullet point usage")
        
        return issues 