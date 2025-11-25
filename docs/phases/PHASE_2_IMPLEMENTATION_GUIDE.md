# 🛠️ Phase 2: 구현 가이드

**목표:** 공공 API 기반 동적 크롤링 범위 지정 시스템 구축
**기간:** 4주 (Week 1-4)
**담당:** Phase 2 개발팀

---

## 📋 주간별 구현 계획

### Week 1: 기초 데이터 파이프라인 구성

#### 1-1: 커리어넷 API 통합 (Day 1-2)

**준비 작업:**
```bash
# 1. 커리어넷 API 키 발급
# https://www.career.go.kr/cnet/openapi/getOpenApi 방문
# API 가입 후 serviceKey 발급

# 2. .env 파일에 키 저장
echo "CAREER_API_KEY=YOUR_KEY_HERE" >> .env
```

**구현:**
```python
# src/services/career_api_client.py

from typing import List, Dict
import requests
from tenacity import retry, stop_after_attempt

class CareerAPIClient:
    """
    커리어넷 오픈 API 클라이언트
    """

    BASE_URL = "https://www.career.go.kr/cnet/openapi/getOpenApi"

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.session = requests.Session()

    @retry(stop=stop_after_attempt(3))
    def search_universities(self, page: int = 1, page_size: int = 100) -> List[Dict]:
        """
        전국 대학 및 학과 정보 조회
        """
        params = {
            "serviceKey": self.api_key,
            "subject": "school",
            "thisPage": page,
            "listSize": page_size,
            "dataType": "json"
        }

        response = self.session.get(self.BASE_URL, params=params)
        response.raise_for_status()

        data = response.json()
        return data.get("dataSearch", [])

    def search_by_category(self, category: str, page: int = 1) -> List[Dict]:
        """
        계열별 대학/학과 조회 (예: "공학", "자연과학")
        """
        params = {
            "serviceKey": self.api_key,
            "subject": "school",
            "majorGroup": category,
            "thisPage": page,
            "listSize": 100,
            "dataType": "json"
        }

        response = self.session.get(self.BASE_URL, params=params)
        response.raise_for_status()

        return response.json().get("dataSearch", [])
```

#### 1-2: crawl_targets 테이블 설계 (Day 2-3)

**마이그레이션 스크립트:**
```python
# src/scripts/migrations/002_create_crawl_targets.py

def migrate_up(db_connection):
    """
    crawl_targets 테이블 생성
    """
    db_connection.execute("""
        CREATE TABLE crawl_targets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            university_id VARCHAR(50),
            university_name VARCHAR(255) NOT NULL,
            university_name_ko VARCHAR(255),
            university_url VARCHAR(512),
            college_id VARCHAR(50),
            college_name VARCHAR(255),
            college_name_ko VARCHAR(255),
            college_url VARCHAR(512),
            department_id VARCHAR(50),
            department_name VARCHAR(255),
            department_name_ko VARCHAR(255),
            department_url VARCHAR(512),
            category VARCHAR(100),
            status VARCHAR(50) DEFAULT 'Ready',
            priority INT DEFAULT 0,
            attempts INT DEFAULT 0,
            last_error TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # 인덱스 생성
    db_connection.execute(
        "CREATE INDEX idx_crawl_status ON crawl_targets(status)"
    )
    db_connection.execute(
        "CREATE INDEX idx_crawl_university ON crawl_targets(university_name)"
    )
    db_connection.execute(
        "CREATE INDEX idx_crawl_category ON crawl_targets(category)"
    )

    db_connection.commit()
```

#### 1-3: SeedGenerator 구현 (Day 3-4)

**파일:** `src/scripts/seedgen/seed_generator.py`

```python
from typing import List, Dict
import sqlite3
from datetime import datetime
from src.services.career_api_client import CareerAPIClient

class SeedGenerator:
    """
    커리어넷 API를 통해 크롤링 타겟 리스트 자동 생성
    """

    def __init__(self, db_path: str, api_client: CareerAPIClient):
        self.db_path = db_path
        self.api_client = api_client

    def generate_seeds_for_category(self, category: str, max_pages: int = 10):
        """
        특정 계열의 모든 대학/학과 Seed 생성
        """
        print(f"📊 {category} 계열 대학/학과 정보 수집 중...")

        all_seeds = []
        for page in range(1, max_pages + 1):
            seeds = self.api_client.search_by_category(category, page=page)

            if not seeds:
                break

            all_seeds.extend(seeds)
            print(f"   ✓ {page}페이지: {len(seeds)}개 데이터")

        print(f"✅ 총 {len(all_seeds)}개 데이터 수집 완료")

        return all_seeds

    def save_seeds_to_db(self, seeds: List[Dict]):
        """
        수집한 Seed를 DB에 저장
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        inserted = 0
        for seed in seeds:
            try:
                cursor.execute("""
                    INSERT INTO crawl_targets (
                        university_name, university_name_ko,
                        college_name, college_name_ko,
                        department_name, department_name_ko,
                        category, status, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    seed.get("schoolName", ""),
                    seed.get("schoolNameKo", ""),
                    seed.get("majorName", ""),
                    seed.get("majorNameKo", ""),
                    seed.get("departmentName", ""),
                    seed.get("departmentNameKo", ""),
                    seed.get("majorGroup", "기타"),
                    "Ready",
                    datetime.now()
                ))
                inserted += 1
            except sqlite3.IntegrityError:
                # 중복 데이터 스킵
                pass

        conn.commit()
        conn.close()

        print(f"💾 {inserted}개 데이터 DB 저장 완료")

    def run(self, categories: List[str] = None):
        """
        전체 Seed 생성 파이프라인
        """
        if categories is None:
            categories = ["공학", "자연과학", "의학"]

        for category in categories:
            seeds = self.generate_seeds_for_category(category)
            self.save_seeds_to_db(seeds)
```

**실행:**
```bash
# src/scripts/seedgen/run_seed_generator.py
python -m src.scripts.seedgen.run_seed_generator \
    --api-key $CAREER_API_KEY \
    --categories "공학" "자연과학" "의학" \
    --db univ_insight.db
```

---

### Week 2: URL 발견 (URL Discovery)

#### 2-1: Google Custom Search API 통합 (선택 사항)

```python
# src/services/google_search_client.py

class GoogleSearchClient:
    """
    Google Custom Search API를 통한 URL 발견
    """

    def __init__(self, api_key: str, search_engine_id: str):
        self.api_key = api_key
        self.search_engine_id = search_engine_id

    def find_department_url(self, university: str, department: str) -> str:
        """
        "{대학명} {학과명} 홈페이지" 검색
        """
        query = f"{university} {department} 홈페이지"
        # ... API 호출 ...
        return url
```

#### 2-2: 직접 웹 스크래핑 기반 URL 추출 (권장)

```python
# src/scripts/urldiscovery/college_url_mapper.py

from typing import Dict, List
from bs4 import BeautifulSoup
import requests

class CollegeURLMapper:
    """
    각 대학 웹사이트에서 학과 URL 자동 추출
    """

    # 대학별 단과대학 URL 패턴
    UNIVERSITY_PATTERNS = {
        "서울대학교": {
            "base_url": "http://snu.ac.kr",
            "colleges_path": "/about/colleges",
            "css_selector": "a.college-link"
        },
        "KAIST": {
            "base_url": "http://kaist.ac.kr",
            "colleges_path": "/academics/schools",
            "css_selector": "a.school-link"
        },
        # ... 더 많은 대학들 ...
    }

    def map_university_urls(self, university_name: str) -> List[Dict]:
        """
        특정 대학의 학과 URL 매핑
        """
        if university_name not in self.UNIVERSITY_PATTERNS:
            return []

        pattern = self.UNIVERSITY_PATTERNS[university_name]
        base_url = pattern["base_url"]
        colleges_url = base_url + pattern["colleges_path"]

        try:
            response = requests.get(colleges_url, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')
            departments = []

            for link in soup.select(pattern["css_selector"]):
                dept_name = link.get_text(strip=True)
                dept_url = link.get("href", "")

                # 상대 경로인 경우 절대 경로로 변환
                if not dept_url.startswith("http"):
                    dept_url = base_url + dept_url

                departments.append({
                    "name": dept_name,
                    "url": dept_url
                })

            return departments

        except Exception as e:
            print(f"❌ {university_name} URL 추출 실패: {e}")
            return []

    def update_database(self, db_path: str):
        """
        DB의 crawl_targets 테이블 업데이트
        """
        import sqlite3

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # 모든 대학 조회
        cursor.execute("SELECT DISTINCT university_name FROM crawl_targets")
        universities = [row[0] for row in cursor.fetchall()]

        for university in universities:
            departments = self.map_university_urls(university)

            for dept in departments:
                # 해당 학과 업데이트
                cursor.execute("""
                    UPDATE crawl_targets
                    SET department_url = ?, status = 'URLFound'
                    WHERE university_name = ? AND department_name = ?
                """, (dept["url"], university, dept["name"]))

        conn.commit()
        conn.close()

        print(f"✅ {len(universities)}개 대학 URL 업데이트 완료")
```

**실행:**
```bash
python -m src.scripts.urldiscovery.update_department_urls \
    --db univ_insight.db
```

---

### Week 3: DynamicCrawler 리팩토링

#### 3-1: Phase 1 SNUCrawler 분석 및 재설계

**기존 코드 분석:**
```python
# src/services/snu_crawler.py 검토
# → 서울대 특화 코드 분리
# → 범용 크롤링 로직 추출
```

#### 3-2: DynamicCrawler 구현

```python
# src/services/dynamic_crawler.py

from typing import List, Dict, Optional
import sqlite3
from datetime import datetime
import requests
from bs4 import BeautifulSoup

class DynamicCrawler:
    """
    Phase 2: 범위가 지정된 동적 크롤링
    """

    def __init__(self, db_path: str, batch_size: int = 100):
        self.db_path = db_path
        self.batch_size = batch_size
        self.session = requests.Session()

    def get_targets_for_crawl(self, status: str = "URLFound", limit: int = 100) -> List[Dict]:
        """
        크롤링할 타겟 학과 조회
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, university_name, department_name, department_url
            FROM crawl_targets
            WHERE status = ? AND department_url IS NOT NULL
            LIMIT ?
        """, (status, limit))

        targets = [dict(row) for row in cursor.fetchall()]
        conn.close()

        return targets

    def crawl_department(self, target: Dict) -> Dict:
        """
        개별 학과 페이지에서 교수 정보 크롤링
        """
        try:
            response = self.session.get(target["department_url"], timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # 교수 정보 추출 (대학별 커스텀 로직)
            professors = self._extract_professors(
                soup,
                target["university_name"],
                target["department_name"]
            )

            return {
                "success": True,
                "professors": professors,
                "count": len(professors)
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "count": 0
            }

    def _extract_professors(self, soup: BeautifulSoup, univ_name: str, dept_name: str) -> List[Dict]:
        """
        대학별 다양한 HTML 구조 대응
        """
        # Phase 1 SNUCrawler 로직 재사용 + 확장
        professors = []

        # 일반적인 CSS 셀렉터 시도
        common_selectors = [
            "div.professor-item",
            "div.faculty-member",
            "tr.professor-row",
            "article.professor"
        ]

        for selector in common_selectors:
            elements = soup.select(selector)
            if elements:
                for elem in elements:
                    prof = self._parse_professor_element(elem)
                    if prof:
                        professors.append(prof)
                break

        return professors

    def _parse_professor_element(self, element) -> Optional[Dict]:
        """
        교수 요소에서 정보 추출
        """
        try:
            # 기본 정보 추출
            name = element.select_one(".professor-name, .name")
            title = element.select_one(".professor-title, .title")
            email = element.select_one(".professor-email, a[href^='mailto']")

            if not name:
                return None

            return {
                "name": name.get_text(strip=True),
                "title": title.get_text(strip=True) if title else "교수",
                "email": email.get_text(strip=True) if email else None
            }

        except Exception:
            return None

    def crawl_all_targets(self):
        """
        모든 타겟 학과에서 크롤링 실행
        """
        targets = self.get_targets_for_crawl(status="URLFound")

        print(f"🎯 {len(targets)}개 학과에서 크롤링 시작...")

        successful = 0
        failed = 0

        for i, target in enumerate(targets, 1):
            print(f"[{i}/{len(targets)}] {target['university_name']} - {target['department_name']}", end=" ")

            result = self.crawl_department(target)

            if result["success"]:
                print(f"✅ {result['count']}명 교수")
                successful += 1
                self._update_target_status(target["id"], "Complete", None)
            else:
                print(f"❌ 실패: {result['error'][:50]}")
                failed += 1
                self._update_target_status(target["id"], "Failed", result["error"])

            # 서버 부하 방지
            import time
            time.sleep(1)

        print(f"\n📊 완료: {successful}개 성공, {failed}개 실패")

    def _update_target_status(self, target_id: int, status: str, error: Optional[str]):
        """
        크롤링 상태 업데이트
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE crawl_targets
            SET status = ?, last_error = ?, updated_at = ?
            WHERE id = ?
        """, (status, error, datetime.now(), target_id))

        conn.commit()
        conn.close()
```

**실행:**
```bash
# src/scripts/pipelines/run_dynamic_crawler.py
python -m src.scripts.pipelines.run_dynamic_crawler \
    --db univ_insight.db \
    --limit 100  # 처음엔 100개 테스트
```

---

### Week 4: 테스트 및 최적화

#### 4-1: E2E 테스트

```python
# tests/e2e/test_dynamic_crawler_pipeline.py

import pytest
from src.scripts.seedgen.seed_generator import SeedGenerator
from src.scripts.urldiscovery.college_url_mapper import CollegeURLMapper
from src.services.dynamic_crawler import DynamicCrawler

class TestDynamicCrawlerPipeline:
    """
    Phase 2 동적 크롤러 파이프라인 E2E 테스트
    """

    def test_seed_generation(self, db_path):
        """
        Seed 생성 테스트
        """
        # ... 테스트 코드 ...

    def test_url_discovery(self, db_path):
        """
        URL 발견 테스트
        """
        # ... 테스트 코드 ...

    def test_dynamic_crawling(self, db_path):
        """
        동적 크롤링 테스트
        """
        # ... 테스트 코드 ...

    def test_end_to_end_pipeline(self, db_path):
        """
        전체 파이프라인 E2E 테스트
        """
        # 1. Seed 생성
        # 2. URL 발견
        # 3. 크롤링
        # 4. 데이터 검증
```

#### 4-2: 성능 최적화

```python
# src/scripts/performance/crawl_performance_test.py

import time
import statistics

class CrawlPerformanceTest:
    """
    크롤링 성능 측정 및 최적화
    """

    def measure_crawl_speed(self, target_count: int = 100):
        """
        크롤링 속도 측정
        """
        times = []

        for i in range(target_count):
            start = time.time()
            # 크롤링 실행
            elapsed = time.time() - start
            times.append(elapsed)

        print(f"평균: {statistics.mean(times):.2f}초")
        print(f"최소: {min(times):.2f}초")
        print(f"최대: {max(times):.2f}초")

        return {
            "mean": statistics.mean(times),
            "median": statistics.median(times),
            "std": statistics.stdev(times)
        }
```

---

## 📊 기대 효과

### 확장성
```
Phase 1 → Phase 2
대학:  1개 → 50개 (50배)
학과:  6개 → 500개 (83배)
교수:  4명 → 5,000명 (1,250배)
```

### 자동화율
```
Phase 1: 0% (하드코드)
Phase 2: 90% (API 자동)
```

---

## 🔧 문제 해결

### 문제 1: API 쿼터 초과
**해결책:**
- 배치 처리 + 딜레이
- 캐싱 메커니즘 도입

### 문제 2: 다양한 웹 구조
**해결책:**
- 대학별 CSS 셀렉터 라이브러리 구축
- Fallback 패턴 정의

### 문제 3: 네트워크 오류
**해결책:**
- Retry 메커니즘 (tenacity)
- 상태 추적 및 재시도

---

## 📋 체크리스트

- [ ] 커리어넷 API 키 발급
- [ ] crawl_targets 테이블 마이그레이션
- [ ] SeedGenerator 구현 완료
- [ ] URL Discovery 구현 완료
- [ ] DynamicCrawler 구현 완료
- [ ] 100개 대학 테스트 통과
- [ ] 성능 기준 달성 (< 5초/학과)
- [ ] 문서화 완료

---

**마지막 업데이트:** 2025-11-25
**상태:** 📋 Phase 2 구현 가이드 완성
**다음:** Phase 2 개발 착수

🤖 Generated with Claude Code
