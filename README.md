# Univ-Insight

AI 기반 대학 연구 큐레이션 및 진로 설계 에이전트

## Project Overview
This project aims to translate complex university research papers into easy-to-understand content for high school students, connecting them with career paths and study topics.

## Structure
- `src/core`: Configuration and core logic
- `src/domain`: Data models (Pydantic schemas)
- `src/services`: Business logic (Crawler, LLM, etc.)
- `src/api`: FastAPI application (Future)

## Running the Mock Verification
To verify the core process flow (Crawler -> LLM -> Report), run the mock script:

```bash
# 1. Create Virtual Environment (if not exists)
python3 -m venv venv

# 2. Install Dependencies
./venv/bin/pip install -r requirements.txt

# 3. Run Mock Script
./venv/bin/python main_mock.py
```

## Status

### ✅ Backend Implementation (Complete)
- [x] Project Structure Setup
- [x] Domain Models Definition & Database (SQLAlchemy 5 tables)
- [x] Crawler Service (KaistCrawler + Crawl4AI async)
- [x] LLM Service (OllamaLLM + analysis)
- [x] Vector Store (ChromaDB with embeddings)
- [x] Recommendation Engine (Plan B with user matching)
- [x] FastAPI Application (8 endpoints)
- [x] Notification Services (Notion + Kakao Talk)
- [x] APScheduler Background Jobs
- [x] Unit & Integration Tests
- [x] Process Verification with E2E Mock

### ✅ Frontend Implementation (Complete)
- [x] React 18 + TypeScript + Vite Setup
- [x] Authentication (LoginPage with role-based access)
- [x] Dashboard (HomePage with quick actions)
- [x] Paper Search (ResearchPage with filters & details modal)
- [x] Plan B Alternatives (PlanBPage with similarity scoring)
- [x] Report Generation (ReportPage with history)
- [x] User Profile (ProfilePage with settings)
- [x] API Integration (Axios client with JWT)
- [x] State Management (Zustand store)
- [x] Responsive Design (Tailwind CSS)
