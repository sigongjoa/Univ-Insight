"""
추천 엔진 (Phase 3)

주요 기능:
1. 진로 추천
2. 대학 플랜 B 제안
3. 관련 주제 클러스터링
"""

import logging
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)


class RecommendationEngine:
    """추천 엔진"""

    # 대학별 연구 주제 매핑 (예시)
    UNIVERSITY_RESEARCH_MAP = {
        "AI/머신러닝": [
            {"university": "서울대학교", "department": "컴퓨터학과", "lab": "AI 연구실"},
            {"university": "KAIST", "department": "전자공학과", "lab": "AI 칩 연구실"},
            {"university": "고려대학교", "department": "컴퓨터학과", "lab": "머신러닝 센터"},
            {"university": "한양대학교", "department": "컴퓨터학과", "lab": "딥러닝 랩"},
            {"university": "성균관대학교", "department": "소프트웨어학과", "lab": "AI 응용 연구실"},
        ],
        "자율주행": [
            {"university": "서울대학교", "department": "기계항공공학과", "lab": "로봇/자동차 연구실"},
            {"university": "KAIST", "department": "전기공학과", "lab": "자율주행 센터"},
            {"university": "한국교통대학교", "department": "자동차학과", "lab": "자율주행 연구실"},
            {"university": "홍익대학교", "department": "기계공학과", "lab": "모빌리티 랩"},
        ],
        "반도체/칩 설계": [
            {"university": "KAIST", "department": "전자공학과", "lab": "칩 설계 연구실"},
            {"university": "서울대학교", "department": "전기정보공학과", "lab": "반도체 랩"},
            {"university": "성균관대학교", "department": "전자공학과", "lab": "반도체 설계 센터"},
            {"university": "홍익대학교", "department": "전자정보통신공학과", "lab": "칩 설계실"},
        ],
        "생명공학/바이오": [
            {"university": "서울대학교", "department": "생명과학부", "lab": "생물공학 연구실"},
            {"university": "KAIST", "department": "생명화학공학과", "lab": "바이오 연구센터"},
            {"university": "이화여자대학교", "department": "생명과학과", "lab": "생명공학 랩"},
            {"university": "연세대학교", "department": "의료정보학과", "lab": "바이오정보 연구실"},
        ],
    }

    # 기업 정보 (산업별)
    COMPANY_MAP = {
        "AI/머신러닝": [
            {"company": "Google", "job": "AI 엔지니어", "salary": "1.5~2.5억원"},
            {"company": "Meta", "job": "머신러닝 엔지니어", "salary": "1.2~2억원"},
            {"company": "Microsoft", "job": "AI 연구원", "salary": "1.3~2.2억원"},
            {"company": "Naver", "job": "AI 개발자", "salary": "1~1.5억원"},
            {"company": "Kakao", "job": "머신러닝 엔지니어", "salary": "0.9~1.4억원"},
        ],
        "자율주행": [
            {"company": "Tesla", "job": "자율주행 엔지니어", "salary": "1.5~2.5억원"},
            {"company": "Waymo", "job": "자율주행 알고리즘 엔지니어", "salary": "1.5~2.3억원"},
            {"company": "현대/기아", "job": "자율주행 개발자", "salary": "0.9~1.5억원"},
            {"company": "BMW", "job": "자율주행 시스템 엔지니어", "salary": "1.1~1.8억원"},
        ],
        "반도체/칩 설계": [
            {"company": "NVIDIA", "job": "칩 설계 엔지니어", "salary": "1.2~2억원"},
            {"company": "Samsung", "job": "칩 설계 연구원", "salary": "0.8~1.4억원"},
            {"company": "SK하이닉스", "job": "반도체 설계자", "salary": "0.8~1.3억원"},
            {"company": "Intel", "job": "CPU 설계 엔지니어", "salary": "1.3~2.1억원"},
            {"company": "ARM", "job": "아키텍처 디자이너", "salary": "1.2~1.9억원"},
        ],
    }

    def __init__(self):
        """초기화"""
        logger.info("🚀 RecommendationEngine 초기화")

    async def get_career_recommendations(
        self,
        research_topic: str,
        top_n: int = 5,
    ) -> List[Dict]:
        """진로 추천"""
        # 주제와 일치하는 회사 찾기
        for topic, companies in self.COMPANY_MAP.items():
            if any(keyword in research_topic for keyword in topic.split("/")):
                recommendations = companies[:top_n]
                logger.info(f"💼 {len(recommendations)}개 진로 추천")
                return recommendations

        # 기본값
        logger.warning("⚠️  정확한 주제 매칭 실패, 기본 추천 제공")
        return self.COMPANY_MAP.get("AI/머신러닝", [])[:top_n]

    async def get_plan_b_universities(
        self,
        research_topic: str,
        exclude_university: str = "",
    ) -> List[Dict]:
        """플랜 B 대학 제안"""
        # 주제와 일치하는 대학 찾기
        for topic, universities in self.UNIVERSITY_RESEARCH_MAP.items():
            if any(keyword in research_topic for keyword in topic.split("/")):
                # 제외 대학 제거
                if exclude_university:
                    plan_b = [
                        u for u in universities
                        if u["university"] != exclude_university
                    ]
                else:
                    plan_b = universities

                logger.info(f"🎓 {len(plan_b)}개 플랜 B 대학 제안")
                return plan_b

        # 기본값
        logger.warning("⚠️  정확한 주제 매칭 실패, 기본 대학 제공")
        return list(self.UNIVERSITY_RESEARCH_MAP.values())[0]

    async def cluster_related_topics(
        self,
        research_topic: str,
    ) -> List[str]:
        """관련 주제 클러스터링"""
        # 간단한 키워드 기반 클러스터링
        related_topics = []

        if "AI" in research_topic or "머신" in research_topic:
            related_topics = [
                "딥러닝", "신경망", "자연어처리", "컴퓨터 비전", "강화학습"
            ]
        elif "자율주행" in research_topic or "자동" in research_topic:
            related_topics = [
                "센서 기술", "라이다", "이미지 인식", "경로 계획", "제어 시스템"
            ]
        elif "반도체" in research_topic or "칩" in research_topic:
            related_topics = [
                "회로 설계", "신호 처리", "아키텍처", "전력 최적화", "캐시"
            ]
        elif "바이오" in research_topic or "생명" in research_topic:
            related_topics = [
                "유전자", "단백질", "세포 생물학", "약학", "의료 기술"
            ]
        else:
            related_topics = [
                "기본 연구", "응용 기술", "산업 응용", "파급 효과"
            ]

        logger.info(f"🔗 {len(related_topics)}개 관련 주제 클러스터링")
        return related_topics

    async def generate_student_roadmap(
        self,
        research_topic: str,
        student_interests: Optional[List[str]] = None,
    ) -> Dict:
        """학생 학습 로드맵 생성"""
        careers = await self.get_career_recommendations(research_topic, top_n=3)
        plan_b = await self.get_plan_b_universities(research_topic)
        topics = await self.cluster_related_topics(research_topic)

        roadmap = {
            "research_topic": research_topic,
            "career_paths": careers,
            "plan_b_universities": plan_b[:3],
            "related_topics": topics[:5],
            "action_items": [
                "해당 분야의 고등학교 교과목 우선 학습",
                "논문 요약 및 분석 능력 개발",
                "프로젝트 또는 수행평가로 실제 적용 경험",
                "관련 온라인 강좌 수강 (Coursera, MIT OpenCourseWare 등)",
                "멘토 찾기 또는 대학 교수님께 메일 드리기"
            ],
            "timeline": {
                "고1": "기초 과목 집중 + 관심 분야 탐색",
                "고2": "심화 공부 + 수행평가/논문 탐구",
                "고3": "수능 준비 + 대학 입시 준비"
            }
        }

        logger.info("📚 학생 로드맵 생성 완료")
        return roadmap

    async def get_stats(self) -> Dict:
        """통계 조회"""
        return {
            "universities_count": sum(
                len(unis) for unis in self.UNIVERSITY_RESEARCH_MAP.values()
            ),
            "companies_count": sum(
                len(comps) for comps in self.COMPANY_MAP.values()
            ),
            "recommendation_engine": "operational",
        }
