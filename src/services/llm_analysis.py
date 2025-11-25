"""
LLM 분석 서비스 (Phase 3)

주요 기능:
1. 논문 분석 및 요약
2. 진로 연결
3. 수행평가 제안
4. 구조화된 JSON 출력
"""

import logging
import json
import re
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class LLMAnalysisService:
    """LLM 분석 서비스"""

    def __init__(self, llm_provider: str = "ollama", model: str = "llama2"):
        """초기화"""
        self.llm_provider = llm_provider
        self.model = model
        logger.info(f"🚀 LLMAnalysisService 초기화 ({llm_provider}/{model})")

    async def analyze_research_paper(self, rag_prompt: str) -> Dict:
        """논문 분석"""
        # 실제 LLM 호출 시뮬레이션
        response = await self._call_llm(rag_prompt)

        # JSON 파싱
        analysis_result = self._parse_response(response)

        logger.info("✅ 논문 분석 완료")
        return analysis_result

    async def _call_llm(self, prompt: str) -> str:
        """LLM 호출"""
        if self.llm_provider == "ollama":
            return await self._call_ollama(prompt)
        elif self.llm_provider == "mock":
            return self._mock_response(prompt)
        else:
            raise ValueError(f"Unknown LLM provider: {self.llm_provider}")

    async def _call_ollama(self, prompt: str) -> str:
        """Ollama LLM 호출"""
        import subprocess

        try:
            result = subprocess.run(
                ["curl", "http://localhost:11434/api/generate"],
                input=json.dumps({
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                }).encode(),
                capture_output=True,
                text=True,
                timeout=60
            )

            response = json.loads(result.stdout)
            logger.info("✅ Ollama 응답 수신")
            return response.get("response", "")

        except Exception as e:
            logger.error(f"❌ Ollama 호출 실패: {e}")
            raise

    def _mock_response(self, prompt: str) -> str:
        """모의 응답"""
        return json.dumps({
            "title": "AI가 전기를 덜 먹게 만드는 방법",
            "research": "트랜스포머 모델은 ChatGPT의 핵심 기술입니다. 이 연구는 수십억 개의 매개변수를 가진 거대한 AI 모델을 더 효율적으로 작동시키는 기술을 제시합니다. 마치 큰 반도체 칩이 전력을 많이 소비하는 것처럼, AI 모델도 계산할 때마다 엄청난 에너지를 써요. 이 연구는 그 에너지를 줄이면서도 성능은 유지하는 방법을 찾았습니다.",
            "career_paths": [
                "NVIDIA - AI 칩 설계 엔지니어 - 1.2억원",
                "삼성전자 - AI 최적화 연구원 - 1억원",
                "Google - Machine Learning Engineer - 1.5억원"
            ],
            "action_items": [
                "수학(선형대수, 미적분)",
                "물리(에너지, 효율)",
                "수행평가: '생활 속 AI의 전력소비 분석'"
            ]
        })

    def _parse_response(self, response: str) -> Dict:
        """응답 파싱"""
        if not response:
            logger.warning("⚠️  빈 응답")
            return {}

        # JSON 추출 시도
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            json_str = json_match.group(0)
            return json.loads(json_str)

        logger.warning("⚠️  JSON 파싱 실패")
        return {
            "raw_response": response,
            "parse_error": True
        }

    async def extract_career_paths(self, analysis: Dict) -> list:
        """진로 정보 추출"""
        career_paths = analysis.get("career_paths", [])
        logger.info(f"📊 {len(career_paths)}개 진로 추출")
        return career_paths

    async def extract_action_items(self, analysis: Dict) -> list:
        """실행 항목 추출"""
        action_items = analysis.get("action_items", [])
        logger.info(f"📋 {len(action_items)}개 실행항목 추출")
        return action_items

    async def get_stats(self) -> Dict:
        """통계 조회"""
        return {
            "llm_provider": self.llm_provider,
            "model": self.model,
            "status": "operational",
        }
