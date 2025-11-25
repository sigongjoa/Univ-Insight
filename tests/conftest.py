"""
Pytest configuration and fixtures for Univ-Insight tests.

Provides:
- Database fixtures (in-memory SQLite)
- FastAPI test client
- Mock services (Crawler, LLM)
- Test data fixtures
"""

import pytest
import json
from datetime import datetime, timedelta
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient
from typing import Generator

from src.core.database import get_db
from src.domain.models import Base
from src.api.main import app


# ==================== Database Fixtures ====================

@pytest.fixture(scope="session")
def test_db_engine():
    """Create in-memory test database."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db_session(test_db_engine) -> Generator[Session, None, None]:
    """Create a fresh database session for each test."""
    connection = test_db_engine.connect()
    transaction = connection.begin()
    session = sessionmaker(autocommit=False, autoflush=False, bind=connection)()

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def override_get_db(db_session):
    """Override FastAPI database dependency."""
    def get_db_override():
        yield db_session

    app.dependency_overrides[get_db] = get_db_override
    yield
    app.dependency_overrides.clear()


# ==================== FastAPI Test Client Fixture ====================

@pytest.fixture
def client(override_get_db) -> TestClient:
    """Create FastAPI test client."""
    return TestClient(app)


# ==================== Test Data Fixtures ====================

@pytest.fixture
def sample_university_data():
    """Sample university data for testing."""
    return {
        "id": "snu-001",
        "name": "Seoul National University",
        "name_ko": "서울대학교",
        "location": "Seoul",
        "ranking": 1,
        "tier": 1,
        "url": "https://www.snu.ac.kr",
        "description": "Top-tier Korean university",
        "established_year": 1946
    }


@pytest.fixture
def sample_college_data(sample_university_data):
    """Sample college data for testing."""
    return {
        "id": "snu-col-engineering",
        "university_id": sample_university_data["id"],
        "name": "College of Engineering",
        "name_ko": "공과대학",
        "description": "Engineering faculty"
    }


@pytest.fixture
def sample_research_paper():
    """Sample research paper for testing."""
    return {
        "id": "paper_test_001",
        "title": "Efficient Transformer Architecture for Mobile Devices",
        "url": "https://snu.ac.kr/research/paper_001",
        "university": "Seoul National University",
        "department": "Computer Science",
        "pub_date": datetime(2024, 5, 20).date(),
        "content_raw": "This is a sample research paper content...",
        "university_tier": 1,
        "crawled_at": datetime.utcnow()
    }


@pytest.fixture
def sample_analysis_result(sample_research_paper):
    """Sample analysis result for testing."""
    return {
        "paper_id": sample_research_paper["id"],
        "summary": "This research paper discusses efficient transformer architectures...",
        "job_title": "AI Model Optimizer",
        "salary_hint": "60000000-80000000",
        "related_companies": ["Samsung Electronics", "Naver", "Google"],
        "action_items": {
            "subject": "Advanced Mathematics",
            "topic": "Matrix operations and optimization"
        },
        "analyzed_at": datetime.utcnow()
    }


@pytest.fixture
def sample_user_profile():
    """Sample user profile for testing."""
    return {
        "id": "test_user_001",
        "name": "Test Student",
        "role": "student",
        "interests": ["Artificial Intelligence", "Robotics"],
        "notion_page_id": "notion_page_123"
    }


# ==================== Mock Service Fixtures ====================

class MockCrawler:
    """Mock crawler for testing."""

    async def crawl(self, url: str):
        """Mock crawl method."""
        return {
            "title": "Sample Research Paper",
            "content": "This is sample content",
            "url": url,
            "date": datetime.utcnow().isoformat()
        }


class MockLLM:
    """Mock LLM service for testing."""

    async def analyze(self, content: str):
        """Mock analyze method."""
        return {
            "summary": "Sample summary",
            "career_paths": ["Engineer", "Researcher"],
            "action_items": ["Study Math"]
        }


@pytest.fixture
def mock_crawler():
    """Provide mock crawler for tests."""
    return MockCrawler()


@pytest.fixture
def mock_llm():
    """Provide mock LLM for tests."""
    return MockLLM()


# ==================== Utility Fixtures ====================

@pytest.fixture
def auth_headers():
    """Sample authorization headers for testing."""
    return {
        "Authorization": "Bearer test_token_123"
    }


@pytest.fixture
def json_headers():
    """JSON content type headers."""
    return {
        "Content-Type": "application/json"
    }


# ==================== Pytest Hooks ====================

def pytest_configure(config):
    """Configure pytest."""
    # Register custom markers
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )


@pytest.fixture(autouse=True)
def reset_db(db_session):
    """Reset database before each test."""
    yield
    # Cleanup happens automatically with transaction rollback
