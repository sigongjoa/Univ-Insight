import asyncio
import re
import uuid
from typing import Optional
from datetime import datetime
from src.domain.schemas import ResearchPaper

# Try importing crawl4ai, handle if not installed yet
try:
    from crawl4ai import AsyncWebCrawler
except ImportError:
    AsyncWebCrawler = None


class BaseCrawler:
    """Base crawler interface"""
    def crawl(self, url: str) -> ResearchPaper:
        raise NotImplementedError


class KaistCrawler(BaseCrawler):
    """
    Crawler for KAIST (Korea Advanced Institute of Science and Technology)
    research papers and news.
    """

    def crawl(self, url: str = "https://cs.kaist.ac.kr/news/research") -> Optional[ResearchPaper]:
        """
        Crawl KAIST research page and extract paper information.

        Args:
            url: Target URL to crawl

        Returns:
            ResearchPaper object or None if crawling fails
        """
        if not AsyncWebCrawler:
            print("   [Error] crawl4ai not installed.")
            return None
        return asyncio.run(self._crawl_async(url))

    async def _crawl_async(self, url: str) -> Optional[ResearchPaper]:
        """Async crawling implementation"""
        print(f"   [KaistCrawler] Starting crawl for {url}...")

        try:
            async with AsyncWebCrawler(verbose=False) as crawler:
                result = await crawler.arun(
                    url=url,
                    timeout=30,
                    wait_until="networkidle"
                )

                if not result.success:
                    print(f"   [KaistCrawler] Failed to crawl: {result.error_message}")
                    return None

                print(f"   [KaistCrawler] Successfully crawled. Content length: {len(result.markdown)}")

                # Extract title from the page
                title = self._extract_title(result.markdown, url)

                # Create ResearchPaper object with the new schema
                paper = ResearchPaper(
                    id=str(uuid.uuid4()),
                    url=url,
                    title=title,
                    university="KAIST",
                    department="CS",
                    pub_date=datetime.now().date(),
                    content_raw=result.markdown[:8000],  # Limit content size
                    crawled_at=datetime.now()
                )

                return paper

        except Exception as e:
            print(f"   [KaistCrawler] Error during crawling: {str(e)}")
            return None

    @staticmethod
    def _extract_title(content: str, url: str) -> str:
        """Extract title from markdown content"""
        # Try to find the first heading
        match = re.search(r'#\s+(.+)', content)
        if match:
            return match.group(1).strip()
        # Fallback to URL-based title
        return f"Research from {url}"


class MockCrawler(BaseCrawler):
    """Mock crawler for testing without actual web requests"""

    def crawl(self, url: str) -> ResearchPaper:
        """Return mock research paper"""
        return ResearchPaper(
            id=str(uuid.uuid4()),
            url=url,
            title="Efficient Transformer Architectures for Mobile Devices",
            university="KAIST (Mock)",
            department="CS",
            pub_date=datetime.now().date(),
            content_raw="This research focuses on optimizing transformer models to run efficiently on mobile devices. Traditional transformers are computationally expensive, but this work introduces novel quantization and pruning techniques that reduce model size by 70% while maintaining 95% accuracy. The approach combines knowledge distillation with hardware-aware optimization, making it practical for deployment on smartphones and IoT devices.",
            crawled_at=datetime.now()
        )
