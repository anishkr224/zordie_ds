# Resume Intelligence System

A comprehensive system for analyzing resumes against job descriptions, providing insights into section structure, skill alignment, and project validation.

## Components

### A. Section & Structure Detector
Automatically identifies and extracts standard résumé sections (Education, Work Experience, Projects, Certifications, Skills, Summary, Links) and flags any that are missing or too sparse.

**Key Techniques & Tools:**
- Document parsing: PyMuPDF for PDF/DOCX ingestion
- Section detection: spaCy (rule-based patterns + custom NER) combined with Regex heuristics
- Deep models: Transformer encoders (e.g., fine-tuned BERT) to spot non-standard headings

### B. Skill-to-JD Semantic Matcher
Measures how well the candidate's listed skills align with a target job description, yielding an overall "alignment %" and pinpointing missing critical competencies.

**Key Techniques & Tools:**
- Embeddings: SBERT or BERT to encode both skill lists and job-description text
- Similarity scoring: Cosine similarity over embedding vectors to compute alignment scores
- Visualization: Optionally produce a gap-analysis heatmap or ranked list of unmet skills

### C. Project Validation System
Verifies that each project entry truly reflects the claimed skillset, scoring projects on both technical depth and relevance.

**Key Techniques & Tools:**
- NLP analysis: spaCy + custom dependency parses to extract key action-verb–technology pairs
- Relevance scoring: Compare extracted keywords against the candidate's skills using TF-IDF or embedding overlaps
- Flagging: Mark "unrelated" or "superficial" projects for human review

## Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Download required spaCy model
python -m spacy download en_core_web_lg
```

## Usage

```bash
# Analyze a resume against a job description
python analyze_resume.py path/to/resume.pdf path/to/job_description.txt
```

## Project Structure

```
ResumeIntelligenceSystem/
├── analyze_resume.py       # Main analysis script
├── requirements.txt        # Dependencies
├── README.md               # This file
├── resume_intelligence/    # Core modules
│   ├── section_detector.py # Section detection module
│   ├── skill_matcher.py    # Skill matching module
│   ├── project_validator.py# Project validation module
│   ├── visualizer.py       # Visualization utilities
│   └── utils/              # Utility modules
│       └── document_parser.py # Document parsing utilities
├── samples/                # Sample resumes and job descriptions
└── output/                 # Output directory for results
```

## Output Files

The system generates the following output files in the specified output directory:

- `sections.json`: Detected resume sections and their content
- `skill_alignment.json`: Skill alignment scores and missing skills
- `project_validation.json`: Project validation scores and flagged projects
- `resume_analysis_report.md`: Comprehensive analysis report
- `skill_alignment.png`: Visualization of skill alignment
- `project_validation.png`: Visualization of project validation