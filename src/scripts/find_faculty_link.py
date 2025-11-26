
import sys
import os
import re
from bs4 import BeautifulSoup

# Add project root to path
sys.path.append(os.getcwd())

from src.core.database import SessionLocal
from src.domain.models import ResearchPaper

def find_faculty_link():
    db = SessionLocal()
    try:
        # Get the crawled main page
        paper = db.query(ResearchPaper).filter(ResearchPaper.url.like("%cse.snu.ac.kr%")).order_by(ResearchPaper.crawled_at.desc()).first()
        
        if not paper:
            print("❌ No crawled paper found.")
            return

        print(f"ℹ️ Analyzing content from: {paper.url}")
        
        # Parse HTML (assuming full_text contains HTML or Markdown)
        # Since crawl4ai returns markdown by default, we might need to look at raw links if available,
        # or rely on markdown links [Text](URL)
        
        content = paper.full_text
        
        # Find links in Markdown format: [Text](URL)
        links = re.findall(r'\[(.*?)\]\((.*?)\)', content)
        
        print(f"ℹ️ Found {len(links)} links in markdown content.")
        
        faculty_keywords = ["Faculty", "Professor", "People", "교수", "구성원"]
        
        found_links = []
        for text, url in links:
            if any(kw.lower() in text.lower() for kw in faculty_keywords):
                print(f"✅ Found candidate link: [{text}]({url})")
                found_links.append(url)
                
        if not found_links:
            print("⚠️ No faculty links found in markdown. The crawler might have converted navigation to text poorly.")
            # Fallback: Guess common URLs
            print("ℹ️ Suggesting common patterns:")
            print(f"   - {paper.url}/people/faculty")
            print(f"   - {paper.url}/faculty")
            print(f"   - {paper.url}/member/professor")

    finally:
        db.close()

if __name__ == "__main__":
    find_faculty_link()
