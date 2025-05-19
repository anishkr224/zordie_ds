from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import aiohttp
import asyncio
from bs4 import BeautifulSoup
import logging
from datetime import datetime

class BaseCrawler(ABC):
    """Base crawler class with common functionality."""
    
    def __init__(self, rate_limit: int = 1):
        self.rate_limit = rate_limit
        self.session = None
        self.logger = logging.getLogger(self.__class__.__name__)

    async def initialize(self):
        """Initialize async session."""
        if not self.session:
            self.session = aiohttp.ClientSession()

    async def cleanup(self):
        """Cleanup resources."""
        if self.session:
            await self.session.close()

    @abstractmethod
    async def extract_data(self, soup: BeautifulSoup, url: str) -> Dict[str, Any]:
        """Extract data from parsed HTML."""
        pass

    async def crawl(self, url: str) -> Optional[Dict[str, Any]]:
        """Main crawling method."""
        try:
            await self.initialize()
            async with self.session.get(url) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    return await self.extract_data(soup, url)
                else:
                    self.logger.error(f"Failed to fetch {url}: {response.status}")
                    return None
        except Exception as e:
            self.logger.error(f"Error crawling {url}: {str(e)}")
            return None