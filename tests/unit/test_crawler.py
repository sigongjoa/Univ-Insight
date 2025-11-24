"""
Unit tests for Crawler services.
"""

import pytest
from src.services.crawler import MockCrawler


class TestMockCrawler:
    """Tests for MockCrawler"""

    def test_crawl_returns_research_paper(self):
        """Test that crawl returns a valid ResearchPaper"""
        crawler = MockCrawler()
        paper = crawler.crawl("https://example.com")

        assert paper is not None
        assert paper.title is not None
        assert paper.content is not None
        assert paper.source == "KAIST (Mock)"
        assert paper.url == "https://example.com"

    def test_crawl_paper_has_required_fields(self):
        """Test that returned paper has all required fields"""
        crawler = MockCrawler()
        paper = crawler.crawl("https://test.com")

        # Check all required fields are present
        assert hasattr(paper, 'source')
        assert hasattr(paper, 'title')
        assert hasattr(paper, 'content')
        assert hasattr(paper, 'date')
        assert hasattr(paper, 'url')

    def test_crawl_content_is_meaningful(self):
        """Test that crawled content is not empty"""
        crawler = MockCrawler()
        paper = crawler.crawl("https://test.com")

        assert len(paper.content) > 0
        assert "transformer" in paper.title.lower() or "mobile" in paper.content.lower()

    def test_multiple_crawls_are_independent(self):
        """Test that multiple crawls don't interfere with each other"""
        crawler = MockCrawler()

        paper1 = crawler.crawl("https://test1.com")
        paper2 = crawler.crawl("https://test2.com")

        assert paper1.url == "https://test1.com"
        assert paper2.url == "https://test2.com"
        assert paper1.id != paper2.id  # Should have different titles/content generated
