#!/usr/bin/env python3
"""
서울대 경제학부 E2E 파이프라인
크롤링 → 분석 → 리포트 생성
"""

import sys
import os
sys.path.append(os.getcwd())

from src.core.database import SessionLocal
from src.domain.models import University, College, Department, Professor, Laboratory, ResearchPaper, PaperAnalysis, User, Report
from src.services.llm import OllamaLLM, MockLLM
from src.services.pdf_generator import PDFGenerator
from src.domain.schemas import ResearchPaper as SchemaResearchPaper
from datetime import datetime, date
import uuid

def run_economics_pipeline():
    print("="*80)
    print("🎓 서울대 경제학부 E2E 파이프라인")
    print("="*80)
    
    db = SessionLocal()
    
    try:
        # ==================== STEP 1: 데이터 확인 ====================
        print("\n[STEP 1] 서울대 경제학부 데이터 확인...")
        
        # Find SNU
        uni = db.query(University).filter(University.name.like("%Seoul%National%")).first()
        
        print(f"✅ 학과: {target_dept.name_ko}")
        print(f"   교수 수: {len(target_dept.professors)}")
        
        if len(target_dept.professors) == 0:
            print("❌ 교수 데이터가 없습니다. 먼저 크롤링을 실행하세요.")
            return
        
        # ==================== STEP 2: 논문 분석 ====================
        print("\n[STEP 2] 교수 연구 분석 중...")
        
        # Initialize LLM
        try:
            llm = OllamaLLM(model='qwen2:7b')
            print("   Using OllamaLLM (qwen2:7b)")
        except:
            llm = MockLLM()
            print("   Using MockLLM (fallback)")
        
        analyzed_count = 0
        
        for prof in target_dept.professors[:5]:  # Top 5 professors
            print(f"\n   교수: {prof.name_ko}")
            
            # Find or create paper
            paper = None
            if prof.laboratories:
                for lab in prof.laboratories:
                    if lab.papers:
                        paper = lab.papers[0]
                        break
            
            if not paper:
                # Create virtual paper from research interests
                interests = ", ".join(prof.research_interests) if prof.research_interests else "Economics Research"
                paper = ResearchPaper(
                    id=f"virtual-econ-{prof.id}",
                    lab_id=prof.laboratories[0].id if prof.laboratories else None,
                    title=f"{prof.name_ko} 교수님의 연구: {interests}",
                    abstract=f"Research on {interests}",
                    url=f"virtual://econ/{prof.id}",
                    crawled_at=datetime.now()
                )
                db.add(paper)
                db.flush()
                print(f"   ✅ 가상 논문 생성")
            
            # Check if already analyzed
            existing_analysis = db.query(PaperAnalysis).filter(PaperAnalysis.paper_id == paper.id).first()
            if existing_analysis and existing_analysis.topic_easy:
                print(f"   ⏭️  이미 분석됨")
                analyzed_count += 1
                continue
            
            # Convert to schema
            schema_paper = SchemaResearchPaper(
                id=paper.id,
                url=paper.url or "",
                title=paper.title,
                university=uni.name,
                department=target_dept.name,
                pub_date=paper.publication_date or date.today(),
                content_raw=paper.abstract or paper.title
            )
            
            # Analyze
            try:
                result = llm.analyze(schema_paper)
                print(f"   ✅ 분석 완료: {result.topic_easy}")
                
                # Save to DB
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
                analyzed_count += 1
                print(f"   💾 DB 저장 완료")
                
            except Exception as e:
                print(f"   ❌ 분석 실패: {e}")
                db.rollback()
                continue
        
        print(f"\n✅ 총 {analyzed_count}개 연구 분석 완료")
        
        # ==================== STEP 3: 사용자 생성 ====================
        print("\n[STEP 3] 사용자 생성...")
        
        user_id = "econ-student"
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            user = User(
                id=user_id,
                name="경제학 관심 학생",
                role="student",
                interests=["Economics", "Finance", "Policy"]
            )
            db.add(user)
            db.commit()
            print(f"✅ 사용자 생성: {user.name}")
        else:
            print(f"✅ 기존 사용자 사용: {user.name}")
        
        # ==================== STEP 4: 리포트 생성 ====================
        print("\n[STEP 4] 리포트 생성 중...")
        
        # Get analyzed papers for target department
        analyses = db.query(PaperAnalysis).join(ResearchPaper).join(Laboratory).join(Professor).filter(
            Professor.department_id == target_dept.id
        ).all()
        
        if not analyses:
            print("❌ 분석된 연구가 없습니다.")
            return
        
        print(f"   {len(analyses)}개의 분석 결과 사용")
        
        # Prepare report data
        analysis_results = []
        for analysis in analyses[:10]:  # Top 10
            prof_name = "Unknown"
            if analysis.paper.laboratory and analysis.paper.laboratory.professor:
                prof_name = analysis.paper.laboratory.professor.name_ko
            
            analysis_results.append({
                "topic_easy": analysis.topic_easy or "연구 주제",
                "topic_technical": analysis.topic_technical or "Technical Topic",
                "explanation": analysis.explanation or analysis.easy_summary,
                "reference_link": analysis.reference_link or "",
                "deep_dive": analysis.deep_dive or {
                    "keywords": [],
                    "recommendations": [],
                    "related_concepts": []
                },
                "career_path": {
                    "job_title": analysis.job_roles[0] if analysis.job_roles else "Economist",
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
        
        pdf_filename = f"SNU_Economics_Report_{datetime.now().strftime('%Y%m%d')}.pdf"
        pdf_path = pdf_gen.generate(report_data, pdf_filename)
        print(f"✅ PDF 생성 완료: {pdf_path}")
        
        # Save report to DB
        report = Report(
            id=str(uuid.uuid4()),
            user_id=user.id,
            status="sent",
            content=f"서울대 경제학부 {len(analysis_results)}개 연구 분석",
            report_type="career_guide_progressive",
            pdf_path=pdf_path
        )
        db.add(report)
        db.commit()
        print(f"✅ 리포트 DB 저장: {report.id}")
        
        # ==================== STEP 5: 결과 요약 ====================
        print("\n" + "="*80)
        print("✅ 서울대 경제학부 리포트 생성 완료!")
        print("="*80)
        print(f"\n📄 생성된 리포트: {pdf_path}")
        print(f"🎓 학과: {target_dept.name_ko}")
        print(f"👨‍🏫 교수 수: {len(target_dept.professors)}")
        print(f"📊 분석된 연구: {len(analysis_results)}개")
        print(f"👤 사용자: {user.name}")
        
        print("\n📋 포함된 연구 주제:")
        for i, result in enumerate(analysis_results[:5], 1):
            print(f"   {i}. {result['topic_easy']}")
            print(f"      교수: {result['professor_name']}")
        
        if len(analysis_results) > 5:
            print(f"   ... 외 {len(analysis_results) - 5}개")
        
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    run_economics_pipeline()
