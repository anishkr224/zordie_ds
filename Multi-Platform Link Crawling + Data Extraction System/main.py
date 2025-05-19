import os
import json
from typing import Dict, Any, List
from resume_parser import ResumeParser
from web_scraper import WebScraper
from scorer import ResumeScorer
from explainer import ScoreExplainer
from hr_explainer import HRExplainabilityLayer
import asyncio
import dataclasses

class ResumeAnalyzer:
    def __init__(self):
        print("Initializing ResumeAnalyzer...")
        self.resume_parser = ResumeParser()
        self.web_scraper = WebScraper()
        self.scorer = ResumeScorer()
        self.explainer = ScoreExplainer()
        self.hr_explainer = HRExplainabilityLayer()

    async def analyze_resume(self, file_path: str) -> Dict[str, Any]:
        """Main method to analyze a resume and its associated profiles."""
        print(f"\nStarting analysis of: {file_path}")
        
        # Parse resume
        print("Parsing resume...")
        if file_path.lower().endswith('.pdf'):
            resume_data = self.resume_parser.parse_pdf(file_path)
        elif file_path.lower().endswith('.doc') or file_path.lower().endswith('.docx'):
            resume_data = self.resume_parser.parse_doc(file_path)
        else:
            raise ValueError("Unsupported file format. Please provide a PDF or DOC/DOCX file.")
        
        print(f"Found {len(resume_data['urls'])} URLs in resume: {resume_data['urls']}")

        # Scrape profile data
        print("\nStarting profile scraping...")
        profile_data = []
        for url in resume_data["urls"]:
            try:
                print(f"\nScraping URL: {url}")
                profile_info = await self.web_scraper.scrape_url(url)
                if "error" not in profile_info:
                    profile_data.append(profile_info)
                    print(f"Successfully scraped {url}")
                else:
                    print(f"Error scraping {url}: {profile_info.get('error')}")
            except Exception as e:
                print(f"Exception while scraping {url}: {str(e)}")

        print(f"\nSuccessfully scraped {len(profile_data)} profiles")

        # Generate scores and recommendations
        print("\nGenerating scores and recommendations...")
        analysis_result = self.scorer.score_resume(resume_data, profile_data)

        # Generate explanations
        print("\nGenerating explanations...")
        explanations = self.explainer.generate_explanations(analysis_result)
        analysis_result["explanations"] = explanations

        # Generate HR analysis
        print("\nGenerating HR analysis...")
        hr_analysis = await self.hr_explainer.analyze_candidate(file_path, "Candidate")
        analysis_result["hr_analysis"] = hr_analysis

        # Add raw data for reference
        analysis_result["raw_data"] = {
            "resume_data": resume_data,
            "profile_data": profile_data
        }

        return analysis_result

def dataclass_to_dict(obj):
    if dataclasses.is_dataclass(obj):
        return {k: dataclass_to_dict(v) for k, v in dataclasses.asdict(obj).items()}
    elif isinstance(obj, dict):
        return {k: dataclass_to_dict(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [dataclass_to_dict(v) for v in obj]
    else:
        return obj

async def main():
    print("Starting Resume Analysis System...")
    # Example usage
    analyzer = ResumeAnalyzer()
    
    # Use the specific resume path
    file_path = "Mrinal.pdf"
    print(f"Using resume file: {file_path}")
    
    if not os.path.exists(file_path):
        print(f"Error: File not found at {file_path}")
        return
    
    try:
        # Analyze the resume
        print("\nBeginning resume analysis...")
        result = await analyzer.analyze_resume(file_path)
        
        # Print the results
        print("\nResume Analysis Results:")
        print("=" * 50)
        
        # Print HR Analysis
        if 'hr_analysis' in result:
            print("\nHR ANALYSIS REPORT")
            print("=" * 50)
            print(result['hr_analysis']['report'])
        
        # Print regular analysis results
        print(f"\nOverall Score: {result['overall_score']}/100")
        print("\nOverall Explanation:")
        print(result['explanations']['overall_explanation'])
        
        print("\nResume Score:")
        print(f"Score: {result['resume_score']['score']}/100")
        print("\nResume Explanation:")
        print(result['explanations']['resume_explanation'])
        if result['resume_score']['deductions']:
            print("Issues found:")
            for deduction in result['resume_score']['deductions']:
                print(f"- {deduction}")
        
        print("\nPlatform Scores:")
        for platform, score_data in result['platform_scores'].items():
            print(f"\n{platform}:")
            print(f"Score: {score_data['score']}/100")
            print("\nPlatform Explanation:")
            print(result['explanations']['platform_explanations'][platform])
            if score_data['deductions']:
                print("Issues found:")
                for deduction in score_data['deductions']:
                    print(f"- {deduction}")
        
        if result['trustworthiness_flags']:
            print("\nTrustworthiness Flags:")
            for flag in result['trustworthiness_flags']:
                print(f"- {flag}")
            print("\nTrust Explanation:")
            print(result['explanations']['trust_explanation'])
        
        print("\nRecommendations:")
        for recommendation in result['recommendations']:
            print(f"- {recommendation}")
        
        # Save detailed results to a JSON file
        output_file = "resume_analysis_result.json"
        with open(output_file, 'w') as f:
            json.dump(dataclass_to_dict(result), f, indent=2)
        print(f"\nDetailed results have been saved to {output_file}")
        
    except Exception as e:
        print(f"Error analyzing resume: {str(e)}")
        import traceback
        print("\nFull error traceback:")
        print(traceback.format_exc())

if __name__ == "__main__":
    asyncio.run(main()) 