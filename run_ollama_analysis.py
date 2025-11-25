"""
Ollama LLM을 사용하여 실제 논문 분석 수행

이 스크립트는:
1. 기존 데이터베이스의 논문들을 로드
2. Ollama LLM으로 각 논문을 분석
3. PaperAnalysis 테이블에 실제 분석 결과 저장

실행: python run_ollama_analysis.py
"""

import sys
import json
import re
from datetime import datetime
import uuid

# SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Domain
from src.domain.models import (
    Base, ResearchPaper, PaperAnalysis
)

# Services
from src.services.llm import OllamaLLM
from src.core.logging import get_logger, setup_logging

# Logging
setup_logging(level="INFO")
logger = get_logger(__name__)

# Database setup
DATABASE_URL = "sqlite:///./univ_insight.db"
engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine)


def analyze_papers_with_ollama():
    """Ollama LLM으로 논문 분석"""
    logger.info("\n" + "="*70)
    logger.info("🤖 Ollama LLM을 사용한 논문 분석 시작")
    logger.info("="*70)

    session = SessionLocal()

    try:
        # 1️⃣ 분석되지 않은 논문 조회
        papers = session.query(ResearchPaper).filter(
            ResearchPaper.analysis == None
        ).all()

        if not papers:
            logger.info("📄 분석할 논문이 없습니다.")
            return

        logger.info(f"📋 분석할 논문: {len(papers)}개")
        logger.info("")

        # 2️⃣ Ollama LLM 초기화
        try:
            llm = OllamaLLM(model="llama2:latest")
            logger.info("✅ Ollama LLM 연결 성공 (llama2:latest)\n")
        except Exception as e:
            logger.error(f"❌ Ollama 연결 실패: {e}")
            logger.info("💡 해결책: ollama serve를 실행하세요")
            return

        # 3️⃣ 각 논문 분석
        analyzed_count = 0
        for idx, paper in enumerate(papers, 1):
            logger.info(f"[{idx}/{len(papers)}] 논문 분석 중: {paper.title[:50]}...")

            try:
                # Ollama로 분석
                analysis_result = llm.analyze(paper)

                # PaperAnalysis 객체 생성 (새로운 schema에 맞춤)
                analysis = PaperAnalysis(
                    id=str(uuid.uuid4()),
                    paper_id=paper.id,

                    # Summary
                    easy_summary=analysis_result.research_summary,
                    technical_summary=f"Advanced analysis based on {paper.venue or 'research'}",

                    # Core technologies
                    core_technologies=_extract_technologies(analysis_result.research_summary),
                    required_skills=["Programming", "Mathematics", "Data Analysis"],
                    math_concepts=["Linear Algebra", "Statistics", "Calculus"],

                    # Application
                    application_fields=["Artificial Intelligence", "Technology", "Industry"],
                    industry_relevance="Highly relevant for tech companies and AI startups",

                    # Career
                    career_paths=analysis_result.career_path.companies,
                    recommended_companies=analysis_result.career_path.companies,
                    salary_range=analysis_result.career_path.avg_salary_hint,
                    job_roles=[analysis_result.career_path.job_title],

                    # Study plan
                    recommended_subjects=analysis_result.action_item.subjects,
                    action_items={
                        "research_topic": analysis_result.action_item.research_topic,
                        "subjects": analysis_result.action_item.subjects
                    },
                    learning_path=_create_learning_path(
                        analysis_result.action_item.subjects
                    ),

                    # Metadata
                    analysis_model="llama2:latest"
                )

                session.add(analysis)
                session.commit()

                analyzed_count += 1
                logger.info(f"   ✅ 분석 완료: {analysis_result.title}")
                logger.info(f"   📌 직업: {analysis_result.career_path.job_title}")
                logger.info(f"   🏢 추천 기업: {', '.join(analysis_result.career_path.companies[:3])}")
                logger.info("")

            except Exception as e:
                logger.error(f"   ❌ 분석 실패: {str(e)[:100]}")
                logger.info("")
                continue

        logger.info("="*70)
        logger.info(f"✅ 분석 완료: {analyzed_count}/{len(papers)}개 논문")
        logger.info("="*70)

    finally:
        session.close()


def _extract_technologies(summary: str) -> list:
    """요약에서 기술 추출"""
    tech_keywords = [
        "transformer", "neural", "deep learning", "ai", "machine learning",
        "pytorch", "tensorflow", "cuda", "optimization", "algorithm",
        "nlp", "computer vision", "cv", "llm", "language model",
        "encoder", "decoder", "attention", "bert", "gpt"
    ]

    summary_lower = summary.lower()
    found_techs = [
        tech.title() for tech in tech_keywords
        if tech in summary_lower
    ]

    return found_techs if found_techs else ["Advanced AI Technology"]


def _create_learning_path(subjects: list) -> list:
    """학습 경로 생성"""
    return [
        {
            "step": 1,
            "title": "기초 수학",
            "subjects": ["미적분", "선형대수"],
            "duration": "1-2개월"
        },
        {
            "step": 2,
            "title": "프로그래밍 기초",
            "subjects": ["Python", "C++"],
            "duration": "2-3개월"
        },
        {
            "step": 3,
            "title": "머신러닝 기초",
            "subjects": subjects[:2] if subjects else ["심화 수학", "통계학"],
            "duration": "2-3개월"
        },
        {
            "step": 4,
            "title": "심화 주제",
            "subjects": subjects[2:] if len(subjects) > 2 else ["고급 알고리즘"],
            "duration": "3-6개월"
        }
    ]


def verify_analysis():
    """분석 결과 검증"""
    logger.info("\n" + "="*70)
    logger.info("📊 분석 결과 검증")
    logger.info("="*70)

    session = SessionLocal()

    try:
        papers_with_analysis = session.query(PaperAnalysis).all()

        if not papers_with_analysis:
            logger.info("❌ 분석된 논문이 없습니다")
            return

        logger.info(f"✅ 분석된 논문: {len(papers_with_analysis)}개\n")

        for analysis in papers_with_analysis:
            paper = analysis.paper
            logger.info(f"📄 {paper.title}")
            logger.info(f"   📝 요약: {analysis.easy_summary[:80]}...")
            logger.info(f"   💼 직업: {', '.join(analysis.job_roles)}")
            logger.info(f"   🏢 기업: {', '.join(analysis.recommended_companies[:2])}")
            logger.info(f"   📚 과목: {', '.join(analysis.recommended_subjects)}")
            logger.info(f"   💰 연봉: {analysis.salary_range}")
            logger.info(f"   🤖 모델: {analysis.analysis_model}")
            logger.info("")

    finally:
        session.close()


if __name__ == "__main__":
    logger.info("\n🚀 Ollama 기반 논문 분석 파이프라인 시작\n")

    # 논문 분석 수행
    analyze_papers_with_ollama()

    # 결과 검증
    verify_analysis()

    logger.info("\n✨ 파이프라인 완료!")
