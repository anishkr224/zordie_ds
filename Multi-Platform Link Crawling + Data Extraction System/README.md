# Resume Analysis System

This system analyzes resumes (PDF or DOC/DOCX) and associated professional profiles to provide comprehensive feedback and scoring. It extracts URLs from resumes, visits associated profiles (GitHub, LinkedIn, etc.), and generates scores and recommendations based on various metrics.

## Features

- Resume parsing (PDF and DOC/DOCX support)
- URL extraction from resumes
- Automated web scraping of professional profiles
- Platform-specific metrics analysis:
  - GitHub: repositories, stars, forks, commit activity
  - LinkedIn: profile completeness, endorsements
  - LeetCode: solved problems, acceptance rate
  - Figma: project metrics
- Comprehensive scoring system
- Trustworthiness checks
- Detailed recommendations
- JSON output for further processing

## Installation

1. Clone this repository:
```bash
git clone <repository-url>
cd resume-analysis-system
```

2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

3. Install Playwright browsers:
```bash
playwright install
```

## Usage

1. Run the main script:
```bash
python main.py
```

2. When prompted, enter the path to your resume file (PDF or DOC/DOCX).

3. The system will:
   - Parse your resume
   - Extract URLs
   - Visit associated profiles
   - Generate scores and recommendations
   - Save detailed results to `resume_analysis_result.json`

## Output

The system generates both console output and a detailed JSON file containing:

- Overall score
- Resume format score
- Platform-specific scores
- Trustworthiness flags
- Recommendations for improvement
- Raw data from resume parsing and profile scraping

## Supported Platforms

- GitHub
- LinkedIn
- LeetCode
- Figma

## Notes

- LinkedIn scraping may be limited due to authentication requirements
- Some websites may block automated access
- The system requires an active internet connection
- Processing time depends on the number of URLs and website response times

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details. 