from dotenv import load_dotenv
import os

def test_env_config():
    load_dotenv()
    
    required_vars = ['GITHUB_TOKEN', 'OPENAI_API_KEY']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"Missing required environment variables: {', '.join(missing_vars)}")
        return False
    
    print("Environment configuration verified successfully!")
    return True

if __name__ == "__main__":
    test_env_config()