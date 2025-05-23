from typing import Dict, Any, Optional
from playwright.async_api import async_playwright, Page, TimeoutError
import re
from urllib.parse import urlparse
import time
from datetime import datetime
import asyncio

class WebScraper:
    def __init__(self):
        self.platform_handlers = {
            'github.com': self._scrape_github,
            'linkedin.com': self._scrape_linkedin,
            'figma.com': self._scrape_figma,
            'leetcode.com': self._scrape_leetcode
        }
        self.max_retries = 3
        self.retry_delay = 2  # seconds

    async def scrape_url(self, url: str) -> Dict[str, Any]:
        """Main method to scrape any URL and return platform-specific data."""
        domain = urlparse(url).netloc.lower()
        
        # Find the appropriate handler for the domain
        handler = None
        for platform_domain, platform_handler in self.platform_handlers.items():
            if platform_domain in domain:
                handler = platform_handler
                break
        
        if not handler:
            return {"error": "Unsupported platform", "url": url}

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            try:
                # Set longer timeout for initial page load
                page.set_default_timeout(60000)  # 60 seconds
                return await handler(page, url)
            except TimeoutError as e:
                return {"error": f"Timeout while loading page: {str(e)}", "url": url}
            except Exception as e:
                return {"error": str(e), "url": url}
            finally:
                await browser.close()

    async def _scrape_github(self, page: Page, url: str) -> Dict[str, Any]:
        """Scrape GitHub profile or repository data with retries."""
        for attempt in range(self.max_retries):
            try:
                await page.goto(url, wait_until='networkidle')
                await asyncio.sleep(self.retry_delay)  # Allow dynamic content to load
                
                data = {
                    "platform": "GitHub",
                    "url": url,
                    "metrics": {}
                }

                # Check if it's a profile or repository
                if "/repositories" in url or not any(x in url for x in ["/repos", "/stars", "/followers"]):
                    # Profile metrics
                    data["metrics"]["repos_count"] = await self._extract_number(page, '[aria-label*="repositories"]')
                    data["metrics"]["stars"] = await self._extract_number(page, '[aria-label*="stars"]')
                    data["metrics"]["followers"] = await self._extract_number(page, '[aria-label*="followers"]')
                    
                    # Get contribution graph data
                    contribution_graph = await page.query_selector('.js-calendar-graph')
                    if contribution_graph:
                        data["metrics"]["contributions"] = await self._extract_number(
                            page, '.js-calendar-graph .f4.text-normal'
                        )
                else:
                    # Repository metrics
                    data["metrics"]["stars"] = await self._extract_number(page, '[aria-label*="star"]')
                    data["metrics"]["forks"] = await self._extract_number(page, '[aria-label*="fork"]')
                    data["metrics"]["last_commit"] = await self._get_last_commit_date(page)

                return data

            except TimeoutError:
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delay * (attempt + 1))  # Exponential backoff
                    continue
                raise
            except Exception as e:
                data["error"] = str(e)
                return data

    async def _scrape_linkedin(self, page: Page, url: str) -> Dict[str, Any]:
        """Scrape LinkedIn profile data."""
        await page.goto(url)
        await asyncio.sleep(2)
        
        data = {
            "platform": "LinkedIn",
            "url": url,
            "metrics": {}
        }

        try:
            # Note: LinkedIn scraping is limited due to authentication requirements
            data["metrics"]["profile_completeness"] = await self._get_profile_completeness(page)
            data["metrics"]["connection_count"] = await self._extract_number(page, '.t-16.t-black.t-bold')
            data["metrics"]["endorsements"] = await self._get_endorsements(page)
        except Exception as e:
            data["error"] = str(e)

        return data

    async def _scrape_figma(self, page: Page, url: str) -> Dict[str, Any]:
        """Scrape Figma project data."""
        await page.goto(url)
        await asyncio.sleep(2)
        
        data = {
            "platform": "Figma",
            "url": url,
            "metrics": {}
        }

        try:
            h1_element = await page.query_selector('h1')
            data["metrics"]["project_name"] = await h1_element.inner_text() if h1_element else None
            data["metrics"]["likes"] = await self._extract_number(page, '[aria-label*="like"]')
            data["metrics"]["views"] = await self._extract_number(page, '[aria-label*="view"]')
        except Exception as e:
            data["error"] = str(e)

        return data

    async def _scrape_leetcode(self, page: Page, url: str) -> Dict[str, Any]:
        """Scrape LeetCode profile data."""
        for attempt in range(self.max_retries):
            try:
                await page.goto(url, wait_until='networkidle')
                await asyncio.sleep(self.retry_delay)  # Allow dynamic content to load
                
                data = {
                    "platform": "LeetCode",
                    "url": url,
                    "metrics": {}
                }

                # Check if it's a profile or problem page
                if "/problems/" in url:
                    # Problem metrics
                    h1_element = await page.query_selector('h1')
                    data["metrics"]["problem_name"] = await h1_element.inner_text() if h1_element else None
                    diff_element = await page.query_selector('[diff]')
                    data["metrics"]["difficulty"] = await diff_element.get_attribute('diff') if diff_element else None
                    data["metrics"]["acceptance_rate"] = await self._extract_number(page, '[data-cy="acceptance-rate"]')
                else:
                    # Profile metrics
                    data["metrics"]["solved_problems"] = await self._extract_number(page, '[data-cy="solved-problems"]')
                    data["metrics"]["acceptance_rate"] = await self._extract_number(page, '[data-cy="acceptance-rate"]')
                    data["metrics"]["ranking"] = await self._extract_number(page, '[data-cy="ranking"]')
                    
                    # Get difficulty-wise solved problems
                    difficulty_stats = {}
                    for diff in ['Easy', 'Medium', 'Hard']:
                        selector = f'[data-cy="{diff.lower()}-solved"]'
                        solved = await self._extract_number(page, selector)
                        if solved is not None:
                            difficulty_stats[diff] = solved
                    data["metrics"]["difficulty_stats"] = difficulty_stats
                    
                    # Get recent activity
                    recent_activity = []
                    activity_elements = await page.query_selector_all('.activity-item')
                    for element in activity_elements[:5]:  # Get last 5 activities
                        activity_text = await element.inner_text()
                        if activity_text:
                            recent_activity.append(activity_text)
                    data["metrics"]["recent_activity"] = recent_activity

                return data

            except TimeoutError:
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delay * (attempt + 1))  # Exponential backoff
                    continue
                raise
            except Exception as e:
                data["error"] = str(e)
                return data

    async def _extract_number(self, page: Page, selector: str) -> Optional[int]:
        """Helper method to extract numbers from elements."""
        element = await page.query_selector(selector)
        if element:
            text = await element.inner_text()
            numbers = re.findall(r'\d+', text)
            return int(numbers[0]) if numbers else None
        return None

    async def _get_last_commit_date(self, page: Page) -> Optional[str]:
        """Extract the last commit date from a GitHub repository."""
        element = await page.query_selector('relative-time')
        return await element.get_attribute('datetime') if element else None

    async def _get_profile_completeness(self, page: Page) -> Optional[int]:
        """Estimate LinkedIn profile completeness."""
        # This is a simplified version - actual implementation would be more complex
        completeness = 0
        selectors = [
            '.pv-top-card-section__headline',
            '.pv-top-card-section__summary-info',
            '.experience-section',
            '.education-section',
            '.skills-section'
        ]
        
        for selector in selectors:
            if await page.query_selector(selector):
                completeness += 20
                
        return completeness

    async def _get_endorsements(self, page: Page) -> Dict[str, int]:
        """Extract skill endorsements from LinkedIn."""
        endorsements = {}
        skill_elements = await page.query_selector_all('.pv-skill-category-entity__name')
        
        for skill in skill_elements:
            skill_name = await skill.inner_text()
            endorsement_count = await self._extract_number(
                page,
                f'[data-test-id="endorsement-count"][aria-label*="{skill_name}"]'
            )
            if endorsement_count:
                endorsements[skill_name] = endorsement_count
                
        return endorsements 