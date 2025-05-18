"""
Section & Structure Detector for Resume Intelligence System

This module identifies and extracts standard resume sections (education, experience, skills, etc.)
using a combination of NLP techniques and pattern matching.
"""

import json
import re
from pathlib import Path

import spacy


class SectionDetector:
    
    def __init__(self):

        # Common section headers in resumes
        self.section_patterns = {
            'Summary': [r'(?i)\b(summary|profile|objective|about me)\b'],
            'Education': [r'(?i)\b(education|academic|degree|university|college)\b'],
            'Work Experience': [r'(?i)\b(experience|work|employment|job|career|professional)\b'],
            'Skills': [r'(?i)\b(skills|expertise|competencies|proficiencies|technical|technologies)\b'],
            'Projects': [r'(?i)\b(projects|portfolio|works|assignments)\b'],
            'Certifications': [r'(?i)\b(certifications|certificates|credentials|qualifications)\b'],
            'Languages': [r'(?i)\b(languages|language proficiency)\b'],
            'Interests': [r'(?i)\b(interests|hobbies|activities)\b'],
            'References': [r'(?i)\b(references|referees)\b'],
            'Publications': [r'(?i)\b(publications|papers|articles|research)\b'],
            'Awards': [r'(?i)\b(awards|honors|achievements|recognitions)\b'],
            'Volunteer': [r'(?i)\b(volunteer|community|service)\b']
        }
        
        # Load spaCy model for NLP tasks
        try:
            self.nlp = spacy.load("en_core_web_lg")
        except OSError:
            # If model is not installed, use a smaller one
            print("Warning: en_core_web_lg not found. Using en_core_web_sm instead.")
            try:
                self.nlp = spacy.load("en_core_web_sm")
            except OSError:
                print("Warning: No spaCy models found. Downloading en_core_web_sm...")
                spacy.cli.download("en_core_web_sm")
                self.nlp = spacy.load("en_core_web_sm")
    
    def detect_sections(self, text):

        # Preprocess text
        text = self._preprocess_text(text)
        
        # Find potential section headers
        potential_headers = self._find_potential_headers(text)
        
        # Extract sections based on identified headers
        sections = self._extract_sections(text, potential_headers)
        
        # Apply post-processing to improve section detection
        sections = self._post_process_sections(sections, text)
        
        return sections
    
    def _preprocess_text(self, text):

        # Replace multiple newlines with double newlines
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        # Replace tabs with spaces
        text = text.replace('\t', ' ')
        
        # Remove excessive spaces
        text = re.sub(r' {2,}', ' ', text)
        
        return text
    
    def _find_potential_headers(self, text):

        potential_headers = []
        
        # Split text into lines
        lines = text.split('\n')
        
        # Track current position in text
        current_pos = 0
        
        for line in lines:
            line = line.strip()
            if not line:
                current_pos += 1  # Account for newline
                continue
            
            # Check if line matches any section pattern
            for section_name, patterns in self.section_patterns.items():
                for pattern in patterns:
                    if re.search(pattern, line, re.IGNORECASE):
                        # Enhanced header detection criteria
                        is_header = False
                        
                        # Standard header formats
                        if len(line) < 50 and (line.endswith(':') or line.isupper() or line.istitle()):
                            is_header = True
                        
                        # Check for standalone words that are likely headers
                        elif len(line.split()) <= 3 and len(line) < 30:
                            # Check if the line is followed by a blank line or bullet points
                            if current_pos + len(line) + 1 < len(text):
                                next_line = text[current_pos + len(line) + 1:].split('\n', 1)[0].strip()
                                if not next_line or next_line.startswith(('•', '-', '*', '\t', '    ')):
                                    is_header = True
                        
                        # Check for centered text (potential header)
                        elif line.strip() == line and len(line) < 30:
                            surrounding_lines = [l.strip() for l in lines[max(0, lines.index(line)-2):min(len(lines), lines.index(line)+3)]]
                            if all(len(l) < len(line) or not l for l in surrounding_lines if l != line):
                                is_header = True
                        
                        if is_header:
                            potential_headers.append((section_name, current_pos, line))
                            break
            
            current_pos += len(line) + 1  # +1 for newline
        
        # Sort headers by position in text
        potential_headers.sort(key=lambda x: x[1])
        
        return potential_headers
    
    def _extract_sections(self, text, potential_headers):

        sections = {}
        
        # If no headers found, return empty dict
        if not potential_headers:
            return sections
        
        # Extract content between headers
        for i, (section_name, start_pos, _) in enumerate(potential_headers):
            # Determine end position (next header or end of text)
            if i < len(potential_headers) - 1:
                end_pos = potential_headers[i + 1][1]
            else:
                end_pos = len(text)
            
            # Extract section content
            section_content = text[start_pos:end_pos].strip()
            
            # Remove the header line from content
            section_content = re.sub(r'^.*?\n', '', section_content, count=1).strip()
            
            # Add to sections dict, merging with existing content if needed
            if section_name in sections:
                sections[section_name] += '\n\n' + section_content
            else:
                sections[section_name] = section_content
        
        return sections
    
    def _post_process_sections(self, sections, original_text):

        # If no sections were detected, try a fallback approach
        if not sections:
            return self._fallback_section_detection(original_text)
        
        # Check for missing key sections and try to extract them
        if 'Skills' not in sections:
            skills_section = self._extract_skills_section(original_text)
            if skills_section:
                sections['Skills'] = skills_section
        
        # Clean up section content
        for section_name, content in sections.items():
            # Remove any remaining header-like text from beginning
            content = re.sub(r'^.*?:\s*', '', content)
            sections[section_name] = content.strip()
        
        return sections
    
    def _fallback_section_detection(self, text):

        sections = {}
        
        # Try to identify sections based on formatting patterns first
        lines = text.split('\n')
        current_section = None
        current_content = []
        
        # First pass: look for clear section headers
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
            
            # Enhanced header detection
            is_header = False
            
            # Standard header formats (all caps, title case, ends with colon)
            if (line.isupper() or line.istitle() or line.endswith(':')) and len(line) < 30:
                is_header = True
            
            # Check for lines that are followed by bullet points or indented text
            elif len(line) < 30 and i < len(lines) - 1:
                next_line = lines[i+1].strip() if i+1 < len(lines) else ''
                if next_line.startswith(('•', '-', '*', '\t')) or (next_line and next_line[0].isspace()):
                    is_header = True
            
            # Check for centered text (potential header)
            elif len(line) < 30 and i > 0 and i < len(lines) - 1:
                prev_line = lines[i-1].strip()
                next_line = lines[i+1].strip()
                if (not prev_line or len(prev_line) < len(line)) and (not next_line or len(next_line) < len(line)):
                    is_header = True
            
            if is_header:
                # Save previous section if exists
                if current_section and current_content:
                    sections[current_section] = '\n'.join(current_content)
                
                # Start new section with improved section type guessing
                current_section = self._guess_section_type(line)
                current_content = []
            elif current_section:
                current_content.append(line)
        
        # Add the last section
        if current_section and current_content:
            sections[current_section] = '\n'.join(current_content)
        
        # If formatting-based approach didn't work well, use NLP approach
        if not sections or len(sections) < 2:
            # Use NLP to identify potential sections
            doc = self.nlp(text)
            
            # Look for skill-related keywords
            skill_keywords = ['skills', 'technologies', 'tools', 'languages', 'frameworks']
            skill_sentences = [sent.text for sent in doc.sents 
                              if any(keyword in sent.text.lower() for keyword in skill_keywords)]
            
            if skill_sentences:
                # Extract a few sentences around skill mentions as the Skills section
                skills_text = ' '.join(skill_sentences)
                sections['Skills'] = skills_text
            
            # Look for education-related keywords
            edu_keywords = ['degree', 'university', 'college', 'bachelor', 'master', 'phd', 'diploma']
            edu_sentences = [sent.text for sent in doc.sents 
                            if any(keyword in sent.text.lower() for keyword in edu_keywords)]
            
            if edu_sentences:
                sections['Education'] = ' '.join(edu_sentences)
            
            # Look for experience-related keywords
            exp_keywords = ['experience', 'work', 'job', 'position', 'role', 'company', 'employer']
            exp_sentences = [sent.text for sent in doc.sents 
                            if any(keyword in sent.text.lower() for keyword in exp_keywords)]
            
            if exp_sentences:
                sections['Work Experience'] = ' '.join(exp_sentences)
            
            # Look for project-related keywords
            proj_keywords = ['project', 'developed', 'created', 'built', 'implemented', 'designed', 'github']
            proj_sentences = [sent.text for sent in doc.sents 
                            if any(keyword in sent.text.lower() for keyword in proj_keywords)]
            
            if proj_sentences:
                sections['Projects'] = ' '.join(proj_sentences)
        
        return sections
    
    def _extract_skills_section(self, text):

        # Look for common skills section patterns
        skills_patterns = [
            r'(?i)skills[:\s]*(.*?)(?:\n\n|\Z)',
            r'(?i)technical skills[:\s]*(.*?)(?:\n\n|\Z)',
            r'(?i)technologies[:\s]*(.*?)(?:\n\n|\Z)'
        ]
        
        for pattern in skills_patterns:
            match = re.search(pattern, text, re.DOTALL)
            if match:
                return match.group(1).strip()
        
        return ""
    
    def save_sections(self, sections, output_path):

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(sections, f, indent=2)
    
    def load_sections(self, input_path):

        with open(input_path, 'r', encoding='utf-8') as f:
            return json.load(f)
            
    def analyze_structure(self, sections):

        # Define expected sections and their importance (weight)
        expected_sections = {
            'Summary': 0.10,
            'Education': 0.15,
            'Work Experience': 0.25,
            'Skills': 0.20,
            'Projects': 0.15,
            'Certifications': 0.05,
            'Languages': 0.05,
            'Interests': 0.05
        }
        
        # Define minimum content length for each section (in characters)
        min_section_length = {
            'Summary': 100,
            'Education': 100,
            'Work Experience': 200,
            'Skills': 100,
            'Projects': 150,
            'Certifications': 50,
            'Languages': 30,
            'Interests': 30
        }
        
        # Initialize results
        missing_sections = []
        sparse_sections = []
        section_scores = {}
        
        # Calculate base score for each section
        total_weight = 0
        total_score = 0
        
        # Evaluate each expected section
        for section_name, weight in expected_sections.items():
            if section_name not in sections:
                missing_sections.append(section_name)
                section_scores[section_name] = 0
            else:
                content = sections[section_name]
                content_length = len(content)
                
                # Check if section is sparse
                if content_length < min_section_length.get(section_name, 50):
                    sparse_sections.append(section_name)
                    # Partial score based on content length
                    section_score = (content_length / min_section_length.get(section_name, 50)) * 100
                else:
                    # Full score for adequate content
                    section_score = 100
                
                # Apply weight to section score
                section_scores[section_name] = section_score
                total_score += section_score * weight
                
            total_weight += weight
        
        # Normalize total score if we have weights
        if total_weight > 0:
            structure_score = total_score / total_weight
        else:
            structure_score = 0
        
        # Check for unexpected but valuable sections
        for section_name in sections:
            if section_name not in expected_sections and len(sections[section_name]) > 100:
                # Add a small bonus for additional valuable sections
                structure_score += 2
        
        # Cap the score at 100
        structure_score = min(structure_score, 100)
        
        return {
            'structure_score': structure_score,
            'missing_sections': missing_sections,
            'sparse_sections': sparse_sections,
            'section_scores': section_scores
        }