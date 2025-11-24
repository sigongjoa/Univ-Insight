# SDD & TDD Gap Analysis & Requirements

To transition from the initial plan to a robust implementation using SDD (Software Design Description) and TDD (Test-Driven Development), the following gaps must be addressed and defined.

## 1. SDD Gaps (Detailed Design Needs)

Before writing code, we need to define these specific technical details to ensure the system is robust and maintainable.

### A. Database Schema Design (Physical Data Model)
*   **Current Status:** Conceptual classes defined (`ResearchPaper`, `UserProfile`).
*   **Missing:**
    *   **SQL/NoSQL Choice:** SQLite (for MVP) or PostgreSQL? -> *Decision: SQLite for local MVP, scalable to Postgres.*
    *   **Table Definitions:**
        *   `papers`: `id` (PK), `url` (Unique), `title`, `content_raw`, `crawled_at`.
        *   `analysis`: `paper_id` (FK), `summary`, `career_tags`, `embedding_id`.
        *   `users`: `id`, `platform_id` (Kakao/Notion), `preferences` (JSON).
        *   `reports`: `id`, `user_id` (FK), `paper_ids` (JSON), `sent_at`.

### B. Configuration & Secret Management
*   **Missing:** Standardized way to handle API Keys (OpenAI, Notion, Kakao).
*   **Requirement:** Use `.env` file with `pydantic-settings`.
    *   `OPENAI_API_KEY`
    *   `NOTION_API_KEY`
    *   `KAKAO_CLIENT_ID`
    *   `DB_URL`

### C. Error Handling & Logging Strategy
*   **Missing:** How to handle crawler failures or LLM hallucinations?
*   **Requirement:**
    *   **Global Exception Handler:** FastAPI middleware to catch unhandled errors.
    *   **Retry Logic:** Decorators for external API calls (LLM, Crawler) with exponential backoff.
    *   **Logging:** Structured JSON logging (Time, Level, Component, Message) for debugging.

### D. External API Interface Definitions
*   **Missing:** Exact payload structures for Notion and Kakao APIs.
*   **Requirement:** Define Pydantic models for *outgoing* requests to these services to ensure type safety before sending.

---

## 2. TDD Requirements (Test Infrastructure)

To support TDD, we need a test environment that allows us to write the test *before* the code.

### A. Testing Framework
*   **Tool:** `pytest` (Standard for Python).
*   **Plugins:** `pytest-asyncio` (for async FastAPI/Playwright), `pytest-cov` (coverage), `pytest-html` (reporting).

### B. Mocking Strategy (Critical for Cost & Speed)
*   **LLM Service:** Do NOT call OpenAI in unit tests.
    *   *Solution:* Create `MockLLMService` returning predefined JSON responses.
*   **Crawler:** Do NOT hit live websites in unit tests.
    *   *Solution:* Load local HTML files as fixtures to test parsing logic.
*   **Database:** Use an in-memory SQLite database for tests.

### C. Test Data Fixtures
*   `sample_paper_html.html`: A saved HTML file from a target university lab page.
*   `sample_analysis_result.json`: A perfect example of what the LLM *should* output.
*   `user_profile_fixture.json`: A standard user profile for testing recommendations.

### D. CI/CD Integration
*   Tests must run automatically.
*   **Requirement:** A `Makefile` or script to run `pytest` and generate a report.
