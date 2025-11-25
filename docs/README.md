# 📚 Univ-Insight 문서

**버전:** 1.0
**최종 업데이트:** 2024-11-25
**상태:** Phase 1 완료

---

## 🎯 문서 구조

```
docs/
├── README.md                          (이 파일)
├── ARCHITECTURE.md                    ⭐ 전체 아키텍처 개요
├── QUICK_START.md                     ⭐ 빠른 시작 가이드
│
├── phases/                            (Phase별 상세 문서)
│   ├── PHASE_TEMPLATE.md              (새로운 Phase 작성용 템플릿)
│   ├── PHASE_1_CORE_INFRASTRUCTURE.md ✅ Phase 1 상세 (완료)
│   ├── PHASE_2_API_EXTENSION.md       (예정)
│   └── PHASE_3_FRONTEND.md            (예정)
│
├── api/                               (API 문서)
│   ├── API_ENDPOINTS.md               (모든 엔드포인트)
│   ├── CURL_EXAMPLES.md               (curl 사용 예시)
│   └── PYTHON_EXAMPLES.md             (Python 코드 예시)
│
├── guides/                            (운영 가이드)
│   ├── SETUP_GUIDE.md                 (개발 환경 설정)
│   ├── RUNNING_GUIDE.md               (실행 방법)
│   ├── DEPLOYMENT_GUIDE.md            (배포 가이드)
│   └── TROUBLESHOOTING.md             (문제 해결)
│
└── templates/                         (재사용 가능한 템플릿)
    ├── COMPONENT_TEMPLATE.md          (새로운 컴포넌트)
    ├── API_ENDPOINT_TEMPLATE.md       (새로운 API)
    └── TEST_TEMPLATE.md               (새로운 테스트)
```

---

## 📖 문서별 안내

### 🌟 필독 문서 (꼭 읽어야 함)

#### 1. **ARCHITECTURE.md** ⭐
- **대상:** 모든 개발자
- **내용:** 전체 시스템 아키텍처, 데이터 흐름, 컴포넌트 설명
- **읽는 시간:** 15분
- **필독 이유:** 시스템 이해의 기초

#### 2. **PHASE_1_CORE_INFRASTRUCTURE.md** ✅
- **대상:** Phase 1 작업자, 리더
- **내용:** Phase 1 완료 상태, 구현된 기능, 테스트 결과
- **읽는 시간:** 20분
- **필독 이유:** 현재 시스템의 상태를 이해

#### 3. **QUICK_START.md** (예정)
- **대상:** 새로운 개발자
- **내용:** 5분 안에 시작하기
- **읽는 시간:** 5분

---

### 🔧 개발자 가이드

#### **guides/SETUP_GUIDE.md** (예정)
개발 환경 설정 방법
- Python 환경 구성
- 의존성 설치
- 데이터베이스 초기화
- 테스트 실행

#### **guides/RUNNING_GUIDE.md** (예정)
시스템 실행 방법
- 데이터 파이프라인 실행
- API 서버 시작
- 테스트 실행

#### **guides/TROUBLESHOOTING.md** (예정)
문제 해결
- 자주 묻는 질문 (FAQ)
- 에러 메시지 해석
- 디버깅 팁

---

### 📡 API 문서

#### **api/API_ENDPOINTS.md**
모든 API 엔드포인트 상세 명세
- 요청/응답 형식
- 파라미터 설명
- 에러 코드
- HTTP 상태 코드

#### **api/CURL_EXAMPLES.md**
curl을 이용한 API 테스트 예시
```bash
curl http://localhost:8000/api/v1/universities
```

#### **api/PYTHON_EXAMPLES.md**
Python requests를 이용한 API 호출 예시
```python
import requests
response = requests.get('http://localhost:8000/api/v1/universities')
```

---

### 📋 Phase 문서

#### **phases/PHASE_TEMPLATE.md**
새로운 Phase를 문서화할 때 사용하는 템플릿
- 개요, 목표, 산출물
- 아키텍처
- 체크리스트
- 테스트 결과
- 성능 지표

#### **phases/PHASE_1_CORE_INFRASTRUCTURE.md** ✅
Phase 1의 전체 기록
- 완료된 작업
- 구현 세부사항
- 테스트 결과
- 다음 단계

#### **phases/PHASE_2_API_EXTENSION.md** (예정)
Phase 2 계획 및 진행 상황
- API 확장
- 추천 엔진
- 사용자 인증

---

### 🛠️ 템플릿

#### **templates/COMPONENT_TEMPLATE.md**
새로운 서비스/컴포넌트 추가 시 사용
- 파일 위치
- 클래스/함수 정의
- 테스트 코드
- 통합 방법

#### **templates/API_ENDPOINT_TEMPLATE.md**
새로운 API 엔드포인트 추가 시 사용
- URL 패턴
- HTTP 메서드
- 요청/응답
- 에러 처리

#### **templates/TEST_TEMPLATE.md**
새로운 테스트 작성 시 사용
- 테스트 구조
- Fixture 정의
- 단언문
- 커버리지

---

## 🚀 빠른 참조 (Quick Reference)

### Phase 1 상태
```
✅ 데이터 모델:    100% 완료 (9개 테이블)
✅ 크롤러:        100% 완료 (SNUCrawler)
✅ LLM:          100% 완료 (Ollama)
✅ 벡터 저장소:    100% 완료 (ChromaDB)
✅ API:          100% 완료 (8 엔드포인트)
✅ 테스트:        100% 완료 (E2E)
───────────────────────────────
총 완료도: 100%
```

### 주요 파일 위치

| 항목 | 경로 |
|------|------|
| 데이터 모델 | `src/domain/models.py` |
| 크롤러 | `src/services/snu_crawler.py` |
| LLM | `src/services/llm.py` |
| 벡터 저장소 | `src/services/vector_store.py` |
| API | `src/api/routes.py` |
| 테스트 | `test_e2e_full_pipeline.py` |
| 데이터베이스 | `./univ_insight.db` |
| 벡터 DB | `./chroma_db/` |

### 실행 명령어

```bash
# 데이터 수집
python run_real_pipeline.py

# LLM 분석
python run_ollama_reanalysis.py

# 벡터 인덱싱
python run_chromadb_indexing.py

# E2E 테스트
python test_e2e_full_pipeline.py

# API 서버 시작
python -m uvicorn src.api.main:app --reload
```

---

## 📚 다른 주요 파일

### 프로젝트 루트
- **CLAUDE.md** - 프로젝트 개요 및 설계 결정
- **README.md** - 프로젝트 소개 (사용자용)
- **requirements.txt** - Python 의존성

### 파이프라인 스크립트
- **run_real_pipeline.py** - 실제 데이터 수집
- **run_ollama_reanalysis.py** - LLM 분석
- **run_chromadb_indexing.py** - 벡터 인덱싱
- **test_e2e_full_pipeline.py** - E2E 테스트

---

## 🎯 문서 작성 가이드

### 새로운 Phase 추가 시

1. `docs/phases/PHASE_TEMPLATE.md` 복사
2. 파일명을 `PHASE_{NUMBER}_{NAME}.md`로 변경
3. 템플릿의 모든 섹션 채우기
4. 이 README.md에 링크 추가
5. 완료 후 커밋

### 새로운 가이드 추가 시

1. `docs/guides/` 폴더에 파일 생성
2. 마크다운 형식으로 작성
3. 목차 추가
4. 이 README.md에 링크 추가

### 문서 업데이트 규칙

- 코드 변경 시 관련 문서도 업데이트
- 새로운 기능 추가 시 문서화
- 월 1회 전체 문서 검토
- 오래된 정보는 "더 이상 사용되지 않음" 표시

---

## 📅 문서 유지보수 일정

| 주기 | 항목 | 담당 |
|------|------|------|
| 매번 | 코드 변경 시 문서 동시 업데이트 | 개발자 |
| 주1회 | 체크리스트 진행 상황 업데이트 | PM |
| 월1회 | 전체 문서 검토 및 정리 | Tech Lead |
| Phase 완료 시 | Phase 문서 작성 및 검증 | PM + Tech Lead |

---

## 🔗 외부 링크

### 프로젝트 관련
- [GitHub 저장소](https://github.com/your-repo)
- [Notion 페이지](https://notion.so/your-page)
- [Slack 채널](https://slack.com/your-channel)

### 기술 문서
- [FastAPI 공식 문서](https://fastapi.tiangolo.com/)
- [SQLAlchemy 가이드](https://docs.sqlalchemy.org/)
- [ChromaDB 문서](https://docs.trychroma.com/)
- [Ollama 가이드](https://ollama.ai/)

---

## ❓ FAQ

### Q: 문서가 너무 많은데 어디서 시작해야 할까요?
**A:** 이 순서로 읽으세요:
1. ARCHITECTURE.md (15분)
2. PHASE_1_CORE_INFRASTRUCTURE.md (20분)
3. 필요한 특정 문서 참조

### Q: Phase 2를 추가하려면?
**A:**
1. `docs/phases/PHASE_TEMPLATE.md` 복사
2. `PHASE_2_NAME.md`로 저장
3. 각 섹션 작성
4. 이 README에 링크 추가

### Q: API 문서가 없어요.
**A:** Phase 2에서 추가될 예정입니다. 지금은 코드의 주석과 `READY_TO_RUN.md` 참조하세요.

---

## 📝 버전 이력

| 버전 | 날짜 | 변경 사항 |
|------|------|----------|
| 1.0 | 2024-11-25 | Phase 1 완료, 문서 정리 |
| - | 예정 | Phase 2 추가 |

---

## 👥 기여 가이드

문서 개선에 참여하고 싶으신가요?

1. 오류 발견 시 issue 제출
2. 개선 사항 제안
3. 새로운 가이드 작성 제안
4. Pull Request로 기여

---

**마지막 업데이트:** 2024-11-25
**다음 업데이트:** Phase 2 시작 시
**문의:** [your-email@example.com](mailto:your-email@example.com)
