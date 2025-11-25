from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime, date

class ResearchPaper(BaseModel):
    id: str
    url: str
    title: str
    university: str
    department: Optional[str] = None
    pub_date: Optional[date] = None
    content_raw: str
    crawled_at: datetime = Field(default_factory=datetime.now)

class CareerPath(BaseModel):
    companies: List[str]
    job_title: str
    avg_salary_hint: str

class ActionItem(BaseModel):
    subjects: List[str]
    research_topic: str

class AnalysisResult(BaseModel):
    paper_id: str
    title: str
    research_summary: str
    career_path: CareerPath
    action_item: ActionItem


class DepartmentInfo(BaseModel):
    id: Optional[str] = None
    university_name: str
    department_name: str
    category: Optional[str] = None  # 예: 공학계열
    url: Optional[str] = None       # 학과 홈페이지 (추후 매핑)

class UniversityInfo(BaseModel):
    name: str
    region: Optional[str] = None
    url: Optional[str] = None       # 학교 대표 URL
    departments: List[DepartmentInfo] = []
