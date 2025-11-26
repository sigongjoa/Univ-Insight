import json
import re
from typing import Optional
import ollama
from src.domain.schemas import ResearchPaper, AnalysisResult, CareerPath, ActionItem, DeepDive

class BaseLLM:
    def analyze(self, paper: ResearchPaper) -> AnalysisResult:
        raise NotImplementedError

class OllamaLLM(BaseLLM):
    def __init__(self, model: str = "qwen2:7b"):
        self.model = model

    def analyze(self, paper: ResearchPaper) -> AnalysisResult:
        print(f"   [OllamaLLM] Analyzing content with {self.model}...")

        # Use content_raw from the updated Pydantic schema
        content_to_analyze = paper.content_raw or paper.title

        # Construct the prompt
        prompt = f"""
        You are a career mentor for high school students.
        Your task is to analyze the following research paper content and create a report that is easy to understand but also provides depth for interested students.

        Input Content:
        Title: {paper.title}
        Content: {content_to_analyze[:2000]}... (truncated)
        
        Instructions:
        1. **Explanation**: Use simple analogies and everyday terms suitable for high school students.
        2. **Professionalism**: Put accurate 'academic terms' in parentheses after easy explanations.
        3. **Expansion**: Provide 'Deep Dive Keywords' and 'Reference Titles' for further study.
        
        Output Format:
        You MUST return ONLY a valid JSON object with the following structure. Do not add any markdown formatting or explanations outside the JSON.
        {{
            "topic_easy": "A catchy, easy-to-understand title (e.g., 'Connecting Eyes and Mouth of AI')",
            "topic_technical": "The exact technical term (e.g., 'Vision-Language Grounding')",
            "explanation": "Simple explanation using analogies...",
            "reference_link": "Google Scholar Search: [Key Term]",
            "deep_dive": {{
                "keywords": ["Keyword 1", "Keyword 2"],
                "recommendations": ["Paper/Book Title 1", "Paper/Book Title 2"],
                "related_concepts": ["High School Math Concept", "Basic Physics Concept"]
            }},
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

        response = ollama.chat(model=self.model, messages=[
            {
                'role': 'user',
                'content': prompt,
            },
        ])
        
        content = response['message']['content']
        
        # Attempt to clean and parse JSON
        json_match = re.search(r'\{.*\}', content, re.DOTALL)
        if not json_match:
            raise ValueError(f"No JSON found in Ollama response: {content[:200]}")

        json_str = json_match.group(0)
        data = json.loads(json_str)
        
        return AnalysisResult(
            paper_id=paper.id,
            topic_easy=data.get("topic_easy", "Untitled"),
            topic_technical=data.get("topic_technical", "Technical Topic"),
            explanation=data.get("explanation", "No explanation provided."),
            reference_link=data.get("reference_link", ""),
            deep_dive=DeepDive(
                keywords=data.get("deep_dive", {}).get("keywords", []),
                recommendations=data.get("deep_dive", {}).get("recommendations", []),
                related_concepts=data.get("deep_dive", {}).get("related_concepts", [])
            ),
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

class MockLLM(BaseLLM):
    def analyze(self, paper: ResearchPaper) -> AnalysisResult:
        # Mock logic to simulate LLM processing
        # Now accepts a paper object to correctly set the paper_id
        paper_id = paper.id if paper else "mock_paper_id"
        return AnalysisResult(
            paper_id=paper_id,
            topic_easy="인공지능의 눈과 입 연결하기",
            topic_technical="Vision-Language Grounding",
            explanation="우리가 강아지 사진을 보고 '귀여운 강아지가 잔디에 앉아 있네'라고 말하는 것처럼, 컴퓨터도 사진을 보고 문장으로 설명할 수 있게 만드는 기술입니다. 로봇이 사람의 말을 듣고 주변 물건을 찾아오는 데 사용됩니다.",
            reference_link="Google Scholar Search: Vision-Language Grounding",
            deep_dive=DeepDive(
                keywords=["Multimodal Learning", "Visual Question Answering (VQA)", "Cross-modal Attention"],
                recommendations=["Learning Transferable Visual Models From Natural Language Supervision (CLIP)", "ViLT: Vision-and-Language Transformer"],
                related_concepts=["조건부 확률(확률과 통계)", "벡터의 내적(기하와 벡터)"]
            ),
            career_path=CareerPath(
                companies=["Google DeepMind", "Naver Clova", "Kakao Brain"],
                job_title="Multimodal AI Researcher",
                avg_salary_hint="초봉 6,000만 원 이상"
            ),
            action_item=ActionItem(
                subjects=["수학(기하, 확률)", "정보(Python)"],
                research_topic="이미지 캡셔닝 모델의 원리 탐구 및 간단한 구현"
            )
        )
