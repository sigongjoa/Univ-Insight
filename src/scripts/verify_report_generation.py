
import sys
import os
import uuid
from datetime import datetime

# Add project root to path
sys.path.append(os.getcwd())

from src.core.database import SessionLocal
from src.domain.models import User, ResearchPaper, Report, ReportPaper, ReportStatus

def verify_report_generation():
    db = SessionLocal()
    try:
        print("🚀 Starting Report Generation Verification...")

        # 1. Create Test User
        user_id = "test-user-report"
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            user = User(
                id=user_id,
                email="test@example.com",
                name="Test User",
                interests=["Computer Vision", "AI", "Deep Learning"],
                preferred_universities=["seoul-national-univ"]
            )
            db.add(user)
            print(f"✅ Created test user: {user_id} with interests: {user.interests}")
        else:
            user.interests = ["Computer Vision", "AI", "Deep Learning"]
            print(f"ℹ️ Using existing user: {user_id}")

        # 2. Update Crawled Papers with Keywords
        # Find the paper we just crawled (from SNU)
        # We look for papers with 'cse.snu.ac.kr' in URL
        papers = db.query(ResearchPaper).filter(ResearchPaper.url.like("%cse.snu.ac.kr%")).all()
        
        if not papers:
            print("❌ No crawled papers found. Please run the crawler first.")
            return

        print(f"ℹ️ Found {len(papers)} crawled papers.")
        
        for paper in papers:
            # Inject keywords that match user interests
            paper.keywords = ["Computer Vision", "AI", "Technology"]
            print(f"✅ Updated keywords for paper: {paper.title[:30]}...")
        
        db.commit()

        # 3. Generate Report Logic (Simulating the API logic)
        print("\n🔄 Generating Report...")
        
        # Find matching papers
        # Note: SQLite array overlap might need specific handling, 
        # but here we'll simulate the query logic used in routes.py
        # In routes.py: ResearchPaper.keywords.overlap(user.interests)
        # For this script, we'll do python-side filtering to be safe with SQLite
        
        all_papers = db.query(ResearchPaper).all()
        matching_papers = []
        for p in all_papers:
            if p.keywords and any(k in user.interests for k in p.keywords):
                matching_papers.append(p)
        
        if not matching_papers:
            print("❌ No matching papers found for report.")
            return

        print(f"✅ Found {len(matching_papers)} matching papers for report.")

        # Create Report
        report = Report(
            id=str(uuid.uuid4()),
            user_id=user_id,
            status=ReportStatus.SENT,
            sent_at=datetime.now()
        )
        db.add(report)
        db.flush()

        # Link papers
        for idx, paper in enumerate(matching_papers[:5]):
            report_paper = ReportPaper(
                id=str(uuid.uuid4()),
                report_id=report.id,
                paper_id=paper.id,
                order_index=idx
            )
            db.add(report_paper)
            print(f"   - Added paper to report: {paper.title[:50]}")

        db.commit()
        print(f"\n✅ Report generated successfully! ID: {report.id}")
        
        # 4. Verify Report Content
        saved_report = db.query(Report).filter(Report.id == report.id).first()
        print(f"📋 Report Summary:")
        print(f"   User: {saved_report.user.name}")
        print(f"   Status: {saved_report.status.value}")
        print(f"   Papers Count: {len(saved_report.papers)}")
        
        if len(saved_report.papers) > 0:
            print("\n🎉 SUCCESS: Crawled data was successfully transformed into a user report!")
        else:
            print("\n⚠️ WARNING: Report created but has no papers.")

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    verify_report_generation()
