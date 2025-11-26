"""
FastAPI routes for Univ-Insight API.

Implements endpoints for:
- Hierarchical navigation (University → College → Department → Professor → Lab)
- Research paper listing and analysis
- Personalized report generation
- Plan B suggestions
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List, Optional
import uuid

from src.core.database import get_db
from src.domain.models import (
    University, College, Department, Professor, Laboratory, LabMember,
    ResearchPaper, PaperAnalysis, User, Report, UserRole, ReportStatus, ReportPaper
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
                "lab_count": len(p.laboratories)
            }
            for p in department.professors
        ]
    }


@router.get("/professors/{prof_id}")
def get_professor(
    prof_id: str,
    db: Session = Depends(get_db)
):
    """Get professor and their laboratories"""
    professor = db.query(Professor).filter(Professor.id == prof_id).first()

    if not professor:
        raise HTTPException(status_code=404, detail="Professor not found")

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
            "salary_range": analysis.salary_range,
            "job_roles": analysis.job_roles,
            "recommended_subjects": analysis.recommended_subjects,
            "action_items": analysis.action_items,
            "learning_path": analysis.learning_path,
            "limitations": analysis.limitations,
            "challenges": analysis.challenges
        }
    }


# ==================== Recommendations & Reports ====================

@router.post("/reports/generate")
def generate_personalized_report(
    user_id: str,
    db: Session = Depends(get_db)
):
    """
    Generate personalized report for a user based on interests.

    Returns list of recommended papers and creates a report record.
    """
    # Get user
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Get recommendations
    if not user.interests:
        raise HTTPException(
            status_code=400,
            detail="User has no interests set"
        )

    # Get papers matching user interests
    papers = db.query(ResearchPaper).filter(
        ResearchPaper.keywords.overlap(user.interests)
    ).limit(5).all()

    if not papers:
        raise HTTPException(
            status_code=404,
            detail="No matching papers found"
        )

    # Create report
    report = Report(
        id=str(uuid.uuid4()),
        user_id=user_id,
        status=ReportStatus.SENT
    )
    db.add(report)
    db.flush()

    # Add papers to report (through ReportPaper junction table)
    for idx, paper in enumerate(papers):
        report_paper = ReportPaper(
            id=str(uuid.uuid4()),
            report_id=report.id,
            paper_id=paper.id,
            order_index=idx
        )
        db.add(report_paper)

    db.commit()

    return {
        "status": "success",
        "report_id": report.id,
        "papers": [
            {
                "paper_id": p.id,
                "title": p.title,
                "authors": p.authors,
                "publication_year": p.publication_year,
                "venue": p.venue
            }
            for p in papers
        ]
    }


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
            print("❌ Crawling failed - no result returned")
            
    except Exception as e:
        print(f"❌ Error in crawler task: {str(e)}")
        import traceback
        traceback.print_exc()
        db.rollback()
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
