from src.domain.schemas import ResearchPaper

class BaseCrawler:
    def crawl(self, url: str) -> ResearchPaper:
        raise NotImplementedError

class MockCrawler(BaseCrawler):
    def crawl(self, url: str) -> ResearchPaper:
        # Mock data representing a crawled paper
        return ResearchPaper(
            source="KAIST",
            title="Efficient Transformer Architectures for Mobile Devices",
            content="""
            Abstract:
            Recent advances in Transformer models have led to significant improvements in NLP tasks. 
            However, their high computational cost makes them difficult to deploy on mobile devices. 
            In this paper, we propose a novel architecture that reduces parameter count by 40% while maintaining 95% of the accuracy.
            We utilize depth-wise separable convolutions and a modified attention mechanism...
            """,
            date="2024-05-20",
            url=url
        )
