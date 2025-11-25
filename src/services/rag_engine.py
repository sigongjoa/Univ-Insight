"""
RAG (Retrieval-Augmented Generation) 엔진 (Phase 3)

주요 기능:
1. 문서 검색
2. 컨텍스트 구성
3. LLM 프롬프트 생성
"""

import logging
from typing import List, Dict, Optional

from src.services.vector_store import ChromaVectorStore

logger = logging.getLogger(__name__)


class RAGEngine:
    """RAG 엔진"""

    def __init__(self, vector_store: ChromaVectorStore):
        """초기화"""
        self.vector_store = vector_store
        logger.info("🚀 RAGEngine 초기화")

    async def search_context(
        self,
        query: str,
        top_k: int = 5,
        similarity_threshold: float = 0.3,
    ) -> List[Dict]:
        """컨텍스트 검색

        Args:
            query: 검색 쿼리
            top_k: 상위 결과 개수
            similarity_threshold: 유사도 임계값 (낮을수록 유사)

        Returns:
            필터링된 검색 결과
        """
        results = await self.vector_store.search(query, top_k)

        # 유사도 필터링
        filtered = [r for r in results if r["distance"] < similarity_threshold]

        logger.info(f"🔍 검색: {len(filtered)}개 결과 (임계값: {similarity_threshold})")
        return filtered

    def build_rag_prompt(
        self,
        query: str,
        context_docs: List[Dict],
        system_role: str = "default",
    ) -> str:
        """RAG 프롬프트 구성

        Args:
            query: 사용자 질문
            context_docs: 검색된 컨텍스트 문서
            system_role: 시스템 역할 설정

        Returns:
            구성된 프롬프트
        """
        # 컨텍스트 텍스트 구성
        context_text = "\n\n".join([
            f"[{doc['title']}]\n{doc['content'][:500]}..."
            for doc in context_docs
        ])

        if system_role == "career_translator":
            prompt = f"""당신은 입시 컨설턴트이자 10년 차 공학 멘토입니다.
어려운 논문을 고등학생이 이해하기 쉽게 번역하고, 이를 그들의 진로(취업)와 연결해주는 것이 임무입니다.

[참고 자료]
{context_text}

[질문]
{query}

다음 4가지 섹션으로 구성된 리포트를 작성하세요. 톤앤매너는 친절하고 유머러스한 '해요체'입니다.

1. [Title]: 호기심을 자극하는 유튜브 썸네일 스타일 제목
2. [Research]: 중학생도 알기 쉽게 설명 + 왜 미래를 바꾸는지
3. [Career Path]: 관련 기업 3곳 + 직무명 + 초봉 수준
4. [Action Item]: 고등학교 때 집중해야 할 과목 + 수행평가 주제

JSON 형식으로 반환하세요:
{{
    "title": "...",
    "research": "...",
    "career_paths": ["회사명 - 직무 - 연봉"],
    "action_items": ["과목", "수행평가 주제"]
}}"""

        else:
            prompt = f"""주어진 컨텍스트를 바탕으로 다음 질문에 답하세요.

[컨텍스트]
{context_text}

[질문]
{query}

상세하고 정확한 답변을 제공하세요."""

        return prompt

    async def retrieve_and_rank(
        self,
        query: str,
        top_k: int = 5,
    ) -> Dict:
        """검색 및 순위 매기기

        Returns:
            {
                "query": "...",
                "context_docs": [...],
                "rag_prompt": "..."
            }
        """
        context_docs = await self.search_context(query, top_k)

        rag_prompt = self.build_rag_prompt(
            query,
            context_docs,
            system_role="career_translator"
        )

        return {
            "query": query,
            "context_docs": context_docs,
            "rag_prompt": rag_prompt,
            "context_count": len(context_docs),
        }

    async def get_stats(self) -> Dict:
        """통계 조회"""
        vector_stats = await self.vector_store.get_stats()
        return {
            "vector_store": vector_stats,
            "rag_engine": "operational",
        }
