# 프론트엔드 설정 가이드

## 📦 기본 패키지 설치 완료

```bash
npm install
```

다음 패키지가 자동으로 설치됩니다:
- react 18
- react-dom 18
- typescript
- vite

---

## 🎨 추가 패키지 설치

### 1단계: Tailwind CSS + Shadcn/ui 설정

```bash
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p

npm install -D clsx class-variance-authority lucide-react
npx shadcn-ui@latest init
```

### 2단계: 라우팅, 상태관리, API 통신

```bash
npm install react-router-dom zustand @tanstack/react-query axios
```

### 3단계: 유틸리티

```bash
npm install date-fns classnames
```

---

## 🔧 설정 파일

### tailwind.config.js
```javascript
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
```

### tsconfig.json 주요 설정
```json
{
  "compilerOptions": {
    "baseUrl": ".",
    "paths": {
      "@/*": ["./src/*"]
    }
  }
}
```

### vite.config.ts
```typescript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      }
    }
  }
})
```

---

## 📝 필수 파일 구조

### src/main.tsx
```typescript
import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.tsx'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
```

### src/App.tsx
```typescript
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import LoginPage from './pages/LoginPage'
import HomePage from './pages/HomePage'

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/" element={<HomePage />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App
```

### src/index.css
```css
@tailwind base;
@tailwind components;
@tailwind utilities;
```

---

## 🚀 개발 서버 실행

```bash
npm run dev
```

브라우저에서 `http://localhost:5173` 접속

---

## 📋 다음 단계

1. [ ] Tailwind CSS 설정 완료
2. [ ] Shadcn/ui 초기화
3. [ ] 라우팅 설정
4. [ ] 상태 관리 설정
5. [ ] API 클라이언트 구성
6. [ ] 로그인 페이지 작성
