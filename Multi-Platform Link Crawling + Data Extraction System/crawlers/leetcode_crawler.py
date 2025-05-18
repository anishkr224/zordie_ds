from crawlers.base_crawler import BaseCrawler
from bs4 import BeautifulSoup
from typing import Dict, Any
from datetime import datetime

class LeetCodeCrawler(BaseCrawler):
    """LeetCode profile crawler."""

    async def extract_data(self, soup: BeautifulSoup, url: str) -> Dict[str, Any]:
        username = url.split('/')[-1]
        
        metrics = {
            'solved_problems': self._extract_solved_count(soup),
            'acceptance_rate': self._extract_acceptance_rate(soup),
            'contest_rating': self._extract_contest_rating(soup),
            'global_ranking': self._extract_ranking(soup),
            'problem_stats': self._extract_problem_stats(soup)
        }

        return {
            'platform': 'leetcode',
            'username': username,
            'url': url,
            'metrics': metrics,
            'crawl_date': datetime.now().isoformat()
        }

    def _extract_solved_count(self, soup: BeautifulSoup) -> int:
        try:
            solved_element = soup.find('div', {'class': 'total-solved-count'})
            return int(solved_element.text.strip()) if solved_element else 0
        except:
            return 0

    def _extract_acceptance_rate(self, soup: BeautifulSoup) -> float:
        try:
            rate_element = soup.find('div', {'class': 'acceptance-rate'})
            return float(rate_element.text.strip('%')) if rate_element else 0.0
        except:
            return 0.0