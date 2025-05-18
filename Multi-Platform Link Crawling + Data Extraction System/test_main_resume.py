import asyncio
from hr_explainer import HRExplainabilityLayer

async def analyze_resume():
    try:
        print("Starting resume analysis...")
        explainer = HRExplainabilityLayer()
        
        # Replace with your resume path
        pdf_path = "aparna.pdf"
        
        print(f"\nAnalyzing resume: {pdf_path}")
        analysis = await explainer.analyze_candidate(pdf_path, "Aparna Mondal")
        
        print("\n" + "="*50)
        print("RESUME ANALYSIS RESULTS")
        print("="*50)
        
        # Print credibility scores
        cred_results = analysis['credibility_results']
        print("\nCredibility Verification:")
        print(f"Overall Score: {cred_results['overall_credibility_score']}%")
        
        # Print component verifications
        for key, value in cred_results.items():
            if key not in ['overall_credibility_score', 'verification_timestamp']:
                if isinstance(value, list):
                    print(f"\n{key.replace('_', ' ').title()}:")
                    for v in value:
                        print(f"- {v.details}")
                else:
                    print(f"\n{key.replace('_', ' ').title()}:")
                    print(f"- {value.details}")
        
        # Print detailed report
        print("\n" + "="*50)
        print("DETAILED HR REPORT")
        print("="*50)
        print(analysis['report'])
        
    except FileNotFoundError:
        print(f"Error: Resume file not found. Please ensure 'aparna.pdf' is in the directory.")
    except Exception as e:
        print(f"Error analyzing resume: {str(e)}")
        import traceback
        print("\nFull error details:")
        print(traceback.format_exc())

if __name__ == "__main__":
    asyncio.run(analyze_resume())