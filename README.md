# 🎓 Univ-Insight

**AI 기반 대학 연구 큐레이션 및 진로 설계 에이전트**

- **상태:** Phase 1 완료 ✅
- **최종 업데이트:** 2024-11-25
- **시스템 준비도:** 100%

---

## 🎯 프로젝트 소개

Univ-Insight는 대학의 복잡한 연구 논문을 **고등학생 수준의 쉬운 한국어로 번역**하고, **직업/회사 추천**과 **학습 경로 제시**를 하는 AI 기반 시스템입니다.

### 핵심 기능
```
서울대학교 선택
  ↓
공과대학 → 컴퓨터공학부 → 교수 → 연구실
  ↓
논문 목록 조회
  ↓
🤖 Ollama LLM으로 자동 분석
  ↓
📊 결과 제시:
  • 쉬운 설명 (한국어)
  • 관련 직업
  • 추천 회사
  • 필요한 과목
```

---

## 🚀 빠른 시작 (5분)

### 1️⃣ 설치
```bash
# 의존성 설치
pip install -r requirements.txt

# (선택) Ollama LLM 설정
ollama pull llama2:latest
ollama serve  # 별도 터미널에서 실행
```

### 2️⃣ 실행
```bash
# 데이터 수집 및 분석 (자동)
python run_real_pipeline.py          # 데이터 수집
python run_ollama_reanalysis.py      # LLM 분석
python run_chromadb_indexing.py      # 벡터 인덱싱

# API 서버 시작
python -m uvicorn src.api.main:app --reload --port 8000

# 브라우저 열기
open http://localhost:8000/docs
```

### 3️⃣ 테스트
```bash
# E2E 테스트 실행
python test_e2e_full_pipeline.py
```

---

## 📊 현재 시스템 상태

### 데이터
```
✅ 1개 대학 (Seoul National University)
✅ 3개 단과대학 (공과, 자연과학, 의학)
✅ 6개 전공
✅ 4명 교수
✅ 4개 연구실
✅ 5개 논문 (자동 분석됨)
```

### 기술 스택
```
🗄️  Database: SQLite + SQLAlchemy ORM
🕷️  Crawler: SNUCrawler (서울대 데이터)
🤖  LLM: Ollama (llama2:latest)
📊  Vector DB: ChromaDB (벡터 검색)
🌐  API: FastAPI (8개 엔드포인트)
✅  Tests: E2E 검증 완료
```

### 완료도
```
✅ 데이터 계층:     100% (9개 테이블)
✅ 크롤러:         100% (SNUCrawler)
✅ LLM 분석:       100% (Ollama 통합)
✅ 벡터 저장소:    100% (ChromaDB)
✅ API:           100% (8개 엔드포인트)
✅ 테스트:        100% (E2E 통과)
───────────────────────────────
총 완료도: 100%
```

---

## 📚 주요 API 엔드포인트

```bash
# 대학 목록
GET http://localhost:8000/api/v1/universities

# 서울대 단과대학 조회
GET http://localhost:8000/api/v1/universities/seoul-national-univ

# 공과대학의 전공들
GET http://localhost:8000/api/v1/colleges/snu-college-eng

# 컴퓨터공학부의 교수들
GET http://localhost:8000/api/v1/departments/snu-dept-cs

# 교수의 연구실
GET http://localhost:8000/api/v1/professors/prof-kim-ai-001

# 모든 논문
GET http://localhost:8000/api/v1/research

# 논문 상세 분석
GET http://localhost:8000/api/v1/research/paper-snu-001/analysis
```

자세한 내용은 [API 문서](docs/api/API_ENDPOINTS.md) 참조

---

## 📖 문서

### 필독 문서
| 문서 | 내용 | 읽는 시간 |
|------|------|---------|
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | 전체 시스템 아키텍처 | 15분 |
| [docs/phases/PHASE_1_CORE_INFRASTRUCTURE.md](docs/phases/PHASE_1_CORE_INFRASTRUCTURE.md) | Phase 1 완료 보고서 | 20분 |
| [docs/README.md](docs/README.md) | 문서 가이드 | 5분 |

### 개발자 가이드
- [docs/guides/SETUP_GUIDE.md](docs/guides/SETUP_GUIDE.md) - 개발 환경 설정
- [docs/guides/RUNNING_GUIDE.md](docs/guides/RUNNING_GUIDE.md) - 실행 방법
- [docs/api/CURL_EXAMPLES.md](docs/api/CURL_EXAMPLES.md) - curl 사용 예시
- [docs/api/PYTHON_EXAMPLES.md](docs/api/PYTHON_EXAMPLES.md) - Python 코드 예시

### Phase 문서
- [PHASE_1 완료](docs/phases/PHASE_1_CORE_INFRASTRUCTURE.md) ✅ 2024-11-25
- PHASE_2 예정 (API 확장 및 추천 엔진)
- PHASE_3 예정 (프론트엔드)

---

## 🏗️ 프로젝트 구조

```
Univ-Insight/
├── src/
│   ├── api/                     (FastAPI 앱)
│   │   ├── main.py
│   │   └── routes.py
│   ├── domain/
│   │   ├── models.py            (ORM 모델)
│   │   └── schemas.py
│   ├── services/
│   │   ├── snu_crawler.py       (크롤러)
│   │   ├── llm.py               (LLM)
│   │   ├── vector_store.py      (벡터 저장소)
│   │   └── recommendation.py    (추천)
│   └── core/
│       ├── logging.py           (로깅)
│       ├── exceptions.py        (예외)
│       └── middleware.py        (미들웨어)
│
├── docs/                        (📚 문서)
│   ├── README.md                (문서 가이드)
│   ├── ARCHITECTURE.md          (아키텍처)
│   ├── phases/                  (Phase별 문서)
│   ├── api/                     (API 문서)
│   ├── guides/                  (실행 가이드)
│   └── templates/               (재사용 템플릿)
│
├── test_*.py                    (테스트 파일)
├── run_*.py                     (파이프라인 스크립트)
├── univ_insight.db              (데이터베이스)
├── chroma_db/                   (벡터 저장소)
├── requirements.txt             (의존성)
└── README.md                    (이 파일)
```

---

## 🧪 테스트

### E2E 테스트 실행
```bash
python test_e2e_full_pipeline.py
```

### 테스트 결과 (최신)
```
✅ 데이터베이스 계층:        PASS
✅ LLM 분석 계층 (Ollama):  PASS
✅ 벡터 저장소 (ChromaDB):   PASS
✅ API 엔드포인트:          PASS
───────────────────────────────
🎉 전체 테스트: ALL PASS
```

---

## 🔧 개발 가이드

### 새로운 Phase 시작 시

1. **템플릿 복사**
   ```bash
   cp docs/phases/PHASE_TEMPLATE.md docs/phases/PHASE_2_NAME.md
   ```

2. **템플릿 채우기**
   - 개요, 목표, 산출물 작성
   - 아키텍처 다이어그램 추가
   - 체크리스트 작성

3. **이 README 업데이트**
   - Phase 2 링크 추가
   - 기술 스택 업데이트
   - 완료도 업데이트

### 새로운 기능 추가 시

1. **컴포넌트 문서화**
   - `docs/templates/COMPONENT_TEMPLATE.md` 참조

2. **API 엔드포인트 추가**
   - `docs/templates/API_ENDPOINT_TEMPLATE.md` 참조

3. **테스트 작성**
   - `docs/templates/TEST_TEMPLATE.md` 참조

---

## ⚙️ 시스템 요구사항

### 필수
- Python 3.8+
- pip / conda
- SQLite (포함됨)

### 선택
- Ollama (LLM 분석 시)
- Git (버전 관리)

### 사양
- 메모리: 4GB+ 권장
- 디스크: 1GB 여유 필요
- 인터넷: 초기 설정 시 필요

---

## 🚀 다음 단계 (Phase 2)

### 예정된 작업
```
Phase 2: API 확장 및 추천 엔진
├── 벡터 검색 API 엔드포인트
├── 추천 엔진 고도화 (Plan B)
├── 사용자 인증 시스템
├── Notion 자동 페이지 생성
└── Kakao Talk 알림 발송
```

### 예상 일정
- **시작:** 2024-12-01
- **완료:** 2024-12-15

---

## 📝 변경 이력

| 버전 | 날짜 | 변경 사항 |
|------|------|----------|
| 1.0 | 2024-11-25 | Phase 1 완료, 문서 정리 |
| - | 예정 | Phase 2 추가 |

---

## ❓ FAQ

### Q: 처음 시작하는데 어디서 부터 할까요?
**A:** 이 순서로 진행하세요:
1. `README.md` 읽기 (지금 보고 있는 이것!)
2. [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) 읽기
3. [docs/phases/PHASE_1_CORE_INFRASTRUCTURE.md](docs/phases/PHASE_1_CORE_INFRASTRUCTURE.md) 읽기
4. "빠른 시작" 섹션 따라하기

### Q: 개발 환경 설정은?
**A:** [docs/guides/SETUP_GUIDE.md](docs/guides/SETUP_GUIDE.md) 참조

### Q: 시스템이 제대로 동작하지 않아요.
**A:** [docs/guides/TROUBLESHOOTING.md](docs/guides/TROUBLESHOOTING.md) 참조

### Q: API 사용 방법은?
**A:**
- curl: [docs/api/CURL_EXAMPLES.md](docs/api/CURL_EXAMPLES.md)
- Python: [docs/api/PYTHON_EXAMPLES.md](docs/api/PYTHON_EXAMPLES.md)

### Q: Phase 2는 언제 시작되나요?
**A:** 2024-12-01 예정입니다.

---

## 🤝 기여

이 프로젝트에 기여하고 싶으신가요?

1. Issue 제출
2. Fork 후 feature 브랜치 생성
3. 변경사항 커밋
4. Pull Request 생성

문서 개선도 적극 환영합니다!

---

## 📄 라이선스

MIT License - [LICENSE](LICENSE) 파일 참조

---

## 📞 연락처

- **이메일:** [your-email@example.com](mailto:your-email@example.com)
- **이슈:** [GitHub Issues](https://github.com/your-repo/issues)
- **토론:** [GitHub Discussions](https://github.com/your-repo/discussions)

---

## 🙏 감사의 말

이 프로젝트는 다음을 기반으로 합니다:
- [FastAPI](https://fastapi.tiangolo.com/)
- [SQLAlchemy](https://www.sqlalchemy.org/)
- [ChromaDB](https://www.trychroma.com/)
- [Ollama](https://ollama.ai/)

---

**마지막 업데이트:** 2024-11-25
**다음 Phase:** Phase 2 (2024-12-01 예상)
**문서 버전:** 1.0

