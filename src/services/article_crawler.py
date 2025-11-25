
import asyncio
import re
import uuid
from typing import Optional
from datetime import datetime
from bs4 import BeautifulSoup
import os
import sys

# 프로젝트 루트를 sys.path에 추가
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.domain.schemas import ResearchPaper

try:
    from crawl4ai import AsyncWebCrawler
except ImportError:
    AsyncWebCrawler = None

class ArticleCrawler:
    """
    주어진 URL에서 단일 연구/기사 페이지를 크롤링하여
    제목과 본문을 추출하고 ResearchPaper 객체를 생성합니다.
    """

    def __init__(self):
        if not AsyncWebCrawler:
            raise ImportError("crawl4ai is not installed. Please install it with 'pip install crawl4ai'")

    async def crawl(self, url: str, university: str, department: str) -> Optional[ResearchPaper]:
        """
        주어진 URL을 비동기적으로 크롤링하고 ResearchPaper 객체를 반환합니다.
        """
        print(f"   [ArticleCrawler] Starting crawl for {url}...")
        html_content = await self._fetch_page_content(url)
        if not html_content:
            return None

        title = self._extract_title(html_content) or "Title Not Found"
        content = self._extract_main_content(html_content)

        if not content:
            print(f"   [ArticleCrawler] Could not extract main content from {url}")
            return None

        paper = ResearchPaper(
            id=str(uuid.uuid4()),
            url=url,
            title=title,
            university=university,
            department=department,
            pub_date=datetime.now().date(),
            content_raw=content[:8000],  # Limit content size
            crawled_at=datetime.now()
        )
        print(f"   [ArticleCrawler] Successfully crawled and parsed article: {title}")
        return paper

    async def _fetch_page_content(self, url: str) -> str:
        """주어진 URL의 페이지를 crawl4ai로 가져와 HTML 콘텐츠를 반환합니다."""
        async with AsyncWebCrawler(verbose=False) as crawler:
            result = await crawler.arun(url=url, timeout=30, wait_until="networkidle")
            if result.success:
                # 404 오류 페이지인지 확인 (소프트 404 대응)
                if "404" in result.html and "not found" in result.html.lower():
                     print(f"   [ArticleCrawler] Soft 404 detected for {url}")
                     return ""
                return result.html
            else:
                print(f"   [ArticleCrawler] crawl4ai fetch 실패 ({url}): {result.error_message}")
                return ""

    def _extract_title(self, html_content: str) -> Optional[str]:
        """HTML에서 h1, h2, title 태그를 사용하여 제목을 추출합니다."""
        soup = BeautifulSoup(html_content, 'html.parser')
        for tag in ['h1', 'h2', 'title']:
            title_tag = soup.find(tag)
            if title_tag and title_tag.get_text(strip=True):
                return title_tag.get_text(strip=True)
        return None

    def _extract_main_content(self, html_content: str) -> str:
        """
        HTML에서 주요 본문 콘텐츠를 추출합니다.
        <article>, <main>, 또는 주요 콘텐츠 div를 우선적으로 탐색합니다.
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Clean up irrelevant tags
        for tag in soup(['script', 'style', 'nav', 'header', 'footer', 'aside']):
            tag.decompose()

        # Find main content container
        main_content = soup.find('article') or \
                       soup.find('main') or \
                       soup.find('div', id='content') or \
                       soup.find('div', class_='content') or \
                       soup.body

        return main_content.get_text(separator='\n', strip=True) if main_content else ""

if __name__ == '__main__':
    # 테스트 실행
    async def main():
        test_url = "https://cs.kaist.ac.kr/news/read?id=5218" # 실제 KAIST CS 연구 뉴스
        crawler = ArticleCrawler()
        paper = await crawler.crawl(url=test_url, university="KAIST", department="CS")
        if paper:
            print("\n--- Crawled Paper ---")
            print(f"ID: {paper.id}")
            print(f"Title: {paper.title}")
            print(f"URL: {paper.url}")
            print(f"University: {paper.university}")
            print(f"Content (first 100 chars): {paper.content_raw[:100]}...")
            print("--------------------")
    
    asyncio.run(main())
