import os
import json
from dotenv import load_dotenv
from github_analyzer import GitHubAnalyzer

def test_github_analysis():
    # Load environment variables
    load_dotenv()
    
    # Initialize analyzer with API key
    analyzer = GitHubAnalyzer(os.getenv('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'))
    
    # Test repository URL - replace with actual repo
    test_repo = test_repo ="https://github.com/tensorflow/tensorflow"

    
    try:
        # Analyze repository
        result = analyzer.analyze_repository(test_repo)
        
        # Print formatted results
        print("\nGitHub Analysis Results:")
        print("=" * 50)
        print(f"Technical Score: {result['technical_score']:.2f}/100")
        print(f"Code Quality: {result['code_quality_grade']}")
        print(f"Originality: {result['originality_percentage']:.1f}%")
        
        # Save results to file
        output_file = "github_analysis_results.json"
        with open(output_file, 'w') as f:
            json.dump(result, f, indent=2)
        print(f"\nDetailed results saved to: {output_file}")
        
    except Exception as e:
        print(f"Error analyzing repository: {str(e)}")

if __name__ == "__main__":
    test_github_analysis()