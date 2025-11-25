
import os
import sqlite3
import pytest
import sys
import importlib.util
import json
from unittest.mock import patch, AsyncMock

# 프로젝트 루트를 sys.path에 추가
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.services.article_crawler import ArticleCrawler
from src.services.llm import MockLLM
from src.services.pipeline_service import PipelineService
from src.domain.schemas import ResearchPaper

# --- Helper function to read mock HTML ---
def load_mock_html(file_name: str) -> str:
    path = os.path.join(project_root, 'tests', 'fixtures', file_name)
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

# --- Test Fixtures ---
@pytest.fixture(scope="function")
def test_db_for_e2e():
    db_path = "test_e2e_scenario_a.db"
    if os.path.exists(db_path):
        os.remove(db_path)
    
    conn = sqlite3.connect(db_path)
    
    # 모든 마이그레이션 실행
    migrations_dir = os.path.join(project_root, 'src', 'scripts', 'migrations')
    migration_files = sorted([f for f in os.listdir(migrations_dir) if f.endswith('.py')])
    
    for mf in migration_files:
        migration_path = os.path.join(migrations_dir, mf)
        spec = importlib.util.spec_from_file_location(mf, migration_path)
        migration_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(migration_module)
        if hasattr(migration_module, 'migrate_up'):
            migration_module.migrate_up(conn)

    yield db_path
    
    conn.close()
    if os.path.exists(db_path):
        os.remove(db_path)

# --- Test Cases ---
@pytest.mark.asyncio
class TestScenarioA:
    """
    시나리오 A: "New Paper" Discovery E2E 테스트
    """

    @patch('src.services.article_crawler.ArticleCrawler._fetch_page_content', new_callable=AsyncMock)
    async def test_new_paper_discovery_pipeline(self, mock_fetch, test_db_for_e2e):
        # 1. Setup
        db_path = test_db_for_e2e
        test_url = "http://mock.kaist.ac.kr/cs/news/ai-for-healthcare"
        
        # 크롤러가 mock HTML을 반환하도록 설정
        mock_article_html = load_mock_html('mock_article_page.html')
        mock_fetch.return_value = mock_article_html
        
        # 서비스 초기화
        crawler = ArticleCrawler()
        llm_service = MockLLM() # 실제 LLM 대신 Mock 사용
        pipeline = PipelineService(crawler=crawler, llm_service=llm_service, db_path=db_path)

        # 2. Execution
        result = await pipeline.process_url(url=test_url, university="KAIST", department="CS")

        # 3. Verification
        assert result is not None
        
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # 3.1. research_papers 테이블 검증
        cursor.execute("SELECT * FROM research_papers WHERE url = ?", (test_url,))
        paper_row = cursor.fetchone()
        assert paper_row is not None
        assert paper_row['title'] == "AI for Healthcare: A New Approach"
        assert paper_row['university'] == "KAIST"
        assert "This paper introduces a novel deep learning model" in paper_row['content_raw']
        
        paper_id = paper_row['id']

        # 3.2. analysis_results 테이블 검증
        cursor.execute("SELECT * FROM analysis_results WHERE paper_id = ?", (paper_id,))
        analysis_row = cursor.fetchone()
        assert analysis_row is not None
        
        # MockLLM이 반환하는 값과 일치하는지 확인
        # MockLLM.analyze는 ResearchPaper 객체를 기대하므로, DB에서 읽은 데이터로 객체를 만들어 전달합니다.
        mock_paper_for_llm = ResearchPaper(
            id=paper_row['id'],
            url=paper_row['url'],
            title=paper_row['title'],
            university=paper_row['university'],
            content_raw=paper_row['content_raw']
        )
        mock_llm_result = llm_service.analyze(mock_paper_for_llm)
        
        assert analysis_row['research_summary'] == mock_llm_result.research_summary
        assert analysis_row['job_title'] == mock_llm_result.career_path.job_title
        
        related_companies = json.loads(analysis_row['related_companies'])
        assert related_companies == mock_llm_result.career_path.companies

        conn.close()
