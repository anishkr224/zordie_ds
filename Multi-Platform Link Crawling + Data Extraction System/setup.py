from setuptools import setup, find_packages

setup(
    name="resume-analyzer",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        'aiohttp>=3.9.1',
        'beautifulsoup4>=4.12.2',
        'requests>=2.31.0',
        'python-dotenv>=1.0.0',
        'lxml>=4.9.3',
        'playwright>=1.41.0',
        'pydantic>=2.7.4',  # Added specific version for langchain compatibility
        'langchain>=0.3.7',
        'pydantic-settings>=2.6.1'
    ],
    python_requires='>=3.9',
)