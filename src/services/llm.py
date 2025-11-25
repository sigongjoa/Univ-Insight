import json
import re
from typing import Optional
import ollama
from src.domain.schemas import ResearchPaper, AnalysisResult, CareerPath, ActionItem

class BaseLLM:
    def analyze(self, paper: ResearchPaper) -> AnalysisResult:
        raise NotImplementedError

class OllamaLLM(BaseLLM):
    def __init__(self, model: str = "llama2:latest"):
        self.model = model

    def analyze(self, paper: ResearchPaper) -> AnalysisResult:
        print(f"   [OllamaLLM] Analyzing content with {self.model}...")

        # Use full_text or abstract, whichever is available
        content_to_analyze = paper.full_text or paper.abstract or paper.title

        # Construct the prompt
        prompt = f"""
        You are an expert education consultant and AI researcher.
        Your task is to analyze the following research paper content and translate it for high school students.

        Input Content:
        Title: {paper.title}
        Content: {content_to_analyze[:2000]}... (truncated)
        
        Instructions:
        1. Summarize the research in simple terms (middle school level).
        2. Suggest related career paths, companies, and job titles.
        3. Suggest high school subjects and a research topic related to this.
        
        Output Format:
        You MUST return ONLY a valid JSON object with the following structure. Do not add any markdown formatting or explanations outside the JSON.
        {{
            "title": "A catchy, easy-to-understand title for students",
            "research_summary": "Simple explanation of the research",
            "career_path": {{
                "companies": ["Company A", "Company B"],
                "job_title": "Job Title",
                "avg_salary_hint": "Salary hint (e.g. $100k+)"
            }},
            "action_item": {{
                "subjects": ["Subject 1", "Subject 2"],
                "research_topic": "A specific research topic for high school students"
            }}
        }}
        """

        try:
            response = ollama.chat(model=self.model, messages=[
                {
                    'role': 'user',
                    'content': prompt,
                },
            ])
            
            content = response['message']['content']
            
            # Attempt to clean and parse JSON
            # Sometimes LLMs add ```json ... ``` or other text
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                data = json.loads(json_str)
                
                return AnalysisResult(
                    title=data.get("title", "Untitled"),
                    research_summary=data.get("research_summary", "No summary provided."),
                    career_path=CareerPath(
                        companies=data.get("career_path", {}).get("companies", []),
                        job_title=data.get("career_path", {}).get("job_title", "Unknown"),
                        avg_salary_hint=data.get("career_path", {}).get("avg_salary_hint", "Unknown")
                    ),
                    action_item=ActionItem(
                        subjects=data.get("action_item", {}).get("subjects", []),
                        research_topic=data.get("action_item", {}).get("research_topic", "Unknown")
                    )
                )
            else:
                print(f"   [OllamaLLM] Failed to find JSON in response: {content[:100]}...")
                raise ValueError("No JSON found in response")

        except Exception as e:
            print(f"   [OllamaLLM] Error: {e}")
            # Fallback to a basic error result
            return AnalysisResult(
                title="Error during analysis",
                research_summary=f"Failed to analyze due to: {str(e)}",
                career_path=CareerPath(companies=[], job_title="Error", avg_salary_hint="Error"),
                action_item=ActionItem(subjects=[], research_topic="Error")
            )

class MockLLM(BaseLLM):
    def analyze(self, paper: ResearchPaper) -> AnalysisResult:
        # Mock logic to simulate LLM processing
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
