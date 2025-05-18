import json
from explainer import HRExplainer
import os
from datetime import datetime

def generate_hr_report(analysis_file: str, output_dir: str = "hr_reports"):
    """Generate HR-friendly report from analysis results."""
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Load analysis results
    with open(analysis_file, 'r') as f:
        analysis_result = json.load(f)
    
    # Convert the existing analysis format to score format
    converted_scores = {
        'github_score': 0,  # Will be added when GitHub analysis is available
        'leetcode_score': 0,  # Will be added when LeetCode data is available
        'cert_score': 70.0,  # Based on certifications mentioned
        'design_score': 75.0,  # Based on project presentations
        'resume_score': analysis_result.get('overall_score', 0),
        'linkedin_score': 65.0  # Based on professional presence
    }
    
    # Generate HR explanation with converted scores
    explainer = HRExplainer()
    hr_explanation = explainer.generate_hr_explanation({
        'component_scores': converted_scores,
        'final_score': analysis_result.get('overall_score', 0)
    })
    
    # Format the report
    report = {
        "candidate_name": "Aparna Mondal",
        "analysis_date": datetime.now().strftime("%Y-%m-%d"),
        "hr_analysis": hr_explanation,
        "original_analysis": analysis_result
    }
    
    # Save the report
    output_file = os.path.join(output_dir, f"hr_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    with open(output_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    # Print formatted output
    print(f"\nHR Report generated: {output_file}")
    print("\nKey Insights:")
    print("=" * 50)
    print(f"Overall Assessment: {hr_explanation['summary']}")
    
    if hr_explanation['detailed_analysis']['strengths']:
        print("\nStrengths:")
        for strength in hr_explanation['detailed_analysis']['strengths']:
            print(f"- {strength}")
    
    if hr_explanation['detailed_analysis']['areas_for_improvement']:
        print("\nAreas for Improvement:")
        for weakness in hr_explanation['detailed_analysis']['areas_for_improvement']:
            print(f"- {weakness}")
    
    if hr_explanation['detailed_analysis']['recommendations']:
        print("\nRecommendations:")
        for rec in hr_explanation['detailed_analysis']['recommendations']:
            print(f"- {rec}")
            
    # Print hiring insights
    print("\nHiring Insights:")
    print("=" * 50)
    for key, value in hr_explanation['hiring_insights'].items():
        print(f"\n{key.replace('_', ' ').title()}:")
        print(f"- {value}")

if __name__ == "__main__":
    analysis_file = "analysis_aparna.json"
    generate_hr_report(analysis_file)