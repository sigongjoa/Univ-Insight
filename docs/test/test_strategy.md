# Test Strategy & Plan

This document defines the testing levels, scope, and scenarios for the Univ-Insight project.

## 1. Testing Levels

### Level 1: Backend Unit Tests (TDD Core)
*   **Scope:** Individual functions and classes.
*   **Goal:** Verify logic in isolation.
*   **Tools:** `pytest`, `unittest.mock`.
*   **Key Targets:**
    *   `CrawlerService._parse_html()`: Verify it extracts title/content correctly from sample HTML.
    *   `LLMService._create_prompt()`: Verify prompt string formatting.
    *   `RecommendationService.calculate_similarity()`: Verify math logic.

### Level 2: Integration Tests
*   **Scope:** Interaction between modules (Service + DB).
*   **Goal:** Verify data persistence and service wiring.
*   **Key Targets:**
    *   **DB Integration:** Save a `ResearchPaper` -> Retrieve it -> Verify fields match.
    *   **API Integration:** `TestClient(app).get("/research")` returns 200 OK and valid JSON structure.

### Level 3: Frontend / Delivery Layer Tests
*   *Note: Since there is no custom Web App UI, "Frontend" refers to the Output Interfaces (Notion/Kakao).*
*   **Scope:** Verification of the final output format and API communication.
*   **Key Targets:**
    *   **Notion Renderer:** Verify that the JSON report is correctly converted to Notion Block objects (Heading, Paragraph, Callout).
    *   **Kakao Template:** Verify the text message fits within Kakao's character limits and template structure.

### Level 4: End-to-End (E2E) Tests
*   **Scope:** Full workflow from Trigger to Delivery.
*   **Goal:** Ensure the entire pipeline works together.
*   **Method:** Run a "Dry Run" mode where:
    1.  Crawler fetches a *cached* page.
    2.  LLM returns a *mocked* analysis.
    3.  System saves to *Test DB*.
    4.  System calls *Mock Notion API*.
    5.  Verify the final "Mock Notion API" received the correct payload.

---

## 2. Test Scenarios (User Stories)

These scenarios serve as the acceptance criteria for the system.

### Scenario A: The "New Paper" Discovery
1.  **Given** the crawler runs on the KAIST CS department page.
2.  **When** a new post "AI for Healthcare" is detected.
3.  **Then** the system should:
    *   Parse the content.
    *   Generate an analysis using LLM.
    *   Save it to the database.
    *   Create a vector embedding.

### Scenario B: Personalized Report Generation
1.  **Given** User A has interest "Bio-Health".
2.  **When** the weekly report job triggers.
3.  **Then** the system should:
    *   Select the "AI for Healthcare" paper (high similarity).
    *   Find a "Plan B" paper from a lower-tier university with similar keywords.
    *   Format a Notion page with these two items.
    *   Send a notification to User A.

### Scenario C: Parent Guide Generation
1.  **Given** a report is generated for Student A.
2.  **When** the system finalizes the report.
3.  **Then** it should generate a separate "Parent Guide" section containing:
    *   A conversation starter question.
    *   A simplified explanation of the career value.

---

## 3. Test Reporting & Artifacts

### Automated Test Report
*   Every test run must generate a report to visualize health.
*   **Command:** `pytest --html=artifacts/test_reports/report.html --self-contained-html`
*   **Content:**
    *   Summary (Pass/Fail count).
    *   Coverage Report (Percentage of code tested).
    *   List of failed tests with stack traces.

### Manual Verification Log
*   For UI/UX (Notion pages), a manual check log is maintained for the first few iterations to ensure formatting aesthetics.
