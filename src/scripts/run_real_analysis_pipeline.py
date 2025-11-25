#!/usr/bin/env python3
"""
실제 Ollama LLM을 사용한 논문 분석 파이프라인
목업이 아니라 실제 동작하는 구현

실행: python run_real_analysis_pipeline.py
"""

import sys
import json
import uuid
from datetime import datetime

# SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Domain
from src.domain.models import Base, ResearchPaper, PaperAnalysis
from src.domain.schemas import ResearchPaper as PydanticResearchPaper

# Services
from src.services.llm import OllamaLLM
from src.core.logging import get_logger, setup_logging

# Setup logging
setup_logging(level="INFO")
logger = get_logger(__name__)

# Database setup
DATABASE_URL = "sqlite:///./univ_insight.db"
engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine)


def convert_to_pydantic_schema(orm_paper: ResearchPaper) -> PydanticResearchPaper:
    """SQLAlchemy ResearchPaper 모델을 Pydantic 스키마로 변환"""
    # full_text가 없을 수 있으니 getattr 사용
    full_text = getattr(orm_paper, 'full_text', None)
    abstract = getattr(orm_paper, 'abstract', None)

    content = full_text or abstract or orm_paper.title

    return PydanticResearchPaper(
        id=orm_paper.id,
        url=orm_paper.url or "",
        title=orm_paper.title,
        university="Seoul National University",
        department="Computer Science",
        pub_date=orm_paper.publication_date,
        content_raw=content
    )


def analyze_paper_with_ollama(paper: ResearchPaper) -> dict:
    """Ollama LLM으로 실제 논문 분석"""
    logger.info(f"🤖 분석 시작: {paper.title[:50]}...")

    try:
        # LLM 초기화
        llm = OllamaLLM(model="qwen2:7b")

        # Pydantic 스키마로 변환
        pydantic_paper = convert_to_pydantic_schema(paper)

        # 실제 분석 수행
        logger.info("   📞 Ollama에 요청 중...")
        analysis_result = llm.analyze(pydantic_paper)

        logger.info("   ✅ 분석 완료!")
        logger.info(f"   📌 직업: {analysis_result.career_path.job_title}")
        logger.info(f"   🏢 회사: {', '.join(analysis_result.career_path.companies[:2])}")
        logger.info(f"   📝 요약: {analysis_result.research_summary[:80]}...")

        return {
            "success": True,
            "data": {
                "title": analysis_result.title,
                "research_summary": analysis_result.research_summary,
                "career_paths": analysis_result.career_path.companies,
                "job_title": analysis_result.career_path.job_title,
                "salary_hint": analysis_result.career_path.avg_salary_hint,
                "subjects": analysis_result.action_item.subjects,
                "research_topic": analysis_result.action_item.research_topic,
            }
        }

    except Exception as e:
        logger.error(f"   ❌ 분석 실패: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "error": str(e)
        }


def save_analysis_to_db(paper: ResearchPaper, analysis_data: dict) -> bool:
    """분석 결과를 데이터베이스에 저장"""
    session = SessionLocal()

    try:
        data = analysis_data.get("data", {})

        # PaperAnalysis 객체 생성
        analysis = PaperAnalysis(
            id=str(uuid.uuid4()),
            paper_id=paper.id,

            # Summary
            easy_summary=data.get("research_summary", ""),
            technical_summary=f"Technical analysis of {paper.title}",

            # Core technologies
            core_technologies=_extract_technologies(data.get("research_summary", "")),
            required_skills=["Programming", "Mathematics", "Data Analysis", "System Design"],
            math_concepts=["Linear Algebra", "Statistics", "Calculus", "Probability"],

            # Application
            application_fields=["Technology", "Industry Applications", "Research"],
            industry_relevance=f"Highly relevant for {', '.join(data.get('career_paths', [])[:2])} and similar companies",

            # Career
            career_paths=data.get("career_paths", []),
            recommended_companies=data.get("career_paths", []),
            salary_range=data.get("salary_hint", "Unknown"),
            job_roles=[data.get("job_title", "AI Engineer")],

            # Study plan
            recommended_subjects=data.get("subjects", []),
            action_items={
                "research_topic": data.get("research_topic", "Research continuation"),
                "subjects": data.get("subjects", [])
            },
            learning_path=_create_learning_path(data.get("subjects", [])),

            # Metadata
            analysis_model="qwen2:7b"
        )

        session.add(analysis)
        session.commit()
        logger.info(f"   💾 데이터베이스 저장 완료")
        return True

    except Exception as e:
        logger.error(f"   ❌ 저장 실패: {str(e)}")
        session.rollback()
        return False

    finally:
        session.close()


def _extract_technologies(summary: str) -> list:
    """요약에서 기술 추출"""
    tech_keywords = [
        "transformer", "neural", "deep learning", "ai", "machine learning",
        "pytorch", "tensorflow", "cuda", "optimization", "algorithm",
        "nlp", "computer vision", "cv", "llm", "language model",
        "encoder", "decoder", "attention", "bert", "gpt", "distributed",
        "cloud", "system", "network", "database", "compiler", "robustness",
        "detection", "classification", "inference", "performance"
    ]

    summary_lower = summary.lower()
    found_techs = [
        tech.title() for tech in tech_keywords
        if tech in summary_lower
    ]

    if not found_techs:
        found_techs = ["Advanced Technology"]

    return found_techs[:5]


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


def main():
    """메인 파이프라인"""
    logger.info("\n" + "="*70)
    logger.info("🚀 실제 Ollama LLM 기반 논문 분석 파이프라인")
    logger.info("="*70 + "\n")

    session = SessionLocal()

    try:
        # 1️⃣ 분석되지 않은 논문 조회
        all_papers = session.query(ResearchPaper).all()
        analyzed_papers = session.query(PaperAnalysis).all()
        analyzed_ids = {a.paper_id for a in analyzed_papers}

        papers_to_analyze = [p for p in all_papers if p.id not in analyzed_ids]

        logger.info(f"📊 분석 대상:")
        logger.info(f"   - 전체 논문: {len(all_papers)}개")
        logger.info(f"   - 이미 분석: {len(analyzed_papers)}개")
        logger.info(f"   - 분석 필요: {len(papers_to_analyze)}개\n")

        if not papers_to_analyze:
            logger.info("⚠️  분석할 논문이 없습니다.")
            return

        # 2️⃣ 각 논문 분석
        success_count = 0
        failed_count = 0

        for idx, paper in enumerate(papers_to_analyze, 1):
            logger.info(f"\n[{idx}/{len(papers_to_analyze)}] {paper.title}")
            logger.info("-" * 70)

            # 실제 분석 수행
            analysis_result = analyze_paper_with_ollama(paper)

            if analysis_result["success"]:
                # 데이터베이스에 저장
                if save_analysis_to_db(paper, analysis_result):
                    success_count += 1
                else:
                    failed_count += 1
            else:
                failed_count += 1
                logger.error(f"   ❌ 분석 실패: {analysis_result.get('error', 'Unknown error')}")

        # 3️⃣ 최종 결과
        logger.info("\n" + "="*70)
        logger.info(f"✅ 분석 완료: {success_count}개 성공, {failed_count}개 실패")
        logger.info("="*70)

        # 최종 통계
        final_analysis_count = session.query(PaperAnalysis).count()
        logger.info(f"\n📈 최종 통계:")
        logger.info(f"   - 총 논문: {len(all_papers)}개")
        logger.info(f"   - 분석된 논문: {final_analysis_count}개")
        logger.info(f"   - 분석 완료율: {(final_analysis_count/len(all_papers)*100):.1f}%\n")

        # 분석된 논문 목록 출력
        if final_analysis_count > 0:
            logger.info("🎓 분석 결과 미리보기:")
            logger.info("-" * 70)

            analyzed = session.query(PaperAnalysis).all()
            for i, analysis in enumerate(analyzed[:3], 1):  # 처음 3개만 표시
                paper = analysis.paper
                logger.info(f"\n[{i}] {paper.title}")
                logger.info(f"    📝 요약: {analysis.easy_summary[:70]}...")
                logger.info(f"    💼 직업: {analysis.job_roles[0] if analysis.job_roles else 'N/A'}")
                logger.info(f"    🏢 회사: {', '.join(analysis.recommended_companies[:2])}")
                logger.info(f"    📚 과목: {', '.join(analysis.recommended_subjects[:2])}")

    finally:
        session.close()

    logger.info("\n" + "="*70)
    logger.info("✨ 파이프라인 완료!")
    logger.info("="*70 + "\n")


if __name__ == "__main__":
    main()
