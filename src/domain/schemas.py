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

class DeepDive(BaseModel):
    keywords: List[str]
    recommendations: List[str]
    related_concepts: List[str]

class AnalysisResult(BaseModel):
    paper_id: str
    topic_easy: str
    topic_technical: str
    explanation: str
    reference_link: str
    deep_dive: DeepDive
    career_path: CareerPath
    action_item: ActionItem
    
    # Backward compatibility (optional, or just map new fields to old ones if needed)
    @property
    def title(self):
        return self.topic_easy

    @property
    def research_summary(self):
        return self.explanation


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
