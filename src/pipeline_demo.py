from src.services.crawler import MockCrawlerService
from src.services.llm import MockLLMService
import json

def run_mock_pipeline():
    print("=== Univ-Insight Pipeline Simulation (Mock) ===\n")

    # 1. Initialize Services
    crawler = MockCrawlerService()
    llm = MockLLMService()

    # 2. Crawl Data
    target_url = "https://cs.kaist.ac.kr/news/research"
    papers = crawler.crawl(target_url)
    print(f"✅ Crawled {len(papers)} papers.\n")

    # 3. Analyze Data
    results = []
    for paper in papers:
        analysis = llm.analyze(paper)
        results.append(analysis)
        print(f"   -> Analysis Complete: {analysis.job_title}")

    # 4. Show Result
    print("\n=== Final Report Preview ===")
    for res in results:
        print(f"\n[Paper ID: {res.paper_id}]")
        print(f"Summary: {res.easy_summary}")
        print(f"Career: {res.job_title} @ {', '.join(res.related_companies)}")
        print(f"Action: {res.action_item_subject} - {res.action_item_topic}")

if __name__ == "__main__":
    run_mock_pipeline()
