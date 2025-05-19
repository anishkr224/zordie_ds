import asyncio
from credibility_engine import CredibilityEngine
from datetime import datetime

async def check_resume_verification():
    print("\n=== Resume Verification Checker ===")
    print("Checking credentials and generating report...")
    print("=" * 40)

    engine = CredibilityEngine()
    
    # Test data - replace with your actual URLs
    test_data = {
        'github_url': 'https://github.com/YourGithubUsername',
        'linkedin_url': 'https://linkedin.com/in/YourLinkedInUsername',
        'leetcode_url': 'https://leetcode.com/YourLeetCodeUsername',
        'certificates': [
            {
                'name': 'Microsoft Azure Fundamentals',
                'verification_url': 'https://learn.microsoft.com/en-us/users/validate-certification/MS-900-123456'
            },
            {
                'name': 'AWS Cloud Practitioner',
                'verification_url': 'https://aws.amazon.com/verification/AWS-12-123456'
            }
        ]
    }

    try:
        # Get verification results
        results = await engine.verify_all_credentials(test_data)
        
        # Print results in a readable format
        print("\n🔍 Verification Results:")
        print("-" * 40)
        
        # GitHub Verification
        github_result = results['github_verification']
        print("\n📂 GitHub Profile:")
        print(f"Status: {'✅ Verified' if github_result.is_valid else '❌ Not Verified'}")
        print(f"Details: {github_result.details}")
        
        # LinkedIn Verification
        linkedin_result = results['linkedin_verification']
        print("\n💼 LinkedIn Profile:")
        print(f"Status: {'✅ Verified' if linkedin_result.is_valid else '❌ Not Verified'}")
        print(f"Details: {linkedin_result.details}")
        
        # LeetCode Verification
        leetcode_result = results['leetcode_verification']
        print("\n💻 LeetCode Profile:")
        print(f"Status: {'✅ Verified' if leetcode_result.is_valid else '❌ Not Verified'}")
        print(f"Details: {leetcode_result.details}")
        
        # Certificates Verification
        print("\n📜 Certificates:")
        for cert in results['certificate_verifications']:
            print(f"Status: {'✅ Verified' if cert.is_valid else '❌ Not Verified'}")
            print(f"Details: {cert.details}")
        
        # Overall Score
        print("\n📊 Overall Credibility Score:")
        print(f"Score: {results['overall_credibility_score']}%")
        print(f"Last Updated: {datetime.fromisoformat(results['verification_timestamp']).strftime('%Y-%m-%d %H:%M:%S')}")

    except Exception as e:
        print(f"\n❌ Error during verification: {str(e)}")

if __name__ == "__main__":
    asyncio.run(check_resume_verification())