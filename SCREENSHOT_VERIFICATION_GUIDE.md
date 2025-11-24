# 스크린샷 MD5 해시 검증 가이드

**목적:** Playwright로 캡처한 스크린샷이 실제로 서로 다른 이미지인지 MD5 해시로 검증

---

## 🎬 개요

이 가이드는 다음을 수행합니다:

1. **스크린샷 캡처** - Playwright로 각 페이지의 스크린샷 생성
2. **MD5 해시 계산** - 각 이미지 파일의 MD5 해시 계산
3. **해시 비교** - 모든 스크린샷이 서로 다른지 검증
4. **리포트 생성** - 상세한 검증 리포트 출력
5. **JSON 저장** - 검증 정보를 JSON 파일로 저장

---

## 📋 스크린샷 검증 방법

### 방법 1: Playwright E2E 테스트를 통한 검증

#### 단계 1: 프론트엔드 개발 서버 시작
```bash
cd frontend
npm run dev
```

#### 단계 2: 스크린샷 검증 테스트 실행
```bash
npm run test:e2e -- screenshot-verification.spec.ts
```

**실행 내용:**
- 각 페이지에 접속
- 스크린샷 캡처
- MD5 해시 계산
- 검증 정보 저장
- 해시 비교

**출력 예시:**
```
✅ Home Page 스크린샷 저장됨
   파일: homepage.png
   크기: 1234567 bytes
   MD5: a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6

✅ Research Page 스크린샷 저장됨
   파일: research-page.png
   크기: 2345678 bytes
   MD5: b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7

...

✨ 모든 스크린샷이 성공적으로 검증되었습니다!
   총 4개의 스크린샷
```

### 방법 2: Python 스크립트를 통한 검증

#### 기존 스크린샷 검증
```bash
python tests/screenshot_verification.py --verify
```

#### Playwright 테스트 실행 후 검증
```bash
python tests/screenshot_verification.py --run
```

#### 둘 다 수행
```bash
python tests/screenshot_verification.py --both
```

**출력 예시:**
```
📋 스크린샷 검증 리포트
════════════════════════════════════════════════════════════════════
페이지명        | 파일명                    | 파일 크기    | MD5 해시
────────────────────────────────────────────────────────────────
Home Page       | homepage.png              |  1234567 B  | a1b2c3d4...
Research Page   | research-page.png         |  2345678 B  | b2c3d4e5...
Profile Page    | profile-page.png          |  3456789 B  | c3d4e5f6...
Report Page     | report-page.png           |  4567890 B  | d4e5f6g7...
════════════════════════════════════════════════════════════════════

📊 통계:
   총 파일 수: 4
   총 파일 크기: 11,604,924 bytes (11.07 MB)
```

---

## 🔍 MD5 해시 검증 로직

### 계산 과정

```
원본 이미지 파일 (PNG)
        ↓
MD5 알고리즘 적용
        ↓
32자리 16진수 해시
예: a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6
```

### 검증 기준

1. **해시 포맷 검증**
   ```
   정규식: ^[a-f0-9]{32}$
   - 32자리 16진수 숫자
   - 소문자만 포함
   ```

2. **고유성 검증**
   ```
   모든 스크린샷의 MD5 해시가 서로 다른지 확인

   예:
   ✅ homepage.png (a1b2c3d4...) vs research-page.png (b2c3d4e5...) : 다름
   ✅ homepage.png (a1b2c3d4...) vs profile-page.png (c3d4e5f6...) : 다름
   ```

3. **파일 무결성 검증**
   ```
   같은 파일을 다시 읽었을 때 동일한 해시가 나와야 함
   ```

---

## 📁 파일 구조

```
frontend/
├── tests/e2e/
│   └── screenshot-verification.spec.ts    # Playwright 검증 테스트
├── screenshots/                            # 스크린샷 디렉토리
│   ├── homepage.png
│   ├── research-page.png
│   ├── profile-page.png
│   ├── report-page.png
│   └── screenshot-verification.json        # 검증 정보

tests/
└── screenshot_verification.py              # Python 검증 스크립트
```

---

## 📄 검증 JSON 형식

### 파일 위치
`frontend/screenshots/screenshot-verification.json`

### 파일 내용 예시
```json
[
  {
    "pageName": "Home Page",
    "fileName": "homepage.png",
    "path": "/path/to/frontend/screenshots/homepage.png",
    "md5Hash": "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6",
    "fileSize": 1234567,
    "timestamp": "2025-11-24T15:30:45.123456"
  },
  {
    "pageName": "Research Page",
    "fileName": "research-page.png",
    "path": "/path/to/frontend/screenshots/research-page.png",
    "md5Hash": "b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7",
    "fileSize": 2345678,
    "timestamp": "2025-11-24T15:30:50.654321"
  }
]
```

---

## 🔐 MD5 해시의 의미

### MD5란?
- **MD5 (Message-Digest Algorithm 5)**
- 임의의 길이 데이터를 128비트 (32자 16진수) 해시로 변환
- 동일한 파일은 항상 동일한 해시 생성
- 파일이 조금만 달라도 완전히 다른 해시 생성

### 검증 원리

```
파일 A: 1,234,567 bytes
    ↓ (MD5 해시)
MD5(A) = a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6

파일 B: 2,345,678 bytes
    ↓ (MD5 해시)
MD5(B) = b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7

MD5(A) ≠ MD5(B) → ✅ 서로 다른 파일 확인됨
```

### 신뢰성

- **암호학적 충돌 저항성**
  - 같은 해시를 갖는 서로 다른 파일을 찾기는 실질적으로 불가능
  - 확률: 2^128 ≈ 3.4 × 10^38

- **결정성**
  - 같은 파일은 항상 같은 해시 생성
  - 파일 캡처 시간 상관없이 일관성 있음

---

## 🧪 테스트 케이스

### 테스트 1: 홈페이지 스크린샷
```typescript
test('홈페이지 스크린샷', async ({ page }) => {
  // /login → 로그인 → /home으로 이동
  const info = await captureAndVerifyScreenshot(page, 'Home Page', 'homepage.png')

  // 해시가 유효한 MD5 형식인지 확인
  expect(info.md5Hash).toMatch(/^[a-f0-9]{32}$/)
})
```

### 테스트 2: 논문 검색 페이지 스크린샷
```typescript
test('논문 검색 페이지 스크린샷', async ({ page }) => {
  await page.goto('/research')
  const info = await captureAndVerifyScreenshot(page, 'Research Page', 'research-page.png')
  expect(info.md5Hash).toMatch(/^[a-f0-9]{32}$/)
})
```

### 테스트 3: 스크린샷 해시 검증
```typescript
test('스크린샷 해시 검증', async ({ page }) => {
  // JSON 파일에서 모든 스크린샷 로드
  const screenshots: ScreenshotInfo[] = JSON.parse(fs.readFileSync(VERIFICATION_FILE))

  for (const screenshot of screenshots) {
    // 현재 파일의 MD5 다시 계산
    const currentHash = calculateMD5(screenshot.path)

    // 저장된 해시와 일치하는지 확인
    expect(currentHash).toBe(screenshot.md5Hash)
  }
})
```

### 테스트 4: 서로 다른 스크린샷 비교
```typescript
test('서로 다른 스크린샷 비교', async ({ page }) => {
  const screenshots = JSON.parse(fs.readFileSync(VERIFICATION_FILE))
  const hashes = screenshots.map(s => s.md5Hash)

  // 모든 해시가 고유한지 확인 (중복 없음)
  const uniqueHashes = new Set(hashes)
  expect(uniqueHashes.size).toBe(hashes.length)
})
```

---

## 🚀 실행 예제

### 예제 1: Playwright 테스트 실행
```bash
cd frontend
npm run test:e2e -- screenshot-verification.spec.ts

# 출력:
# ✅ Home Page 스크린샷 저장됨
# ✅ Research Page 스크린샷 저장됨
# ✅ Profile Page 스크린샷 저장됨
# ✅ Report Page 스크린샷 저장됨
# ✨ 모든 스크린샷이 성공적으로 검증되었습니다!
```

### 예제 2: Python 스크립트로 검증
```bash
cd /mnt/d/progress/Univ-Insight
python tests/screenshot_verification.py --verify

# 출력:
# 📋 스크린샷 검증 리포트
# ════════════════════════════════════════════════════════════════
# 페이지명     | 파일명            | 파일 크기  | MD5 해시
# ────────────────────────────────────────────────────────────────
# Home Page    | homepage.png      | 1234567 B | a1b2c3d4...
# ...
```

### 예제 3: UI 모드로 시각적 확인
```bash
cd frontend
npm run test:e2e:ui -- screenshot-verification.spec.ts

# 브라우저에서:
# - 각 페이지의 스크린샷이 캡처되는 것을 시각적으로 확인
# - 로깅된 MD5 해시 값 확인
# - 검증 진행 과정 실시간 모니터링
```

---

## 📊 검증 결과 해석

### ✅ 성공 케이스

```
✅ Home Page 스크린샷 저장됨
   파일: homepage.png
   크기: 1234567 bytes
   MD5: a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6

✅ 모든 스크린샷이 서로 다릅니다!
   총 4개의 고유한 이미지
```

**의미:**
- 각 이미지가 성공적으로 생성됨
- 모든 스크린샷이 서로 다른 내용을 포함
- MD5 해시가 유효한 형식

### ⚠️ 경고 케이스

```
⚠️ 중복된 스크린샷이 있습니다!
   총 4개 중 3개가 고유함

Home Page vs Research Page : 동일
Research Page vs Profile Page : 다름
```

**의미:**
- Home Page와 Research Page의 MD5 해시가 동일
- 두 페이지가 실제로 같은 내용일 가능성
- 페이지 렌더링 문제 또는 의도적 중복

---

## 🔧 고급 사용법

### 커스텀 스크린샷 디렉토리 지정
```bash
python tests/screenshot_verification.py --verify --dir /custom/path/screenshots
```

### 스크린샷 파일 직접 검증
```python
from tests.screenshot_verification import ScreenshotVerifier

verifier = ScreenshotVerifier('frontend/screenshots')
info = verifier.verify_screenshot('frontend/screenshots/homepage.png', 'Home Page')
print(f"MD5: {info.md5_hash}")
```

### 해시 값 수동 계산
```bash
# Linux/Mac
md5sum frontend/screenshots/homepage.png

# 출력:
# a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6  frontend/screenshots/homepage.png

# Windows
certutil -hashfile frontend/screenshots/homepage.png MD5
```

---

## 📝 트러블슈팅

### Q: "스크린샷 파일을 찾을 수 없습니다" 오류

**원인:** 스크린샷 디렉토리가 없거나 파일이 생성되지 않음

**해결책:**
```bash
# 디렉토리 확인
ls -la frontend/screenshots/

# 테스트 다시 실행
npm run test:e2e -- screenshot-verification.spec.ts
```

### Q: "빈 파일입니다" 오류

**원인:** 스크린샷 파일이 0 bytes (내용 없음)

**해결책:**
```bash
# 파일 크기 확인
ls -lh frontend/screenshots/*.png

# 문제 있는 파일 삭제
rm frontend/screenshots/homepage.png

# 테스트 다시 실행
```

### Q: "모든 스크린샷의 해시가 동일합니다" 경고

**원인:** 모든 페이지의 내용이 같거나 렌더링 실패

**해결책:**
```bash
# 페이지별 스크린샷 수동 확인
open frontend/screenshots/homepage.png
open frontend/screenshots/research-page.png

# 개발 서버 상태 확인
npm run dev  # frontend 개발 서버 재시작

# 테스트 다시 실행
```

---

## ✅ 검증 체크리스트

- [ ] Playwright 설치됨 (`npm install @playwright/test`)
- [ ] Python 3.7+ 설치됨
- [ ] 프론트엔드 개발 서버 실행 중
- [ ] 스크린샷 디렉토리 생성됨
- [ ] 테스트 실행: `npm run test:e2e -- screenshot-verification.spec.ts`
- [ ] 검증 파일 확인: `frontend/screenshots/screenshot-verification.json`
- [ ] 모든 스크린샷이 고유한 해시를 가짐
- [ ] 파일 무결성 확인됨

---

## 🎯 결론

이 검증 방식을 통해:

✅ **신뢰성**: MD5 해시로 이미지 고유성 보증
✅ **자동화**: 스크린샷 캡처부터 검증까지 자동화
✅ **추적성**: 모든 스크린샷의 히스토리 기록
✅ **투명성**: JSON 파일로 모든 정보 저장

**지금 바로 검증을 시작하세요! 🚀**

```bash
npm run test:e2e -- screenshot-verification.spec.ts
```
