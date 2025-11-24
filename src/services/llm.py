from src.domain.schemas import ResearchPaper, AnalysisResult, CareerPath, ActionItem

class BaseLLM:
    def analyze(self, paper: ResearchPaper) -> AnalysisResult:
        raise NotImplementedError

class MockLLM(BaseLLM):
    def analyze(self, paper: ResearchPaper) -> AnalysisResult:
        # Mock logic to simulate LLM processing
        # In a real scenario, this would call OpenAI/Claude API with a prompt
        
        return AnalysisResult(
            title="스마트폰에서도 쌩쌩 돌아가는 AI, 어떻게 만들까?",
            research_summary="이 연구는 마치 무거운 배낭을 메고 달리는 육상 선수(기존 AI)에게 가벼운 운동복을 입혀주는 것과 같아요. 복잡한 계산을 줄여서 스마트폰 같은 작은 기기에서도 AI가 빠르게 작동하도록 만드는 기술입니다.",
            career_path=CareerPath(
                companies=["삼성전자 MX사업부", "네이버 클라우드", "Kakao Brain"],
                job_title="온디바이스 AI 엔지니어",
                avg_salary_hint="초봉 약 5,000만 원 이상"
            ),
            action_item=ActionItem(
                subjects=["수학(행렬)", "정보(알고리즘)"],
                research_topic="행렬 연산의 효율성을 높이는 알고리즘 탐구"
            )
        )
