# 🚀 Phase {PHASE_NUMBER}: {PHASE_NAME}

**상태:** {STATUS}
**시작일:** {START_DATE}
**완료일:** {END_DATE}
**담당:** {OWNER}

---

## 📋 개요

{PHASE_OVERVIEW}

### 핵심 목표
- {OBJECTIVE_1}
- {OBJECTIVE_2}
- {OBJECTIVE_3}

### 주요 산출물
- {OUTPUT_1}
- {OUTPUT_2}
- {OUTPUT_3}

---

## 🏗️ 아키텍처

```
{ARCHITECTURE_DIAGRAM}
```

---

## ✅ 구현 체크리스트

### 핵심 컴포넌트
- [ ] {COMPONENT_1}
- [ ] {COMPONENT_2}
- [ ] {COMPONENT_3}

### 테스트
- [ ] 단위 테스트
- [ ] 통합 테스트
- [ ] E2E 테스트

### 문서
- [ ] API 문서
- [ ] 구현 가이드
- [ ] 배포 가이드

---

## 📊 현재 상태

### 데이터베이스
```
{DATABASE_STATUS}
```

### API 엔드포인트
```
{API_STATUS}
```

### 시스템 통계
```
{STATISTICS}
```

---

## 🔧 주요 기술 스택

| 계층 | 기술 | 역할 |
|------|------|------|
| {LAYER_1} | {TECH_1} | {ROLE_1} |
| {LAYER_2} | {TECH_2} | {ROLE_2} |
| {LAYER_3} | {TECH_3} | {ROLE_3} |

---

## 📝 구현 세부사항

### {COMPONENT_NAME}

**파일:** `src/{FILE_PATH}`

**주요 기능:**
- {FEATURE_1}
- {FEATURE_2}

**사용 예시:**
```python
{USAGE_EXAMPLE}
```

---

## 🧪 테스트 결과

### 단위 테스트 (Unit Tests)
```
✅ 총 테스트: {TOTAL_UNIT_TESTS}개
✅ 성공: {PASSED_UNIT_TESTS}개
❌ 실패: {FAILED_UNIT_TESTS}개
```

**테스트 파일:** `test_{COMPONENT_NAME}.py`

### 통합 테스트 (Integration Tests)
```
✅ 총 테스트: {TOTAL_INTEGRATION_TESTS}개
✅ 성공: {PASSED_INTEGRATION_TESTS}개
❌ 실패: {FAILED_INTEGRATION_TESTS}개
```

### E2E 시나리오 테스트 (End-to-End)
```
✅ 총 시나리오: {TOTAL_SCENARIOS}개
✅ 성공: {PASSED_SCENARIOS}개
❌ 실패: {FAILED_SCENARIOS}개
```

**테스트 파일:** `test_backend_e2e_scenarios.py` or `test_frontend_e2e_scenarios.py`

#### 구현된 시나리오
- {SCENARIO_1}: {DESCRIPTION}
- {SCENARIO_2}: {DESCRIPTION}
- {SCENARIO_3}: {DESCRIPTION}

### 테스트 커버리지
```
전체 커버리지: {COVERAGE_PERCENT}%
  - 라인: {LINE_COVERAGE}%
  - 분기: {BRANCH_COVERAGE}%
  - 함수: {FUNCTION_COVERAGE}%
```

**커버리지 리포트:** `htmlcov/index.html` 또는 `pytest --cov`

### 주요 테스트 케이스
- {TEST_1}: ✅ PASS
- {TEST_2}: ✅ PASS
- {TEST_3}: ✅ PASS

---

## 📈 성능 분석

### API 응답 시간
```
엔드포인트              평균      최소      최대      샘플수
────────────────────────────────────────────────────────
GET /api/v1/universities    {AVG_UNI}ms   {MIN_UNI}ms   {MAX_UNI}ms   {COUNT_UNI}
GET /api/v1/research        {AVG_RES}ms   {MIN_RES}ms   {MAX_RES}ms   {COUNT_RES}
GET /api/v1/search          {AVG_SEA}ms   {MIN_SEA}ms   {MAX_SEA}ms   {COUNT_SEA}
```

**측정 방법:**
- pytest-benchmark 사용
- 최소 10회 이상 반복 실행
- 평균값 기반 성능 평가

**성능 표준:**
- API 응답: <500ms
- 데이터베이스 쿼리: <200ms
- 벡터 검색: <1000ms

### 리소스 사용량
```
메모리 (Memory)
  - 초기 메모리: {INITIAL_MEMORY} MB
  - 피크 메모리: {PEAK_MEMORY} MB
  - 평균 메모리: {AVG_MEMORY} MB

CPU 사용률
  - 평균: {AVG_CPU}%
  - 최대: {MAX_CPU}%

디스크 사용량
  - 데이터베이스: {DB_SIZE} MB
  - 로그 파일: {LOG_SIZE} MB
  - 벡터 저장소: {VECTOR_SIZE} MB
  - 총합: {TOTAL_SIZE} MB
```

**측정 도구:**
- psutil (메모리, CPU)
- du (디스크)
- tracemalloc (메모리 프로파일링)

### 데이터베이스 성능
```
쿼리 타입              실행 시간   인덱스 활용
────────────────────────────────────────────
SELECT (단순)         {SIMPLE_SELECT}ms  ✅
SELECT (JOIN)         {JOIN_SELECT}ms    ✅
INSERT (단건)         {INSERT_ONE}ms     ✅
INSERT (배치)         {INSERT_BATCH}ms   ✅
```

### 동시성 테스트
```
동시 요청수    응답 시간   에러율    상태
────────────────────────────────────────
10개          {RT_10}ms   {ER_10}%   {ST_10}
50개          {RT_50}ms   {ER_50}%   {ST_50}
100개         {RT_100}ms  {ER_100}%  {ST_100}
```

**테스트 도구:**
- locust 또는 Apache JMeter
- 최소 5분 이상 부하 테스트

### 성능 비교 (이전 버전 대비)
```
지표                    이전    현재    개선율
────────────────────────────────────────────
평균 응답 시간          {OLD_RT}   {NEW_RT}   {IMPROVE_RT}%
메모리 사용             {OLD_MEM}  {NEW_MEM}  {IMPROVE_MEM}%
데이터베이스 쿼리       {OLD_DB}   {NEW_DB}   {IMPROVE_DB}%
벡터 검색 시간          {OLD_VS}   {NEW_VS}   {IMPROVE_VS}%
```

---

## 📸 스크린샷 및 검증

### API 엔드포인트 스크린샷
```
endpoints/
├── 1_universities_list.png          (GET /universities)
├── 2_university_detail.png          (GET /universities/{id})
├── 3_college_detail.png             (GET /colleges/{id})
├── 4_department_detail.png          (GET /departments/{id})
├── 5_professor_detail.png           (GET /professors/{id})
├── 6_lab_detail.png                 (GET /laboratories/{id})
├── 7_research_list.png              (GET /research)
└── 8_research_analysis.png          (GET /research/{id}/analysis)
```

### 스크린샷 검증 (MD5 Hash)
```
파일명                          MD5 Hash                         날짜         상태
────────────────────────────────────────────────────────────────────────────────
1_universities_list.png         {MD5_1}                         {DATE_1}     ✅
2_university_detail.png         {MD5_2}                         {DATE_2}     ✅
3_college_detail.png            {MD5_3}                         {DATE_3}     ✅
4_department_detail.png         {MD5_4}                         {DATE_4}     ✅
5_professor_detail.png          {MD5_5}                         {DATE_5}     ✅
6_lab_detail.png                {MD5_6}                         {DATE_6}     ✅
7_research_list.png             {MD5_7}                         {DATE_7}     ✅
8_research_analysis.png         {MD5_8}                         {DATE_8}     ✅
```

**검증 방법:**
```bash
# 스크린샷 캡처
python capture_screenshots.py

# MD5 해시 계산
md5sum endpoints/*.png > endpoints/md5_hashes.txt

# 스크린샷 비교 (변경 감지)
python verify_screenshots.py
```

### 프론트엔드 UI 스크린샷
```
frontend/
├── 1_login_page.png
├── 2_dashboard_page.png
├── 3_university_list.png
├── 4_research_page.png
├── 5_paper_detail.png
└── 6_plan_b_page.png
```

**스크린샷 검증 결과:**
```
✅ 총 스크린샷: {TOTAL_SCREENSHOTS}개
✅ 고유한 스크린샷: {UNIQUE_SCREENSHOTS}개
⚠️ 중복/변경: {CHANGED_SCREENSHOTS}개
```

---

## 🚀 다음 Phase 준비

### Phase {NEXT_PHASE} 미리보기
```
{NEXT_PHASE_PREVIEW}
```

### 선행 조건
- [ ] {PRECONDITION_1}
- [ ] {PRECONDITION_2}

### 신규 기술/도구
- {NEW_TECH_1}
- {NEW_TECH_2}

---

## 📚 참고 자료

### 관련 문서
- [CLAUDE.md](../../CLAUDE.md) - 프로젝트 개요
- [ARCHITECTURE.md](../ARCHITECTURE.md) - 전체 아키텍처

### 외부 리소스
- {EXTERNAL_RESOURCE_1}
- {EXTERNAL_RESOURCE_2}

---

## 🔗 의존성

### 내부 의존성
```
{INTERNAL_DEPENDENCIES}
```

### 외부 라이브러리
```
{EXTERNAL_DEPENDENCIES}
```

---

## 📞 연락처

**리드:** {PHASE_LEAD}
**검수:** {REVIEWER}
**배포:** {DEPLOYMENT_OWNER}

---

**마지막 업데이트:** {LAST_UPDATE}
**다음 검토 예정:** {NEXT_REVIEW}
