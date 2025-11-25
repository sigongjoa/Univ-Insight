# Implementation Guide: Completing Univ-Insight

**Last Updated:** 2024-11-25
**Status:** Infrastructure Phase Complete | API Phase In Progress

---

## Overview

This guide provides step-by-step instructions to complete the implementation of Univ-Insight based on the documentation in `/docs` and gaps identified in `IMPLEMENTATION_GAP_ANALYSIS.md`.

## Phase 1: ✅ Infrastructure (COMPLETED)

### Completed Components

1. **Structured Logging** (`src/core/logging.py`)
   - JSON formatted logs with timestamp, level, component, message
   - File rotation and console output
   - Integration with existing modules via `get_logger()`

2. **Error Handling System** (`src/core/exceptions.py`)
   - Custom exception hierarchy for all error types
   - Consistent error codes and details
   - Exception types: Crawler, LLM, API, Notification, Database, Recommendation

3. **Retry Mechanism** (`src/utils/retry.py`)
   - Exponential backoff decorator with jitter
   - Async and sync support
   - Predefined configs: QUICK_RETRY, NETWORK_RETRY, LONG_RETRY

4. **FastAPI Middleware** (`src/core/middleware.py`)
   - Global exception handler
   - Unified error response format
   - Request ID tracking and logging

5. **External API Schemas** (`src/domain/external_api_schemas.py`)
   - Pydantic models for Notion API
   - Pydantic models for Kakao API
   - GitHub API models
   - Response/Request standardization

6. **Environment Configuration** (`.env.example`)
   - Comprehensive environment variables documentation
   - Database, API, LLM, Notification settings
   - Development/production guidance

7. **Test Infrastructure** (`tests/`, `pytest.ini`, `tests/conftest.py`)
   - In-memory SQLite test database
   - FastAPI test client
   - Test data fixtures and mock services
   - pytest configuration with markers

---

## Phase 2: API Completion (IN PROGRESS)

### What Needs to Be Done

According to `docs/api/api_specification.md`, the following endpoints need completion:

#### Missing Endpoints

1. **Authentication** ❌
   - `GET /auth/kakao/callback` - Kakao OAuth callback handler
   - Status: Missing JWT token generation

2. **User Management** ⚠️
   - `POST /users/profile` - Register/update user
   - `GET /users/{user_id}` - Get user profile
   - Status: Not implemented

3. **Research Endpoints** ⚠️
   - `GET /research` - List papers with filtering
   - `GET /research/{paper_id}/analysis` - Get analysis
   - Status: Partially implemented

4. **Report Generation** ⚠️
   - `POST /reports/generate` - Generate and send report
   - Status: Partially implemented

5. **Admin Endpoints** ⚠️
   - `POST /admin/crawl` - Trigger crawler manually
   - Status: Partially implemented

### Implementation Steps

#### Step 1: Create Authentication Module

File: `src/api/auth.py`

```python
"""Authentication endpoints"""

from fastapi import APIRouter, HTTPException
from src.domain.external_api_schemas import SuccessResponse

router = APIRouter(prefix="/auth", tags=["authentication"])

@router.get("/kakao/callback")
async def kakao_callback(code: str):
    """
    Handle Kakao OAuth callback.

    Args:
        code: Authorization code from Kakao

    Returns:
        Access token for API authentication
    """
    # TODO: Exchange code for Kakao token
    # TODO: Get user info from Kakao
    # TODO: Create or update user in DB
    # TODO: Generate JWT token
    pass
```

#### Step 2: Create User Management Module

File: `src/api/users.py`

```python
"""User management endpoints"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.core.database import get_db
from src.domain.models import User

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/profile")
async def register_user(user_data: dict, db: Session = Depends(get_db)):
    """Register or update user profile"""
    # TODO: Validate user data
    # TODO: Create/update user in database
    # TODO: Return created user
    pass

@router.get("/{user_id}")
async def get_user(user_id: str, db: Session = Depends(get_db)):
    """Get user profile"""
    # TODO: Query user from database
    # TODO: Return user details
    pass
```

#### Step 3: Update Research Endpoints

File: `src/api/routes.py` (update existing functions)

Add filtering support to research endpoints:

```python
@router.get("/research")
def list_research_papers(
    university: Optional[str] = None,
    topic: Optional[str] = None,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """
    List research papers with filtering.

    Query parameters:
    - university: Filter by university
    - topic: Filter by topic
    - limit: Maximum results
    """
    # TODO: Add filtering logic
    pass
```

#### Step 4: Implement Report Generation

File: `src/api/reports.py`

```python
"""Report generation and distribution"""

from fastapi import APIRouter
from src.services.notification import NotificationManager

router = APIRouter(prefix="/reports", tags=["reports"])

@router.post("/generate")
async def generate_report(user_id: str, target_date: str):
    """
    Generate and send personalized report.

    - Gets user interests
    - Finds matching papers
    - Generates summary
    - Sends to Notion and/or Kakao
    """
    # TODO: Fetch user interests
    # TODO: Query matching papers
    # TODO: Generate report content
    # TODO: Send notifications
    pass
```

#### Step 5: Add Admin Endpoints

File: `src/api/admin.py`

```python
"""Admin endpoints for system management"""

from fastapi import APIRouter
from src.services.crawler import KaistCrawler

router = APIRouter(prefix="/admin", tags=["admin"])

@router.post("/crawl")
async def trigger_crawler(target: str = "KAIST_CS", depth: int = 1):
    """
    Manually trigger crawler.

    Args:
        target: Crawler target (e.g., "KAIST_CS", "SNU_CS")
        depth: Crawl depth
    """
    # TODO: Validate admin permission
    # TODO: Trigger crawler
    # TODO: Return job status
    pass
```

---

## Phase 3: Testing (READY)

### Test Structure Created

```
tests/
├── __init__.py
├── conftest.py              ✅ Done
├── unit/
│   ├── __init__.py
│   ├── test_services.py     📝 Needs writing
│   ├── test_crawler.py      📝 Needs writing
│   └── test_llm.py          📝 Needs writing
├── integration/
│   ├── __init__.py
│   ├── test_api.py          📝 Needs writing
│   └── test_database.py     📝 Needs writing
└── fixtures/
    ├── __init__.py
    ├── sample_papers.json   📝 Optional
    └── sample_results.json  📝 Optional
```

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio pytest-cov pytest-html

# Run all tests
pytest -v

# Run with coverage
pytest --cov=src tests/

# Run specific test file
pytest tests/unit/test_services.py -v

# Run tests with specific marker
pytest -m unit tests/

# Generate HTML report
pytest --html=report.html
```

---

## Phase 4: Integration

### Using New Infrastructure Components

#### 1. Using Structured Logging

```python
from src.core.logging import get_logger

logger = get_logger(__name__)

logger.debug("Starting operation", extra={"user_id": user_id})
logger.info("Operation completed")
logger.warning("Potential issue detected", extra={"detail": "..."})
logger.error("Operation failed", extra={"error": "..."})
```

#### 2. Using Retry Decorator

```python
from src.utils.retry import retry, NETWORK_RETRY

@retry(max_attempts=3, initial_delay=1.0)
def fetch_data(url: str):
    # This will retry on any exception
    pass

@NETWORK_RETRY.to_decorator(exceptions=(ConnectionError, TimeoutError))
def fetch_with_config(url: str):
    # Uses predefined network retry config
    pass
```

#### 3. Using Custom Exceptions

```python
from src.core.exceptions import (
    CrawlTimeoutError, LLMParseError, NotFoundError
)

try:
    crawl_result = crawler.crawl(url)
except CrawlTimeoutError as e:
    logger.error(f"Crawl timeout: {e.message}", extra=e.details)
except Exception as e:
    logger.error(f"Unexpected error: {e}")
```

#### 4. Using External API Schemas

```python
from src.domain.external_api_schemas import NotionPageCreateRequest

request = NotionPageCreateRequest(
    parent={"database_id": "db_id"},
    properties={
        "Name": {
            "title": [{"type": "text", "text": {"content": "Paper Title"}}]
        }
    }
)

# Request is now validated by Pydantic
```

---

## Files Created/Modified Summary

### Created Files ✅

| File | Purpose | Status |
|------|---------|--------|
| `src/core/logging.py` | Structured JSON logging | ✅ Complete |
| `src/core/exceptions.py` | Custom exception hierarchy | ✅ Complete |
| `src/core/middleware.py` | Global exception handler | ✅ Complete |
| `src/utils/retry.py` | Retry decorator with backoff | ✅ Complete |
| `src/domain/external_api_schemas.py` | API request/response models | ✅ Complete |
| `.env.example` | Environment variables | ✅ Complete |
| `pytest.ini` | pytest configuration | ✅ Complete |
| `tests/conftest.py` | Test fixtures and config | ✅ Complete |
| `tests/` directory structure | Test organization | ✅ Complete |
| `IMPLEMENTATION_GAP_ANALYSIS.md` | Gap analysis report | ✅ Complete |
| `IMPLEMENTATION_GUIDE.md` | This file | ✅ Complete |

### Files to Modify ⏳

| File | Changes Needed |
|------|-----------------|
| `src/api/main.py` | Add new routers, middleware |
| `src/api/routes.py` | Update filters, add missing endpoints |
| `src/core/config.py` | Add environment validation |
| `src/services/crawler.py` | Add retry decorator |
| `src/services/llm.py` | Add retry decorator |

---

## Quick Start for Developers

### 1. Setup Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your actual values
# Install dependencies
pip install -r requirements.txt

# Install test dependencies
pip install pytest pytest-asyncio pytest-cov
```

### 2. Initialize Database

```bash
python -c "from src.core.database import init_db; init_db()"
```

### 3. Run Tests

```bash
pytest -v --cov=src
```

### 4. Start Development Server

```bash
python -m uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

---

## Next Steps

### Immediate (This Week)
1. ✅ Create infrastructure (COMPLETED)
2. Create missing API endpoints
3. Integrate logging into existing services
4. Write unit tests for services

### Short Term (Next Week)
1. Complete integration tests
2. Add API documentation (OpenAPI/Swagger)
3. Set up CI/CD pipeline
4. Performance testing

### Medium Term (2-3 Weeks)
1. Database migration setup (Alembic)
2. Docker containerization
3. Deployment configuration
4. Monitoring and alerting

---

## Validation Checklist

After implementing each component:

- [ ] Code follows project style guide
- [ ] Logging is structured and useful
- [ ] Exceptions are properly caught and logged
- [ ] Tests pass with >80% coverage
- [ ] Documentation is updated
- [ ] No hardcoded secrets or credentials
- [ ] Environment variables used correctly
- [ ] API responses match specification

---

## Support & References

### Project Documentation
- `/docs/api/api_specification.md` - API endpoints
- `/docs/design/database_schema.md` - Database models
- `/docs/test/test_strategy.md` - Testing approach
- `CLAUDE.md` - Project overview and commands

### Implementation Gap Analysis
- `IMPLEMENTATION_GAP_ANALYSIS.md` - Detailed gap analysis

### Code Structure
- `src/core/` - Core infrastructure
- `src/domain/` - Data models
- `src/api/` - API endpoints
- `src/services/` - Business logic
- `src/utils/` - Utility functions
- `tests/` - Test suite

---

## Common Issues & Solutions

### Issue: Import errors for new modules

**Solution:** Ensure module has `__init__.py` files in all parent directories

### Issue: Test database conflicts

**Solution:** Use in-memory SQLite (configured in conftest.py)

### Issue: Async test failures

**Solution:** Use `@pytest.mark.asyncio` for async tests

### Issue: .env variables not loading

**Solution:** Ensure `.env` file is in project root, not in subdirectories

---

Generated with ❤️ for Univ-Insight
For questions, refer to CLAUDE.md or project documentation.
