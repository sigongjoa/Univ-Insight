from pydantic import BaseModel
from typing import List, Optional

class ResearchPaper(BaseModel):
    source: str
    title: str
    content: str
    date: str
    url: str

class CareerPath(BaseModel):
    companies: List[str]
    job_title: str
    avg_salary_hint: str

class ActionItem(BaseModel):
    subjects: List[str]
    research_topic: str

class AnalysisResult(BaseModel):
    title: str
    research_summary: str
    career_path: CareerPath
    action_item: ActionItem
