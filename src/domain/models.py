"""
SQLAlchemy ORM Models for Univ-Insight (Hierarchical Structure)

This module defines the database schema for storing:
- Universities, Colleges, Departments, Professors (hierarchical)
- Laboratories and Lab Members
- Research Papers with full details
- Paper Analysis results
- Users, Reports, and preferences
"""

from datetime import datetime
from typing import Optional, List
import uuid
from sqlalchemy import (
    Column, String, Text, Integer, DateTime, Date, JSON, ForeignKey,
    Enum as SQLEnum, UniqueConstraint, Float, Boolean
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import enum

Base = declarative_base()


# ==================== Enums ====================

class UniversityTier(int, enum.Enum):
    """University tier for Plan B logic (1=Top, 5=Lower)"""
    TOP = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4
    VERY_LOW = 5


class UserRole(str, enum.Enum):
    """User role type"""
    STUDENT = "student"
    PARENT = "parent"


class ReportStatus(str, enum.Enum):
    """Report status"""
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"


class LabMemberRole(str, enum.Enum):
    """Lab member role"""
    PROFESSOR = "professor"
    POSTDOC = "postdoc"
    PHD_STUDENT = "phd_student"
    MASTER_STUDENT = "master_student"
    UNDERGRADUATE = "undergraduate"
    RESEARCH_SCIENTIST = "research_scientist"


# ==================== Hierarchical Models ====================

class University(Base):
    """
    Represents a university.

    Table: universities
    """
    __tablename__ = "universities"

    id = Column(String(100), primary_key=True)  # e.g., "seoul-national-univ"
    name = Column(String(255), nullable=False, unique=True, index=True)
    name_ko = Column(String(255), nullable=False)  # Korean name
    location = Column(String(100), nullable=True)
    ranking = Column(Integer, nullable=True)  # National ranking
    tier = Column(SQLEnum(UniversityTier), default=UniversityTier.TOP, nullable=False)
    url = Column(String(500), nullable=True)
    description = Column(Text, nullable=True)
    established_year = Column(Integer, nullable=True)
    crawled_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    colleges = relationship("College", back_populates="university", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<University(id={self.id}, name={self.name})>"


class College(Base):
    """
    Represents a college/faculty within a university.

    Table: colleges
    """
    __tablename__ = "colleges"

    id = Column(String(100), primary_key=True)  # e.g., "snu-college-eng"
    university_id = Column(String(100), ForeignKey("universities.id"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    name_ko = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    established_year = Column(Integer, nullable=True)
    crawled_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    university = relationship("University", back_populates="colleges")
    departments = relationship("Department", back_populates="college", cascade="all, delete-orphan")

    __table_args__ = (UniqueConstraint("university_id", "name", name="uq_college_per_uni"),)

    def __repr__(self):
        return f"<College(id={self.id}, name={self.name})>"


class Department(Base):
    """
    Represents a department within a college.

    Table: departments
    """
    __tablename__ = "departments"

    id = Column(String(100), primary_key=True)  # e.g., "snu-dept-eecs"
    college_id = Column(String(100), ForeignKey("colleges.id"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    name_ko = Column(String(255), nullable=False)
    faculty_count = Column(Integer, nullable=True)
    description = Column(Text, nullable=True)
    established_year = Column(Integer, nullable=True)
    website = Column(String(500), nullable=True)
    crawled_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    college = relationship("College", back_populates="departments")
    professors = relationship("Professor", back_populates="department", cascade="all, delete-orphan")
    laboratories = relationship("Laboratory", back_populates="department", cascade="all, delete-orphan")

    __table_args__ = (UniqueConstraint("college_id", "name", name="uq_dept_per_college"),)

    def __repr__(self):
        return f"<Department(id={self.id}, name={self.name})>"


class Professor(Base):
    """
    Represents a professor.

    Table: professors
    """
    __tablename__ = "professors"

    id = Column(String(100), primary_key=True)  # e.g., "prof-hong-123"
    department_id = Column(String(100), ForeignKey("departments.id"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    name_ko = Column(String(100), nullable=False)
    email = Column(String(100), nullable=True)
    phone = Column(String(20), nullable=True)
    title = Column(String(50), nullable=True)  # e.g., "Associate Professor"
    research_interests = Column(JSON, default=list, nullable=False)  # List of keywords
    education = Column(JSON, default=dict, nullable=False)  # {"phd": "MIT", "masters": "..."}
    h_index = Column(Integer, nullable=True)
    publications_count = Column(Integer, nullable=True)
    profile_url = Column(String(500), nullable=True)
    profile_image_url = Column(String(500), nullable=True)
    bio = Column(Text, nullable=True)
    crawled_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    department = relationship("Department", back_populates="professors")
    laboratories = relationship("Laboratory", back_populates="professor", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Professor(id={self.id}, name={self.name})>"


class Laboratory(Base):
    """
    Represents a research laboratory.

    Table: laboratories
    """
    __tablename__ = "laboratories"

    id = Column(String(100), primary_key=True)  # e.g., "lab-ai-ml-001"
    professor_id = Column(String(100), ForeignKey("professors.id"), nullable=False, index=True)
    department_id = Column(String(100), ForeignKey("departments.id"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    name_ko = Column(String(255), nullable=False)
    research_areas = Column(JSON, default=list, nullable=False)  # ["Deep Learning", "NLP"]
    description = Column(Text, nullable=True)
    established_year = Column(Integer, nullable=True)
    member_count = Column(Integer, nullable=True)
    website = Column(String(500), nullable=True)
    email = Column(String(100), nullable=True)
    location = Column(String(255), nullable=True)  # Building and room number
    current_projects = Column(JSON, default=list, nullable=False)  # List of project names
    funding_info = Column(JSON, default=dict, nullable=False)  # Funding sources
    facilities = Column(JSON, default=list, nullable=False)  # Available equipment/facilities
    crawled_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    professor = relationship("Professor", back_populates="laboratories")
    department = relationship("Department", back_populates="laboratories")
    members = relationship("LabMember", back_populates="laboratory", cascade="all, delete-orphan")
    papers = relationship("ResearchPaper", back_populates="laboratory", cascade="all, delete-orphan")

    __table_args__ = (UniqueConstraint("professor_id", "name", name="uq_lab_per_prof"),)

    def __repr__(self):
        return f"<Laboratory(id={self.id}, name={self.name})>"


class LabMember(Base):
    """
    Represents a member of a research laboratory.

    Table: lab_members
    """
    __tablename__ = "lab_members"

    id = Column(String(100), primary_key=True)
    lab_id = Column(String(100), ForeignKey("laboratories.id"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    name_ko = Column(String(100), nullable=False)
    email = Column(String(100), nullable=True)
    role = Column(SQLEnum(LabMemberRole), nullable=False)
    research_topic = Column(String(255), nullable=True)
    joined_year = Column(Integer, nullable=True)
    status = Column(String(20), default="active", nullable=False)  # active, graduated, left
    profile_url = Column(String(500), nullable=True)
    crawled_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    laboratory = relationship("Laboratory", back_populates="members")

    def __repr__(self):
        return f"<LabMember(id={self.id}, name={self.name}, role={self.role})>"


# ==================== Research Paper Models ====================

class ResearchPaper(Base):
    """
    Stores research paper with full details linked to laboratory.

    Table: research_papers
    """
    __tablename__ = "research_papers"

    id = Column(String(100), primary_key=True)
    lab_id = Column(String(100), ForeignKey("laboratories.id"), nullable=True, index=True)
    title = Column(String(500), nullable=False)
    authors = Column(JSON, default=list, nullable=False)  # List of author names
    abstract = Column(Text, nullable=True)
    publication_year = Column(Integer, nullable=True)
    publication_date = Column(Date, nullable=True)
    venue = Column(String(255), nullable=True)  # Conference/Journal name
    venue_type = Column(String(20), nullable=True)  # conference, journal
    citation_count = Column(Integer, default=0, nullable=False)
    doi = Column(String(100), nullable=True)
    url = Column(String(500), nullable=True, unique=True, index=True)
    pdf_url = Column(String(500), nullable=True)
    keywords = Column(JSON, default=list, nullable=False)
    full_text = Column(Text, nullable=True)  # For papers we can access
    embedding_id = Column(String(100), nullable=True)  # ChromaDB embedding ID

    # Metadata
    crawled_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    laboratory = relationship("Laboratory", back_populates="papers")
    analysis = relationship("PaperAnalysis", back_populates="paper", uselist=False, cascade="all, delete-orphan")
    report_papers = relationship("ReportPaper", back_populates="paper", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<ResearchPaper(id={self.id}, title={self.title})>"


class PaperAnalysis(Base):
    """
    Stores LLM-processed insights for each research paper.

    Table: paper_analysis
    """
    __tablename__ = "paper_analysis"

    id = Column(String(100), primary_key=True, default=lambda: str(uuid.uuid4()))
    paper_id = Column(String(100), ForeignKey("research_papers.id"), nullable=False, unique=True, index=True)

    # Summary and main content
    easy_summary = Column(Text, nullable=False)  # Simple explanation
    technical_summary = Column(Text, nullable=True)  # Technical details

    # Core technologies and skills
    core_technologies = Column(JSON, default=list, nullable=False)  # ["PyTorch", "CUDA", "Vision Transformer"]
    required_skills = Column(JSON, default=list, nullable=False)  # Programming languages, tools
    math_concepts = Column(JSON, default=list, nullable=False)  # Mathematical concepts needed

    # Application and relevance
    application_fields = Column(JSON, default=list, nullable=False)  # Where this research applies
    industry_relevance = Column(Text, nullable=True)

    # Career information
    career_paths = Column(JSON, default=list, nullable=False)  # Possible careers
    recommended_companies = Column(JSON, default=list, nullable=False)  # Companies working on similar tech
    salary_range = Column(String(100), nullable=True)  # e.g., "$100,000-150,000"
    job_roles = Column(JSON, default=list, nullable=False)  # Possible job titles

    # Study plan
    recommended_subjects = Column(JSON, default=list, nullable=False)  # Subjects to study
    action_items = Column(JSON, default=dict, nullable=False)  # Detailed action items
    learning_path = Column(JSON, default=list, nullable=False)  # Step-by-step learning path

    # Limitations and challenges
    limitations = Column(Text, nullable=True)
    challenges = Column(JSON, default=list, nullable=False)

    # Metadata
    analyzed_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    analysis_model = Column(String(50), nullable=True)  # Which LLM model was used

    # Relationships
    paper = relationship("ResearchPaper", back_populates="analysis")

    def __repr__(self):
        return f"<PaperAnalysis(id={self.id}, paper_id={self.paper_id})>"


# ==================== User and Report Models ====================

class User(Base):
    """
    Stores user profiles and preferences.

    Table: users
    """
    __tablename__ = "users"

    id = Column(String(50), primary_key=True)  # Kakao ID or UUID
    name = Column(String(50), nullable=False)
    role = Column(SQLEnum(UserRole), nullable=False)
    parent_id = Column(String(50), ForeignKey("users.id"), nullable=True)
    interests = Column(JSON, default=list, nullable=False)  # Research interests
    saved_labs = Column(JSON, default=list, nullable=False)  # Favorite laboratories
    saved_papers = Column(JSON, default=list, nullable=False)  # Favorite papers
    notion_page_id = Column(String(100), nullable=True)
    kakao_connected = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    reports = relationship("Report", back_populates="user", cascade="all, delete-orphan")
    parent = relationship(
        "User",
        remote_side=[id],
        backref="children",
        foreign_keys=[parent_id]
    )

    def __repr__(self):
        return f"<User(id={self.id}, name={self.name})>"


class Report(Base):
    """
    Log of reports sent to users.

    Table: reports
    """
    __tablename__ = "reports"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(50), ForeignKey("users.id"), nullable=False, index=True)
    lab_id = Column(String(100), ForeignKey("laboratories.id"), nullable=True)  # Focus lab
    title = Column(String(255), nullable=True)
    sent_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    status = Column(SQLEnum(ReportStatus), default=ReportStatus.PENDING, nullable=False)
    notion_page_url = Column(String(255), nullable=True)
    report_type = Column(String(50), nullable=True)  # 'lab_summary', 'research_path', etc.

    # Relationships
    user = relationship("User", back_populates="reports")
    papers = relationship("ReportPaper", back_populates="report", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Report(id={self.id}, user_id={self.user_id})>"


class ReportPaper(Base):
    """
    Junction table linking Reports and ResearchPapers (many-to-many).

    Table: report_papers
    """
    __tablename__ = "report_papers"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    report_id = Column(String(36), ForeignKey("reports.id"), nullable=False, index=True)
    paper_id = Column(String(100), ForeignKey("research_papers.id"), nullable=False, index=True)
    order_index = Column(Integer, nullable=True)  # For ordering papers in report
    relevance_score = Column(Float, nullable=True)  # How relevant to user

    # Relationships
    report = relationship("Report", back_populates="papers")
    paper = relationship("ResearchPaper", back_populates="report_papers")

    __table_args__ = (UniqueConstraint("report_id", "paper_id", name="uq_report_paper"),)

    def __repr__(self):
        return f"<ReportPaper(report_id={self.report_id}, paper_id={self.paper_id})>"
