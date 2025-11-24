import sys
import os

# Add the current directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.services.crawler import KaistCrawler
from src.services.llm import MockLLM, OllamaLLM

def main():
    print(">>> [Univ-Insight] Real Pipeline Demo Start")
    
    # 1. Crawler Step (Real)
    print("\n>>> 1. Crawling KAIST CS Research News...")
    crawler = KaistCrawler()
    # KAIST CS Main Page (Verified to exist)
    target_url = "https://cs.kaist.ac.kr" 
    
    papers = crawler.crawl(target_url)
    
    if not papers:
        print("   [Crawler] No papers found or connection failed.")
        return

    # Limit to 1 paper for demo speed
    for i, paper in enumerate(papers[:1]):
        print(f"\n   --- Paper #{i+1} ---")
        print(f"   [Source] {paper.source}")
        print(f"   [Title] {paper.title}")
        print(f"   [Date] {paper.date}")
        print(f"   [Content Preview] {paper.content.strip()[:100]}...")

        # 2. LLM Analysis Step (Real - Ollama)
        print(f"\n   >>> 2. Analyzing Paper #{i+1} with AI Agent (Ollama)...")
        llm = OllamaLLM() # Uses llama2:latest by default
        result = llm.analyze(paper)
        
        print(f"   [Generated Report Title] {result.title}")
        print(f"   [Summary] {result.research_summary}")
        print(f"   [Career Path] {result.career_path.job_title} at {', '.join(result.career_path.companies)}")
        print(f"   [Action Item] {result.action_item.research_topic}")

    print("\n>>> [Univ-Insight] Demo Complete.")

if __name__ == "__main__":
    main()
