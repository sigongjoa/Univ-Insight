"""
FastAPI routes for Univ-Insight API.

Implements endpoints for:
- User management
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
    ResearchPaper, AnalysisResult, User, Report, UserRole, ReportStatus
)
from src.services.recommendation import RecommendationService
from src.services.vector_store import VectorStore

router = APIRouter()

# Initialize services
vector_store = VectorStore()
recommendation_service = RecommendationService(vector_store)


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

@router.get("/research")
def list_research_papers(
    university: Optional[str] = Query(None),
    topic: Optional[str] = Query(None),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """
    List research papers with optional filtering.

    Args:
        university: Filter by university (e.g., "KAIST", "SNU")
        topic: Filter by topic (searches in title and content)
        limit: Number of results to return
        offset: Pagination offset
    """
    query = db.query(ResearchPaper)

    # Apply filters
    if university:
        query = query.filter(ResearchPaper.university == university)

    if topic:
        query = query.filter(
            (ResearchPaper.title.ilike(f"%{topic}%")) |
            (ResearchPaper.content_raw.ilike(f"%{topic}%"))
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
                "university": p.university,
                "date": p.pub_date.isoformat() if p.pub_date else None,
                "summary_preview": p.content_raw[:200]
            }
            for p in papers
        ]
    }


@router.get("/research/{paper_id}/analysis")
def get_research_analysis(
    paper_id: str,
    db: Session = Depends(get_db)
):
    """Get detailed LLM analysis for a research paper"""
    paper = db.query(ResearchPaper).filter(ResearchPaper.id == paper_id).first()

    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")

    analysis = db.query(AnalysisResult).filter(
        AnalysisResult.paper_id == paper_id
    ).first()

    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")

    return {
        "paper_id": paper.id,
        "title": paper.title,
        "university": paper.university,
        "analysis": {
            "easy_summary": analysis.summary,
            "career_path": {
                "companies": analysis.related_companies or [],
                "job_title": analysis.job_title,
                "salary_hint": analysis.salary_hint
            },
            "action_item": analysis.action_items or {}
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

    recommendations = recommendation_service.get_papers_for_user(
        db=db,
        interests=user.interests,
        top_k=5
    )

    if not recommendations:
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
    from src.domain.models import ReportPaper
    for rec in recommendations:
        report_paper = ReportPaper(
            report_id=report.id,
            paper_id=rec["paper_id"]
        )
        db.add(report_paper)

    db.commit()

    return {
        "status": "success",
        "report_id": report.id,
        "papers": [
            {
                "paper_id": rec["paper_id"],
                "title": rec["title"],
                "summary": rec["summary"][:200]
            }
            for rec in recommendations
        ]
    }


@router.get("/research/{paper_id}/plan-b")
def get_plan_b_suggestions(
    paper_id: str,
    db: Session = Depends(get_db)
):
    """
    Get Plan B (fallback) university suggestions for a paper.

    Returns papers with similar research topics from more accessible universities.
    """
    paper = db.query(ResearchPaper).filter(ResearchPaper.id == paper_id).first()

    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")

    suggestions = recommendation_service.get_plan_b_suggestions(
        db=db,
        paper_id=paper_id,
        similarity_threshold=0.8
    )

    return {
        "original_paper": {
            "title": paper.title,
            "university": paper.university,
            "university_tier": paper.university_tier.value if paper.university_tier else None
        },
        "plan_b_suggestions": suggestions
    }


# ==================== Admin ====================

@router.post("/admin/crawl")
def trigger_crawler(
    target: str = "KAIST_CS",
    db: Session = Depends(get_db)
):
    """
    Trigger manual crawling job.

    Args:
        target: Crawler target (e.g., "KAIST_CS", "SNU_CS")
    """
    # This is a placeholder for crawler integration
    # In production, this would trigger a background job

    return {
        "status": "queued",
        "target": target,
        "message": "Crawling job has been queued"
    }
