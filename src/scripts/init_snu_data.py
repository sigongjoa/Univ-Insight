#!/usr/bin/env python
"""
Initialize Seoul National University Data in Database

This script crawls SNU data using SNUCrawler and populates it into the database.
It creates the complete hierarchical structure:
- University → College → Department → Professor → Laboratory → Papers
"""

import sys
from pathlib import Path
from typing import Dict, List

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy.orm import Session
from src.core.database import SessionLocal, init_db
from src.domain.models import (
    University, College, Department, Professor, Laboratory, LabMember,
    ResearchPaper, PaperAnalysis, UniversityTier, LabMemberRole
)
from src.services.snu_crawler import SNUCrawler
import logging
from datetime import datetime, date

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_university(db: Session, uni_data: Dict) -> University:
    """Create university record"""
    university = University(
        id=uni_data["id"],
        name=uni_data["name"],
        name_ko=uni_data["name_ko"],
        location=uni_data.get("location"),
        ranking=uni_data.get("ranking"),
        tier=UniversityTier[uni_data.get("tier", "TOP")],
        url=uni_data.get("url"),
        description=uni_data.get("description"),
        established_year=uni_data.get("established_year"),
        crawled_at=datetime.utcnow()
    )
    db.add(university)
    db.flush()
    return university


def create_college(db: Session, college_data: Dict) -> College:
    """Create college record"""
    college = College(
        id=college_data["id"],
        university_id=college_data["university_id"],
        name=college_data["name"],
        name_ko=college_data["name_ko"],
        description=college_data.get("description"),
        established_year=college_data.get("established_year"),
        crawled_at=datetime.utcnow()
    )
    db.add(college)
    db.flush()
    return college


def create_department(db: Session, dept_data: Dict) -> Department:
    """Create department record"""
    department = Department(
        id=dept_data["id"],
        college_id=dept_data["college_id"],
        name=dept_data["name"],
        name_ko=dept_data["name_ko"],
        faculty_count=dept_data.get("faculty_count"),
        description=dept_data.get("description"),
        established_year=dept_data.get("established_year"),
        website=dept_data.get("website"),
        crawled_at=datetime.utcnow()
    )
    db.add(department)
    db.flush()
    return department


def create_professor(db: Session, prof_data: Dict) -> Professor:
    """Create professor record"""
    professor = Professor(
        id=prof_data["id"],
        department_id=prof_data["department_id"],
        name=prof_data["name"],
        name_ko=prof_data["name_ko"],
        email=prof_data.get("email"),
        phone=prof_data.get("phone"),
        title=prof_data.get("title", "Professor"),
        research_interests=prof_data.get("research_interests", []),
        education=prof_data.get("education", {}),
        h_index=prof_data.get("h_index"),
        publications_count=prof_data.get("publications_count"),
        profile_url=prof_data.get("profile_url"),
        profile_image_url=prof_data.get("profile_image_url"),
        bio=prof_data.get("bio"),
        crawled_at=datetime.utcnow()
    )
    db.add(professor)
    db.flush()
    return professor


def create_laboratory(db: Session, lab_data: Dict) -> Laboratory:
    """Create laboratory record"""
    laboratory = Laboratory(
        id=lab_data["id"],
        professor_id=lab_data["professor_id"],
        department_id=lab_data["department_id"],
        name=lab_data["name"],
        name_ko=lab_data["name_ko"],
        research_areas=lab_data.get("research_areas", []),
        description=lab_data.get("description"),
        established_year=lab_data.get("established_year"),
        member_count=lab_data.get("member_count"),
        website=lab_data.get("website"),
        email=lab_data.get("email"),
        location=lab_data.get("location"),
        current_projects=lab_data.get("current_projects", []),
        funding_info=lab_data.get("funding_info", {}),
        facilities=lab_data.get("facilities", []),
        crawled_at=datetime.utcnow()
    )
    db.add(laboratory)
    db.flush()
    return laboratory


def create_lab_member(db: Session, member_data: Dict) -> LabMember:
    """Create lab member record"""
    member = LabMember(
        id=member_data["id"],
        lab_id=member_data["lab_id"],
        name=member_data["name"],
        name_ko=member_data["name_ko"],
        email=member_data.get("email"),
        role=LabMemberRole[member_data["role"]],
        research_topic=member_data.get("research_topic"),
        joined_year=member_data.get("joined_year"),
        status=member_data.get("status", "active"),
        profile_url=member_data.get("profile_url"),
        crawled_at=datetime.utcnow()
    )
    db.add(member)
    db.flush()
    return member


def create_research_paper(db: Session, paper_data: Dict) -> ResearchPaper:
    """Create research paper record"""
    paper = ResearchPaper(
        id=paper_data["id"],
        lab_id=paper_data.get("lab_id"),
        title=paper_data["title"],
        authors=paper_data.get("authors", []),
        abstract=paper_data.get("abstract"),
        publication_year=paper_data.get("publication_year"),
        publication_date=paper_data.get("publication_date"),
        venue=paper_data.get("venue"),
        venue_type=paper_data.get("venue_type"),
        citation_count=paper_data.get("citation_count", 0),
        doi=paper_data.get("doi"),
        url=paper_data.get("url"),
        pdf_url=paper_data.get("pdf_url"),
        keywords=paper_data.get("keywords", []),
        full_text=paper_data.get("full_text"),
        crawled_at=datetime.utcnow()
    )
    db.add(paper)
    db.flush()
    return paper


def create_paper_analysis(db: Session, paper_id: str, analysis_data: Dict) -> PaperAnalysis:
    """Create paper analysis record"""
    analysis = PaperAnalysis(
        paper_id=paper_id,
        easy_summary=analysis_data.get("easy_summary", ""),
        technical_summary=analysis_data.get("technical_summary"),
        core_technologies=analysis_data.get("core_technologies", []),
        required_skills=analysis_data.get("required_skills", []),
        math_concepts=analysis_data.get("math_concepts", []),
        application_fields=analysis_data.get("application_fields", []),
        industry_relevance=analysis_data.get("industry_relevance"),
        career_paths=analysis_data.get("career_paths", []),
        recommended_companies=analysis_data.get("recommended_companies", []),
        salary_range=analysis_data.get("salary_range"),
        job_roles=analysis_data.get("job_roles", []),
        recommended_subjects=analysis_data.get("recommended_subjects", []),
        action_items=analysis_data.get("action_items", {}),
        learning_path=analysis_data.get("learning_path", []),
        limitations=analysis_data.get("limitations"),
        challenges=analysis_data.get("challenges", []),
        analyzed_at=datetime.utcnow(),
        analysis_model="mock-crawler"
    )
    db.add(analysis)
    db.flush()
    return analysis


def populate_snu_data(db: Session):
    """Populate SNU data from crawler into database"""
    logger.info("=" * 80)
    logger.info("🚀 Starting SNU Data Population")
    logger.info("=" * 80)

    # Get crawled data
    crawler = SNUCrawler()
    snu_data = crawler.crawl_snu_complete()

    # 1. Create University
    logger.info("\n📍 Creating University...")
    university = create_university(db, snu_data["university"])
    logger.info(f"  ✅ University created: {university.name_ko} ({university.id})")

    # 2. Create Colleges and nested structures
    college_count = 0
    dept_count = 0
    prof_count = 0
    lab_count = 0
    member_count = 0
    paper_count = 0

    for college_data in snu_data["colleges"]:
        # Create College
        college = create_college(db, college_data["college"])
        college_count += 1
        logger.info(f"\n📚 College created: {college.name_ko}")

        # Create Departments
        for dept_data in college_data.get("departments", []):
            department = create_department(db, dept_data["department"])
            dept_count += 1
            logger.info(f"  🏛️  Department created: {department.name_ko}")

            # Create Professors
            for prof_data in dept_data.get("professors", []):
                professor = create_professor(db, prof_data["professor"])
                prof_count += 1
                logger.info(f"    👨‍🏫 Professor created: {professor.name_ko}")

                # Create Laboratories
                for lab_data in prof_data.get("laboratories", []):
                    # Update lab_data with department_id
                    lab_data["laboratory"]["department_id"] = department.id

                    laboratory = create_laboratory(db, lab_data["laboratory"])
                    lab_count += 1
                    logger.info(f"      🔬 Laboratory created: {laboratory.name_ko}")

                    # Create Lab Members
                    for member_data in lab_data.get("members", []):
                        member_data["lab_id"] = laboratory.id
                        member = create_lab_member(db, member_data)
                        member_count += 1
                        logger.info(f"        👤 Lab member created: {member.name_ko} ({member.role.value})")

                    # Create Research Papers
                    for paper_data in lab_data.get("papers", []):
                        paper_data["lab_id"] = laboratory.id
                        paper = create_research_paper(db, paper_data)
                        paper_count += 1
                        logger.info(f"        📄 Paper created: {paper.title[:60]}...")

                        # Create Paper Analysis if provided
                        if "analysis" in paper_data:
                            create_paper_analysis(db, paper.id, paper_data["analysis"])
                            logger.info(f"           📊 Analysis created for paper")

    # Commit all changes
    db.commit()

    # Print summary
    logger.info("\n" + "=" * 80)
    logger.info("✅ SNU Data Population Complete!")
    logger.info("=" * 80)
    logger.info(f"""
Summary:
  - Universities:    {1}
  - Colleges:        {college_count}
  - Departments:     {dept_count}
  - Professors:      {prof_count}
  - Laboratories:    {lab_count}
  - Lab Members:     {member_count}
  - Research Papers: {paper_count}
    """)


def main():
    """Main entry point"""
    try:
        # Initialize database
        logger.info("Initializing database...")
        init_db()

        # Get database session
        db = SessionLocal()

        # Check if SNU data already exists
        existing_uni = db.query(University).filter(
            University.id == "seoul-national-univ"
        ).first()

        if existing_uni:
            logger.warning("⚠️  SNU data already exists in database. Skipping initialization.")
            logger.info(f"   Found: {existing_uni.name_ko} with {len(existing_uni.colleges)} colleges")
        else:
            # Populate SNU data
            populate_snu_data(db)

        db.close()

    except Exception as e:
        logger.error(f"❌ Error during initialization: {str(e)}")
        import traceback
        traceback.print_exc()
        raise


if __name__ == "__main__":
    main()
