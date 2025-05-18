from typing import Dict, Any
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import re
from datetime import datetime

class UniversalLinkCrawler:
    def __init__(self):
        self.platform_patterns = {
            'github': r'github\.com',
            'leetcode': r'leetcode\.com',
            'kaggle': r'kaggle\.com',
            'linkedin': r'linkedin\.com',
            'figma': r'figma\.com',
            'dribbble': r'dribbble\.com'
        }

    def crawl_link(self, url: str) -> Dict[str, Any]:
        """Crawl any professional profile URL and extract metadata."""
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                page.goto(url, wait_until="networkidle")
                
                # Get platform type
                platform = self._detect_platform(url)
                
                # Extract metadata based on platform
                metadata = self._extract_metadata(page, platform)
                
                browser.close()
                return {
                    "platform": platform,
                    "url": url,
                    "is_public": self._check_public_access(page),
                    "metadata": metadata,
                    "last_activity": self._get_last_activity(page, platform),
                    "crawl_date": datetime.now().isoformat()
                }
        except Exception as e:
            return {
                "error": str(e),
                "url": url
            }

    def _detect_platform(self, url: str) -> str:
        """Detect the platform from URL."""
        for platform, pattern in self.platform_patterns.items():
            if re.search(pattern, url, re.IGNORECASE):
                return platform
        return "unknown"

    def _check_public_access(self, page) -> bool:
        """Check if the profile is publicly accessible."""
        return "404" not in page.title() and "private" not in page.title().lower()

    def _extract_metadata(self, page, platform: str) -> Dict[str, Any]:
        """Extract platform-specific metadata."""
        html = page.content()
        soup = BeautifulSoup(html, 'html.parser')
        
        if platform == "github":
            return self._extract_github_metadata(soup)
        elif platform == "leetcode":
            return self._extract_leetcode_metadata(soup)
        elif platform == "linkedin":
            return self._extract_linkedin_metadata(soup)
        # Add other platform extractors as needed
        return {}

    def _get_last_activity(self, page, platform: str) -> str:
        """Get the date of last activity."""
        try:
            html = page.content()
            soup = BeautifulSoup(html, 'html.parser')
            
            if platform == "github":
                activity = soup.find("div", {"class": "ContributionCalendar-day"})
                return activity.get("data-date") if activity else None
            # Add other platform activity checks
            return None
        except:
            return None

    def _extract_github_metadata(self, soup) -> Dict[str, Any]:
        """Extract GitHub specific metadata."""
        return {
            "repositories": len(soup.find_all("div", {"class": "repo"})),
            "followers": self._extract_number(soup.find("span", {"class": "text-bold"})),
            "contributions": self._extract_number(soup.find("h2", {"class": "f4"})),
            "projects": self._extract_projects(soup)
        }

    def _extract_leetcode_metadata(self, soup) -> Dict[str, Any]:
        """Extract LeetCode specific metadata."""
        return {
            "solved_problems": self._extract_number(soup.find("div", {"class": "total-solved"})),
            "contest_rating": self._extract_number(soup.find("div", {"class": "rating"})),
            "global_ranking": self._extract_number(soup.find("div", {"class": "ranking"}))
        }

    def _extract_linkedin_metadata(self, soup) -> Dict[str, Any]:
        """Extract LinkedIn specific metadata."""
        return {
            "connections": self._extract_number(soup.find("span", {"class": "connection-count"})),
            "endorsements": self._count_endorsements(soup),
            "posts": self._count_posts(soup)
        }

    def _extract_number(self, element) -> int:
        """Extract number from text."""
        if not element:
            return 0
        text = element.text.strip()
        numbers = re.findall(r'\d+', text)
        return int(numbers[0]) if numbers else 0

    def _extract_projects(self, soup) -> list:
        """Extract project names."""
        projects = []
        project_elements = soup.find_all("div", {"class": "repo"})
        for proj in project_elements[:5]:  # Get top 5 projects
            name = proj.find("a")
            if name:
                projects.append(name.text.strip())
        return projects

    def _count_endorsements(self, soup) -> int:
        """Count LinkedIn endorsements from profile."""
        try:
            # Find endorsement elements
            endorsements = soup.find_all("span", {"class": "skill-endorsement-count"})
            total = sum(int(e.text.strip()) for e in endorsements if e.text.strip().isdigit())
            return total
        except Exception as e:
            print(f"Error counting endorsements: {str(e)}")
            return 0

    def _count_posts(self, soup) -> int:
        """Count LinkedIn posts from profile."""
        try:
            # Find post elements
            posts = soup.find_all("div", {"class": "feed-shared-update-v2"})
            return len(posts)
        except Exception as e:
            print(f"Error counting posts: {str(e)}")
            return 0