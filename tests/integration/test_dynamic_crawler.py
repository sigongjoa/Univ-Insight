
import os
import sqlite3
import pytest
import sys
import importlib.util
from unittest.mock import patch, AsyncMock

# 프로젝트 루트를 sys.path에 추가
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.services.dynamic_crawler import DynamicCrawler

# --- Helper function to read mock HTML ---
def load_mock_html(file_name: str) -> str:
    path = os.path.join(project_root, 'tests', 'fixtures', file_name)
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

# --- Test Fixtures ---
@pytest.fixture(scope="function")
def test_db_for_dynamic_crawler():
    db_path = "test_dynamic_crawler.db"
    if os.path.exists(db_path):
        os.remove(db_path)
    
    conn = sqlite3.connect(db_path)
    migration_file_path = os.path.join(project_root, 'src', 'scripts', 'migrations', '002_create_crawl_targets.py')
    spec = importlib.util.spec_from_file_location("002_create_crawl_targets", migration_file_path)
    migration_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(migration_module)
    migration_module.migrate_up(conn)
    
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO crawl_targets (id, university_name, department_name, department_url, status) VALUES
        (1, '서울대학교', '컴퓨터공학부', 'http://mock.snu.ac.kr/cse', 'URLFound'),
        (2, 'KAIST', '전산학부', 'http://mock.kaist.ac.kr/cs', 'URLFound'),
        (3, '포항공과대학교', '전자전기공학과', 'http://mock.postech.ac.kr/ee', 'Ready')
    """)
    conn.commit()
    
    yield db_path
    
    conn.close()
    if os.path.exists(db_path):
        os.remove(db_path)

# --- Test Cases ---
@pytest.mark.asyncio
class TestDynamicCrawler:
    """
    DynamicCrawler에 대한 통합 테스트
    """

    @patch('src.services.dynamic_crawler.DynamicCrawler._fetch_page_content', new_callable=AsyncMock)
    async def test_crawl_all_targets_with_mock_html(self, mock_fetch, test_db_for_dynamic_crawler):
        # 1. Setup
        db_path = test_db_for_dynamic_crawler
        
        mock_snu_cse_html = load_mock_html('mock_snu_cse_faculty_page.html')
        
        def side_effect(url):
            if "mock.snu.ac.kr" in url:
                return mock_snu_cse_html
            return ""
        
        mock_fetch.side_effect = side_effect
        
        crawler = DynamicCrawler(db_path=db_path)

        # 2. Execution
        await crawler.crawl_all_targets()

        # 3. Verification
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # 서울대학교 컴퓨터공학부 상태 확인
        cursor.execute("SELECT status FROM crawl_targets WHERE id=1")
        snu_target = cursor.fetchone()
        assert snu_target is not None
        assert snu_target['status'] == "Complete"

        # KAIST 전산학부 상태 확인 (mock HTML이 없으므로 NoData 또는 Failed)
        cursor.execute("SELECT status FROM crawl_targets WHERE id=2")
        kaist_target = cursor.fetchone()
        assert kaist_target is not None
        assert kaist_target['status'] in ["NoData", "Failed"]

        # 포항공대 상태 확인 (status가 'Ready'이므로 크롤링 대상이 아님)
        cursor.execute("SELECT status FROM crawl_targets WHERE id=3")
        postech_target = cursor.fetchone()
        assert postech_target is not None
        assert postech_target['status'] == "Ready"

        conn.close()

    async def test_extract_professors(self, test_db_for_dynamic_crawler):
        """
        _extract_professors 메서드가 mock HTML에서 교수 정보를 정확히 파싱하는지 테스트합니다.
        """
        # 1. Setup
        crawler = DynamicCrawler(db_path=test_db_for_dynamic_crawler)
        mock_html = load_mock_html('mock_snu_cse_faculty_page.html')

        # 2. Execution
        professors = await crawler._extract_professors(mock_html, "서울대학교")

        # 3. Verification
        assert len(professors) == 3
        
        # 김철수 교수 정보 확인
        prof_kim = next((p for p in professors if p['name'] == '김철수'), None)
        assert prof_kim is not None
        assert prof_kim['email'] == 'prof.kim@snu.ac.kr'
        assert prof_kim['website'] == 'https://kim-lab.snu.ac.kr'

        # 박영준 교수 정보 확인 (이메일 없음)
        prof_park = next((p for p in professors if p['name'] == '박영준'), None)
        assert prof_park is not None
        assert prof_park['email'] is None
        assert prof_park['website'] == 'https://park-lab.snu.ac.kr'
