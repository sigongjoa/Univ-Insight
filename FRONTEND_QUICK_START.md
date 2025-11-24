# 프론트엔드 빠른 시작 가이드

## 🎯 현재 상태

**완료된 것:**
✅ React 18 + TypeScript + Vite 프로젝트 생성
✅ 기본 디렉토리 구조 생성
✅ API 클라이언트 (axios) 설정
✅ 상태 관리 (Zustand) 설정
✅ 로그인 페이지 구현
✅ 홈 페이지 구현
✅ 타입 정의 (TypeScript)
✅ 서비스 계층 (API 통신)

**다음 할 것:**
- UI 컴포넌트 추가 (연구 논문 검색, 리포트 등)
- 페이지 개발 (Research, Report, Profile)
- Tailwind CSS 통합
- 반응형 디자인 완성
- 배포 설정

---

## 🚀 개발 서버 실행

```bash
cd frontend
npm run dev
```

브라우저에서 `http://localhost:5173` 접속

---

## 📁 프로젝트 구조

```
frontend/
├── src/
│   ├── components/        # React 컴포넌트
│   ├── pages/
│   │   ├── LoginPage.tsx    ✅ 완료
│   │   ├── HomePage.tsx     ✅ 완료
│   │   ├── ResearchPage.tsx (예정)
│   │   ├── ReportPage.tsx   (예정)
│   │   └── ProfilePage.tsx  (예정)
│   ├── services/
│   │   ├── api.ts           ✅ 완료
│   │   ├── userService.ts   ✅ 완료
│   │   ├── paperService.ts  ✅ 완료
│   │   └── reportService.ts ✅ 완료
│   ├── store/
│   │   └── authStore.ts     ✅ 완료
│   ├── types/
│   │   └── index.ts         ✅ 완료
│   ├── App.tsx              ✅ 완료
│   └── main.tsx
├── package.json
└── vite.config.ts
```

---

## 🔑 주요 파일 설명

### 1. **API 클라이언트** (`src/services/api.ts`)
- Axios 인스턴스 생성
- 인터셉터로 JWT 토큰 자동 추가
- 401 에러 자동 처리 (로그인 페이지로 리다이렉트)

### 2. **상태 관리** (`src/store/authStore.ts`)
- Zustand 기반 인증 상태 관리
- 사용자 정보 저장/로드
- localStorage 연동

### 3. **서비스 계층**
- `userService.ts`: 사용자 프로필, 로그인
- `paperService.ts`: 논문 검색, 상세 조회, Plan B 제안
- `reportService.ts`: 리포트 생성

### 4. **페이지**
- `LoginPage.tsx`: 로그인/회원가입
- `HomePage.tsx`: 홈 대시보드

---

## 💻 개발 팁

### 새 페이지 추가하기

```typescript
// src/pages/ResearchPage.tsx
import { useEffect, useState } from 'react'
import { paperService } from '../services/paperService'
import { ResearchPaper } from '../types'

export default function ResearchPage() {
  const [papers, setPapers] = useState<ResearchPaper[]>([])
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    const loadPapers = async () => {
      setLoading(true)
      try {
        const result = await paperService.listPapers()
        setPapers(result.items)
      } catch (error) {
        console.error('Failed to load papers:', error)
      } finally {
        setLoading(false)
      }
    }
    loadPapers()
  }, [])

  return (
    <div>
      {loading ? <div>로딩 중...</div> : <div>논문 목록</div>}
    </div>
  )
}
```

### 새 라우트 추가하기

```typescript
// src/App.tsx
import ResearchPage from './pages/ResearchPage'

// Routes에 추가
<Route path="/research" element={<ResearchPage />} />
```

### API 호출하기

```typescript
import { paperService } from '../services/paperService'

// 논문 목록 조회
const papers = await paperService.listPapers({
  university: 'KAIST',
  limit: 10
})

// 논문 상세 조회
const analysis = await paperService.getPaperAnalysis(paperId)

// Plan B 제안
const suggestions = await paperService.getPlanBSuggestions(paperId)
```

---

## 🎨 Tailwind CSS 설정 (선택)

기본 스타일링은 인라인 Tailwind 클래스로 처리했습니다.
필요하면 공식 설정 가이드를 따르세요:

```bash
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p
```

---

## 🔗 백엔드와 연결

### 환경 변수 설정

```bash
# frontend/.env
VITE_API_URL=http://localhost:8000/api/v1
```

### CORS 확인

백엔드의 `src/api/main.py`에서 CORS가 허용되어 있는지 확인:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 또는 특정 도메인
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 📦 빌드

```bash
npm run build
```

빌드 결과물은 `dist/` 디렉토리에 생성됩니다.

---

## 🧪 TypeScript 타입 검사

```bash
npm run lint
```

---

## 📚 다음 단계

1. **Research 페이지 개발**
   - 논문 검색 & 필터
   - 논문 카드 컴포넌트
   - 상세 모달

2. **Report 페이지 개발**
   - 리포트 목록
   - 리포트 생성
   - PDF 다운로드

3. **Profile 페이지 개발**
   - 사용자 정보 수정
   - 관심사 관리
   - 로그아웃

4. **UI 개선**
   - Shadcn/ui 컴포넌트 추가
   - 다크 모드 지원
   - 반응형 디자인 완성

---

## 🆘 트러블슈팅

### API 연결 실패
- 백엔드 서버가 실행 중인지 확인: `http://localhost:8000/health`
- CORS 설정 확인
- 네트워크 탭에서 요청/응답 확인

### 상태 관리 문제
- Redux DevTools 설치해서 디버깅
- localStorage에서 저장된 값 확인

### TypeScript 에러
- `npm run lint` 실행해서 타입 에러 확인
- IDE의 TypeScript 버전 일치 확인

---

**Happy Coding! 🚀**
