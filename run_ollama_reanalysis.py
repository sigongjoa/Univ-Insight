"""
Ollama LLM으로 논문을 다시 분석하는 스크립트

기존 분석을 삭제하고 실제 Ollama LLM으로 다시 분석합니다.

실행: python run_ollama_reanalysis.py
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


def clear_existing_analysis():
    """기존 분석 결과 삭제"""
    logger.info("\n" + "="*70)
    logger.info("🗑️ 기존 분석 결과 삭제 중...")
    logger.info("="*70)

    session = SessionLocal()

    try:
        count = session.query(PaperAnalysis).delete()
        session.commit()
        logger.info(f"✅ {count}개의 기존 분석 결과 삭제\n")
    finally:
        session.close()


def analyze_papers_with_ollama():
    """Ollama LLM으로 논문 분석"""
    logger.info("="*70)
    logger.info("🤖 Ollama LLM을 사용한 논문 분석 시작")
    logger.info("="*70)

    session = SessionLocal()

    try:
        # 1️⃣ 모든 논문 조회
        papers = session.query(ResearchPaper).all()

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
            logger.info("💡 해결책: ollama serve를 다른 터미널에서 실행하세요\n")
            return

        # 3️⃣ 각 논문 분석
        analyzed_count = 0
        failed_count = 0

        for idx, paper in enumerate(papers, 1):
            logger.info(f"[{idx}/{len(papers)}] 분석 중: {paper.title[:50]}...")

            try:
                # Ollama로 분석 (실제 LLM 호출)
                logger.info(f"   📞 Ollama 호출 중...")
                analysis_result = llm.analyze(paper)

                # PaperAnalysis 객체 생성
                analysis = PaperAnalysis(
                    id=str(uuid.uuid4()),
                    paper_id=paper.id,

                    # Summary
                    easy_summary=analysis_result.research_summary,
                    technical_summary=f"Technical analysis of {paper.title}",

                    # Core technologies
                    core_technologies=_extract_technologies(analysis_result.research_summary),
                    required_skills=["Programming", "Mathematics", "Data Analysis", "System Design"],
                    math_concepts=["Linear Algebra", "Statistics", "Calculus", "Probability"],

                    # Application
                    application_fields=["Technology", "Industry Applications", "Research"],
                    industry_relevance=_generate_industry_relevance(
                        paper.title,
                        analysis_result.career_path.companies
                    ),

                    # Career
                    career_paths=analysis_result.career_path.companies,
                    recommended_companies=analysis_result.career_path.companies,
                    salary_range=analysis_result.career_path.avg_salary_hint,
                    job_roles=[analysis_result.career_path.job_title] if analysis_result.career_path.job_title else ["AI Engineer"],

                    # Study plan
                    recommended_subjects=analysis_result.action_item.subjects if analysis_result.action_item.subjects else ["Advanced Mathematics"],
                    action_items={
                        "research_topic": analysis_result.action_item.research_topic if analysis_result.action_item.research_topic else "Research continuation",
                        "subjects": analysis_result.action_item.subjects if analysis_result.action_item.subjects else []
                    },
                    learning_path=_create_learning_path(
                        analysis_result.action_item.subjects if analysis_result.action_item.subjects else ["Advanced Topics"]
                    ),

                    # Metadata
                    analysis_model="llama2:latest"
                )

                session.add(analysis)
                session.commit()

                analyzed_count += 1

                # 결과 출력
                logger.info(f"   ✅ 분석 완료!")
                logger.info(f"   📌 직업: {analysis_result.career_path.job_title}")
                logger.info(f"   🏢 회사: {', '.join(analysis_result.career_path.companies[:2])}")
                logger.info(f"   📝 요약: {analysis_result.research_summary[:60]}...")
                logger.info("")

            except Exception as e:
                failed_count += 1
                logger.error(f"   ❌ 분석 실패: {str(e)[:100]}")
                logger.info("")
                # 실패한 경우도 계속 진행
                continue

        logger.info("="*70)
        logger.info(f"✅ 분석 완료: {analyzed_count}개 성공, {failed_count}개 실패")
        logger.info("="*70)

        # 최종 통계
        total_analysis = session.query(PaperAnalysis).count()
        logger.info(f"\n📊 데이터베이스 현황:")
        logger.info(f"   - 총 논문: {session.query(ResearchPaper).count()}개")
        logger.info(f"   - 분석된 논문: {total_analysis}개")
        logger.info(f"   - 분석 완료율: {(total_analysis/len(papers)*100):.1f}%\n")

    finally:
        session.close()


def _extract_technologies(summary: str) -> list:
    """요약에서 기술 추출"""
    tech_keywords = [
        "transformer", "neural", "deep learning", "ai", "machine learning",
        "pytorch", "tensorflow", "cuda", "optimization", "algorithm",
        "nlp", "computer vision", "cv", "llm", "language model",
        "encoder", "decoder", "attention", "bert", "gpt", "distributed",
        "cloud", "system", "network", "database", "compiler"
    ]

    summary_lower = summary.lower()
    found_techs = [
        tech.title() for tech in tech_keywords
        if tech in summary_lower
    ]

    if not found_techs:
        found_techs = ["Advanced Technology"]

    return found_techs[:5]  # 최대 5개


def _generate_industry_relevance(title: str, companies: list) -> str:
    """산업 관련성 생성"""
    if not companies:
        return "Relevant for technology sector and AI industry"

    return f"Highly relevant for {', '.join(companies[:2])} and similar technology companies"


def _create_learning_path(subjects: list) -> list:
    """학습 경로 생성"""
    base_path = [
        {
            "step": 1,
            "title": "기초 이론",
            "subjects": ["미적분", "선형대수", "확률통계"],
            "duration": "1-2개월",
            "focus": "Mathematical foundations"
        },
        {
            "step": 2,
            "title": "프로그래밍 기초",
            "subjects": ["Python", "C++", "Java"],
            "duration": "2-3개월",
            "focus": "Programming fundamentals"
        },
        {
            "step": 3,
            "title": "전공 기초",
            "subjects": subjects[:3] if subjects else ["Advanced Mathematics", "Algorithms"],
            "duration": "2-3개월",
            "focus": "Domain-specific knowledge"
        },
        {
            "step": 4,
            "title": "심화 학습",
            "subjects": subjects[3:] if len(subjects) > 3 else ["Research Topics"],
            "duration": "3-6개월",
            "focus": "Advanced topics and research"
        }
    ]

    return base_path


def verify_analysis():
    """분석 결과 검증 및 출력"""
    logger.info("\n" + "="*70)
    logger.info("📊 분석 결과 검증")
    logger.info("="*70 + "\n")

    session = SessionLocal()

    try:
        papers_with_analysis = session.query(PaperAnalysis).all()

        if not papers_with_analysis:
            logger.info("❌ 분석된 논문이 없습니다\n")
            return

        logger.info(f"✅ 총 {len(papers_with_analysis)}개 논문 분석 완료\n")

        for idx, analysis in enumerate(papers_with_analysis, 1):
            paper = analysis.paper
            logger.info(f"[{idx}] {paper.title}")
            logger.info(f"   📝 요약: {analysis.easy_summary[:80]}...")
            logger.info(f"   💼 직업: {', '.join(analysis.job_roles)}")
            logger.info(f"   🏢 기업: {', '.join(analysis.recommended_companies[:2])}")
            logger.info(f"   📚 과목: {', '.join(analysis.recommended_subjects[:3])}")
            logger.info(f"   💰 연봉: {analysis.salary_range}")
            logger.info(f"   🤖 모델: {analysis.analysis_model}")
            logger.info("")

    finally:
        session.close()


if __name__ == "__main__":
    logger.info("\n" + "="*70)
    logger.info("🚀 Ollama LLM 기반 논문 재분석 파이프라인")
    logger.info("="*70)

    # 기존 분석 삭제
    clear_existing_analysis()

    # 논문 분석 수행
    analyze_papers_with_ollama()

    # 결과 검증
    verify_analysis()

    logger.info("="*70)
    logger.info("✨ 파이프라인 완료!")
    logger.info("="*70 + "\n")
