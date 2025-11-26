# End-to-End Integration Test Plan

## Objective
Implement complete integration test flow:
Frontend → Backend API → Crawler → DB → Frontend Result Display

## Implementation Steps

### Phase 1: Backend - Save Crawl Results ✅
**Files to modify:**
- `src/api/routes.py` - Update `run_crawler_task` to save to DB
- Add endpoint `GET /api/v1/universities/{id}/papers` - Get crawled papers

**Tasks:**
1. Create new DB session in background task
2. Save crawled paper to `research_papers` table
3. Link paper to university (via lab_id or new field)
4. Add API endpoint to retrieve papers by university

### Phase 2: Frontend - Display Results
**Files to create/modify:**
- `frontend/src/services/universityService.ts` - Add `getPapers` method
- `frontend/src/pages/UniversityDetail.tsx` - Add papers list section

**Tasks:**
1. Add "View Results" button on detail page
2. Fetch papers after crawl completes
3. Display paper list with title, URL, crawled date
4. Add refresh button to check for new results

### Phase 3: Integration Test
**Test Scenario:**
1. Navigate to University Detail page
2. Enter crawl URL (e.g., https://cse.snu.ac.kr)
3. Click "Start Crawl"
4. Wait for crawl to complete (or poll status)
5. Click "View Results" or auto-refresh
6. Verify papers are displayed

### Phase 4: Optional Enhancements
- Add crawl job status tracking (pending/running/completed/failed)
- Implement polling or WebSocket for real-time updates
- Add pagination for paper list
- Add paper detail view with full content

## Expected Outcome
Complete E2E flow where user can:
1. Select a university
2. Trigger crawling
3. See crawled papers in the UI
4. Verify data is persisted in DB

## Test Cases
- TC-001: Crawl job saves paper to DB
- TC-002: API returns papers for university
- TC-003: Frontend displays papers after crawl
- TC-004: Multiple crawls accumulate papers
- TC-005: Error handling for failed crawls
