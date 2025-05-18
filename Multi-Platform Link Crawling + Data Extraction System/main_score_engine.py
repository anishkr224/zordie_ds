import unittest
from score_engine import MultiPlatformScorer
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

class TestMultiPlatformScorer(unittest.TestCase):
    def setUp(self):
        self.scorer = MultiPlatformScorer(
            openai_key=os.getenv('OPENAI_API_KEY'),
            github_token=os.getenv('GITHUB_TOKEN')
        )

    def test_final_score_calculation(self):
        test_data = {
            'github_analysis': {'average_technical_score': 85.0},
            'leetcode_data': {'total_problems_solved': 200, 'contest_rating': 1500, 'hard_problems_solved': 30},
            'certifications': [{'level': 'professional'}, {'level': 'associate'}],
            'design_data': {'total_likes': 500, 'followers': 200, 'total_projects': 15},
            'resume_score': {'score': 90.0},
            'linkedin_data': {'connections': 400, 'endorsements': 50, 'posts_last_year': 25}
        }

        result = self.scorer.calculate_final_score(test_data)
        
        # Print detailed results
        print("\nDetailed Score Breakdown:")
        print("=" * 50)
        print(f"Final Score: {result['final_score']:.2f}/100")
        print("\nComponent Scores:")
        for platform, score in result['component_scores'].items():
            print(f"{platform}: {score:.2f}/100")
        
        print("\nWeights Used:")
        for platform, weight in result['weights'].items():
            print(f"{platform}: {weight*100}%")

        # Original assertions
        self.assertIsNotNone(result['final_score'])
        self.assertGreaterEqual(result['final_score'], 0)
        self.assertLessEqual(result['final_score'], 100)

def main():
    # Run single test with output
    test = TestMultiPlatformScorer()
    test.setUp()
    test.test_final_score_calculation()

if __name__ == '__main__':
    main()