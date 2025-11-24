"""
Unit tests for LLM services.
"""

import pytest
from src.services.llm import MockLLM
from src.domain.schemas import ResearchPaper


class TestMockLLM:
    """Tests for MockLLM"""

    @pytest.fixture
    def sample_paper(self):
        """Create a sample research paper"""
        return ResearchPaper(
            source="KAIST",
            title="Test Paper on AI",
            content="This is a test paper about artificial intelligence",
            date="2024-11-24",
            url="https://test.com"
        )

    def test_analyze_returns_analysis_result(self, sample_paper):
        """Test that analyze returns a valid AnalysisResult"""
        llm = MockLLM()
        result = llm.analyze(sample_paper)

        assert result is not None
        assert result.title is not None
        assert result.research_summary is not None

    def test_analysis_has_career_path(self, sample_paper):
        """Test that analysis includes career path information"""
        llm = MockLLM()
        result = llm.analyze(sample_paper)

        assert result.career_path is not None
        assert result.career_path.companies is not None
        assert len(result.career_path.companies) > 0
        assert result.career_path.job_title is not None

    def test_analysis_has_action_items(self, sample_paper):
        """Test that analysis includes action items"""
        llm = MockLLM()
        result = llm.analyze(sample_paper)

        assert result.action_item is not None
        assert result.action_item.subjects is not None
        assert len(result.action_item.subjects) > 0
        assert result.action_item.research_topic is not None

    def test_analysis_is_meaningful(self, sample_paper):
        """Test that analysis content is meaningful"""
        llm = MockLLM()
        result = llm.analyze(sample_paper)

        # Check that summary is not empty and somewhat relevant
        assert len(result.research_summary) > 10
        assert len(result.title) > 5
        assert result.research_summary != "Error during analysis"

    def test_multiple_analyses_produce_consistent_results(self):
        """Test that mock LLM produces consistent results"""
        llm = MockLLM()

        paper = ResearchPaper(
            source="KAIST",
            title="Test Paper",
            content="Content",
            date="2024-11-24",
            url="https://test.com"
        )

        result1 = llm.analyze(paper)
        result2 = llm.analyze(paper)

        # Results should be consistent for mock
        assert result1.title == result2.title
        assert result1.job_title == result2.job_title
