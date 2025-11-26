import sys
import os
import uuid
from datetime import datetime

# Add project root to path
sys.path.append(os.getcwd())

from src.core.database import SessionLocal
from src.domain.models import User, Professor, Department, College, University, ResearchPaper, Laboratory
from src.services.llm import OllamaLLM, MockLLM
from src.services.pdf_generator import PDFGenerator
from src.domain.schemas import ResearchPaper as SchemaResearchPaper

def run_progressive_report_test():
    print("🚀 Starting Integrated Progressive Report Test...")
    
    db = SessionLocal()
    try:
        # 1. Setup Dummy Data (User, Prof, Paper)
        user_id = "test-student-001"
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            user = User(id=user_id, name="김학생", role="student", interests=["Computer Vision", "Robotics"])
            db.add(user)
        
        # Ensure we have a professor and paper
        # Check by ID first, then Name
        uni = db.query(University).filter(University.id == "snu").first()
        if not uni:
            uni = db.query(University).filter(University.name == "Seoul National University").first()
            if not uni:
                uni = University(id="snu", name="Seoul National University", name_ko="서울대학교")
                db.add(uni)
            
        col = db.query(College).filter(College.id == "snu-eng").first()
        if not col:
            col = db.query(College).filter(College.university_id == uni.id, College.name == "College of Engineering").first()
            if not col:
                col = College(id="snu-eng", university_id=uni.id, name="College of Engineering", name_ko="공과대학")
                db.add(col)
            
        dept = db.query(Department).filter(Department.id == "snu-cse").first()
        if not dept:
            dept = db.query(Department).filter(Department.college_id == col.id, Department.name == "Computer Science").first()
            if not dept:
                dept = Department(id="snu-cse", college_id=col.id, name="Computer Science", name_ko="컴퓨터공학부")
                db.add(dept)
            
        prof = db.query(Professor).filter(Professor.id == "prof-test").first()
        if not prof:
            prof = Professor(
                id="prof-test", 
                department_id=dept.id, 
                name="Lee Sang-woo", 
                name_ko="이상우", 
                research_interests=["Vision-Language Models", "Robot Learning"]
            )
            db.add(prof)
            
        lab = db.query(Laboratory).filter(Laboratory.id == "lab-test").first()
        if not lab:
            lab = Laboratory(
                id="lab-test",
                professor_id=prof.id,
                department_id=dept.id,
                name="Vision Lab",
                name_ko="비전 연구실"
            )
            db.add(lab)
            
        paper = db.query(ResearchPaper).filter(ResearchPaper.id == "paper-test").first()
        if not paper:
            paper = ResearchPaper(
                id="paper-test",
                lab_id=lab.id,
                title="Learning to Navigate with Vision-Language Models",
                abstract="We present a method for robot navigation using VLMs...",
                url="http://example.com"
            )
            db.add(paper)
            
        db.commit()
        
        # 2. Simulate "create_report" logic
        print(f"User Interests: {user.interests}")
        print("Finding professors...")
        
        # Mock finding professors (just use our test prof)
        top_profs = [(prof, 1.0)]
        
        analysis_results = []
        
        # Initialize LLM
        try:
            llm = OllamaLLM(model='qwen2.5:14b')
        except:
            llm = MockLLM()
            
        for p, score in top_profs:
            print(f"Processing Professor: {p.name_ko}")
            
            # Find paper
            target_paper = None
            if p.laboratories and p.laboratories[0].papers:
                db_p = p.laboratories[0].papers[0]
                target_paper = SchemaResearchPaper(
                    id=db_p.id,
                    url=db_p.url or "",
                    title=db_p.title,
                    university="Seoul National University",
                    department="Computer Science",
                    content_raw=db_p.abstract or db_p.title
                )
            else:
                target_paper = SchemaResearchPaper(
                    id="virtual",
                    url="",
                    title=f"{p.name} 교수님의 연구",
                    university="Seoul National University",
                    department="Computer Science",
                    content_raw="Research on Vision-Language Models"
                )
                
            # Analyze
            print(f"Analyzing paper: {target_paper.title}")
            try:
                result = llm.analyze(target_paper)
            except Exception as e:
                print(f"LLM failed, using Mock: {e}")
                result = MockLLM().analyze(target_paper)
                
            result_dict = result.dict()
            result_dict["professor_name"] = p.name_ko
            analysis_results.append(result_dict)
            
        # 3. Generate PDF
        print("Generating PDF...")
        pdf_gen = PDFGenerator(output_dir="docs/reports")
        report_data = {
            "user_name": user.name,
            "interests": ", ".join(user.interests),
            "report_date": datetime.now().strftime("%Y-%m-%d"),
            "analysis_results": analysis_results
        }
        
        pdf_path = pdf_gen.generate(report_data, "Integrated_Progressive_Report.pdf")
        print(f"✅ Report generated at: {pdf_path}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    run_progressive_report_test()
