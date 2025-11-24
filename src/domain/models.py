"""
SQLAlchemy ORM Models for Univ-Insight

This module defines the database schema for storing research papers,
analysis results, users, and reports.
"""

from datetime import datetime
from typing import Optional, List
import uuid
from sqlalchemy import Column, String, Text, Integer, DateTime, Date, JSON, ForeignKey, Enum as SQLEnum, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import enum

Base = declarative_base()


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


class ResearchPaper(Base):
    """
    Stores raw research paper data crawled from university websites.

    Table: research_papers
    """
    __tablename__ = "research_papers"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    url = Column(String(512), unique=True, nullable=False, index=True)
    title = Column(String(255), nullable=False)
    university = Column(String(50), nullable=False, index=True)
    university_tier = Column(SQLEnum(UniversityTier), default=UniversityTier.TOP, nullable=False)
    department = Column(String(50), nullable=True)
    pub_date = Column(Date, nullable=True)
    content_raw = Column(Text, nullable=False)
    crawled_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    analysis_results = relationship("AnalysisResult", back_populates="paper", cascade="all, delete-orphan")
    report_papers = relationship("ReportPaper", back_populates="paper", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<ResearchPaper(id={self.id}, title={self.title}, university={self.university})>"


class AnalysisResult(Base):
    """
    Stores LLM-processed insights for each research paper.

    Table: analysis_results
    """
    __tablename__ = "analysis_results"

    id = Column(Integer, primary_key=True, autoincrement=True)
    paper_id = Column(String(36), ForeignKey("research_papers.id"), nullable=False, index=True)
    summary = Column(Text, nullable=False)
    job_title = Column(String(100), nullable=True)
    salary_hint = Column(String(100), nullable=True)
    related_companies = Column(JSON, nullable=True)  # List of company names
    action_items = Column(JSON, nullable=True)  # {"subjects": [...], "research_topic": "..."}
    embedding_id = Column(String(100), nullable=True)  # ID in ChromaDB
    analyzed_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    paper = relationship("ResearchPaper", back_populates="analysis_results")

    def __repr__(self):
        return f"<AnalysisResult(id={self.id}, paper_id={self.paper_id})>"


class User(Base):
    """
    Stores user profiles and preferences.

    Table: users
    """
    __tablename__ = "users"

    id = Column(String(50), primary_key=True)  # Kakao ID or UUID
    name = Column(String(50), nullable=False)
    role = Column(SQLEnum(UserRole), nullable=False)
    parent_id = Column(String(50), ForeignKey("users.id"), nullable=True)  # Link to parent (if student)
    interests = Column(JSON, default=list, nullable=False)  # List of keywords
    notion_page_id = Column(String(100), nullable=True)
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
        return f"<User(id={self.id}, name={self.name}, role={self.role})>"


class Report(Base):
    """
    Log of reports sent to users.

    Table: reports
    """
    __tablename__ = "reports"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(50), ForeignKey("users.id"), nullable=False, index=True)
    sent_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    status = Column(SQLEnum(ReportStatus), default=ReportStatus.PENDING, nullable=False)
    notion_page_url = Column(String(255), nullable=True)

    # Relationships
    user = relationship("User", back_populates="reports")
    papers = relationship("ReportPaper", back_populates="report", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Report(id={self.id}, user_id={self.user_id}, status={self.status})>"


class ReportPaper(Base):
    """
    Junction table linking Reports and ResearchPapers (many-to-many).

    Table: report_papers
    """
    __tablename__ = "report_papers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    report_id = Column(String(36), ForeignKey("reports.id"), nullable=False, index=True)
    paper_id = Column(String(36), ForeignKey("research_papers.id"), nullable=False, index=True)

    # Unique constraint to prevent duplicates
    __table_args__ = (UniqueConstraint("report_id", "paper_id", name="uq_report_paper"),)

    # Relationships
    report = relationship("Report", back_populates="papers")
    paper = relationship("ResearchPaper", back_populates="report_papers")

    def __repr__(self):
        return f"<ReportPaper(report_id={self.report_id}, paper_id={self.paper_id})>"
