#!/usr/bin/env python3
"""
서울대 경영학과 리포트 생성
"""

import sys
import os
sys.path.append(os.getcwd())

from src.core.database import SessionLocal
from src.domain.models import University, Department, Professor, Laboratory, ResearchPaper, PaperAnalysis, User, Report
from src.services.llm import OllamaLLM, MockLLM
from src.services.pdf_generator import PDFGenerator
from src.domain.schemas import ResearchPaper as SchemaResearchPaper
from datetime import datetime, date
import uuid

def main():
    print("="*80)
    print("🎓 서울대 경영학과 리포트 생성")
    print("="*80)
    
    db = SessionLocal()
    
    try:
        # Find department
        dept = db.query(Department).filter(Department.name_ko.like('%경영%')).first()
        
        if not dept:
            print("❌ 경영학과를 찾을 수 없습니다.")
            return
        
        print(f"\n✅ 학과: {dept.name_ko}")
        print(f"   교수 수: {len(dept.professors)}")
        
        if len(dept.professors) == 0:
            print("❌ 교수 데이터가 없습니다.")
            return
        
        # Initialize LLM
        try:
            llm = OllamaLLM(model='qwen2:7b')
            print("   Using OllamaLLM")
        except:
            llm = MockLLM()
            print("   Using MockLLM")
        
        # Analyze professors
        print("\n[분석 중...]")
        
        for prof in dept.professors[:3]:
            print(f"\n   교수: {prof.name_ko}")
            
            # Create virtual paper
            interests = ", ".join(prof.research_interests) if prof.research_interests else "Business Research"
            paper = ResearchPaper(
                id=f"virtual-cba-{prof.id}",
                lab_id=prof.laboratories[0].id if prof.laboratories else None,
                title=f"{prof.name_ko} 교수님의 연구: {interests}",
                abstract=f"Research on {interests}",
                url=f"virtual://cba/{prof.id}",
                crawled_at=datetime.now()
            )
            db.add(paper)
            db.flush()
            
            # Check existing analysis
            existing = db.query(PaperAnalysis).filter(PaperAnalysis.paper_id == paper.id).first()
            if existing and existing.topic_easy:
                print(f"   ⏭️  이미 분석됨")
                continue
            
            # Analyze
            schema_paper = SchemaResearchPaper(
                id=paper.id,
                url=paper.url,
                title=paper.title,
                university="Seoul National University",
                department=dept.name,
                pub_date=date.today(),
                content_raw=paper.abstract
            )
            
            try:
                result = llm.analyze(schema_paper)
                print(f"   ✅ 분석 완료: {result.topic_easy}")
                
                # Save
                analysis = PaperAnalysis(
                    id=str(uuid.uuid4()),
                    paper_id=paper.id,
                    easy_summary=result.explanation,
                    technical_summary=f"Technical: {result.topic_technical}",
                    topic_easy=result.topic_easy,
                    topic_technical=result.topic_technical,
                    explanation=result.explanation,
                    reference_link=result.reference_link,
                    deep_dive={
                        "keywords": result.deep_dive.keywords,
                        "recommendations": result.deep_dive.recommendations,
                        "related_concepts": result.deep_dive.related_concepts
                    },
                    core_technologies=[],
                    required_skills=[],
                    math_concepts=result.deep_dive.related_concepts,
                    application_fields=[],
                    career_paths=result.career_path.companies,
                    recommended_companies=result.career_path.companies,
                    salary_range=result.career_path.avg_salary_hint,
                    job_roles=[result.career_path.job_title],
                    recommended_subjects=result.action_item.subjects,
                    action_items={"research_topic": result.action_item.research_topic},
                    learning_path=[],
                    analysis_model="qwen2:7b"
                )
                db.add(analysis)
                db.commit()
                print(f"   💾 저장 완료")
                
            except Exception as e:
                print(f"   ❌ 분석 실패: {e}")
                db.rollback()
        
        # Generate report
        print("\n[리포트 생성...]")
        
        # Get analyses
        analyses = db.query(PaperAnalysis).join(ResearchPaper).join(Laboratory).join(Professor).filter(
            Professor.department_id == dept.id
        ).all()
        
        if not analyses:
            print("❌ 분석 데이터 없음")
            return
        
        # Create user
        user_id = "cba-student"
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            user = User(
                id=user_id,
                name="경영학 관심 학생",
                role="student",
                interests=["Business", "Management", "Finance"]
            )
            db.add(user)
            db.commit()
        
        # Prepare data
        analysis_results = []
        for analysis in analyses:
            prof_name = "Unknown"
            if analysis.paper.laboratory and analysis.paper.laboratory.professor:
                prof_name = analysis.paper.laboratory.professor.name_ko
            
            analysis_results.append({
                "topic_easy": analysis.topic_easy or "연구 주제",
                "topic_technical": analysis.topic_technical or "Technical Topic",
                "explanation": analysis.explanation or analysis.easy_summary,
                "reference_link": analysis.reference_link or "",
                "deep_dive": analysis.deep_dive or {},
                "career_path": {
                    "job_title": analysis.job_roles[0] if analysis.job_roles else "Business Professional",
                    "companies": analysis.recommended_companies or [],
                    "avg_salary_hint": analysis.salary_range or "Unknown"
                },
                "action_item": {
                    "subjects": analysis.recommended_subjects or [],
                    "research_topic": analysis.action_items.get("research_topic", "") if analysis.action_items else ""
                },
                "professor_name": prof_name
            })
        
        # Generate PDF
        pdf_gen = PDFGenerator(output_dir="docs/reports")
        report_data = {
            "user_name": user.name,
            "interests": ", ".join(user.interests),
            "report_date": datetime.now().strftime("%Y-%m-%d"),
            "analysis_results": analysis_results
        }
        
        pdf_filename = f"SNU_Business_Report_{datetime.now().strftime('%Y%m%d')}.pdf"
        pdf_path = pdf_gen.generate(report_data, pdf_filename)
        
        print(f"\n✅ PDF 생성: {pdf_path}")
        
        # Save report
        report = Report(
            id=str(uuid.uuid4()),
            user_id=user.id,
            status="sent",
            content=f"서울대 경영학과 {len(analysis_results)}개 연구 분석",
            report_type="career_guide_progressive",
            pdf_path=pdf_path
        )
        db.add(report)
        db.commit()
        
        print("\n" + "="*80)
        print("✅ 완료!")
        print("="*80)
        print(f"📄 리포트: {pdf_path}")
        print(f"📊 분석 수: {len(analysis_results)}")
        
    except Exception as e:
        print(f"\n❌ 오류: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    main()
