
import sqlite3
import json
from typing import Optional
import os
import sys

# 프로젝트 루트를 sys.path에 추가
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.services.article_crawler import ArticleCrawler
from src.services.llm import BaseLLM
from src.domain.schemas import ResearchPaper, AnalysisResult

class PipelineService:
    """
    E2E 파이프라인을 관리하는 서비스.
    크롤링 -> DB 저장 -> LLM 분석 -> 결과 저장을 총괄합니다.
    """

    def __init__(self, crawler: ArticleCrawler, llm_service: BaseLLM, db_path: str):
        self.crawler = crawler
        self.llm_service = llm_service
        self.db_path = db_path

    async def process_url(self, url: str, university: str, department: str) -> Optional[AnalysisResult]:
        """
        단일 URL에 대해 전체 파이프라인을 실행합니다.
        """
        # 1. Crawl
        paper = await self.crawler.crawl(url, university, department)
        if not paper:
            print(f"   [Pipeline] Failed to crawl {url}. Aborting.")
            return None
        
        # 2. Save paper to DB
        self._save_paper(paper)
        print(f"   [Pipeline] Saved paper '{paper.title}' to DB.")

        # 3. Analyze with LLM
        analysis_result = self.llm_service.analyze(paper)
        if not analysis_result:
            print(f"   [Pipeline] Failed to analyze {paper.title}. Aborting.")
            return None
        
        # 4. Save analysis result to DB
        self._save_analysis_result(analysis_result)
        print(f"   [Pipeline] Saved analysis for '{paper.title}' to DB.")

        return analysis_result

    def _save_paper(self, paper: ResearchPaper):
        """ResearchPaper 객체를 DB에 저장합니다."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO research_papers (id, url, title, university, department, pub_date, content_raw, crawled_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            paper.id, paper.url, paper.title, paper.university, paper.department,
            paper.pub_date, paper.content_raw, paper.crawled_at
        ))
        conn.commit()
        conn.close()

    def _save_analysis_result(self, result: AnalysisResult):
        """AnalysisResult 객체를 DB에 저장합니다."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO analysis_results (paper_id, research_summary, job_title, salary_hint, related_companies, action_items)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            result.paper_id, result.research_summary, result.career_path.job_title, result.career_path.avg_salary_hint,
            json.dumps(result.career_path.companies), json.dumps(result.action_item.dict())
        ))
        conn.commit()
        conn.close()
