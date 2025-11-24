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
- [x] Project Structure Setup
- [x] Domain Models Definition
- [x] Mock Crawler Implementation
- [x] Mock LLM Implementation
- [x] Process Verification Script
