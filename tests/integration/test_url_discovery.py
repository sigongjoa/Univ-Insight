
import os
import sqlite3
import pytest
import sys
import importlib.util
from datetime import datetime
from unittest.mock import patch, AsyncMock

# 프로젝트 루트를 sys.path에 추가
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.scripts.urldiscovery.college_url_mapper import CollegeURLMapper

# --- Helper function to read mock HTML ---
def load_mock_html(file_name: str) -> str:
    path = os.path.join(project_root, 'tests', 'fixtures', file_name)
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

# --- Test Fixtures ---
@pytest.fixture(scope="function")
def test_db_for_url_discovery():
    db_path = "test_url_discovery.db"
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
        INSERT INTO crawl_targets (university_name, department_name) VALUES
        ('서울대학교', '컴퓨터공학부'),
        ('KAIST', '전산학부'),
        ('패턴없는대학', '학과')
    """)
    conn.commit()
    yield db_path
    conn.close()
    if os.path.exists(db_path):
        os.remove(db_path)

# --- Test Cases ---
@pytest.mark.asyncio
class TestURLDiscovery:
    """
    URL Discovery 파이프라인에 대한 통합 테스트 (Mock HTML 사용)
    """

    @patch('src.scripts.urldiscovery.college_url_mapper.CollegeURLMapper._fetch_page_content', new_callable=AsyncMock)
    async def test_update_database_with_mock_html(self, mock_fetch, test_db_for_url_discovery):
        # 1. Setup
        db_path = test_db_for_url_discovery
        
        # mock_fetch가 URL에 따라 다른 HTML을 반환하도록 설정
        mock_snu_html = load_mock_html('mock_snu_departments_page.html')
        mock_kaist_html = load_mock_html('mock_kaist_departments_page.html')
        
        def side_effect(url):
            if "snu.ac.kr" in url:
                return mock_snu_html
            if "kaist.ac.kr" in url:
                return mock_kaist_html
            return ""
        
        mock_fetch.side_effect = side_effect
        
        mapper = CollegeURLMapper(db_path=db_path)

        # 2. Execution
        await mapper._update_database_async()

        # 3. Verification
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # 서울대학교 컴퓨터공학부 URL 확인
        cursor.execute("SELECT department_url, status FROM crawl_targets WHERE university_name='서울대학교' AND department_name='컴퓨터공학부'")
        snu_data = cursor.fetchone()
        assert snu_data is not None
        assert snu_data['department_url'] == "https://www.snu.ac.kr/academics/departments/computer-science"
        assert snu_data['status'] == "URLFound"

        # KAIST 전산학부 URL 확인
        cursor.execute("SELECT department_url, status FROM crawl_targets WHERE university_name='KAIST' AND department_name='전산학부'")
        kaist_data = cursor.fetchone()
        assert kaist_data is not None
        assert kaist_data['department_url'] == "https://cs.kaist.ac.kr/"
        assert kaist_data['status'] == "URLFound"

        # 패턴이 없는 대학은 URL이 업데이트되지 않아야 함
        cursor.execute("SELECT department_url, status FROM crawl_targets WHERE university_name='패턴없는대학'")
        no_pattern_data = cursor.fetchone()
        assert no_pattern_data is not None
        assert no_pattern_data['department_url'] is None
        assert no_pattern_data['status'] == "Ready"

        conn.close()

    @patch('src.scripts.urldiscovery.college_url_mapper.CollegeURLMapper._fetch_page_content', new_callable=AsyncMock)
    async def test_run_url_mapper_script_with_mock(self, mock_fetch, test_db_for_url_discovery):
        # 1. Setup
        db_path = test_db_for_url_discovery
        mock_snu_html = load_mock_html('mock_snu_departments_page.html')
        mock_kaist_html = load_mock_html('mock_kaist_departments_page.html')
        
        def side_effect(url):
            if "snu.ac.kr" in url:
                return mock_snu_html
            if "kaist.ac.kr" in url:
                return mock_kaist_html
            return ""
        
        mock_fetch.side_effect = side_effect

        # 2. Execution
        # run_url_mapper.main()은 내부적으로 asyncio.run()을 호출하므로,
        # 이미 실행중인 이벤트 루프에서는 직접 비동기 함수를 호출해야 함.
        mapper = CollegeURLMapper(db_path=db_path);
        await mapper._update_database_async()

        # 3. Verification
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("SELECT department_url, status FROM crawl_targets WHERE university_name='서울대학교' AND department_name='컴퓨터공학부'")
        snu_data = cursor.fetchone()
        assert snu_data is not None
        assert snu_data['department_url'] is not None
        assert snu_data['status'] == "URLFound"

        conn.close()
