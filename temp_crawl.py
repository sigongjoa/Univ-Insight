import asyncio
import os
import sys

# Add src to path
project_root = os.path.abspath(os.path.dirname(__file__))
src_path = os.path.join(project_root, 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from services.article_crawler import ArticleCrawler

async def main():
    """
    Crawls a single page and prints its full raw HTML content.
    """
    url = "https://cs.kaist.ac.kr/bbs/news/research"
    crawler = ArticleCrawler()
    # Call the internal method to get the raw HTML
    html_content = await crawler._fetch_page_content(url)
    if html_content:
        print(html_content)
    else:
        print("Failed to crawl the page.")

if __name__ == '__main__':
    asyncio.run(main())