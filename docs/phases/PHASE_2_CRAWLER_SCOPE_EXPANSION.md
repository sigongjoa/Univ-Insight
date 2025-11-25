# 🌐 Phase 2: 크롤러 범위 확장 전략

**상태:** 📋 계획 (Phase 2 사전 설계)
**작성 날짜:** 2025-11-25
**목표:** 하드코딩 된 대학/학과 리스트 → **API 기반 동적 크롤링 범위 지정**

---

## 📌 Phase 1 vs Phase 2

### Phase 1 (완료) ✅
```
SNUCrawler
├── 하드코딩된 1개 대학 (Seoul National University)
├── 하드코딩된 3개 단과대학
├── 하드코딩된 6개 전공
└── 결과: 제한적이지만 검증 완료 ✓
```

### Phase 2 (계획) 🎯
```
DynamicCrawler
├── 📊 커리어넷 API로 전국 대학 리스트 동적 획득
├── 🎓 각 대학별 학과 목록 동적 생성
├── 🔗 학과 URL 자동 발견
└── 📚 범위가 지정된 체계적 크롤링 실행
```

---

## 🎯 크롤링 범위 지정 전략 (Hybrid Approach)

### Step 1: 타겟 리스트 생성 (Seed Generation)

#### 1.1 공공 API 데이터 수집

**커리어넷 오픈 API** 활용
```python
# API 정보
서비스명: 대학학과정보 API (searchMajorUniversity)
제공기관: 교육부 + 한국직업능력연구원
URL: https://www.career.go.kr/cnet/openapi/getOpenApi
비용: 무료
응답형식: JSON/XML

# 예시: 서울대학교 학과 조회
GET /openapi?serviceKey=YOUR_KEY&thisPage=1&listSize=100&subject=school&schoolName=서울대학교

응답:
{
  "schoolName": "서울대학교",
  "majorCode": "2000001",
  "majorName": "공과대학",
  "departmentCode": "2000011",
  "departmentName": "컴퓨터공학부",
  "schoolUrl": "http://snu.ac.kr"
}
```

**대학알리미 데이터**
```
서비스명: 대학알리미 (AcademyInfo)
URL: https://www.academyinfo.go.kr/
범위: 전국 대학(본교/분교)
제공: 명칭, 주소, 대표 URL, 학과 수
```

#### 1.2 Target List DB 생성

**스키마:**
```sql
CREATE TABLE crawl_targets (
  id INTEGER PRIMARY KEY,
  university_name VARCHAR(100),
  university_name_ko VARCHAR(100),
  university_url VARCHAR(255),
  college_name VARCHAR(100),
  college_name_ko VARCHAR(100),
  college_url VARCHAR(255),
  department_name VARCHAR(100),
  department_name_ko VARCHAR(100),
  department_url VARCHAR(255),
  category VARCHAR(50),  -- "공학", "자연과학", "의학" 등
  status VARCHAR(20),    -- "Ready", "In_Progress", "Complete"
  created_at TIMESTAMP,
  updated_at TIMESTAMP
);
```

**파이썬 코드 예시:**
```python
# src/scripts/seedgen/crawl_seed_generator.py

import requests
import sqlite3
from datetime import datetime

class SeedGenerator:
    """
    커리어넷 API를 통해 크롤링 타겟 리스트 자동 생성
    """

    def __init__(self, db_path: str, api_key: str):
        self.db_path = db_path
        self.api_key = api_key
        self.career_api_url = "https://www.career.go.kr/cnet/openapi/getOpenApi"

    def fetch_universities(self, category: str = None):
        """
        커리어넷 API에서 대학 리스트 조회

        Args:
            category: "공학", "자연과학", "의학" 등 필터링 (선택)

        Returns:
            List[Dict]: 대학/학과 정보
        """
        params = {
            "serviceKey": self.api_key,
            "thisPage": 1,
            "listSize": 100,
            "subject": "school",
        }

        if category:
            params["majorGroup"] = category

        try:
            response = requests.get(self.career_api_url, params=params)
            response.raise_for_status()

            data = response.json()
            return data.get("dataSearch", [])

        except Exception as e:
            print(f"❌ API 조회 실패: {e}")
            return []

    def save_to_db(self, universities: List[Dict]):
        """
        조회한 대학/학과 정보를 DB에 저장
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        for univ in universities:
            cursor.execute("""
                INSERT INTO crawl_targets (
                    university_name, college_name, department_name,
                    category, status, created_at
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (
                univ.get("schoolName", ""),
                univ.get("majorName", ""),
                univ.get("departmentName", ""),
                univ.get("majorGroup", "기타"),
                "Ready",
                datetime.now()
            ))

        conn.commit()
        conn.close()

    def generate_seeds(self, category: str = None):
        """
        전체 Seed 생성 파이프라인
        """
        print(f"📊 {category or '전체'} 대학/학과 정보 조회 중...")
        universities = self.fetch_universities(category)

        print(f"✅ {len(universities)}개 대학/학과 정보 수집 완료")
        self.save_to_db(universities)

        print(f"💾 DB 저장 완료: crawl_targets")
```

**실행:**
```bash
# src/scripts/seedgen/generate_seeds.py 실행
python -m src.scripts.seedgen.generate_seeds \
  --api-key YOUR_CAREER_API_KEY \
  --category "공학" \
  --db univ_insight.db
```

**결과:** crawl_targets 테이블에 1000개+ 대학/학과 자동 저장

---

### Step 2: URL 발견 (URL Discovery)

#### 2.1 문제: API에는 학과 URL이 없음

```
API 응답:
{
  "schoolName": "서울대학교",
  "departmentName": "컴퓨터공학부",
  // ❌ URL 없음!
}
```

#### 2.2 해결책 A: 검색 엔진 활용 (Google Custom Search API)

```python
# src/scripts/urldiscovery/url_finder.py

from google.api_core.client_options import ClientOptions
from google.cloud import customsearch_v1

class URLDiscovery:
    """
    학과 홈페이지 URL을 검색 엔진으로 자동 발견
    """

    def __init__(self, api_key: str, search_engine_id: str):
        self.api_key = api_key
        self.search_engine_id = search_engine_id

    def find_department_url(self, university: str, department: str) -> str:
        """
        "{대학명} {학과명} 홈페이지" 검색으로 URL 발견
        """
        query = f"{university} {department} 홈페이지"

        # Google Custom Search API 호출
        # ...실제 구현...

        return "http://cse.snu.ac.kr"  # 예시

    def update_targets(self, db_path: str):
        """
        crawl_targets 테이블의 URL 필드 업데이트
        """
        # SQL: UPDATE crawl_targets SET department_url = ? WHERE id = ?
        pass
```

#### 2.3 해결책 B: 각 대학 웹사이트에서 URL 추출 (더 정확)

**전략:**
1. 각 대학 "단과대학 목록" 페이지만 먼저 크롤링
2. 그 페이지에서 학과별 URL 추출
3. crawl_targets 테이블에 저장

```python
# src/scripts/urldiscovery/college_mapper.py

class CollegeURLMapper:
    """
    대학 웹사이트에서 단과대학/학과 URL 매핑
    """

    def map_snu_college_urls(self):
        """
        서울대학교 예시:
        http://snu.ac.kr/about/colleges
        → 각 단과대학 링크 추출
        → 각 학과 URL 추출
        """
        pass

    def map_kaist_department_urls(self):
        """
        KAIST 예시:
        http://kaist.ac.kr/academics
        → 전산학부, 기계공학부 등 URL 추출
        """
        pass

    def map_university_urls_generic(self, university_url: str):
        """
        일반적인 패턴으로 다른 대학들도 커버
        """
        pass
```

---

### Step 3: 범위가 지정된 크롤링 (Scoped Deep Crawling)

#### 3.1 개선된 DynamicCrawler

```python
# src/services/dynamic_crawler.py

class DynamicCrawler:
    """
    Phase 2: crawl_targets 테이블을 기반으로 동적 크롤링
    """

    def __init__(self, db_path: str):
        self.db_path = db_path
        self.session = requests.Session()

    def get_crawl_targets(self, status: str = "Ready", limit: int = 100):
        """
        DB에서 크롤링할 학과 리스트 조회

        Returns:
            List[Dict]: 크롤링 대상
            [
              {
                "university_name": "Seoul National University",
                "department_name": "Computer Science and Engineering",
                "department_url": "http://cse.snu.ac.kr"
              },
              ...
            ]
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("""
            SELECT university_name, department_name, department_url
            FROM crawl_targets
            WHERE status = ? AND department_url IS NOT NULL
            LIMIT ?
        """, (status, limit))

        targets = [dict(row) for row in cursor.fetchall()]
        conn.close()

        return targets

    def crawl_all_targets(self):
        """
        모든 대상 학과에서 교수/연구실 정보 크롤링
        """
        targets = self.get_crawl_targets(status="Ready")

        print(f"🎯 {len(targets)}개 학과에서 크롤링 시작...")

        for target in targets:
            try:
                # 각 학과 홈페이지 크롤링
                professors = self.crawl_professors(
                    target["department_url"],
                    target["university_name"],
                    target["department_name"]
                )

                print(f"✅ {target['university_name']} - {target['department_name']}: "
                      f"{len(professors)}명 교수 수집")

                # DB 업데이트
                self.update_status(target["id"], "Complete")

            except Exception as e:
                print(f"❌ {target['department_name']} 크롤링 실패: {e}")
                self.update_status(target["id"], "Failed")

    def crawl_professors(self, url: str, univ_name: str, dept_name: str):
        """
        학과 페이지에서 교수 정보 추출
        """
        # Phase 1 SNUCrawler의 로직 재사용
        # + 대학/학과별 다양한 HTML 구조 처리
        pass

    def update_status(self, target_id: int, status: str):
        """
        크롤링 상태 업데이트
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE crawl_targets
            SET status = ?, updated_at = ?
            WHERE id = ?
        """, (status, datetime.now(), target_id))

        conn.commit()
        conn.close()
```

#### 3.2 실행 방식

```bash
# 1단계: Seed 생성 (대학/학과 리스트)
python src/scripts/seedgen/generate_seeds.py \
  --api-key YOUR_KEY \
  --db univ_insight.db

# 2단계: URL 발견
python src/scripts/urldiscovery/discover_urls.py \
  --db univ_insight.db

# 3단계: 범위가 지정된 크롤링 실행
python -m src.scripts.pipelines.run_dynamic_pipeline \
  --db univ_insight.db \
  --limit 100  # 처음엔 100개 대학만 테스트
```

---

## 📊 데이터 흐름도

```
┌─────────────────────────────────────────────────────────────┐
│ 커리어넷 오픈 API + 대학알리미 API                          │
│ (전국 대학/학과 공공 데이터)                                │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
        ┌──────────────────────────────┐
        │ SeedGenerator.generate_seeds() │
        └──────────┬───────────────────┘
                   │
                   ▼
        ┌──────────────────────────────┐
        │ crawl_targets 테이블         │
        │ (1000개+ 대학/학과 리스트)   │
        │ status: Ready                │
        └──────────┬───────────────────┘
                   │
                   ▼
        ┌──────────────────────────────┐
        │ URLDiscovery.find_urls()     │
        │ (검색 엔진 or 웹 스크래핑)   │
        └──────────┬───────────────────┘
                   │
                   ▼
        ┌──────────────────────────────┐
        │ crawl_targets 업데이트       │
        │ department_url 필드 채우기    │
        │ status: URLFound             │
        └──────────┬───────────────────┘
                   │
                   ▼
        ┌──────────────────────────────┐
        │ DynamicCrawler.crawl_all()   │
        │ (범위가 지정된 크롤링)        │
        └──────────┬───────────────────┘
                   │
                   ▼
        ┌──────────────────────────────┐
        │ 교수/연구실 정보 저장         │
        │ status: Complete             │
        └──────────────────────────────┘
```

---

## 🔧 필요한 마스터 데이터 정리

| 데이터 | 소스 | 확보 방식 | 상태 |
|--------|------|---------|------|
| **전국 대학 리스트** | 커리어넷 API / 대학알리미 | API 자동 호출 | ✅ 자동화 |
| **각 대학별 학과** | 커리어넷 API | API 자동 호출 | ✅ 자동화 |
| **학과 홈페이지 URL** | Google CSE / 웹 스크래핑 | URL Discovery | ⚠️ 반자동 |
| **교수 정보** | 각 학과 홈페이지 | 직접 크롤링 필수 | ❌ 필수 크롤링 |
| **연구실 정보** | 교수 페이지 | 직접 크롤링 필수 | ❌ 필수 크롤링 |
| **논문 정보** | 연구실/교수 페이지 | 직접 크롤링 필수 | ❌ 필수 크롤링 |

---

## 📋 Phase 2 체크리스트

### 2-1: 공공 API 통합
- [ ] 커리어넷 API 가입 및 키 발급
- [ ] 대학알리미 데이터 수집 로직 구현
- [ ] crawl_targets 테이블 설계 및 생성

### 2-2: SeedGenerator 구현
- [ ] SeedGenerator 클래스 작성
- [ ] API 연동 및 데이터 저장 기능
- [ ] 에러 처리 및 재시도 로직

### 2-3: URL Discovery
- [ ] Google Custom Search API 또는 오픈 소스 검색 엔진 선택
- [ ] CollegeURLMapper 구현
- [ ] URL 검증 및 업데이트 로직

### 2-4: DynamicCrawler
- [ ] Phase 1 SNUCrawler 리팩토링
- [ ] 다양한 대학 웹사이트 구조 대응
- [ ] 크롤링 상태 추적 및 로깅

### 2-5: 테스트 및 검증
- [ ] SeedGen 테스트 (100개 대학)
- [ ] URL Discovery 검증
- [ ] 범위가 지정된 크롤링 E2E 테스트

---

## 🎯 Phase 2 성공 기준

| 지표 | Phase 1 | Phase 2 목표 | 상태 |
|------|---------|----------|------|
| **대학 수** | 1개 | 50개+ | 50배 확장 |
| **학과 수** | 6개 | 500개+ | 83배 확장 |
| **교수 수** | 4명 | 5000명+ | 1250배 확장 |
| **논문 수** | 5개 | 10,000개+ | 2000배 확장 |
| **자동화율** | 0% (하드코드) | 90% (API 기반) | 대폭 개선 |
| **크롤링 시간** | 수분 | 몇 시간 | 대규모 처리 |

---

## 💡 주요 고려사항

### 1. API 쿼터 제한
- 커리어넷 API: 일일 호출 수 제한 가능
- **대응:** 배치 처리 + 캐싱

### 2. 웹사이트 구조 다양성
- 각 대학마다 학과 페이지 구조가 다름
- **대응:** 정규식/BeautifulSoup 패턴 라이브러리 구축

### 3. 로봇 배제 (robots.txt)
- 크롤링 전에 각 사이트의 robots.txt 확인
- **대응:** User-Agent 설정 + 딜레이 적용

### 4. 개인정보보호
- 교수 개인 이메일 등 민감 정보 처리
- **대응:** 필요한 정보만 최소한으로 수집

---

## 📚 참고 자료

### 공공 API
- [커리어넷 오픈 API](https://www.career.go.kr/cnet/openapi/getOpenApi)
- [대학알리미](https://www.academyinfo.go.kr/)
- [공공데이터포털](https://www.data.go.kr/)

### 개발 자료
- Phase 1 SNUCrawler: `src/services/snu_crawler.py`
- 참고 문서: `docs/ARCHITECTURE.md`

---

## 🚀 다음 단계

1. **Phase 2 시작 전:** 커리어넷 API 키 발급
2. **Week 1:** SeedGenerator 구현 및 테스트
3. **Week 2:** URL Discovery 구현
4. **Week 3:** DynamicCrawler 리팩토링
5. **Week 4:** 대규모 테스트 및 최적화

---

**마지막 업데이트:** 2025-11-25
**작성자:** Claude Code
**상태:** 📋 Phase 2 사전 설계 완료
**다음:** Phase 2 착수

🤖 Generated with Claude Code
