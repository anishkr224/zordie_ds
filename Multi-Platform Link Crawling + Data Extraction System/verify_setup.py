import os
from dotenv import load_dotenv
import openai
import requests
import git
import tempfile
import shutil

def configure_git():
    """Configure Git settings to avoid warnings."""
    os.environ["GIT_PYTHON_REFRESH"] = "quiet"
    git_executable = r"C:\Program Files\Git\cmd\git.exe"
    
    if os.path.exists(git_executable):
        git.refresh(git_executable)
        return True
    return False

def verify_setup():
    """Verify all dependencies and API keys are working."""
    print("Verifying setup...")
    
    # Configure Git first
    if not configure_git():
        print("❌ Git executable not found at expected location")
        return False
    
    # Load environment variables
    load_dotenv()
    
    # Check environment variables
    github_token = os.getenv('GITHUB_TOKEN')
    openai_key = os.getenv('OPENAI_API_KEY')
    
    issues = []
    
    # Verify GitHub token
    if not github_token:
        issues.append("GitHub token not found in .env file")
    else:
        try:
            headers = {'Authorization': f'token {github_token}'}
            response = requests.get('https://api.github.com/user', headers=headers)
            if response.status_code != 200:
                issues.append("GitHub token is invalid")
            else:
                print("✓ GitHub token verified")
        except Exception as e:
            issues.append(f"Error testing GitHub token: {str(e)}")
    
    # Verify OpenAI key
    if not openai_key:
        issues.append("OpenAI API key not found in .env file")
    else:
        try:
            openai.api_key = openai_key
            # Test API call
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "Test"}],
                max_tokens=5
            )
            print("✓ OpenAI API key verified")
        except Exception as e:
            issues.append(f"Error testing OpenAI API key: {str(e)}")
    
    # Verify Git installation
    try:
        test_dir = tempfile.mkdtemp()
        test_repo = "https://github.com/octocat/Hello-World"
        git.Repo.clone_from(test_repo, test_dir)
        shutil.rmtree(test_dir)
        print("✓ Git installation verified")
    except Exception as e:
        issues.append(f"Git installation issue: {str(e)}")
    
    # Print results
    if issues:
        print("\nIssues found:")
        for issue in issues:
            print(f"❌ {issue}")
        return False
    else:
        print("\nAll dependencies and API keys verified successfully! ✓")
        return True

if __name__ == "__main__":
    verify_setup()