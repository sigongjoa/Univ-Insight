import sys
import os
from datetime import datetime

# Add the current directory to sys.path to make imports work
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.services.crawler import MockCrawler
from src.services.llm import MockLLM
from src.core.database import init_db, SessionLocal
from src.domain.models import ResearchPaper, AnalysisResult

def main():
    print(">>> [Univ-Insight] Mock Process Verification Start")

    # Initialize database
    print("\n>>> 0. Initializing Database...")
    init_db()
    print("   ✓ Database initialized")

    # 1. Crawler Step
    print("\n>>> 1. Crawling Target URL...")
    crawler = MockCrawler()
    target_url = "https://cs.kaist.ac.kr/research/paper/1234"
    paper_schema = crawler.crawl(target_url)

    if paper_schema is None:
        print("   ✗ Failed to crawl paper")
        return

    print(f"   [Source] {paper_schema.source}")
    print(f"   [Title] {paper_schema.title}")
    print(f"   [Date] {paper_schema.date}")
    print(f"   [Content Preview] {paper_schema.content.strip()[:100]}...")

    # 2. LLM Analysis Step
    print("\n>>> 2. Analyzing with AI Agent...")
    llm = MockLLM()
    result = llm.analyze(paper_schema)

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

    # 3. Save to Database
    print("\n>>> 3. Saving to Database...")
    db = SessionLocal()
    try:
        # Save Research Paper
        paper_model = ResearchPaper(
            url=paper_schema.url,
            title=paper_schema.title,
            university=paper_schema.source,
            content_raw=paper_schema.content,
            pub_date=datetime.fromisoformat(paper_schema.date).date() if paper_schema.date else None
        )
        db.add(paper_model)
        db.flush()  # Flush to get the generated ID

        # Save Analysis Result
        analysis_model = AnalysisResult(
            paper_id=paper_model.id,
            summary=result.research_summary,
            job_title=result.career_path.job_title,
            salary_hint=result.career_path.avg_salary_hint,
            related_companies=result.career_path.companies,
            action_items={
                "subjects": result.action_item.subjects,
                "research_topic": result.action_item.research_topic
            }
        )
        db.add(analysis_model)
        db.commit()

        print(f"   ✓ Paper saved with ID: {paper_model.id}")
        print(f"   ✓ Analysis saved with ID: {analysis_model.id}")

        # 4. Verify data retrieval
        print("\n>>> 4. Verifying Data Retrieval...")
        retrieved_paper = db.query(ResearchPaper).filter(ResearchPaper.id == paper_model.id).first()
        retrieved_analysis = db.query(AnalysisResult).filter(AnalysisResult.paper_id == paper_model.id).first()

        if retrieved_paper and retrieved_analysis:
            print(f"   ✓ Paper retrieved: {retrieved_paper.title}")
            print(f"   ✓ Analysis retrieved: {retrieved_analysis.job_title}")
        else:
            print("   ✗ Failed to retrieve data")

    finally:
        db.close()

    print("\n>>> [Univ-Insight] Verification Complete. Process is working as expected.")

if __name__ == "__main__":
    main()
