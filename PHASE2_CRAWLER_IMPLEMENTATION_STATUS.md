# Phase 2 크롤러 구현 상태 보고서

**작성 일자:** 2025-11-25
**상태:** 🚀 진행 중 (기반 구조 완성, 정보 추출 개선 진행)

---

## 📋 요약

사용자의 피드백에 따라 **하드코딩된 대학별 크롤러** (SNUCrawler, KAISTCrawler)를 제거하고, **crawl4ai 기반의 범용 크롤러**로 전환했습니다.

### 주요 변경사항
- ❌ ~~SNUCrawler, KAISTCrawler (하드코딩된 각 대학별 크롤러)~~
- ✅ **GenericUniversityCrawler** (crawl4ai 기반 범용 크롤러)
- ✅ **CareerAPIClient** (공개 API를 통한 마스터 데이터 수집)
- ✅ **run_phase2_crawler_pipeline.py** (통합 파이프라인)

---

## 🎯 Phase 2 아키텍처

```
┌─────────────────────────────────────────────────────────────┐
│ 1단계: 마스터 데이터 수집 (공개 API)                         │
├─────────────────────────────────────────────────────────────┤
│ CareerAPIClient.get_universities()                          │
│ → DB에 저장: universities, colleges, departments            │
└──────────────┬──────────────────────────────────────────────┘
               │
┌──────────────▼──────────────────────────────────────────────┐
│ 2단계: crawl4ai를 통한 정보 수집 (범용 크롤러)              │
├─────────────────────────────────────────────────────────────┤
│ GenericUniversityCrawler.crawl_page(url)                   │
│ → AsyncWebCrawler를 사용하여 HTML 다운로드                 │
│ → 정규식 기반 패턴 매칭으로 정보 추출                      │
│ → DB에 저장: professors, laboratories, papers              │
└──────────────┬──────────────────────────────────────────────┘
               │
┌──────────────▼──────────────────────────────────────────────┐
│ 3단계: Ollama 분석 (배치 처리)                             │
├─────────────────────────────────────────────────────────────┤
│ run_real_analysis_pipeline.py                              │
│ → 수집된 모든 논문에 LLM 분석 적용 (이미 구현 완료)       │
└─────────────────────────────────────────────────────────────┘
```

---

## 📦 구현된 컴포넌트

### 1. CareerAPIClient (`src/services/career_api_client.py`)

**목적:** 공개 API를 통해 대학/학과 정보 자동 수집

**구현 내용:**
```python
class CareerAPIClient:
    def get_universities(self) -> Dict:
        # 반환: {total, page, universities: [...]}
        # Mock 데이터: 3개 대학 (서울대, KAIST, 고려대)

    def get_departments(university_id: str) -> Dict:
        # 반환: {colleges: [{college_name, departments: [...]}]}

    def get_majors(department_id: str) -> Dict:
        # 반환: {majors: [{name, description}]}
```

**현재 상태:** ✅ 완료 (Mock 데이터 기반, 실제 API와 연동 가능)

---

### 2. GenericUniversityCrawler (`src/services/generic_university_crawler.py`)

**목적:** 모든 대학 홈페이지에서 작동하는 범용 크롤러

**주요 메서드:**
```python
class GenericUniversityCrawler:
    async def crawl_page(url: str) -> Optional[str]
        # crawl4ai의 AsyncWebCrawler 사용
        # 반환: HTML 콘텐츠 또는 None

    async def extract_professors(page_url: str) -> List[Dict]
        # 패턴 매칭으로 교수 정보 추출
        # 찾는 정보: name, email, office, research_areas

    async def extract_labs(page_url: str) -> List[Dict]
        # 패턴 매칭으로 연구실 정보 추출
        # 찾는 정보: name, professor, research_focus

    async def extract_papers(page_url: str) -> List[Dict]
        # 패턴 매칭으로 논문 정보 추출
        # 찾는 정보: title, authors, year, venue
```

**현재 상태:** 🔄 진행 중
- ✅ crawl4ai 통합 완료
- ✅ 기본 패턴 매칭 구현
- 🔄 정보 추출 정확도 개선 필요

---

### 3. 통합 파이프라인 (`run_phase2_crawler_pipeline.py`)

**3단계 파이프라인:**

```
1단계: API 데이터 수집
   └─ CareerAPIClient.get_universities()
   └─ 3개 대학 데이터 조회 완료 ✅

2단계: crawl4ai 기반 정보 추출
   └─ KAIST 컴퓨터과학과 페이지 크롤링 ✅
   └─ 패턴 매칭으로 교수/연구실 정보 추출 (개선 예정)

3단계: 데이터 검증
   └─ DB 통계: 5개 논문, 5개 분석 (Phase 1 데이터) ✅
```

**현재 상태:** ✅ 기본 골격 완성, 정보 추출 정확도 개선 필요

---

## 🔍 crawl4ai 기반 정보 추출 방식

### 패턴 매칭 전략

**1. 교수 정보 추출**
```python
# 이메일 패턴으로 교수 찾기
pattern = r'\b([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,})\b'

# 이메일 주변 텍스트에서 이름 추출
name_patterns = [
    r'(?:Prof\.|Professor)\s+([A-Za-z0-9\s&-]+)',
    r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s*(?:\(|<|email)',
]
```

**2. 연구실 정보 추출**
```python
# 키워드 기반 검색
keywords = ["laboratory", "lab", "research", "연구실", "실험실"]

# 키워드 주변 문맥 추출
pattern = rf'(?:[^.!?\n]{{0,100}})keyword[^.!?\n]{{0,200}}'
```

**3. 논문 정보 추출**
```python
# 연도 패턴
year_pattern = r'\b(19|20)\d{2}\b'

# 제목 패턴
title_pattern = r'(?:Title|title):\s*"?([^"\n]+?)(?:"|$)'

# 문장 기반 휴리스틱
# → 대문자로 시작하고 20-300자 사이의 문장을 제목으로 간주
```

---

## ✅ 완료된 작업

1. ✅ **crawl4ai 통합**
   - AsyncWebCrawler 초기화 및 페이지 크롤링
   - 타임아웃 및 예외 처리

2. ✅ **API 클라이언트**
   - CareerAPIClient 구현 (Mock 데이터)
   - 대학/학과 정보 조회

3. ✅ **통합 파이프라인**
   - 1단계: API 데이터 수집
   - 2단계: crawl4ai 크롤링
   - 3단계: 데이터 검증

4. ✅ **기본 패턴 매칭**
   - 이메일 주소 추출
   - 키워드 기반 정보 추출
   - 문장 기반 제목 추출

---

## 🔄 진행 중인 작업

### 1. 정보 추출 정확도 개선

**현재 문제:**
- KAIST 컴퓨터과학과 페이지 크롤링은 성공했으나 (2959 bytes)
- 정규식 패턴으로 교수/연구실 정보 추출 못함 (0개)

**개선 계획:**
- [ ] 실제 대학 페이지의 HTML 구조 분석
- [ ] CSS 선택자 기반 보조 추출 로직 추가
- [ ] LLM 기반 콘텐츠 이해 (crawl4ai의 고급 기능)
- [ ] 다양한 대학 페이지에 맞는 휴리스틱 추가

### 2. 실제 대학 페이지 대응

**필요한 작업:**
- [ ] KAIST, 서울대, 고려대 등 실제 페이지 구조 분석
- [ ] 각 대학별 일반적인 정보 배치 패턴 파악
- [ ] JavaScript 렌더링 필요 페이지 대응

### 3. 대규모 데이터 수집 (Phase 2 목표)

**목표:**
- [ ] 50+ 대학 데이터 수집
- [ ] 5000+ 교수 정보
- [ ] 1000+ 연구실
- [ ] 10000+ 논문

---

## 📊 현재 데이터베이스 상태

```
DB Statistics (as of 2025-11-25):
- Universities: 3개 (Mock: SNU, KAIST, Korea Univ.)
- Colleges: 3개 (API로부터)
- Departments: 3개 (API로부터)
- Professors: 0개 (크롤링 진행 중)
- Laboratories: 0개 (크롤링 진행 중)
- ResearchPapers: 5개 (Phase 1 데이터)
- PaperAnalysis: 5개 (Phase 1 분석, 100% 완료) ✅
```

---

## 🚀 다음 단계

### 즉시 (1-2일)
1. **정보 추출 로직 개선**
   - 실제 대학 페이지 HTML 분석
   - 패턴 매칭 알고리즘 개선
   - CSS 선택자 추가

2. **테스트 및 검증**
   - KAIST 페이지에서 실제 교수 정보 추출
   - 다른 대학 페이지도 테스트

### 단기 (1주일)
1. **크롤러 확장**
   - 3개 대학 → 50+ 대학으로 확대
   - 각 대학의 학과별 크롤링

2. **논문 정보 수집**
   - 교수 홈페이지에서 논문 링크 추출
   - 논문 메타데이터 수집

### 중기 (2-3주)
1. **배치 분석**
   - 10000+ 논문에 Ollama 분석 적용
   - 병렬 처리로 성능 최적화

2. **데이터 품질 검증**
   - 추출된 정보의 정확도 평가
   - 누락된 정보 보완

---

## 💡 기술적 고려사항

### 1. crawl4ai vs 하드코딩된 크롤러
- **crawl4ai 장점:**
  - 모든 대학에 동일하게 적용 가능
  - 페이지 구조 변경 시 유연함
  - JavaScript 렌더링 지원

- **한계:**
  - 정규식 기반 패턴 매칭의 한계
  - 각 대학의 고유한 구조에 완벽하게 대응 어려움

### 2. 개선 방향
- **선택지 1:** 더 정교한 패턴 매칭 + CSS 선택자 조합
- **선택지 2:** crawl4ai의 LLM 기반 추출 기능 활용
- **선택지 3:** 대학별로 간단한 설정 파일 (선택자 주소) 작성

---

## 📝 요약

**사용자 피드백에 따른 전환:**
- ❌ 하드코딩된 대학별 크롤러는 50+ 대학 확장에 부적합
- ✅ crawl4ai 기반 범용 크롤러로 모든 대학 지원 가능
- 🔄 정보 추출 정확도 개선가 필요함

**현재 진행 상황:**
- ✅ 기본 구조 완성
- ✅ API 통합 완료
- ✅ crawl4ai 크롤링 작동 확인
- 🔄 정보 추출 로직 개선 필요

**다음 우선순위:**
1. 실제 대학 페이지에서 교수/연구실 정보 추출
2. 크롤러를 50+ 대학으로 확장
3. 대규모 데이터 수집 및 Ollama 분석

---

**마지막 업데이트:** 2025-11-25
**담당자:** Claude Code (Anthropic)

🤖 Generated with Claude Code
