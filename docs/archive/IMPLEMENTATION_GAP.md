# 구현 진행 현황 & 시급한 작업

**작성일:** 2024-11-24
**현황:** MVP 데이터 파이프라인 검증 완료 → 본격 개발 단계 진입

---

## 📊 현재 구현 상태

### ✅ 완료된 것
- **Pydantic Schemas** (`src/domain/schemas.py`) - 데이터 모델 정의
  - `ResearchPaper`, `CareerPath`, `ActionItem`, `AnalysisResult`
- **Mock Services** - 프로토타입 검증
  - `MockCrawler`: 테스트용 더미 크롤러
  - `MockLLM`: 테스트용 더미 LLM 응답
- **Core Pipeline** (`main_mock.py`) - End-to-End 흐름 검증
  - Crawler → LLM → Report 전체 파이프라인 동작 확인

### ⚠️ 부분 구현
- **Crawler Service** (`src/services/crawler.py`)
  - `KaistCrawler`: 기본 뼈대만 있음 (실제 파싱 로직 X)
  - `MockCrawler`: 완성
- **LLM Service** (`src/services/llm.py`)
  - `OllamaLLM`: 기본 구조만 있음 (Ollama 연동은 되지만 프롬프트 최적화 X)
  - `MockLLM`: 완성

### ❌ 구현되지 않은 것
**우선순위 상 시급한 것들:**

1. **Database Layer** (`src/core/database.py`, `src/domain/models.py`)
   - SQLAlchemy ORM 모델 미구현
   - 4개 테이블: `research_papers`, `analysis_results`, `users`, `reports`
   - DB 초기화 및 마이그레이션 설정 필요

2. **FastAPI 백엔드** (`src/api/main.py`, `src/api/routes.py`)
   - 8개 엔드포인트 미구현
   - User management, Research listing, Report generation 등
   - 인증(Kakao Login) 미구현

3. **벡터 저장소 & RAG** (`src/services/vector_store.py`)
   - ChromaDB 연동 미구현
   - 임베딩 생성 및 저장 로직 필요

4. **추천 알고리즘** (`src/services/recommendation.py`)
   - 코사인 유사도 기반 유사 논문 검색 미구현
   - "Plan B" 대학 매칭 로직 필요

5. **알림 서비스** (`src/services/notification.py`)
   - Notion API 연동 미구현
   - Kakao Talk 메시지 전송 미구현

6. **스케줄러** (`src/services/scheduler.py`)
   - APScheduler 연동 미구현
   - 주 1회 자동 크롤링 및 리포트 생성 예약 필요

7. **테스트 스위트** (`tests/unit/`, `tests/integration/`)
   - pytest 기반 단위/통합 테스트 미구현

---

## 🎯 시급한 작업 순서 (Recommended Priority)

### Phase 1: 데이터 저장소 구축 (1-2일)
**왜:** 파이프라인의 데이터를 저장할 곳이 없으면 실제 크롤링 데이터를 검증할 수 없음

- [ ] **Task 1.1:** SQLAlchemy 모델 구현
  - `src/domain/models.py` 작성
  - `ResearchPaper`, `AnalysisResult`, `User`, `Report` ORM 모델
  - 참고: `docs/design/database_schema.md`

- [ ] **Task 1.2:** 데이터베이스 초기화 & 설정
  - `src/core/database.py` 작성 (연결, 세션 관리)
  - SQLite 또는 PostgreSQL 선택 및 설정
  - `requirements.txt` 업데이트 (SQLAlchemy, 드라이버)

- [ ] **Task 1.3:** 기본 마이그레이션
  - Alembic 또는 수동 초기화 스크립트
  - `CREATE TABLE` 스크립트 정의

**완료 기준:** `python main_mock.py`를 실행 후 크롤링 결과가 DB에 저장되고 조회 가능

---

### Phase 2: 실제 크롤러 구현 (1-2일)
**왜:** Mock 데이터로는 실제 대학 사이트 구조를 테스트할 수 없음

- [ ] **Task 2.1:** KAIST CS 사이트 분석 및 파서 작성
  - 현재 `KaistCrawler._crawl_async()` 메서드 완성
  - HTML/Markdown 파싱 로직 추가
  - 참고: `docs/design/crawler_specs.md` (CSS selectors, error handling)

- [ ] **Task 2.2:** Fallback 메커니즘 구현
  - CSS 선택자 실패 시 LLM 기반 콘텐츠 추출
  - User-Agent 로테이션, 재시도 로직

- [ ] **Task 2.3:** 데이터 정제
  - 주기적으로 저장된 데이터 검증
  - 중복 제거 (URL 기반 unique 제약)

**완료 기준:** `KaistCrawler().crawl()`을 실행하면 실제 KAIST 뉴스에서 논문 데이터를 수집해 DB에 저장

---

### Phase 3: LLM 프롬프트 최적화 & 벡터 저장소 (2일)
**왜:** 크롤링된 데이터의 가치는 LLM 번역과 검색 기능에 달려있음

- [ ] **Task 3.1:** 프롬프트 엔지니어링
  - `src/services/llm.py`의 `OllamaLLM.analyze()` 프롬프트 개선
  - 4-섹션 구조 (Title, Research, Career Path, Action Item) 강화
  - 참고: `docs/project_plan.md` → "Secret Sauce" 섹션

- [ ] **Task 3.2:** 벡터 저장소 구현
  - `src/services/vector_store.py` 작성
  - ChromaDB 연동: 분석된 논문 임베딩 저장 및 검색
  - 논문의 `research_summary` 또는 `title`을 벡터화

- [ ] **Task 3.3:** 추천 알고리즘 구현
  - `src/services/recommendation.py` 작성
  - 코사인 유사도 기반 유사 논문 추천 (벡터 저장소 쿼리)
  - "Plan B" 로직: `similarity > 0.8 AND target_univ_tier > current_univ_tier`

**완료 기준:** 크롤링된 논문에 LLM 분석 적용 → 벡터 저장소 저장 → 유사 논문 검색 가능

---

### Phase 4: 백엔드 API 구축 (2-3일)
**왜:** 프론트엔드 또는 외부 시스템과 통신할 인터페이스 필요

- [ ] **Task 4.1:** FastAPI 기본 구조
  - `src/api/main.py` 작성 (FastAPI 앱 초기화)
  - CORS, 에러 핸들링, 로깅 설정

- [ ] **Task 4.2:** 사용자 관리 엔드포인트
  - `POST /api/v1/users/profile` (사용자 등록)
  - `GET /api/v1/users/{user_id}` (사용자 정보 조회)
  - 참고: `docs/api/api_specification.md`

- [ ] **Task 4.3:** 연구 데이터 조회 엔드포인트
  - `GET /api/v1/research` (논문 목록)
  - `GET /api/v1/research/{paper_id}/analysis` (상세 분석)
  - 필터링 (대학, 주제, 제한) 구현

- [ ] **Task 4.4:** 추천 & 리포트 엔드포인트
  - `POST /api/v1/reports/generate` (맞춤형 리포트 생성)
  - `GET /api/v1/research/{paper_id}/plan-b` (Plan B 제안)

**완료 기준:** `uvicorn src.api.main:app --reload` 실행 후 8개 API 엔드포인트 정상 응답

---

### Phase 5: 알림 서비스 (1-2일)
**왜:** 최종 사용자에게 리포트를 전달하는 채널

- [ ] **Task 5.1:** Notion API 연동
  - `src/services/notification.py` 작성
  - 생성된 리포트를 Notion 페이지로 변환 (제목, 단락, 콜아웃)

- [ ] **Task 5.2:** Kakao Talk 메시지
  - Kakao API 연동
  - 사용자에게 알림 메시지 전송 (리포트 링크 포함)

**완료 기준:** 리포트 생성 시 Notion 페이지 자동 생성 + Kakao Talk 알림 전송

---

### Phase 6: 자동화 & 테스트 (2-3일)
**왜:** 운영 중 수동 개입 최소화, 품질 보증

- [ ] **Task 6.1:** 스케줄러 구현
  - `src/services/scheduler.py` 작성 (APScheduler)
  - 주 1회 자동 크롤링 작업
  - 사용자별 주간 리포트 생성 및 발송

- [ ] **Task 6.2:** 단위 & 통합 테스트
  - `tests/unit/test_crawler.py` (크롤러 로직)
  - `tests/unit/test_llm.py` (LLM 응답 파싱)
  - `tests/integration/test_api.py` (전체 API 흐름)
  - pytest, mock 라이브러리 사용

- [ ] **Task 6.3:** CI/CD 설정
  - GitHub Actions 워크플로우 (`.github/workflows/test.yml`)
  - 자동 테스트 실행 및 커버리지 리포트

**완료 기준:** 테스트 커버리지 70% 이상, 모든 엔드포인트 자동 검증

---

## 📋 의존성 업데이트

현재 `requirements.txt`는 최소한의 라이브러리만 포함:
```
pydantic
crawl4ai
ollama
```

**추가 필요한 라이브러리:**
```
fastapi               # 백엔드 API
uvicorn              # ASGI 서버
sqlalchemy           # ORM
psycopg2             # PostgreSQL 드라이버 (또는 sqlite3는 내장)
chromadb             # 벡터 저장소
python-dotenv        # .env 파일 로딩
requests             # HTTP 요청 (Notion/Kakao API)
apscheduler          # 스케줄링
pytest               # 테스트
pytest-asyncio       # 비동기 테스트
```

---

## 🚀 1주일 속성 개발 계획

| 요일 | Phase | 예상 완료 | 우선순위 |
|------|-------|---------|--------|
| **월-화** | Phase 1 (DB) | Task 1.1-1.3 | 🔴 필수 |
| **수-목** | Phase 2 (Crawler) | Task 2.1-2.3 | 🔴 필수 |
| **금** | Phase 3 (LLM+Vector) | Task 3.1-3.3 | 🟠 높음 |
| **월-화 (Week 2)** | Phase 4 (API) | Task 4.1-4.4 | 🟠 높음 |
| **수-목 (Week 2)** | Phase 5-6 | Task 5+6 | 🟡 중간 |

---

## 💡 개발 팁

1. **Mock 서비스는 유지하세요**
   - 단위 테스트에서 실제 크롤링/LLM 호출 없이 검증 가능
   - `main_mock.py`는 빠른 통합 테스트용으로 유용

2. **점진적 통합**
   - Phase 1 완료 후: `main_mock.py` → DB 저장 테스트
   - Phase 2 완료 후: 실제 KAIST 데이터 수집 테스트
   - Phase 3 완료 후: 전체 파이프라인 E2E 테스트

3. **데이터베이스 선택**
   - 초기 개발: SQLite (파일 기반, 설정 최소)
   - 프로덕션: PostgreSQL (동시성, 안정성)

4. **API 설계**
   - `docs/api/api_specification.md`를 정확히 따르세요
   - 각 엔드포인트에 대해 요청/응답 예시가 명시됨

5. **테스트 작성**
   - 새 기능 추가 전에 테스트 케이스 정의 (TDD 원칙)
   - Mock/Fixture를 활용해 외부 의존성 제거

---

## 📚 참고 문서

- `docs/project_plan.md` - 전체 비전 & 4주 로드맵
- `docs/design/database_schema.md` - DB 테이블 설계
- `docs/api/api_specification.md` - API 엔드포인트 명세
- `docs/design/crawler_specs.md` - 크롤러 타겟 & 파싱 규칙
- `docs/test/test_strategy.md` - 테스트 레벨 & 시나리오
- `docs/design/prompt_specs.md` - LLM 프롬프트 설계 (아직 확인 필요)

---

**Next Action:** Phase 1 (Database Layer)부터 시작하세요!
