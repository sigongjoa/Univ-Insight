
import sys
import os
import re

# Add project root to path
sys.path.append(os.getcwd())

from src.core.database import SessionLocal
from src.domain.models import Professor, Department
from src.services.crawler import UniversityCrawler

async def check_markdown_links():
    # Re-crawl to get fresh markdown
    target_url = "https://cse.snu.ac.kr/people/faculty"
    crawler = UniversityCrawler()
    try:
        result = await crawler._crawl_async(target_url)
        content = result.content_raw
        
        print(f"✅ Crawled content length: {len(content)}")
        
        # Find links: [Text](URL)
        links = re.findall(r'\[(.*?)\]\((.*?)\)', content)
        print(f"ℹ️ Found {len(links)} links.")
        
        faculty_links = []
        for text, url in links:
            # Filter likely faculty links
            if "/professor/" in url or "/people/" in url:
                print(f"   Candidate: [{text}]({url})")
                faculty_links.append((text, url))
                
        return faculty_links, content

    except Exception as e:
        print(f"❌ Error: {e}")
        return [], ""

if __name__ == "__main__":
    import asyncio
    asyncio.run(check_markdown_links())
