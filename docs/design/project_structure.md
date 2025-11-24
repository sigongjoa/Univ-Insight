# Project Directory Structure

This document defines the file organization for the Univ-Insight project.

```text
Univ-Insight/
├── .github/                   # CI/CD Workflows
│   └── workflows/
│       └── test.yml
├── docs/                      # Documentation
│   ├── api/
│   ├── architecture/
│   ├── design/                # Specs (DB, Crawler, Prompts)
│   ├── project/
│   └── test/
├── src/                       # Source Code
│   ├── core/                  # Core Configuration
│   │   ├── __init__.py
│   │   ├── config.py          # Pydantic Settings (.env loader)
│   │   └── database.py        # DB Connection & Session
│   ├── domain/                # Business Logic & Models
│   │   ├── __init__.py
│   │   ├── models.py          # SQLAlchemy Models
│   │   └── schemas.py         # Pydantic DTOs
│   ├── services/              # Application Services
│   │   ├── __init__.py
│   │   ├── crawler.py         # Playwright Logic
│   │   ├── llm.py             # OpenAI/Claude Interface
│   │   ├── vector_store.py    # ChromaDB Interface
│   │   ├── notification.py    # Notion/Kakao Interface
│   │   └── scheduler.py       # APScheduler for periodic tasks
│   ├── api/                   # FastAPI Routes
│   │   ├── __init__.py
│   │   ├── main.py            # App Entrypoint
│   │   └── routes.py          # Endpoints
│   └── utils/                 # Helpers
│       └── logger.py
├── tests/                     # Test Suite
│   ├── __init__.py
│   ├── conftest.py            # Fixtures
│   ├── unit/
│   │   ├── test_crawler.py
│   │   └── test_llm.py
│   └── integration/
│       └── test_api.py
├── .env.example               # Template for environment variables
├── .gitignore
├── requirements.txt           # Python dependencies
├── README.md
└── main.py                    # Dev entrypoint (uvicorn)
```
