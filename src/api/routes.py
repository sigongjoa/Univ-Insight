"""
FastAPI routes for Univ-Insight API.

Implements endpoints for:
- Hierarchical navigation (University → College → Department → Professor → Lab)
- Research paper listing and analysis
- Personalized report generation
- Plan B suggestions
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse
from src.services.pdf_generator import PDFGenerator
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List, Optional
import uuid
import ollama

from src.core.database import get_db
from src.domain.models import (
    University, College, Department, Professor, Laboratory, LabMember,
    ResearchPaper, PaperAnalysis, User, Report, UserRole, ReportStatus, ReportPaper, ReportProfessor
)
from src.services.recommendation import RecommendationService
from src.services.vector_store import VectorStore

router = APIRouter()

# Initialize services
vector_store = VectorStore()
recommendation_service = RecommendationService(vector_store)


# ==================== Hierarchical Navigation ====================

@router.get("/universities")
def list_universities(
    db: Session = Depends(get_db)
):
    """
    Get all universities.

    Returns list of universities with basic information.
    """
    universities = db.query(University).order_by(University.ranking).all()

    return {
        "total_count": len(universities),
        "items": [
            {
                "id": u.id,
                "name": u.name,
                "name_ko": u.name_ko,
                "location": u.location,
                "ranking": u.ranking,
                "tier": u.tier.name,
                "established_year": u.established_year,
                "college_count": len(u.colleges)
            }
            for u in universities
        ]
    }


@router.get("/universities/{uni_id}")
def get_university(
    uni_id: str,
    db: Session = Depends(get_db)
):
    """Get detailed university information"""
    university = db.query(University).filter(University.id == uni_id).first()

    if not university:
        raise HTTPException(status_code=404, detail="University not found")

    return {
        "id": university.id,
        "name": university.name,
        "name_ko": university.name_ko,
        "location": university.location,
        "ranking": university.ranking,
        "tier": university.tier.name,
        "url": university.url,
        "description": university.description,
        "established_year": university.established_year,
        "colleges": [
            {
                "id": c.id,
                "name": c.name,
                "name_ko": c.name_ko,
                "department_count": len(c.departments)
            }
            for c in university.colleges
        ]
    }


@router.get("/colleges/{college_id}")
def get_college(
    college_id: str,
    db: Session = Depends(get_db)
):
    """Get college and its departments"""
    college = db.query(College).filter(College.id == college_id).first()

    if not college:
        raise HTTPException(status_code=404, detail="College not found")

    return {
        "id": college.id,
        "name": college.name,
        "name_ko": college.name_ko,
        "university_id": college.university_id,
        "university_name": college.university.name_ko,
        "description": college.description,
        "established_year": college.established_year,
        "departments": [
            {
                "id": d.id,
                "name": d.name,
                "name_ko": d.name_ko,
                "faculty_count": d.faculty_count,
                "professor_count": len(d.professors)
            }
            for d in college.departments
        ]
    }


@router.get("/departments/{dept_id}")
def get_department(
    dept_id: str,
    db: Session = Depends(get_db)
):
    """Get department and its professors"""
    department = db.query(Department).filter(Department.id == dept_id).first()

    if not department:
        raise HTTPException(status_code=404, detail="Department not found")

    return {
        "id": department.id,
        "name": department.name,
        "name_ko": department.name_ko,
        "college_id": department.college_id,
        "college_name": department.college.name_ko,
        "university_name": department.college.university.name_ko,
        "faculty_count": department.faculty_count,
        "website": department.website,
        "description": department.description,
        "established_year": department.established_year,
        "professors": [
            {
                "id": p.id,
                "name": p.name,
                "name_ko": p.name_ko,
                "title": p.title,
                "email": p.email,
                "h_index": p.h_index,
                "publications_count": p.publications_count,
                "lab_count": len(p.laboratories),
                "research_preview": _get_research_preview(p, db)  # NEW: Easy preview
            }
            for p in department.professors
        ]
    }


def _get_research_preview(professor: Professor, db: Session) -> dict:
    """Get a preview of professor's research in easy-to-understand language"""
    # Find the first analyzed paper
    for lab in professor.laboratories:
        for paper in lab.papers[:1]:  # Just the first paper
            analysis = db.query(PaperAnalysis).filter(PaperAnalysis.paper_id == paper.id).first()
            if analysis and analysis.topic_easy:
                return {
                    "topic_easy": analysis.topic_easy,
                    "explanation_preview": analysis.explanation[:200] + "..." if analysis.explanation and len(analysis.explanation) > 200 else analysis.explanation
                }
    
    # Fallback to research interests
    if professor.research_interests:
        return {
            "topic_easy": ", ".join(professor.research_interests[:2]),
            "explanation_preview": "이 분야의 연구를 진행하고 있습니다."
        }
    
    return {
        "topic_easy": "연구 정보 준비 중",
        "explanation_preview": ""
    }


@router.get("/professors/{prof_id}")
def get_professor(
    prof_id: str,
    db: Session = Depends(get_db)
):
    """Get professor and their laboratories with easy-to-understand research explanations"""
    professor = db.query(Professor).filter(Professor.id == prof_id).first()

    if not professor:
        raise HTTPException(status_code=404, detail="Professor not found")

    # Get research analysis for this professor's papers
    research_explanations = []
    
    for lab in professor.laboratories:
        for paper in lab.papers[:3]:  # Top 3 papers per lab
            # Check if we have analysis
            analysis = db.query(PaperAnalysis).filter(PaperAnalysis.paper_id == paper.id).first()
            
            if analysis and analysis.topic_easy:
                research_explanations.append({
                    "topic_easy": analysis.topic_easy,
                    "topic_technical": analysis.topic_technical,
                    "explanation": analysis.explanation,
                    "reference_link": analysis.reference_link,
                    "deep_dive": analysis.deep_dive,
                    "paper_title": paper.title,
                    "paper_id": paper.id
                })

    return {
        "id": professor.id,
        "name": professor.name,
        "name_ko": professor.name_ko,
        "department_id": professor.department_id,
        "department_name": professor.department.name_ko,
        "title": professor.title,
        "email": professor.email,
        "phone": professor.phone,
        "research_interests": professor.research_interests,
        "research_explanations": research_explanations,  # NEW: Easy explanations
        "education": professor.education,
        "h_index": professor.h_index,
        "publications_count": professor.publications_count,
        "profile_url": professor.profile_url,
        "bio": professor.bio,
        "laboratories": [
            {
                "id": l.id,
                "name": l.name,
                "name_ko": l.name_ko,
                "research_areas": l.research_areas,
                "member_count": l.member_count,
                "paper_count": len(l.papers)
            }
            for l in professor.laboratories
        ]
    }


@router.get("/laboratories/{lab_id}")
def get_laboratory(
    lab_id: str,
    db: Session = Depends(get_db)
):
    """Get laboratory details with members and papers"""
    laboratory = db.query(Laboratory).filter(Laboratory.id == lab_id).first()

    if not laboratory:
        raise HTTPException(status_code=404, detail="Laboratory not found")

    return {
        "id": laboratory.id,
        "name": laboratory.name,
        "name_ko": laboratory.name_ko,
        "professor_id": laboratory.professor_id,
        "professor_name": laboratory.professor.name_ko,
        "department_id": laboratory.department_id,
        "department_name": laboratory.department.name_ko,
        "research_areas": laboratory.research_areas,
        "description": laboratory.description,
        "established_year": laboratory.established_year,
        "member_count": laboratory.member_count,
        "website": laboratory.website,
        "email": laboratory.email,
        "location": laboratory.location,
        "current_projects": laboratory.current_projects,
        "funding_info": laboratory.funding_info,
        "facilities": laboratory.facilities,
        "members": [
            {
                "id": m.id,
                "name": m.name,
                "name_ko": m.name_ko,
                "role": m.role.value,
                "email": m.email,
                "research_topic": m.research_topic,
                "joined_year": m.joined_year,
                "status": m.status
            }
            for m in laboratory.members
        ],
        "papers": [
            {
                "id": p.id,
                "title": p.title,
                "authors": p.authors,
                "publication_year": p.publication_year,
                "venue": p.venue,
                "citation_count": p.citation_count,
                "url": p.url
            }
            for p in laboratory.papers
        ]
    }


# ==================== User Management ====================

@router.post("/users/profile")
def create_or_update_user(
    user_id: str,
    name: str,
    role: str,
    interests: List[str] = [],
    db: Session = Depends(get_db)
):
    """
    Create or update user profile with interests.

    Args:
        user_id: Kakao ID or UUID
        name: User name
        role: "student" or "parent"
        interests: List of interests (e.g., ["AI", "Biology"])
    """
    # Validate role
    if role not in ["student", "parent"]:
        raise HTTPException(status_code=400, detail="Invalid role")

    # Check if user exists
    user = db.query(User).filter(User.id == user_id).first()

    if user:
        # Update existing user
        user.name = name
        user.role = UserRole[role.upper()]
        user.interests = interests
    else:
        # Create new user
        user = User(
            id=user_id,
            name=name,
            role=UserRole[role.upper()],
            interests=interests
        )
        db.add(user)

    db.commit()
    return {"status": "success", "user_id": user.id}


@router.get("/users/{user_id}")
def get_user_profile(
    user_id: str,
    db: Session = Depends(get_db)
):
    """Get user profile information"""
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "id": user.id,
        "name": user.name,
        "role": user.role.value,
        "interests": user.interests,
        "created_at": user.created_at.isoformat()
    }


# ==================== Research Data ====================

@router.get("/papers")
def list_research_papers(
    lab_id: Optional[str] = Query(None),
    topic: Optional[str] = Query(None),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """
    List research papers with optional filtering.

    Args:
        lab_id: Filter by laboratory ID
        topic: Filter by topic (searches in title and keywords)
        limit: Number of results to return
        offset: Pagination offset
    """
    query = db.query(ResearchPaper)

    # Apply filters
    if lab_id:
        query = query.filter(ResearchPaper.lab_id == lab_id)

    if topic:
        query = query.filter(
            (ResearchPaper.title.ilike(f"%{topic}%")) |
            (ResearchPaper.abstract.ilike(f"%{topic}%"))
        )

    # Get total count
    total_count = query.count()

    # Apply pagination
    papers = query.order_by(ResearchPaper.crawled_at.desc()).offset(offset).limit(limit).all()

    return {
        "total_count": total_count,
        "items": [
            {
                "id": p.id,
                "title": p.title,
                "authors": p.authors,
                "lab_id": p.lab_id,
                "publication_year": p.publication_year,
                "venue": p.venue,
                "citation_count": p.citation_count,
                "keywords": p.keywords
            }
            for p in papers
        ]
    }


@router.get("/papers/{paper_id}")
def get_research_paper(
    paper_id: str,
    db: Session = Depends(get_db)
):
    """Get detailed research paper information"""
    paper = db.query(ResearchPaper).filter(ResearchPaper.id == paper_id).first()

    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")

    return {
        "id": paper.id,
        "title": paper.title,
        "authors": paper.authors,
        "abstract": paper.abstract,
        "lab_id": paper.lab_id,
        "lab_name": paper.laboratory.name_ko if paper.laboratory else None,
        "publication_year": paper.publication_year,
        "venue": paper.venue,
        "venue_type": paper.venue_type,
        "citation_count": paper.citation_count,
        "doi": paper.doi,
        "url": paper.url,
        "pdf_url": paper.pdf_url,
    }


@router.get("/universities/{uni_id}/papers")
def get_university_papers(
    uni_id: str,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """
    Get papers crawled for a specific university.
    
    Note: Currently papers are not directly linked to universities,
    so we return all recently crawled papers as a demo.
    In production, add a university_id field to ResearchPaper model.
    """
    # For now, return all papers ordered by crawl date
    # TODO: Filter by university when schema is updated
    query = db.query(ResearchPaper).order_by(ResearchPaper.crawled_at.desc())
    
    total_count = query.count()
    papers = query.offset(offset).limit(limit).all()
    
    return {
        "total_count": total_count,
        "items": [
            {
                "id": p.id,
                "title": p.title,
                "url": p.url,
                "abstract": p.abstract[:200] if p.abstract else None,
                "crawled_at": p.crawled_at.isoformat() if p.crawled_at else None,
                "keywords": p.keywords
            }
            for p in papers
        ]
    }


@router.get("/departments/{dept_id}/research")
def get_department_research(
    dept_id: str,
    db: Session = Depends(get_db)
):
    """
    Get organized research information (professors and labs) for a department.
    """
    dept = db.query(Department).filter(Department.id == dept_id).first()
    if not dept:
        raise HTTPException(status_code=404, detail="Department not found")

    # Get professors
    professors = db.query(Professor).filter(Professor.department_id == dept_id).all()
    
    # Get labs
    labs = db.query(Laboratory).filter(Laboratory.department_id == dept_id).all()
    
    return {
        "department": {
            "id": dept.id,
            "name": dept.name,
            "name_ko": dept.name_ko,
            "website": dept.website
        },
        "professors": [
            {
                "id": p.id,
                "name": p.name,
                "name_ko": p.name_ko,
                "email": p.email,
                "profile_url": p.profile_url,
                "research_interests": p.research_interests
            }
            for p in professors
        ],
        "laboratories": [
            {
                "id": l.id,
                "name": l.name,
                "description": l.description,
                "professor_name": l.professor.name if l.professor else None
            }
            for l in labs
        ]
    }



@router.get("/papers/{paper_id}/analysis")
def get_paper_analysis(
    paper_id: str,
    db: Session = Depends(get_db)
):
    """Get detailed LLM analysis for a research paper"""
    paper = db.query(ResearchPaper).filter(ResearchPaper.id == paper_id).first()

    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")

    analysis = db.query(PaperAnalysis).filter(
        PaperAnalysis.paper_id == paper_id
    ).first()

    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")

    return {
        "paper_id": paper.id,
        "title": paper.title,
        "authors": paper.authors,
        "analysis": {
            "easy_summary": analysis.easy_summary,
            "technical_summary": analysis.technical_summary,
            "core_technologies": analysis.core_technologies,
            "required_skills": analysis.required_skills,
            "math_concepts": analysis.math_concepts,
            "application_fields": analysis.application_fields,
            "industry_relevance": analysis.industry_relevance,
            "career_paths": analysis.career_paths,
            "recommended_companies": analysis.recommended_companies,
            "job_roles": analysis.job_roles,
            "recommended_subjects": analysis.recommended_subjects,
            "action_items": analysis.action_items,
            "learning_path": analysis.learning_path,
            "limitations": analysis.limitations,
            "challenges": analysis.challenges
        }
    }


@router.post("/users/{user_id}/reports")
def create_report(
    user_id: str,
    db: Session = Depends(get_db)
):
    """
    Generate personalized report for a user based on interests.
    Recommends professors and labs, and generates a summary using LLM.
    """
    # Get user
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not user.interests:
        raise HTTPException(
            status_code=400,
            detail="User has no interests set"
        )

    # 1. Find Professors matching interests
    all_profs = db.query(Professor).all()
    matched_profs = []
    
    for prof in all_profs:
        score = 0
        prof_interests = prof.research_interests or []
        if isinstance(prof_interests, str):
            prof_interests = [prof_interests]
            
        for user_interest in user.interests:
            for prof_interest in prof_interests:
                if user_interest.lower() in str(prof_interest).lower():
                    score += 1
        
        if score > 0:
            matched_profs.append((prof, score))
    
    # Sort by score
    matched_profs.sort(key=lambda x: x[1], reverse=True)
    top_profs = matched_profs[:5]
    
    if not top_profs:
        # Fallback: Just pick some professors if no match found (for demo)
        top_profs = [(p, 0) for p in all_profs[:3]]

    # 2. Generate Report Content with LLM (Progressive Disclosure)
    from src.services.llm import OllamaLLM, MockLLM
    from src.domain.schemas import ResearchPaper as SchemaResearchPaper
    
    analysis_results = []
    report_content = "" # Fallback content

    try:
        llm = OllamaLLM(model='qwen2.5:14b') # Use high quality model
        # Check if we can connect, else fallback
        # In production, we might want a better check or dependency injection
    except:
        llm = MockLLM()

    print(f"Generating report for {len(top_profs)} professors...")

    for prof, score in top_profs:
        try:
            # Try to find a real paper
            target_paper = None
            
            # Look for papers in professor's labs
            for lab in prof.laboratories:
                if lab.papers:
                    # Pick the most recent or relevant paper
                    # For now, just pick the first one
                    db_paper = lab.papers[0]
                    target_paper = SchemaResearchPaper(
                        id=db_paper.id,
                        url=db_paper.url or "",
                        title=db_paper.title,
                        university=prof.department.college.university.name,
                        department=prof.department.name,
                        pub_date=db_paper.publication_date,
                        content_raw=db_paper.abstract or db_paper.title
                    )
                    break
            
            # If no paper found, create a virtual one from interests
            if not target_paper:
                interests_str = ", ".join(prof.research_interests) if prof.research_interests else "General AI"
                target_paper = SchemaResearchPaper(
                    id=f"prof-{prof.id}-virtual",
                    url="",
                    title=f"{prof.name} 교수님의 연구: {interests_str}",
                    university=prof.department.college.university.name if prof.department else "Unknown",
                    department=prof.department.name if prof.department else "Unknown",
                    content_raw=f"Research interests include: {interests_str}. {prof.bio or ''}"
                )

            # Analyze
            print(f"Analyzing for {prof.name}: {target_paper.title}")
            try:
                result = llm.analyze(target_paper)
            except Exception as e:
                print(f"LLM Analysis failed for {prof.name}, using Mock: {e}")
                mock_llm = MockLLM()
                result = mock_llm.analyze(target_paper)
                
            # Add professor name to the result for the report context
            # We might need to inject this into the result or handle it in the template
            # For now, let's assume the template uses the fields we have.
            # We can prepend the professor name to the topic_easy if needed, 
            # or better, add it to the report_data structure below.
            
            # Convert Pydantic model to dict for JSON serialization
            result_dict = result.dict()
            result_dict["professor_name"] = prof.name
            result_dict["professor_id"] = prof.id
            analysis_results.append(result_dict)

        except Exception as e:
            print(f"Error processing professor {prof.name}: {e}")
            continue

    # 3. Create report
    # We'll store a simple summary in the content field for fallback/preview
    report_content = f"맞춤형 리포트가 생성되었습니다. {len(analysis_results)}개의 연구 분야 분석이 포함되어 있습니다."

    report = Report(
        id=str(uuid.uuid4()),
        user_id=user_id,
        status=ReportStatus.SENT,
        content=report_content,
        report_type="career_guide_progressive"
    )
    db.add(report)
    db.flush()

    # 4. Link Professors
    for prof, score in top_profs:
        rp = ReportProfessor(
            id=str(uuid.uuid4()),
            report_id=report.id,
            professor_id=prof.id,
            relevance_score=float(score),
            reason=f"Matched interests: {user.interests}"
        )
        db.add(rp)

    db.commit()

    # 5. Generate PDF
    pdf_url = None
    try:
        pdf_gen = PDFGenerator()
        
        # Prepare data for Typst template
        # The template expects 'analysis_results'
        report_data = {
            "user_name": user.name,
            "interests": ", ".join(user.interests),
            "report_date": datetime.now().strftime("%Y-%m-%d"),
            "analysis_results": analysis_results
        }
        
        pdf_filename = f"report_{report.id}.pdf"
        pdf_path = pdf_gen.generate(report_data, pdf_filename)
        
        report.pdf_path = pdf_path
        db.commit()
        pdf_url = f"/api/v1/reports/{report.id}/download"
        
    except Exception as e:
        print(f"PDF Generation Failed: {e}")
        import traceback
        traceback.print_exc()

    return {
        "status": "success",
        "report_id": report.id,
        "content": report_content,
        "pdf_url": pdf_url,
        "recommendations": [
            {
                "professor": p.name,
                "score": s,
                "interests": p.research_interests
            }
            for p, s in top_profs
        ]
    }


@router.get("/reports/{report_id}/download")
def download_report(
    report_id: str,
    db: Session = Depends(get_db)
):
    """Download report as PDF"""
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report or not report.pdf_path:
        raise HTTPException(status_code=404, detail="Report PDF not found")
        
    return FileResponse(
        report.pdf_path, 
        media_type="application/pdf", 
        filename=f"UnivInsight_Report_{report_id[:8]}.pdf"
    )


@router.get("/reports/{report_id}")
def get_report(
    report_id: str,
    db: Session = Depends(get_db)
):
    """Get detailed report information"""
    report = db.query(Report).filter(Report.id == report_id).first()

    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    return {
        "id": report.id,
        "user_id": report.user_id,
        "status": report.status.value,
        "sent_at": report.sent_at.isoformat(),
        "content": report.content,
        "report_type": report.report_type,
        "papers": [
            {
                "paper_id": rp.paper.id,
                "title": rp.paper.title,
                "authors": rp.paper.authors,
                "publication_year": rp.paper.publication_year,
                "venue": rp.paper.venue,
                "order": rp.order_index
            }
            for rp in report.papers
        ],
        "professors": [
            {
                "professor_id": rp.professor.id,
                "name": rp.professor.name,
                "name_ko": rp.professor.name_ko,
                "relevance_score": rp.relevance_score,
                "reason": rp.reason
            }
            for rp in report.professors
        ]
    }


@router.get("/laboratories/{lab_id}/plan-b")
def get_plan_b_suggestions(
    lab_id: str,
    db: Session = Depends(get_db)
):
    """
    Get Plan B (fallback) laboratory suggestions with similar research areas.

    Returns labs from other universities with similar research topics.
    """
    laboratory = db.query(Laboratory).filter(Laboratory.id == lab_id).first()

    if not laboratory:
        raise HTTPException(status_code=404, detail="Laboratory not found")

    # Find labs with similar research areas from different universities
    similar_labs = db.query(Laboratory).filter(
        Laboratory.id != lab_id,
        Laboratory.department.has(Department.college.has(College.university_id != laboratory.department.college.university_id))
    ).limit(5).all()

    return {
        "original_lab": {
            "id": laboratory.id,
            "name": laboratory.name_ko,
            "university": laboratory.department.college.university.name_ko,
            "research_areas": laboratory.research_areas
        },
        "plan_b_suggestions": [
            {
                "id": l.id,
                "name": l.name_ko,
                "university": l.department.college.university.name_ko,
                "professor": l.professor.name_ko,
                "research_areas": l.research_areas
            }
            for l in similar_labs
        ]
    }


# ==================== Admin ====================

from pydantic import BaseModel
from fastapi import BackgroundTasks
from src.services.crawler import UniversityCrawler

class CrawlRequest(BaseModel):
    university_id: str
    target_url: Optional[str] = None


def run_crawler_task(university_id: str, target_url: str, db_session_maker):
    """Background task to run crawler"""
    print(f"Starting background crawl for {university_id} at {target_url}")
    
    # Create a new DB session for this background task
    from src.core.database import SessionLocal
    db = SessionLocal()
    
    try:
        crawler = UniversityCrawler()
        # Note: crawler.crawl returns a ResearchPaper schema object, not ORM model
        result = crawler.crawl(target_url)
        
        if result:
            print(f"Successfully crawled: {result.title}")
            
            # Get university to link the paper
            university = db.query(University).filter(University.id == university_id).first()
            
            if university:
                # Create ResearchPaper ORM model from schema
                from src.domain.models import ResearchPaper
                import uuid
                
                db_paper = ResearchPaper(
                    id=str(uuid.uuid4()),
                    lab_id=None,  # We don't have lab info yet
                    title=result.title,
                    authors=[],  # Will be extracted later
                    abstract=result.content_raw[:500] if result.content_raw else None,
                    url=result.url,
                    keywords=[],
                    full_text=result.content_raw,
                    crawled_at=result.crawled_at
                )
                
                db.add(db_paper)
                db.commit()
                print(f"✅ Saved paper to DB: {db_paper.id}")
            else:
                print(f"⚠️ University not found: {university_id}")
        else:
            # This block might not be reached if crawl raises exception, which is good
            print("❌ Crawling failed - no result returned")
            
    except Exception as e:
        print(f"\n{'='*50}")
        print(f"❌ CRITICAL ERROR IN CRAWLER TASK")
        print(f"Target: {target_url} (Univ: {university_id})")
        print(f"Error: {str(e)}")
        print(f"{'='*50}\n")
        import traceback
        traceback.print_exc()
        db.rollback()
        # Re-raise exception to ensure it's recorded as a task failure if monitored
        raise e
    finally:
        db.close()

@router.post("/admin/crawl")
def trigger_crawler(
    request: CrawlRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Trigger crawling job for a university.
    """
    # Get university to find URL if not provided
    university = db.query(University).filter(University.id == request.university_id).first()
    if not university:
        raise HTTPException(status_code=404, detail="University not found")
        
    target_url = request.target_url or university.url
    if not target_url:
        raise HTTPException(status_code=400, detail="No URL found for university")

    # Add to background tasks
    background_tasks.add_task(run_crawler_task, request.university_id, target_url, db)

    return {
        "status": "queued",
        "university_id": request.university_id,
        "target_url": target_url,
        "message": "Crawling job has been queued"
    }
