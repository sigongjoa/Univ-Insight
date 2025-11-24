# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Univ-Insight** is an AI-powered university research curation and career design agent that translates complex academic research papers into accessible content for high school students and connects them with career paths.

**Core Mission:** Translate university research papers (from KAIST, Seoul National University, etc.) into high school-friendly language, match them to career opportunities, and suggest related subjects and research topics.

## Architecture

The system follows a **pipeline architecture** with three main stages:

```
Crawler (fetch papers) → LLM Analysis (translate & analyze) → Output (Notion/Kakao)
```

### Key Components

1. **Crawler Service** (`src/services/crawler.py`)
   - Fetches research papers from university websites using Crawl4AI (async web crawler)
   - Produces `ResearchPaper` objects with source, title, content, date, and URL
   - Currently supports KaistCrawler (production) and MockCrawler (testing)
   - Implements fallback strategies for site structure changes

2. **LLM Service** (`src/services/llm.py`)
   - Analyzes research papers using Ollama (local LLM) or mock responses
   - Translates complex content into student-friendly explanations
   - Generates structured output: title, research summary, career paths, and action items
   - Handles JSON parsing with regex fallback for LLM formatting inconsistencies

3. **Domain Models** (`src/domain/schemas.py`)
   - Pydantic schemas for data validation:
     - `ResearchPaper`: Crawled paper data
     - `AnalysisResult`: LLM-generated analysis
     - `CareerPath`: Company, job title, salary hints
     - `ActionItem`: Related subjects and research topics for students

### Data Flow Example

The mock verification script (`main_mock.py`) demonstrates the end-to-end flow:
1. Crawler fetches a paper → produces `ResearchPaper`
2. LLM analyzes it → produces `AnalysisResult` (with career paths and action items)
3. Output formatted and ready for delivery (Notion/Kakao)

## Development Commands

### Setup & Installation
```bash
# Create virtual environment
python3 -m venv venv

# Install dependencies
./venv/bin/pip install -r requirements.txt

# Verify environment
./venv/bin/pip list
```

### Running the Mock Process
```bash
# Run the end-to-end verification (uses mock data, no real crawling)
./venv/bin/python main_mock.py
```

### Running with Real Crawler
The `KaistCrawler` class uses Crawl4AI to fetch real data. Ensure Ollama is running locally for LLM analysis:
```bash
# Ollama must be running (local LLM server)
# Then adapt main_mock.py or create a real pipeline script
```

### Testing
```bash
# Run all tests (when test suite is implemented)
./venv/bin/pytest

# Run specific test file
./venv/bin/pytest tests/unit/test_crawler.py

# Run with coverage report
./venv/bin/pytest --cov=src tests/
```

## Key Design Decisions

### 1. Mock vs. Real Services
- **MockCrawler** and **MockLLM** are available for development/testing without external dependencies
- Real services (KaistCrawler, OllamaLLM) depend on Crawl4AI and Ollama
- The `main_mock.py` demonstrates the core flow without these dependencies

### 2. Async Crawling
- `KaistCrawler` uses async/await for efficient web crawling via Crawl4AI
- Non-blocking I/O allows concurrent requests if extended to multiple sources

### 3. LLM Output Parsing
- Structured JSON is expected from the LLM for programmatic use
- Regex fallback in `llm.py:61` handles cases where LLM adds markdown formatting around JSON
- Pydantic validation ensures type safety for downstream processes

### 4. Error Handling in Crawler
- Fallback mechanism: if CSS selectors fail (site structure changes), fallback to LLM-based content extraction
- Respects robots.txt and implements user-agent rotation (per spec in `docs/design/crawler_specs.md`)

## Important Files & References

### Documentation
- **Project Plan:** `docs/project_plan.md` (business vision, 4-week roadmap, prompt design)
- **Crawler Specs:** `docs/design/crawler_specs.md` (CSS selectors, error handling, fallback strategy)
- **Test Strategy:** `docs/test/test_strategy.md` (testing levels: unit, integration, E2E)
- **Database Schema:** `docs/design/database_schema.md` (tables for papers, users, embeddings)
- **API Specification:** `docs/api/api_specification.md` (FastAPI endpoints)

### Source Code
- **Entry Point (Mock):** `main_mock.py` - demonstrates full pipeline with mock data
- **Real Entry Point:** Will be `src/api/main.py` (FastAPI app, not yet fully implemented)
- **Core Services:** `src/services/{crawler,llm}.py`
- **Data Models:** `src/domain/schemas.py`

## Dependencies

Key external libraries:
- **crawl4ai**: Web crawling with Playwright (async, handles dynamic pages)
- **ollama**: Local LLM inference
- **pydantic**: Data validation and serialization
- **FastAPI**: Web framework (for future API deployment)
- **pytest**: Testing framework

See `requirements.txt` for complete list.

## Next Steps for Implementation

Based on the project plan, the next phases are:
1. **Week 1-2:** Implement real data crawler for KAIST CS department
2. **Week 2-3:** Refine LLM prompts for better translations (currently using mock responses)
3. **Week 3-4:** Build vector store (ChromaDB) for RAG and implement recommendation logic
4. **Week 4+:** Deploy with FastAPI and integrate Notion/Kakao delivery channels

## Common Pitfalls & Tips

- **Ollama not running:** If using real LLM, ensure Ollama server is active before running pipeline
- **Crawl4AI dependencies:** Requires Playwright; install with `pip install crawl4ai[playwright]` if not already in requirements
- **LLM JSON parsing:** Check `llm.py` regex logic if LLM response structure changes unexpectedly
- **Mock vs. Real:** Use MockCrawler and MockLLM for fast development loops; switch to real services only when needed
