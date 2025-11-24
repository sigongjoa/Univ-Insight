# E2E & 통합 테스트 실행 가이드

**상태:** ✅ 완성
**테스트 유형:** E2E (Playwright) + API 통합 테스트 (pytest)
**총 테스트 케이스:** 40+ 개

---

## 📋 테스트 환경 준비

### 1. 프로젝트 디렉토리 확인
```bash
cd /mnt/d/progress/Univ-Insight
```

### 2. 백엔드 시작 (Terminal 1)
```bash
# Virtual environment 활성화
source venv/bin/activate

# 백엔드 서버 시작
python -m uvicorn src.api.main:app --reload --port 8000
```

**확인:**
- ✅ http://localhost:8000 접속 가능
- ✅ http://localhost:8000/docs에서 Swagger UI 확인

### 3. 프론트엔드 시작 (Terminal 2)
```bash
cd frontend
npm install  # 이미 설치되었으면 스킵
npm run dev
```

**확인:**
- ✅ http://localhost:5173 접속 가능
- ✅ 로그인 페이지 표시

### 4. 테스트 환경 확인
```bash
# 두 서버가 모두 실행 중인지 확인
curl http://localhost:8000/health || echo "Backend not running"
curl http://localhost:5173 || echo "Frontend not running"
```

---

## 🧪 E2E 테스트 실행 (Playwright)

### 전체 E2E 테스트 실행
```bash
cd frontend
npm run test:e2e
```

**예상 출력:**
```
✓ auth.spec.ts (2 tests)
✓ research.spec.ts (5 tests)
✓ planb.spec.ts (5 tests)
✓ report.spec.ts (7 tests)
✓ profile.spec.ts (8 tests)
✓ navigation.spec.ts (8 tests)
✓ responsive.spec.ts (6 tests)

Total: 41 tests passed
```

### 특정 테스트 파일만 실행
```bash
# 인증 테스트만
npm run test:e2e -- auth.spec.ts

# 프로필 테스트만
npm run test:e2e -- profile.spec.ts

# 라우팅 테스트만
npm run test:e2e -- navigation.spec.ts
```

### UI 모드로 테스트 실행 (시각적 확인)
```bash
npm run test:e2e:ui
```

**특징:**
- 브라우저에서 실시간으로 테스트 실행 확인
- 각 스텝별로 일시 정지 가능
- 실패한 스텝을 다시 실행 가능

### 디버그 모드로 테스트 실행
```bash
npm run test:e2e:debug
```

**특징:**
- 개발자 도구 활성화
- 느린 속도로 실행
- 각 스텝에서 검사 가능

### 특정 테스트 케이스만 실행
```bash
# 로그인 관련 테스트만
npm run test:e2e -- --grep "로그인"

# 논문 검색 관련 테스트
npm run test:e2e -- --grep "논문"
```

---

## 📊 API 통합 테스트 실행 (pytest)

### 전체 API 테스트 실행
```bash
cd /mnt/d/progress/Univ-Insight

# Virtual environment 활성화
source venv/bin/activate

# 테스트 실행
pytest tests/e2e_api_test.py -v -s
```

**예상 출력:**
```
test_api_create_user PASSED                        [ 10%]
test_api_list_papers PASSED                        [ 20%]
test_api_list_papers_with_filter PASSED            [ 30%]
test_api_get_paper_analysis PASSED                 [ 40%]
test_api_get_planb_suggestions PASSED              [ 50%]
test_api_generate_report PASSED                    [ 60%]
test_api_health_check PASSED                       [ 70%]
test_api_invalid_paper_id PASSED                   [ 80%]
test_api_missing_required_fields PASSED            [ 90%]
test_list_papers_response_time PASSED              [100%]

======================== 10 passed in 2.34s ========================
```

### 특정 테스트 클래스 실행
```bash
# 통합 테스트만
pytest tests/e2e_api_test.py::TestAPIIntegration -v -s

# 성능 테스트만
pytest tests/e2e_api_test.py::TestAPIPerformance -v -s
```

### 특정 테스트 함수만 실행
```bash
# 사용자 생성 테스트
pytest tests/e2e_api_test.py::TestAPIIntegration::test_api_create_user -v -s

# 논문 조회 테스트
pytest tests/e2e_api_test.py::TestAPIIntegration::test_api_list_papers -v -s
```

### 테스트 결과를 파일로 저장
```bash
# HTML 리포트 생성
pytest tests/e2e_api_test.py -v -s --html=report.html

# JUnit XML 리포트 생성
pytest tests/e2e_api_test.py -v -s --junit-xml=results.xml
```

---

## 🔄 유즈케이스별 테스트

### UC-1: 사용자 회원가입 및 로그인
```bash
# Playwright
npm run test:e2e -- auth.spec.ts

# 또는
npm run test:e2e -- --grep "회원가입"
npm run test:e2e -- --grep "로그인"
```

### UC-2: 논문 검색 및 상세 정보 조회
```bash
npm run test:e2e -- research.spec.ts

# 또는
npm run test:e2e -- --grep "논문"
npm run test:e2e -- --grep "상세 정보"
```

### UC-3: Plan B 대학 대안 조회
```bash
npm run test:e2e -- planb.spec.ts

# 또는
npm run test:e2e -- --grep "Plan B"
npm run test:e2e -- --grep "유사도"
```

### UC-4: 개인 맞춤 리포트 생성
```bash
npm run test:e2e -- report.spec.ts

# API 테스트
pytest tests/e2e_api_test.py::TestAPIIntegration::test_api_generate_report -v -s
```

### UC-5: 사용자 프로필 관리
```bash
npm run test:e2e -- profile.spec.ts

# 또는
npm run test:e2e -- --grep "프로필"
npm run test:e2e -- --grep "로그아웃"
```

### UC-6 & UC-7: 네비게이션 및 접근 제어
```bash
npm run test:e2e -- navigation.spec.ts

# 또는
npm run test:e2e -- --grep "네비게이션"
npm run test:e2e -- --grep "접근"
```

### UC-10: 반응형 디자인
```bash
npm run test:e2e -- responsive.spec.ts

# 또는
npm run test:e2e -- --grep "모바일"
npm run test:e2e -- --grep "태블릿"
```

---

## 📱 특정 브라우저/기기에서 테스트

### 특정 브라우저만 테스트
```bash
# Chrome만
npm run test:e2e -- --project=chromium

# Firefox만
npm run test:e2e -- --project=firefox

# Safari만
npm run test:e2e -- --project=webkit
```

### 모바일 디바이스 테스트
```bash
# iPhone 12로 테스트
npm run test:e2e -- --project="Mobile Chrome"
```

---

## 🐛 테스트 실패 시 디버깅

### 스크린샷 확인
```bash
# 실패한 테스트의 스크린샷
ls test-results/
```

### 비디오 재생
```bash
# 테스트 실행 비디오 보기
ls test-results/
```

### 추적 정보 확인
```bash
# Playwright Trace Viewer 열기
npx playwright show-trace test-results/trace.zip
```

### 느린 실행으로 디버깅
```bash
npm run test:e2e -- --headed --slow-mo=1000
```

---

## 🚀 전체 테스트 스위트 실행 (매뉴얼)

### 순서대로 실행하기
```bash
# 1. E2E 테스트
echo "=== E2E 테스트 시작 ==="
cd frontend
npm run test:e2e

# 2. API 통합 테스트
echo "=== API 통합 테스트 시작 ==="
cd ../
source venv/bin/activate
pytest tests/e2e_api_test.py -v -s

# 3. 백엔드 단위 테스트 (기존)
echo "=== 백엔드 단위 테스트 시작 ==="
pytest tests/unit/ -v -s

echo "=== 모든 테스트 완료 ==="
```

### 빠른 스모크 테스트
```bash
# 핵심 기능만 빠르게 테스트
npm run test:e2e -- auth.spec.ts
npm run test:e2e -- research.spec.ts
npm run test:e2e -- profile.spec.ts
```

---

## 📈 테스트 결과 분석

### E2E 테스트 결과
- **성공:** 모든 시나리오가 예상대로 작동
- **경고:** 타이밍 이슈나 데이터 부재
- **실패:** 기능 버그 또는 설정 오류

### API 테스트 결과
- **성공:** API 엔드포인트가 예상 응답 반환
- **경고:** 레이턴시가 높거나 데이터 없음
- **실패:** API 오류 또는 네트워크 문제

---

## ✅ 테스트 체크리스트

### 기본 동작 확인
- [ ] 프론트엔드 서버 실행 (http://localhost:5173)
- [ ] 백엔드 서버 실행 (http://localhost:8000)
- [ ] E2E 테스트 실행 완료
- [ ] API 테스트 실행 완료
- [ ] 모든 테스트 통과 또는 알려진 이슈만 존재

### 성공 기준
- [ ] E2E 테스트 통과율 95% 이상
- [ ] API 테스트 통과율 100%
- [ ] 응답 시간 < 5초
- [ ] 모바일 호환성 확인
- [ ] 에러 처리 검증

---

## 🔧 커스텀 테스트 작성

### 새 E2E 테스트 추가하기
```typescript
// tests/e2e/custom.spec.ts
import { test, expect } from '@playwright/test'

test.describe('새로운 기능 테스트', () => {
  test('기능이 작동하는지 확인', async ({ page }) => {
    await page.goto('/페이지')

    // 테스트 코드
    await expect(page.locator('text=요소')).toBeVisible()
  })
})
```

### 새 API 테스트 추가하기
```python
# tests/e2e_api_test.py에 추가

def test_new_api_endpoint(self):
    """새 API 엔드포인트 테스트"""
    url = f"{BASE_URL}/new-endpoint"
    response = requests.get(url)

    assert response.status_code == 200
    print(f"✅ 새 엔드포인트 테스트 성공")
```

---

## 📝 테스트 리포트 생성

### HTML 리포트
```bash
npm run test:e2e -- --reporter=html

# 리포트 열기
npx playwright show-report
```

### CLI 리포트
```bash
npm run test:e2e -- --reporter=list
npm run test:e2e -- --reporter=dot
npm run test:e2e -- --reporter=json
```

---

## 🆘 문제 해결

### 포트 충돌
```bash
# 포트 확인
lsof -i :5173
lsof -i :8000

# 프로세스 종료
kill -9 <PID>
```

### 테스트 타임아웃
```bash
# 타임아웃 시간 증가
npm run test:e2e -- --timeout=60000
```

### 네트워크 오류
```bash
# 서버 상태 확인
curl -v http://localhost:8000/health
curl -v http://localhost:5173
```

### 데이터 부재
- Mock 데이터 사용 확인
- 백엔드 데이터베이스 초기화 필요 시:
```bash
source venv/bin/activate
python -c "from src.core.init_db import init_db; init_db()"
```

---

## 📞 추가 정보

- **E2E 테스트 시나리오:** [E2E_TEST_SCENARIOS.md](./E2E_TEST_SCENARIOS.md)
- **프론트엔드 빠른 시작:** [FRONTEND_QUICK_START.md](./frontend/FRONTEND_QUICK_START.md)
- **백엔드 문서:** [IMPLEMENTATION_COMPLETE.md](./IMPLEMENTATION_COMPLETE.md)
- **전체 설정:** [GETTING_STARTED.md](./GETTING_STARTED.md)

---

## 🎯 다음 단계

1. ✅ 모든 테스트 실행 완료
2. ✅ 테스트 결과 분석
3. 🔄 발견된 이슈 해결
4. 🚀 배포 준비

---

**행운을 빕니다! 테스트 실행하세요! 🚀**
