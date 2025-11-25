import asyncio
import json
import logging
import re
from typing import List, Dict, Optional
import ollama
from crawl4ai import AsyncWebCrawler

logger = logging.getLogger(__name__)

class DeepCrawler:
    """
    학과 홈페이지를 방문하여 교수진 정보를 추출하는 정밀 크롤러.
    HTML 파싱 후 LLM을 사용하여 비정형 데이터에서 정보를 추출합니다.
    """

    def __init__(self, model_name: str = "qwen2.5:latest"):
        # qwen2.5 is good for Korean/English extraction, or use user's default
        self.model_name = model_name

    async def extract_professors_from_url(self, url: str) -> List[Dict]:
        """
        URL을 방문하여 교수진 목록을 추출합니다.
        """
        logger.info(f"🕷️ Deep Crawling: {url}")
        
        # 1. HTML Fetching (crawl4ai)
        html_content = await self._fetch_page(url)
        if not html_content:
            return []

        # 2. LLM Extraction
        # HTML이 너무 길 수 있으므로, 텍스트 위주로 변환하거나 청크로 나눠야 할 수도 있음.
        # crawl4ai가 markdown을 주므로 그것을 활용.
        professors = await self._extract_with_llm(html_content)
        
        return professors

    async def _fetch_page(self, url: str) -> Optional[str]:
        try:
            async with AsyncWebCrawler(verbose=True) as crawler:
                result = await crawler.arun(url=url)
                if result.success:
                    # 마크다운으로 변환된 텍스트가 LLM에게 더 친화적일 수 있음
                    logger.info(f"✅ Fetched {len(result.markdown)} chars from {url}")
                    return result.markdown 
                else:
                    logger.error(f"❌ Failed to fetch {url}: {result.error_message}")
                    return None
        except Exception as e:
            logger.error(f"Error fetching {url}: {e}")
            return None

    async def _extract_with_llm(self, content: str) -> List[Dict]:
        """
        LLM에게 콘텐츠를 주고 교수진 정보를 JSON으로 추출하도록 요청
        """
        # 토큰 제한을 고려하여 앞부분 10,000자 정도만 일단 테스트 (목록이 보통 앞/중간에 있음)
        # 실제로는 페이지네이션이나 스크롤 처리가 필요할 수 있음.
        truncated_content = content[:15000] 
        
        prompt = f"""
        You are a data extraction expert. 
        Extract professor information from the following text (markdown from a university department website).
        
        Target Fields:
        - name (Name of the professor)
        - email (Email address)
        - research_areas (List of research interests/keywords)
        - lab_name (Name of their laboratory, if mentioned)
        
        Output Format:
        JSON Array of objects. Example:
        [
            {{
                "name": "Kim Chul-soo",
                "email": "cs.kim@univ.ac.kr",
                "research_areas": ["AI", "Vision"],
                "lab_name": "Visual Computing Lab"
            }}
        ]
        
        If no professors are found, return [].
        Do NOT include any explanation, ONLY the JSON array.
        
        --- Content ---
        {truncated_content}
        """

        try:
            logger.info("🤖 Sending to LLM for extraction...")
            response = ollama.chat(model=self.model_name, messages=[
                {'role': 'user', 'content': prompt}
            ])
            
            response_content = response['message']['content']
            
            # JSON 파싱
            # LLM이 마크다운 코드 블록(```json ... ```)을 쓸 수 있으므로 제거
            clean_json = re.sub(r'```json\s*|\s*```', '', response_content).strip()
            
            data = json.loads(clean_json)
            logger.info(f"✅ Extracted {len(data)} professors.")
            return data
            
        except Exception as e:
            logger.error(f"LLM Extraction failed: {e}")
            logger.debug(f"LLM Response: {response_content if 'response_content' in locals() else 'N/A'}")
            return []
