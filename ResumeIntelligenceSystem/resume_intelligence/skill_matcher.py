"""
Skill-to-JD Semantic Matcher for Resume Intelligence System

This module measures how well a candidate's listed skills align with a target job description,
yielding an overall "alignment %" and pinpointing missing critical competencies.
"""

import json
from pathlib import Path
import re

import numpy as np
import matplotlib.pyplot as plt
import spacy
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer


class SkillMatcher:
    
    def __init__(self, model_name="all-MiniLM-L6-v2"):

        try:
            self.model = SentenceTransformer(model_name)
        except Exception as e:
            print(f"Warning: Could not load model {model_name}. Using TF-IDF instead. Error: {e}")
            self.model = None
        
        self.tfidf = TfidfVectorizer(stop_words='english')
        
        try:
            self.nlp = spacy.load("en_core_web_lg")
        except OSError:
            print("Warning: en_core_web_lg not found. Using en_core_web_sm instead.")
            try:
                self.nlp = spacy.load("en_core_web_sm")
            except OSError:
                print("Warning: No spaCy models found. Downloading en_core_web_sm...")
                spacy.cli.download("en_core_web_sm")
                self.nlp = spacy.load("en_core_web_sm")
    
    def extract_skills(self, text):

        # Split by common delimiters and clean up
        skills = re.split(r'[,;•\n]', text)
        skills = [skill.strip() for skill in skills if skill.strip()]
        
        # Process skills to ensure they're not truncated
        processed_skills = []
        for skill in skills:
            # Check if skill appears to be truncated (ends with incomplete word)
            if len(skill) > 3 and not re.search(r'\w+$', skill):
                # Try to find the complete skill in the original text
                pattern = re.escape(skill) + r'\w*'
                match = re.search(pattern, text)
                if match:
                    processed_skills.append(match.group(0))
                else:
                    processed_skills.append(skill)
            else:
                processed_skills.append(skill)
        
        return processed_skills
    
    def extract_jd_requirements(self, jd_text):

        # Look for requirements section
        requirements_section = ""
        
        # Try to find requirements section using common headers
        req_patterns = [
            r'(?i)requirements\s*:([\s\S]*?)(?:\n\n|\Z)',
            r'(?i)qualifications\s*:([\s\S]*?)(?:\n\n|\Z)',
            r'(?i)skills\s*required\s*:([\s\S]*?)(?:\n\n|\Z)',
            r'(?i)what\s*you\'ll\s*need\s*:([\s\S]*?)(?:\n\n|\Z)'
        ]
        
        for pattern in req_patterns:
            match = re.search(pattern, jd_text)
            if match:
                requirements_section = match.group(1).strip()
                break
        
        # If no requirements section found, use the entire JD
        if not requirements_section:
            requirements_section = jd_text
        
        # Extract bullet points or sentences
        requirements = []
        
        # Try to extract bullet points
        bullet_points = re.findall(r'•\s*([^•\n]+)', requirements_section)
        if bullet_points:
            requirements.extend(bullet_points)
        
        # If no bullet points, split by newlines
        if not requirements:
            lines = requirements_section.split('\n')
            requirements = [line.strip() for line in lines if line.strip()]
        
        # Clean up requirements
        requirements = [req.strip() for req in requirements if req.strip()]
        
        return requirements
    
    def compute_alignment(self, skills_text, jd_text, sections=None):

        # Ensure skills_text is not truncated
        if skills_text and len(skills_text) < 20 and skills_text.endswith(('Scie', 'Sci', 'S')):
            # Try to find the complete skill section in sections if available
            if sections and 'Skills' in sections:
                skills_text = sections['Skills']
        # Extract skills and requirements
        candidate_skills = self.extract_skills(skills_text)
        jd_requirements = self.extract_jd_requirements(jd_text)
        
        if not candidate_skills or not jd_requirements:
            return {
                "overall_alignment": 0.0,
                "skill_scores": {},
                "missing_skills": [],
                "candidate_skills": candidate_skills,
                "jd_requirements": jd_requirements,
                "section_scores": {}
            }
        
        # Compute base alignment using embeddings if model is available
        if self.model:
            base_results = self._compute_alignment_with_embeddings(candidate_skills, jd_requirements)
        else:
            base_results = self._compute_alignment_with_tfidf(candidate_skills, jd_requirements)
        
        # Calculate weighted section scores if sections are provided
        if sections:
            section_scores = self._calculate_section_scores(sections, jd_text)
            base_results["section_scores"] = section_scores
            base_results["overall_alignment"] = section_scores["total_score"]
        
        return base_results
    
    def _compute_alignment_with_embeddings(self, candidate_skills, jd_requirements):

        # Encode skills and requirements
        skill_embeddings = self.model.encode(candidate_skills)
        req_embeddings = self.model.encode(jd_requirements)
        
        # Compute similarity matrix
        similarity_matrix = cosine_similarity(skill_embeddings, req_embeddings)
        
        # For each requirement, find the best matching skill
        req_scores = {}
        for i, req in enumerate(jd_requirements):
            best_score = np.max(similarity_matrix[:, i]) if similarity_matrix.shape[0] > 0 else 0
            req_scores[req] = best_score
        
        # For each skill, find the best matching requirement
        skill_scores = {}
        for i, skill in enumerate(candidate_skills):
            best_score = np.max(similarity_matrix[i, :]) if similarity_matrix.shape[1] > 0 else 0
            skill_scores[skill] = best_score
        
        # Identify missing skills (requirements with low match scores)
        threshold = 0.45  # Slightly lower threshold to be more lenient
        missing_skills = [req for req, score in req_scores.items() if score < threshold]
        
        # Calculate overall alignment score
        overall_alignment = np.mean(list(req_scores.values())) * 100 if req_scores else 0
        
        return {
            "overall_alignment": overall_alignment,
            "skill_scores": skill_scores,
            "requirement_scores": req_scores,
            "missing_skills": missing_skills,
            "candidate_skills": candidate_skills,
            "jd_requirements": jd_requirements
        }
    
    def _compute_alignment_with_tfidf(self, candidate_skills, jd_requirements):

        # Combine skills and requirements for TF-IDF
        all_texts = candidate_skills + jd_requirements
        
        # Compute TF-IDF matrix
        tfidf_matrix = self.tfidf.fit_transform(all_texts)
        
        # Split matrix back into skills and requirements
        skill_vectors = tfidf_matrix[:len(candidate_skills)]
        req_vectors = tfidf_matrix[len(candidate_skills):]
        
        # Compute similarity matrix
        similarity_matrix = cosine_similarity(skill_vectors, req_vectors)
        
        # For each requirement, find the best matching skill
        req_scores = {}
        for i, req in enumerate(jd_requirements):
            best_score = np.max(similarity_matrix[:, i]) if similarity_matrix.shape[0] > 0 else 0
            req_scores[req] = best_score
        
        # For each skill, find the best matching requirement
        skill_scores = {}
        for i, skill in enumerate(candidate_skills):
            best_score = np.max(similarity_matrix[i, :]) if similarity_matrix.shape[1] > 0 else 0
            skill_scores[skill] = best_score
        
        # Identify missing skills (requirements with low match scores)
        threshold = 0.3  # Lower threshold for TF-IDF
        missing_skills = [req for req, score in req_scores.items() if score < threshold]
        
        # Calculate overall alignment score
        overall_alignment = np.mean(list(req_scores.values())) * 100 if req_scores else 0
        
        return {
            "overall_alignment": overall_alignment,
            "skill_scores": skill_scores,
            "requirement_scores": req_scores,
            "missing_skills": missing_skills,
            "candidate_skills": candidate_skills,
            "jd_requirements": jd_requirements
        }
    
    def save_results(self, results, output_path):

        # Convert NumPy values to native Python types before serialization
        def convert_numpy_values(obj):
            if isinstance(obj, dict):
                return {k: convert_numpy_values(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_numpy_values(item) for item in obj]
            elif isinstance(obj, np.integer):
                return int(obj)
            elif isinstance(obj, np.floating):
                return float(obj)
            elif isinstance(obj, np.ndarray):
                return convert_numpy_values(obj.tolist())
            else:
                return obj
                
        # Apply conversion to results
        serializable_results = convert_numpy_values(results)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(serializable_results, f, indent=2)
    
    def _calculate_section_scores(self, sections, jd_text):
        """
        Scoring criteria:
        - Projects: 0-35 points (increased weight for project relevance)
        - Work Experience: 0-30 points
        - Skills: 0-20 points
        - Education: 0-10 points
        - Certifications: 0-5 points
        - Summary: 0-5 points
        """
        section_scores = {}
        jd_doc = self.nlp(jd_text) if self.model else None
        
        # Initialize scores for each section
        section_scores["Projects"] = 0
        section_scores["Work Experience"] = 0
        section_scores["Skills"] = 0
        section_scores["Education"] = 0
        section_scores["Certifications"] = 0
        section_scores["Summary"] = 0
        
        # Calculate Projects score (0-30)
        if "Projects" in sections and sections["Projects"]:
            projects_text = sections["Projects"]
            projects_doc = self.nlp(projects_text) if self.model else None
            
            if self.model:
                # Use embeddings for semantic similarity
                similarity = projects_doc.similarity(jd_doc)
                # Scale to 0-35 range (increased weight for projects)
                section_scores["Projects"] = min(35, similarity * 35)
        else:
            # Use TF-IDF for keyword matching
            project_keywords = self.extract_skills(projects_text)
            jd_keywords = self.extract_jd_requirements(jd_text)
            
            if project_keywords and jd_keywords:
                # Calculate overlap between project keywords and JD keywords
                common_keywords = set(k.lower() for k in project_keywords) & set(k.lower() for k in jd_keywords)
                overlap_ratio = len(common_keywords) / len(jd_keywords) if jd_keywords else 0
                section_scores["Projects"] = min(35, overlap_ratio * 35)
        
        # Calculate Work Experience score (0-30)
        if "Work Experience" in sections and sections["Work Experience"]:
            experience_text = sections["Work Experience"]
            experience_doc = self.nlp(experience_text) if self.model else None
            
            if self.model:
                similarity = experience_doc.similarity(jd_doc)
                section_scores["Work Experience"] = min(30, similarity * 30)
            else:
                experience_keywords = self.extract_skills(experience_text)
                jd_keywords = self.extract_jd_requirements(jd_text)
                
                if experience_keywords and jd_keywords:
                    common_keywords = set(k.lower() for k in experience_keywords) & set(k.lower() for k in jd_keywords)
                    overlap_ratio = len(common_keywords) / len(jd_keywords) if jd_keywords else 0
                    section_scores["Work Experience"] = min(30, overlap_ratio * 30)
        
        # Calculate Skills score (0-20)
        if "Skills" in sections and sections["Skills"]:
            skills_text = sections["Skills"]
            skills_doc = self.nlp(skills_text) if self.model else None
            
            if self.model:
                similarity = skills_doc.similarity(jd_doc)
                section_scores["Skills"] = min(20, similarity * 20)
            else:
                candidate_skills = self.extract_skills(skills_text)
                jd_keywords = self.extract_jd_requirements(jd_text)
                
                if candidate_skills and jd_keywords:
                    common_keywords = set(k.lower() for k in candidate_skills) & set(k.lower() for k in jd_keywords)
                    overlap_ratio = len(common_keywords) / len(jd_keywords) if jd_keywords else 0
                    section_scores["Skills"] = min(20, overlap_ratio * 20)
        
        # Calculate Education score (0-10)
        if "Education" in sections and sections["Education"]:
            education_text = sections["Education"]
            education_doc = self.nlp(education_text) if self.model else None
            
            if self.model:
                similarity = education_doc.similarity(jd_doc)
                section_scores["Education"] = min(10, similarity * 10)
            else:
                education_keywords = self.extract_skills(education_text)
                jd_keywords = self.extract_jd_requirements(jd_text)
                
                if education_keywords and jd_keywords:
                    common_keywords = set(k.lower() for k in education_keywords) & set(k.lower() for k in jd_keywords)
                    overlap_ratio = len(common_keywords) / len(jd_keywords) if jd_keywords else 0
                    section_scores["Education"] = min(10, overlap_ratio * 10)
        
        # Calculate Certifications score (0-5)
        if "Certifications" in sections and sections["Certifications"]:
            certifications_text = sections["Certifications"]
            certifications_doc = self.nlp(certifications_text) if self.model else None
            
            if self.model:
                similarity = certifications_doc.similarity(jd_doc)
                section_scores["Certifications"] = min(5, similarity * 5)
            else:
                certification_keywords = self.extract_skills(certifications_text)
                jd_keywords = self.extract_jd_requirements(jd_text)
                
                if certification_keywords and jd_keywords:
                    common_keywords = set(k.lower() for k in certification_keywords) & set(k.lower() for k in jd_keywords)
                    overlap_ratio = len(common_keywords) / len(jd_keywords) if jd_keywords else 0
                    section_scores["Certifications"] = min(5, overlap_ratio * 5)
        
        # Calculate Summary score (0-5)
        if "Summary" in sections and sections["Summary"]:
            summary_text = sections["Summary"]
            summary_doc = self.nlp(summary_text) if self.model else None
            
            if self.model:
                similarity = summary_doc.similarity(jd_doc)
                section_scores["Summary"] = min(5, similarity * 5)
            else:
                summary_keywords = self.extract_skills(summary_text)
                jd_keywords = self.extract_jd_requirements(jd_text)
                
                if summary_keywords and jd_keywords:
                    common_keywords = set(k.lower() for k in summary_keywords) & set(k.lower() for k in jd_keywords)
                    overlap_ratio = len(common_keywords) / len(jd_keywords) if jd_keywords else 0
                    section_scores["Summary"] = min(5, overlap_ratio * 5)
        
        # Calculate total score (0-100)
        section_scores["total_score"] = (
            section_scores["Projects"] +
            section_scores["Work Experience"] +
            section_scores["Skills"] +
            section_scores["Education"] +
            section_scores["Certifications"] +
            section_scores["Summary"]
        )
        
        return section_scores
        
    def visualize_alignment(self, results, output_path):

        plt.figure(figsize=(12, 8))
        
        # Check if we have section scores
        if "section_scores" in results and results["section_scores"]:
            # Create a bar chart for section scores
            section_scores = results["section_scores"]
            sections = ["Projects", "Work Experience", "Skills", "Education", "Certifications", "Summary"]
            scores = [section_scores.get(section, 0) for section in sections]
            max_scores = [30, 30, 20, 10, 5, 5]  # Maximum possible scores for each section
            
            # Create a horizontal bar chart with section scores
            y_pos = np.arange(len(sections))
            plt.barh(y_pos, scores, align='center', alpha=0.7, color='skyblue')
            
            # Add max score reference lines
            for i, max_score in enumerate(max_scores):
                plt.plot([max_score, max_score], [i-0.4, i+0.4], 'r--', alpha=0.5)
            
            plt.yticks(y_pos, sections)
            plt.xlabel('Score')
            plt.title(f'Resume-JD Alignment (Overall: {results.get("overall_alignment", 0):.1f}/100)')
            
            # Add total score annotation
            plt.text(max(scores) + 5, len(sections)/2, 
                    f"Total: {section_scores.get('total_score', 0):.1f}/100", 
                    verticalalignment='center', fontsize=12)
        else:
            # Extract data for visualization (original implementation)
            skills = results.get("candidate_skills", [])
            requirements = results.get("jd_requirements", [])
            req_scores = results.get("requirement_scores", {})
            
            # Sort requirements by score
            sorted_reqs = sorted(req_scores.items(), key=lambda x: x[1])
            req_labels = [req[:50] + "..." if len(req) > 50 else req for req, _ in sorted_reqs]
            req_values = [score for _, score in sorted_reqs]
            
            # Create bar chart for requirement scores
            y_pos = np.arange(len(req_labels))
            plt.barh(y_pos, req_values, align='center', alpha=0.7, color='skyblue')
            plt.yticks(y_pos, req_labels)
            plt.xlabel('Match Score')
            plt.title(f'Job Requirements Match (Overall: {results.get("overall_alignment", 0):.1f}%)')
            
            # Add a line for the threshold
            plt.axvline(x=0.5, color='r', linestyle='--', alpha=0.7, label='Threshold')
            plt.legend()
        
        # Adjust layout and save
        plt.tight_layout()
        plt.savefig(output_path)
        plt.close()