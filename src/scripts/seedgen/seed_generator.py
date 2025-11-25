
import sqlite3
from datetime import datetime
from typing import List, Dict

# 상위 디렉토리의 모듈을 import 하기 위해 sys.path에 추가
import sys
import os
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.services.career_api_client import CareerAPIClient


class SeedGenerator:
    """
    커리어넷 API를 통해 크롤링 타겟 리스트(seed)를 자동 생성하고 DB에 저장합니다.
    """

    def __init__(self, db_path: str, api_client: CareerAPIClient):
        """
        Args:
            db_path (str): SQLite 데이터베이스 파일 경로
            api_client (CareerAPIClient): 커리어넷 API 클라이언트 (실제 또는 mock)
        """
        self.db_path = db_path
        self.api_client = api_client

    def generate_seeds_for_category(self, category: str, max_pages: int = 10) -> List[Dict]:
        """
        특정 계열의 모든 대학/학과 Seed를 API에서 가져옵니다.

        Args:
            category (str): 조회할 계열 (예: "공학", "자연과학")
            max_pages (int): 조회할 최대 페이지 수

        Returns:
            List[Dict]: API에서 수집된 대학/학과 정보 리스트
        """
        print(f"📊 '{category}' 계열 대학/학과 정보 수집 중...")

        all_seeds = []
        # API 클라이언트가 mock 모드일 경우, 페이징 없이 한 번만 호출합니다.
        if self.api_client.mock:
            max_pages = 1

        for page in range(1, max_pages + 1):
            try:
                seeds = self.api_client.search_by_category(category, page=page)
                if not seeds:
                    print(f"   -> {page}페이지에서 더 이상 데이터가 없어 중단합니다.")
                    break
                
                all_seeds.extend(seeds)
                print(f"   ✓ {page}페이지: {len(seeds)}개 데이터 수집")

            except Exception as e:
                print(f"   ❌ {page}페이지 조회 중 오류 발생: {e}")
                break

        print(f"✅ 총 {len(all_seeds)}개 '{category}' 계열 데이터 수집 완료")
        return all_seeds

    def save_seeds_to_db(self, seeds: List[Dict]):
        """
        수집한 Seed를 데이터베이스에 저장합니다. 중복된 데이터는 무시합니다.

        Args:
            seeds (List[Dict]): 저장할 대학/학과 정보 리스트
        """
        if not seeds:
            print("💾 저장할 데이터가 없습니다. DB 저장을 건너뜁니다.")
            return

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # 중복 확인을 위한 UNIQUE 인덱스 생성 (university_name, department_name)
        # 이미 테이블에 데이터가 있을 수 있으므로, 에러를 무시합니다.
        try:
            cursor.execute("""
                CREATE UNIQUE INDEX IF NOT EXISTS idx_univ_dept_unique 
                ON crawl_targets(university_name, department_name)
            """)
        except sqlite3.OperationalError:
            pass

        inserted_count = 0
        skipped_count = 0
        for seed in seeds:
            try:
                cursor.execute("""
                    INSERT INTO crawl_targets (
                        university_name, university_name_ko,
                        college_name,
                        department_name, department_name_ko,
                        category, status, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    seed.get("schoolName"),
                    seed.get("schoolNameKo", seed.get("schoolName")),
                    seed.get("majorName"),
                    seed.get("departmentName"),
                    seed.get("departmentNameKo", seed.get("departmentName")),
                    seed.get("majorGroup"),
                    'Ready',
                    datetime.now(),
                    datetime.now()
                ))
                inserted_count += 1
            except sqlite3.IntegrityError:
                # 중복 데이터일 경우 건너뜁니다.
                skipped_count += 1
            except Exception as e:
                print(f"DB 저장 중 오류 발생: {e}")
                skipped_count += 1
        
        conn.commit()
        conn.close()

        print(f"💾 DB 저장 완료: {inserted_count}개 신규 저장, {skipped_count}개 중복/오류로 건너뜀.")

    def run(self, categories: List[str]):
        """
        지정된 모든 카테고리에 대해 Seed 생성 및 저장 파이프라인을 실행합니다.

        Args:
            categories (List[str]): 처리할 계열 리스트
        """
        print(f"🚀 Seed 생성 파이프라인 시작 (대상: {', '.join(categories)})")
        for category in categories:
            seeds = self.generate_seeds_for_category(category)
            self.save_seeds_to_db(seeds)
        print("🏁 모든 Seed 생성 작업 완료.")

if __name__ == '__main__':
    import importlib.util
    
    # 이 스크립트를 직접 실행할 때의 예제 코드
    
    # 1. 테스트용 DB 설정
    test_db_path = 'seed_generator_test.db'
    if os.path.exists(test_db_path):
        os.remove(test_db_path)

    # 2. 테스트용 DB에 테이블 생성
    # Dynamically import the migration script
    migration_file_path = os.path.join(project_root, 'src', 'scripts', 'migrations', '002_create_crawl_targets.py')
    spec = importlib.util.spec_from_file_location("002_create_crawl_targets", migration_file_path)
    migration_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(migration_module)

    conn = sqlite3.connect(test_db_path)
    migration_module.migrate_up(conn)
    conn.close()
    
    print(f"테스트 DB '{test_db_path}' 및 테이블 생성 완료.")

    # 3. Mock API 클라이언트 준비
    mock_api_client = CareerAPIClient(api_key="dummy", mock=True)

    # 4. SeedGenerator 인스턴스 생성 및 실행
    seed_generator = SeedGenerator(db_path=test_db_path, api_client=mock_api_client)
    target_categories = ["공학", "자연과학", "의학", "인문사회"] # Mock 데이터에 없는 카테고리 포함
    seed_generator.run(categories=target_categories)

    # 5. 결과 검증
    conn = sqlite3.connect(test_db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM crawl_targets")
    count = cursor.fetchone()[0]
    print(f"\n🔍 최종 검증: DB에 총 {count}개의 레코드가 저장되었습니다.")
    
    cursor.execute("SELECT * FROM crawl_targets LIMIT 1")
    sample_row = cursor.fetchone()
    print(f"샘플 데이터: {sample_row}")

    conn.close()

    # 6. 테스트용 DB 파일 삭제
    os.remove(test_db_path)
    print(f"\n테스트 DB '{test_db_path}' 삭제 완료.")
