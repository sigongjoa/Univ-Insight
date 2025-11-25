
import asyncio
from typing import List, Tuple
import os
import sys
import re
from urllib.parse import urljoin

# 프로젝트 루트를 sys.path에 추가
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

try:
    from crawl4ai import AsyncWebCrawler
    from crawl4ai.extraction_strategy import JsonCssExtractionStrategy
except ImportError:
    AsyncWebCrawler = None
    JsonCssExtractionStrategy = None

class IndexCrawler:
    """
    주어진 대학 학과 메인 페이지에서 시작하여,
    CSS 선택자를 사용해 연구/뉴스 기사 목록의 URL을 안정적으로 찾아냅니다.
    """

    def __init__(self):
        if not AsyncWebCrawler or not JsonCssExtractionStrategy:
            raise ImportError("crawl4ai is not installed. Please install it with 'pip install crawl4ai'")

    async def extract_links_from_index(self, index_url: str) -> List[Tuple[str, str]]:
        """
        주어진 인덱스 페이지에서 CSS 선택자를 기반으로 개별 기사 링크를 추출합니다.
        AI 기반 추출이 실패하여, 보다 안정적인 이 방식으로 전환합니다.
        """
        print(f"   [IndexCrawler] Extracting links from {index_url} using CSS selectors...")
        
        try:
            async with AsyncWebCrawler(verbose=False) as crawler:
                # CSS 선택자 스키마 정의
                # 각 기사는 'li.verti_item'
                # 제목은 'p.tit span'
                # onclick 속성은 'div.item' 요소에 있음
                articles_schema = {
                    "name": "articles",
                    "baseSelector": "ul.item_box li.verti_item",
                    "fields": [
                        {"name": "title", "selector": "p.tit span", "type": "text"},
                        {"name": "onclick", "selector": "div.item", "type": "attribute", "attribute": "onclick"}
                    ]
                }

                strategy = JsonCssExtractionStrategy(schema=articles_schema)

                result = await crawler.arun(
                    url=index_url,
                    extraction_strategy=strategy
                )

                if not result.success or not result.extracted_content:
                    print(f"   [IndexCrawler] Could not extract article data from {index_url}")
                    return []

                # 추출된 데이터 후처리 (URL 조립)
                articles = []
                for item in result.extracted_content:
                    title = item.get('title')
                    onclick_attr = item.get('onclick')

                    if not title or not onclick_attr:
                        continue

                    # onclick="readArticle('news', '11652', ...)" 에서 파라미터 추출
                    match = re.search(r"readArticle\('([^']*)',\s*'([^']*)'", onclick_attr)
                    if not match:
                        continue
                    
                    bbs_id, bbs_sn = match.groups()
                    
                    # URL 조립
                    # readAuthCheck() 함수 로직에 따라 menu 파라미터는 필수는 아닌 것으로 보임
                    article_path = f"/board/view?bbs_id={bbs_id}&bbs_sn={bbs_sn}"
                    absolute_url = urljoin(index_url, article_path)
                    
                    articles.append((title, absolute_url))

                print(f"   [IndexCrawler] Discovered {len(articles)} article links.")
                return articles

        except Exception as e:
            print(f"   [IndexCrawler] An error occurred during discovery: {e}")
            return []

if __name__ == '__main__':
    async def main():
        crawler = IndexCrawler()
        # KAIST 전산학부 연구소식 페이지에서 직접 시작
        article_links = await crawler.extract_links_from_index("https://cs.kaist.ac.kr/bbs/news/research")
        if article_links:
            print("\n--- Discovered Articles ---")
            for i, (title, url) in enumerate(article_links[:5], 1):
                print(f"{i}. {title}: {url}")
            print("-------------------------")
        else:
            print("\n--- No articles discovered. ---")

    asyncio.run(main())
