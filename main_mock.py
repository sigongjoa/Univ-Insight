import sys
import os

# Add the current directory to sys.path to make imports work
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.services.crawler import MockCrawler
from src.services.llm import MockLLM

def main():
    print(">>> [Univ-Insight] Mock Process Verification Start")
    
    # 1. Crawler Step
    print("\n>>> 1. Crawling Target URL...")
    crawler = MockCrawler()
    target_url = "https://cs.kaist.ac.kr/research/paper/1234"
    paper = crawler.crawl(target_url)
    
    print(f"   [Source] {paper.source}")
    print(f"   [Title] {paper.title}")
    print(f"   [Date] {paper.date}")
    print(f"   [Content Preview] {paper.content.strip()[:100]}...")

    # 2. LLM Analysis Step
    print("\n>>> 2. Analyzing with AI Agent...")
    llm = MockLLM()
    result = llm.analyze(paper)
    
    print("\n" + "="*50)
    print(f"   [Generated Report]")
    print("="*50)
    print(f"   1. Title: {result.title}")
    print(f"   2. Research: {result.research_summary}")
    print(f"   3. Career Path:")
    print(f"      - Companies: {', '.join(result.career_path.companies)}")
    print(f"      - Job: {result.career_path.job_title}")
    print(f"      - Salary Hint: {result.career_path.avg_salary_hint}")
    print(f"   4. Action Item:")
    print(f"      - Subjects: {', '.join(result.action_item.subjects)}")
    print(f"      - Topic: {result.action_item.research_topic}")
    print("="*50)
    
    print("\n>>> [Univ-Insight] Verification Complete. Process is working as expected.")

if __name__ == "__main__":
    main()
