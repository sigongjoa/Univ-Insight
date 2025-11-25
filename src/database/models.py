"""
데이터베이스 모델 정의 (SQLAlchemy ORM)

주요 엔티티:
1. CrawlTask - 크롤링 작업
2. CrawlResult - 크롤링 결과
3. Professor - 교수 정보
4. Paper - 논문 정보
5. CrawlMetrics - 크롤링 메트릭스
"""

from sqlalchemy import Column, String, Integer, Float, DateTime, Boolean, Text, ForeignKey, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import hashlib

Base = declarative_base()


class CrawlTask(Base):
    """크롤링 작업"""
    __tablename__ = 'crawl_tasks'

    id = Column(String(64), primary_key=True)  # MD5(url + timestamp)
    url = Column(String(500), nullable=False, index=True)
    university_name = Column(String(100), nullable=False, index=True)
    department_name = Column(String(100))

    # 작업 상태
    status = Column(String(20), default='pending', index=True)  # pending, running, completed, failed
    priority = Column(Integer, default=0)  # 0=normal, 1=high, -1=low

    # 작업 메타데이터
    created_at = Column(DateTime, default=datetime.now, index=True)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)

    # 크롤러 설정
    use_cache = Column(Boolean, default=True)
    use_ocr = Column(Boolean, default=False)
    parallel_crawl = Column(Boolean, default=False)
    timeout_seconds = Column(Integer, default=30)

    # 결과 참조
    result_id = Column(String(64), ForeignKey('crawl_results.id'))
    result = relationship("CrawlResult", back_populates="task", uselist=False)

    # 메트릭스 참조
    metrics = relationship("CrawlMetrics", back_populates="task", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<CrawlTask {self.university_name}:{self.url[:40]}... [{self.status}]>"


class CrawlResult(Base):
    """크롤링 결과"""
    __tablename__ = 'crawl_results'

    id = Column(String(64), primary_key=True)  # MD5(url + result_hash)
    task_id = Column(String(64), ForeignKey('crawl_tasks.id'), index=True)

    # 기본 정보
    url = Column(String(500), nullable=False, index=True)
    university_name = Column(String(100), nullable=False, index=True)

    # 추출 결과
    professors_count = Column(Integer, default=0)
    papers_count = Column(Integer, default=0)
    labs_count = Column(Integer, default=0)
    pages_crawled = Column(Integer, default=0)

    # 콘텐츠
    html_content = Column(Text)  # 원본 HTML (선택사항)
    extracted_text = Column(Text)  # 추출된 텍스트

    # 메타데이터
    accuracy_score = Column(Float, default=0.0)  # 0-100%
    extraction_method = Column(String(50))  # css, email, keyword, ocr, table
    created_at = Column(DateTime, default=datetime.now, index=True)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # 관계
    task = relationship("CrawlTask", back_populates="result", uselist=False)
    professors = relationship("Professor", back_populates="crawl_result", cascade="all, delete-orphan")
    papers = relationship("Paper", back_populates="crawl_result", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<CrawlResult {self.university_name}: {self.professors_count} profs, {self.papers_count} papers>"


class Professor(Base):
    """교수 정보"""
    __tablename__ = 'professors'

    id = Column(String(64), primary_key=True)  # MD5(name + email + university)
    crawl_result_id = Column(String(64), ForeignKey('crawl_results.id'), index=True)

    # 기본 정보
    name = Column(String(100), nullable=False, index=True)
    email = Column(String(100), index=True)
    university_name = Column(String(100), nullable=False, index=True)
    department = Column(String(100))

    # 학위 정보
    title = Column(String(50))  # Professor, Associate, Assistant, Lecturer
    office = Column(String(200))  # 사무실 위치
    phone = Column(String(20))

    # 분류
    is_verified = Column(Boolean, default=False)
    confidence_score = Column(Float, default=0.0)  # 0-100%

    # 메타데이터
    created_at = Column(DateTime, default=datetime.now, index=True)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # 관계
    crawl_result = relationship("CrawlResult", back_populates="professors")
    papers = relationship("Paper", back_populates="professor")

    __table_args__ = (
        UniqueConstraint('name', 'email', 'university_name', name='uq_professor'),
    )

    def __repr__(self):
        return f"<Professor {self.name} ({self.university_name})>"


class Paper(Base):
    """논문 정보"""
    __tablename__ = 'papers'

    id = Column(String(64), primary_key=True)  # MD5(title + authors + year)
    crawl_result_id = Column(String(64), ForeignKey('crawl_results.id'), index=True)
    professor_id = Column(String(64), ForeignKey('professors.id'), index=True)

    # 기본 정보
    title = Column(String(500), nullable=False, index=True)
    authors = Column(Text)  # JSON list
    published_year = Column(Integer, index=True)

    # 출판 정보
    conference = Column(String(200))  # 학회명
    journal = Column(String(200))  # 저널명
    volume = Column(String(50))
    pages = Column(String(50))

    # 링크 및 참고
    url = Column(String(500))
    doi = Column(String(100), index=True)
    abstract = Column(Text)

    # 분류
    is_verified = Column(Boolean, default=False)
    confidence_score = Column(Float, default=0.0)  # 0-100%

    # 메타데이터
    created_at = Column(DateTime, default=datetime.now, index=True)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # 관계
    crawl_result = relationship("CrawlResult", back_populates="papers")
    professor = relationship("Professor", back_populates="papers")

    __table_args__ = (
        UniqueConstraint('title', 'published_year', name='uq_paper'),
    )

    def __repr__(self):
        return f"<Paper {self.title[:50]}... ({self.published_year})>"


class CrawlMetrics(Base):
    """크롤링 메트릭스"""
    __tablename__ = 'crawl_metrics'

    id = Column(String(64), primary_key=True)
    task_id = Column(String(64), ForeignKey('crawl_tasks.id'), index=True)

    # 성능 메트릭
    total_time_seconds = Column(Float)  # 전체 소요 시간
    html_download_time = Column(Float)  # HTML 다운로드 시간
    parsing_time = Column(Float)  # 파싱 시간
    ocr_time = Column(Float)  # OCR 처리 시간

    # 캐시 메트릭
    cache_hit = Column(Boolean, default=False)
    cache_hit_time = Column(Float)

    # 렌더링 메트릭
    js_rendering_used = Column(Boolean, default=False)
    js_rendering_time = Column(Float)

    # 추출 메트릭
    extraction_methods = Column(Text)  # JSON list: ["css", "email", "ocr"]
    items_extracted = Column(Integer)  # 추출된 항목 수

    # 오류 추적
    error_occurred = Column(Boolean, default=False)
    error_message = Column(Text)

    # 메타데이터
    created_at = Column(DateTime, default=datetime.now, index=True)
    worker_id = Column(String(50))  # 처리한 워커 ID

    # 관계
    task = relationship("CrawlTask", back_populates="metrics")

    def __repr__(self):
        return f"<CrawlMetrics task_id={self.task_id} time={self.total_time_seconds:.2f}s>"
