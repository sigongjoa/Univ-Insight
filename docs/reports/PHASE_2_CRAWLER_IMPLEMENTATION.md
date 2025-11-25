# 🚀 Phase 2 크롤러 구현 계획

**목표:** API 기반 대학/학과 정보 수집 후, 각 대학 홈페이지에서 교수/연구실/논문 정보 크롤링

**핵심 원칙:**
- ✅ 공개 API로 대학/학과 기본 정보 자동 수집
- ✅ 각 대학 홈페이지를 기준점으로 구조화된 정보 추출
- ✅ 수집된 논문에 Ollama 분석 자동 적용

---

## 📊 Phase 2 파이프라인 구조

```
┌─────────────────────────────────────────────────────────────┐
│ 1단계: 마스터 데이터 수집 (공개 API)                          │
├─────────────────────────────────────────────────────────────┤
│  • 커리어넷 API → 전국 대학 목록                             │
│  • 각 대학별 학과/전공 정보                                  │
│  • 결과: universities, colleges, departments 테이블 자동 채우기 │
└──────────────┬──────────────────────────────────────────────┘
               │
┌──────────────▼──────────────────────────────────────────────┐
│ 2단계: 각 대학 홈페이지 기준 정보 수집                        │
├─────────────────────────────────────────────────────────────┤
│  • 대학 공식 사이트에서 학과/연구실 URL 찾기                  │
│  • 각 학과별 교수 정보 페이지 접근                           │
│  • 결과: professors, laboratories 테이블 채우기              │
└──────────────┬──────────────────────────────────────────────┘
               │
┌──────────────▼──────────────────────────────────────────────┐
│ 3단계: 연구논문 정보 수집                                     │
├─────────────────────────────────────────────────────────────┤
│  • 교수 홈페이지 → 논문 목록/링크                             │
│  • 연구실 페이지 → 진행 중인 프로젝트/논문                    │
│  • 결과: research_papers 테이블 채우기                        │
└──────────────┬──────────────────────────────────────────────┘
               │
┌──────────────▼──────────────────────────────────────────────┐
│ 4단계: Ollama 분석 자동 적용                                  │
├─────────────────────────────────────────────────────────────┤
│  • run_real_analysis_pipeline.py 실행                       │
│  • 모든 수집된 논문에 LLM 분석 적용                          │
│  • 결과: paper_analysis 테이블 자동 채우기                    │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔧 실제 구현 (대학별 예시)

### 예시 1: 서울대학교 공과대학

```
1. API로 수집:
   - University: 서울대학교
   - College: 공과대학
   - Department: 컴퓨터공학부

2. 홈페이지 크롤링 (engineering.snu.ac.kr):
   - 학과 URL: /cse/ (컴퓨터공학부)
   - 교수 목록: /faculty/
   - 연구실: /labs/

3. 각 교수별 크롤링 (예: 최병희 교수):
   - 홈페이지: /faculty/choi-byoung-hee/
   - 논문 목록: /publications/
   - 연구 주제: "Database Systems"

4. 연구논문 수집:
   - 논문 제목
   - 발표 연도/학회
   - 논문 링크/PDF
   - 공동저자 정보

5. Ollama 분석 자동 실행:
   - 각 논문의 주요 내용 요약
   - 관련 직업/회사 추천
   - 필요한 과목 제시
```

---

## 📋 데이터베이스 테이블 확장

### 기존 (Phase 1):
```
✅ universities (1개 레코드)
✅ colleges (3개)
✅ departments (6개)
✅ professors (4명)
✅ laboratories (4개)
✅ research_papers (5개)
✅ paper_analysis (5개) ← Ollama 분석 결과
```

### Phase 2 목표:
```
📈 universities (50+개)
📈 colleges (200+개)
📈 departments (500+개)
📈 professors (5000+개)
📈 laboratories (1000+개)
📈 research_papers (10000+개)
📈 paper_analysis (10000+개) ← 모두 Ollama 분석
```

---

## 🔍 각 단계별 구현 전략

### 1️⃣ 단계 1: API 기반 마스터 데이터

**사용할 API:**
- **커리어넷 오픈 API** (https://www.career.go.kr)
  - 국가직무능력표준(NCS) 데이터
  - 대학교 정보 및 학과별 정보
  - 진로 정보 데이터

**구현 코드:**
```python
# src/services/career_api_client.py
class CareerAPIClient:
    def get_universities(self) -> List[Dict]:
        """커리어넷 API에서 대학 목록 조회"""
        # GET /openapi/universities
        # 반환: 전국 대학 리스트

    def get_departments(self, university_id: str) -> List[Dict]:
        """특정 대학의 학과 목록 조회"""
        # GET /openapi/universities/{id}/departments
        # 반환: 학과별 정보, 학과 홈페이지 URL

    def get_professors(self, department_id: str) -> List[Dict]:
        """학과의 교수 정보 조회"""
        # 주의: API에서 직접 제공 안 할 수 있음
        # → 대학 홈페이지에서 크롤링 필요
```

**데이터베이스 자동 저장:**
```python
# src/services/seed_generator.py
class SeedGenerator:
    def generate_seeds_from_api(self):
        """API 결과를 DB에 자동 저장"""

        # 1. 모든 대학 저장
        universities = api_client.get_universities()
        for uni in universities:
            db.add(University(**uni))

        # 2. 각 대학별 학과 저장
        for uni in universities:
            departments = api_client.get_departments(uni.id)
            for dept in departments:
                db.add(Department(**dept))

        db.commit()
```

---

### 2️⃣ 단계 2: 대학 홈페이지 기반 정보 수집

**구현 전략:**
```python
# src/services/university_crawler.py
class UniversityCrawler:
    def __init__(self, university_url: str):
        """각 대학 홈페이지 URL을 받아 초기화"""
        self.url = university_url
        self.session = requests.Session()

    def find_department_pages(self) -> Dict[str, str]:
        """홈페이지에서 학과별 페이지 URL 찾기"""
        # 대학 메인 사이트 → 학과/단과대 링크 분석
        # 예: /college/, /department/, /faculty/ 등

    def find_professors(self, department_url: str) -> List[Dict]:
        """학과 페이지에서 교수 정보 추출"""
        # 교수 이름, 직급, 전공, 홈페이지 URL
        # 예: 최병희 교수, 정교수, Database Systems

    def find_research_labs(self, department_url: str) -> List[Dict]:
        """학과에서 연구실 정보 추출"""
        # 연구실 이름, 담당 교수, 주요 연구 분야
```

**대학별 예시 구현:**
```python
# 서울대학교 예시
class SNUCrawler(UniversityCrawler):
    MAIN_URL = "https://www.snu.ac.kr"
    ENGINEERING_URL = "https://engineering.snu.ac.kr"

    def find_cse_professors(self):
        """공대 컴퓨터공학부 교수 목록 크롤링"""
        url = f"{self.ENGINEERING_URL}/cse/people/faculty/"
        # CSS 셀렉터: .professor-card, .faculty-name

# 카이스트 예시
class KAISTCrawler(UniversityCrawler):
    MAIN_URL = "https://www.kaist.ac.kr"

    def find_cs_professors(self):
        """컴퓨터공학과 교수 목록 크롤링"""
        url = f"{self.MAIN_URL}/cs/people/"
```

---

### 3️⃣ 단계 3: 연구논문 정보 수집

**구현 전략:**
```python
# src/services/paper_crawler.py
class PaperCrawler:
    def crawl_professor_papers(self, prof_url: str) -> List[Dict]:
        """교수 홈페이지에서 논문 목록 수집"""
        # 1. 교수 홈페이지 접근
        # 2. 논문 섹션 찾기 (Publications, Research, Papers 등)
        # 3. 각 논문의:
        #    - 제목 (Title)
        #    - 저자 (Authors)
        #    - 발표 연도 (Year)
        #    - 학회/저널 (Venue)
        #    - 논문 링크 (PDF URL)

    def crawl_lab_papers(self, lab_url: str) -> List[Dict]:
        """연구실 페이지에서 진행 중인 프로젝트/논문 수집"""
        # 연구실 홈페이지 → 진행 중인 연구, 발표 논문
```

**데이터 저장:**
```python
# 수집한 논문 정보
{
    "id": "paper-snu-cs-001",
    "title": "Real-time Database System for Autonomous Systems",
    "authors": ["Choi, Byoung-Hee", "Kim, John"],
    "publication_year": 2024,
    "venue": "ACM SIGMOD Conference",
    "url": "https://...",
    "pdf_url": "https://...",
    "abstract": "...",
    "full_text": "..." (가능하면 추출),
    "lab_id": "lab-snu-cs-001"
}
```

---

### 4️⃣ 단계 4: Ollama 분석 자동 적용

**기존 파이프라인 재사용:**
```python
# run_real_analysis_pipeline.py를 그대로 사용
# 단, 입력 논문 수를 대폭 확대

# Phase 1: 5개 논문 분석 (완료)
# Phase 2: 10,000개 논문 분석 (배치 처리)

python run_real_analysis_pipeline.py \
    --batch-size 100 \
    --parallel 4 \
    --start-id 5 \
    --end-id 10005
```

---

## 🎯 현실적인 구현 순서

### Week 1: API 통합 및 마스터 데이터
```
Day 1-2: 커리어넷 API 연동
Day 3-4: 대학/학과 데이터 수집 및 DB 저장
Day 5: 테스트 및 검증
```

### Week 2-3: 대학별 크롤러 구현
```
대학 1 (서울대): CSS 셀렉터 분석 및 크롤러 구현
대학 2 (카이스트): 페이지 구조 분석 및 크롤러
대학 3 (고려대): 페이지 구조 분석 및 크롤러
...
```

### Week 4: 논문 수집 및 분석
```
Day 1-2: 수집된 모든 논문에 Ollama 분석 배치 처리
Day 3-4: 결과 검증 및 최적화
Day 5: 최종 리포트
```

---

## 📊 Phase 2 성공 지표

```
목표:
✅ 대학 50개 이상
✅ 학과 500개 이상
✅ 교수 5,000명 이상
✅ 논문 10,000개 이상
✅ 모든 논문 Ollama 분석 완료

현황 (Phase 1):
- 대학: 1개
- 학과: 6개
- 교수: 4명
- 논문: 5개
- 분석: 5개 (100%)

Phase 2 확대:
- 대학: 50배 증가
- 학과: 83배 증가
- 교수: 1250배 증가
- 논문: 2000배 증가
- 자동 분석: 100% (배치 처리)
```

---

## ✅ 준비 완료 사항

- ✅ Ollama 분석 파이프라인 (run_real_analysis_pipeline.py)
- ✅ 데이터베이스 스키마 (SQLAlchemy 모델)
- ✅ Pydantic 스키마 (LLM 입출력)
- ❌ API 클라이언트 (구현 필요)
- ❌ 대학별 크롤러 (구현 필요)
- ❌ 논문 크롤러 (구현 필요)

---

**다음 단계:** API 클라이언트 및 첫 번째 대학(서울대) 크롤러 구현 시작
