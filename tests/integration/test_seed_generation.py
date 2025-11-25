
import os
import sqlite3
import pytest
import sys
import importlib.util

# 프로젝트 루트를 sys.path에 추가
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.services.career_api_client import CareerAPIClient
from src.scripts.seedgen.seed_generator import SeedGenerator

# --- Dynamically import the migration script ---
migration_file_path = os.path.join(project_root, 'src', 'scripts', 'migrations', '002_create_crawl_targets.py')
spec = importlib.util.spec_from_file_location("002_create_crawl_targets", migration_file_path)
migration_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(migration_module)
# --- End of dynamic import ---

# --- Test Fixtures ---

@pytest.fixture(scope="function")
def test_db():
    """
    테스트용 임시 데이터베이스를 생성하고, 테스트 후 정리하는 Fixture.
    테이블 스키마를 적용하여 반환합니다.
    """
    db_path = "test_seed_generator.db"
    # 이전 테스트 실행 시 파일이 남아있을 경우를 대비해 삭제
    if os.path.exists(db_path):
        os.remove(db_path)
        
    conn = sqlite3.connect(db_path)
    
    # 마이그레이션을 실행하여 테이블 생성
    migration_module.migrate_up(conn)
    
    # DB 경로를 테스트 함수에 전달
    yield db_path
    
    # 테스트 종료 후 연결 종료 및 파일 삭제
    conn.close()
    if os.path.exists(db_path):
        os.remove(db_path)

@pytest.fixture(scope="session")
def mock_api_client():
    """
    Mock 모드로 초기화된 CareerAPIClient 인스턴스를 제공하는 Fixture.
    """
    return CareerAPIClient(api_key="test_key", mock=True)

# --- Test Cases ---

class TestSeedGeneration:
    """
    Seed 생성 파이프라인에 대한 통합 테스트
    (Mock API -> SeedGenerator -> Test DB)
    """

    def test_seed_generator_run(self, test_db, mock_api_client):
        """
        SeedGenerator.run()이 mock 데이터를 DB에 성공적으로 저장하는지 테스트합니다.
        """
        # 1. Setup
        # - test_db: 임시 DB 생성 및 스키마 적용
        # - mock_api_client: mock API 클라이언트
        seed_generator = SeedGenerator(db_path=test_db, api_client=mock_api_client)
        target_categories = ["공학", "자연과학", "의학"]

        # 2. Execution
        seed_generator.run(categories=target_categories)

        # 3. Verification
        conn = sqlite3.connect(test_db)
        cursor = conn.cursor()

        # 전체 레코드 수 확인 (mock 데이터는 4개, 그 중 3개 카테고리에 해당)
        cursor.execute("SELECT COUNT(*) FROM crawl_targets")
        count = cursor.fetchone()[0]
        # mock 데이터에 공학 2, 자연과학 1, 의학 1 = 총 4개
        assert count == 4 

        # 카테고리별 레코드 수 확인
        cursor.execute("SELECT COUNT(*) FROM crawl_targets WHERE category='공학'")
        engineering_count = cursor.fetchone()[0]
        assert engineering_count == 2

        cursor.execute("SELECT COUNT(*) FROM crawl_targets WHERE category='자연과학'")
        science_count = cursor.fetchone()[0]
        assert science_count == 1

        # 데이터 내용 검증 (KAIST 데이터)
        cursor.execute("SELECT * FROM crawl_targets WHERE university_name='KAIST'")
        kaist_row = cursor.fetchone()
        
        assert kaist_row is not None
        # 컬럼명 기반으로 조회하기 위해 row_factory 사용
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM crawl_targets WHERE university_name='KAIST'")
        kaist_row_dict = dict(cursor.fetchone())

        assert kaist_row_dict['university_name_ko'] == "한국과학기술원"
        assert kaist_row_dict['department_name'] == "물리학과"
        assert kaist_row_dict['status'] == "Ready"

        conn.close()

    def test_duplicate_seeds_are_ignored(self, test_db, mock_api_client):
        """
        동일한 카테고리를 두 번 실행했을 때, 중복 데이터가 저장되지 않는지 테스트합니다.
        """
        # 1. Setup
        seed_generator = SeedGenerator(db_path=test_db, api_client=mock_api_client)
        target_categories = ["공학"]

        # 2. Execution (First Run)
        seed_generator.run(categories=target_categories)
        
        # 3. Verification (First Run)
        conn = sqlite3.connect(test_db)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM crawl_targets")
        first_count = cursor.fetchone()[0]
        assert first_count == 2 # Mock 데이터에 공학은 2개

        # 4. Execution (Second Run)
        seed_generator.run(categories=target_categories)

        # 5. Verification (Second Run)
        cursor.execute("SELECT COUNT(*) FROM crawl_targets")
        second_count = cursor.fetchone()[0]
        assert second_count == first_count # 카운트가 변하지 않아야 함

        conn.close()

    def test_run_script_with_mock_flag(self, test_db):
        """
        run_seed_generator.py 스크립트가 --mock 플래그와 함께 실행될 때
        정상적으로 작동하는지 E2E 관점에서 테스트합니다.
        """
        # 1. Setup
        # test_db가 생성되었지만, 스크립트는 파일 경로를 인자로 받음
        db_path = test_db
        
        # 2. Execution
        # 커맨드라인을 통해 스크립트 실행
        # pytest 환경에서 main 스크립트를 직접 실행하는 것은 복잡하므로,
        # 스크립트의 main 함수를 직접 호출하는 방식으로 테스트
        from src.scripts.seedgen import run_seed_generator
        
        # sys.argv를 임시로 조작하여 커맨드라인 인자 전달
        original_argv = sys.argv
        sys.argv = [
            'run_seed_generator.py',
            '--mock',
            '--db', db_path,
            '--categories', '공학', '의학'
        ]
        
        run_seed_generator.main()
        
        # sys.argv 복원
        sys.argv = original_argv

        # 3. Verification
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM crawl_targets")
        count = cursor.fetchone()[0]
        assert count == 3 # 공학 2개 + 의학 1개

        cursor.execute("SELECT COUNT(*) FROM crawl_targets WHERE category='자연과학'")
        science_count = cursor.fetchone()[0]
        assert science_count == 0 # 자연과학은 포함되지 않았으므로 0이어야 함

        conn.close()
