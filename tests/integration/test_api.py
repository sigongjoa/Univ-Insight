"""
Integration tests for FastAPI endpoints.
"""

import pytest
from src.domain.models import ResearchPaper, AnalysisResult, User, UserRole


class TestUserManagement:
    """Tests for user management endpoints"""

    def test_create_user(self, client):
        """Test creating a new user"""
        response = client.post(
            "/api/v1/users/profile",
            params={
                "user_id": "test_user_123",
                "name": "Test User",
                "role": "student",
                "interests": ["AI", "Biology"]
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["user_id"] == "test_user_123"

    def test_get_user_profile(self, client, test_db_session):
        """Test retrieving user profile"""
        # Create user first
        user = User(
            id="test_user_456",
            name="Test User",
            role=UserRole.STUDENT,
            interests=["AI", "ML"]
        )
        test_db_session.add(user)
        test_db_session.commit()

        # Get user
        response = client.get("/api/v1/users/test_user_456")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "test_user_456"
        assert data["name"] == "Test User"
        assert "AI" in data["interests"]

    def test_get_nonexistent_user(self, client):
        """Test getting a user that doesn't exist"""
        response = client.get("/api/v1/users/nonexistent")

        assert response.status_code == 404


class TestResearchEndpoints:
    """Tests for research data endpoints"""

    def test_list_research_papers_empty(self, client):
        """Test listing papers when database is empty"""
        response = client.get("/api/v1/research")

        assert response.status_code == 200
        data = response.json()
        assert data["total_count"] == 0
        assert data["items"] == []

    def test_list_research_papers_with_data(self, client, test_db_session):
        """Test listing papers with data"""
        # Add sample paper
        paper = ResearchPaper(
            url="https://test.com/paper1",
            title="Test Paper",
            university="KAIST",
            content_raw="This is test content"
        )
        test_db_session.add(paper)
        test_db_session.commit()

        response = client.get("/api/v1/research")

        assert response.status_code == 200
        data = response.json()
        assert data["total_count"] == 1
        assert len(data["items"]) == 1
        assert data["items"][0]["title"] == "Test Paper"

    def test_list_research_papers_with_filter(self, client, test_db_session):
        """Test filtering papers by university"""
        # Add multiple papers
        paper1 = ResearchPaper(
            url="https://test.com/paper1",
            title="KAIST Paper",
            university="KAIST",
            content_raw="Content"
        )
        paper2 = ResearchPaper(
            url="https://test.com/paper2",
            title="SNU Paper",
            university="SNU",
            content_raw="Content"
        )
        test_db_session.add_all([paper1, paper2])
        test_db_session.commit()

        response = client.get("/api/v1/research?university=KAIST")

        assert response.status_code == 200
        data = response.json()
        assert data["total_count"] == 1
        assert data["items"][0]["university"] == "KAIST"

    def test_get_research_analysis(self, client, test_db_session):
        """Test getting analysis for a paper"""
        # Add paper and analysis
        paper = ResearchPaper(
            url="https://test.com/paper1",
            title="Test Paper",
            university="KAIST",
            content_raw="Test content"
        )
        test_db_session.add(paper)
        test_db_session.flush()

        analysis = AnalysisResult(
            paper_id=paper.id,
            summary="This is a test summary",
            job_title="AI Engineer",
            salary_hint="100k+",
            related_companies=["Google", "Meta"],
            action_items={"subjects": ["Math"], "topic": "Linear Algebra"}
        )
        test_db_session.add(analysis)
        test_db_session.commit()

        response = client.get(f"/api/v1/research/{paper.id}/analysis")

        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Test Paper"
        assert data["analysis"]["easy_summary"] == "This is a test summary"
        assert data["analysis"]["career_path"]["job_title"] == "AI Engineer"


class TestReportEndpoints:
    """Tests for report generation endpoints"""

    def test_generate_report_no_interests(self, client, test_db_session):
        """Test report generation fails without user interests"""
        # Create user with no interests
        user = User(
            id="test_user",
            name="Test User",
            role=UserRole.STUDENT,
            interests=[]
        )
        test_db_session.add(user)
        test_db_session.commit()

        response = client.post(
            "/api/v1/reports/generate",
            params={"user_id": "test_user"}
        )

        assert response.status_code == 400

    def test_generate_report_with_user_interests(self, client, test_db_session):
        """Test report generation with user interests"""
        # Create user
        user = User(
            id="test_user",
            name="Test User",
            role=UserRole.STUDENT,
            interests=["AI"]
        )
        test_db_session.add(user)

        # Create paper with matching content
        paper = ResearchPaper(
            url="https://test.com/paper1",
            title="AI Research",
            university="KAIST",
            content_raw="This is about artificial intelligence"
        )
        test_db_session.add(paper)
        test_db_session.flush()

        # Add analysis
        analysis = AnalysisResult(
            paper_id=paper.id,
            summary="AI research summary",
            job_title="AI Engineer"
        )
        test_db_session.add(analysis)
        test_db_session.commit()

        response = client.post(
            "/api/v1/reports/generate",
            params={"user_id": "test_user"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "report_id" in data


class TestHealthCheck:
    """Tests for health check endpoint"""

    def test_health_check(self, client):
        """Test health check endpoint"""
        response = client.get("/health")

        assert response.status_code == 200
        assert response.json()["status"] == "ok"
