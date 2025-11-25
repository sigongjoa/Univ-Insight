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

