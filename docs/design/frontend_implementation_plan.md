# Frontend Implementation Plan: University Explorer & Crawler

## 1. Objective
The goal is to create a web interface that allows users to:
1.  View a list of universities loaded from the standard dataset (`전국대학및전문대학정보표준데이터.csv`).
2.  Select a specific university.
3.  Trigger a crawling job for the selected university.
4.  View the crawled results (e.g., research papers, notices).

## 2. Architecture Overview

### Data Flow
1.  **CSV Source**: `전국대학및전문대학정보표준데이터.csv` (Raw Data)
2.  **Database**: SQLite (`univ_insight.db`) - Populated from CSV.
3.  **Backend API**: FastAPI (`src/api`) - Serves university data and triggers crawler.
4.  **Frontend**: React + Vite (`frontend/`) - User interface.

### Tech Stack
*   **Frontend**: React, Vite, Axios (for API calls), React Router.
*   **Backend**: FastAPI, SQLAlchemy.
*   **Crawler**: `crawl4ai` (as defined in `src/services/crawler.py`).

## 3. Implementation Steps

### Phase 1: Data Ingestion (Backend)
**Goal**: Populate the database with the CSV data so the API can serve it.

1.  **Create Import Script**: `src/scripts/import_universities.py`
    *   Read `전국대학및전문대학정보표준데이터.csv`.
    *   Map CSV columns to the `University` model in `src/domain/models.py`.
        *   `학교명` -> `name_ko`
        *   `학교 영문명` -> `name` (generate ID from this or use a slug)
        *   `소재지도로명주소` -> `location`
        *   `홈페이지주소` -> `url`
        *   `설립일자` -> `established_year` (extract year)
    *   Upsert data into the `universities` table.

### Phase 2: Backend API Updates
**Goal**: Ensure endpoints exist to list universities and trigger crawling.

1.  **Verify List Endpoint**: `GET /universities` (Already exists in `src/api/routes.py`).
2.  **Update Crawl Endpoint**: `POST /admin/crawl`
    *   Modify to accept `university_id` and `target_url` as parameters.
    *   Integrate with `KaistCrawler` (or a generic `UniversityCrawler`) to start the job.
    *   For now, it can be a synchronous call or a simple background task.

### Phase 3: Frontend Development
**Goal**: Build the UI.

1.  **Setup API Client**: Configure `axios` instance in `frontend/src/services/api.ts` to point to the backend URL (e.g., `http://localhost:8000`).
2.  **University List Page**: `frontend/src/pages/UniversityList.tsx`
    *   Fetch data from `/universities`.
    *   Display a table with columns: Name (Korean/English), Location, Link.
    *   Add a search bar to filter by name.
3.  **University Detail Page**: `frontend/src/pages/UniversityDetail.tsx`
    *   Show detailed info.
    *   **Action**: "Start Crawling" button.
    *   **Status**: Show "Crawling..." loading state.
    *   **Results**: Display crawled papers/notices (fetch from `/papers?lab_id=...` or similar, might need a new endpoint for university-level papers).

### Phase 4: Integration & Testing
1.  Run the import script: `python src/scripts/import_universities.py`.
2.  Start Backend: `uvicorn src.api.main:app --reload`.
3.  Start Frontend: `npm run dev` (in `frontend/`).
4.  Verify the full flow: List -> Select -> Crawl -> View Results.

## 4. Notes
*   **Encoding**: The CSV file has been converted to UTF-8, so reading it in Python should be straightforward.
*   **Crawler**: The current `KaistCrawler` is specific. We might need to generalize it to `GenericUniversityCrawler` that accepts a URL.
