#!/usr/bin/env python3
"""
Phase 2 크롤러 파이프라인

구조:
1. API에서 대학/학과 정보 조회
2. crawl4ai 기반 범용 크롤러로 각 대학의 교수/연구실 정보 수집
3. 수집된 논문에 Ollama 분석 적용 (배치)

실행: python run_phase2_crawler_pipeline.py
"""

import sys
import asyncio
import logging
from typing import List, Dict

# Domain
from src.domain.models import (
    Base,
    University,
    College,
    Department,
    Professor,
    Laboratory,
    ResearchPaper,
    PaperAnalysis
)

# Services
from src.services.career_api_client import CareerAPIClient
from src.services.generic_university_crawler import GenericUniversityCrawler
from src.core.logging import get_logger, setup_logging

# Database
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Setup logging
setup_logging(level="INFO")
logger = get_logger(__name__)

# Database setup
DATABASE_URL = "sqlite:///./univ_insight.db"
engine = create_engine(DATABASE_URL, echo=False)
Base.metadata.create_all(engine)
SessionLocal = sessionmaker(bind=engine)


async def main():
    """Phase 2 크롤러 파이프라인 메인 실행"""

    logger.info("\n" + "="*70)
    logger.info("🚀 Phase 2 크롤러 파이프라인 시작")
    logger.info("="*70 + "\n")

    session = SessionLocal()
    crawler = GenericUniversityCrawler()

    try:
        # =============== 1단계: API에서 대학 정보 수집 ===============
        logger.info("📊 [1단계] API에서 대학/학과 정보 수집")
        logger.info("-" * 70)

        api_client = CareerAPIClient()

        # 대학 목록 조회
        universities_data = api_client.get_universities()
        logger.info(f"✅ {universities_data['total']}개 대학 정보 조회 완료\n")

        universities_to_process = []

        for uni_data in universities_data["universities"]:
            try:
                # DB에 이미 존재하는지 확인
                existing = session.query(University).filter_by(id=uni_data["id"]).first()
                if existing:
                    logger.info(f"   ⏭️  {uni_data['name_ko']} (이미 존재)")
                    universities_to_process.append(existing)
                    continue

                # 새 대학 추가
                university = University(
                    id=uni_data["id"],
                    name=uni_data["name"],
                    name_ko=uni_data.get("name_ko", uni_data["name"]),
                    location=uni_data.get("location", ""),
                    url=uni_data.get("url", ""),
                    established_year=uni_data.get("established_year")
                )
                session.add(university)
                session.flush()  # 즉시 저장 확인
                universities_to_process.append(university)
                logger.info(f"   ✅ {uni_data['name_ko']} 추가 완료")
            except Exception as e:
                logger.warning(f"   ⚠️  {uni_data.get('name_ko', uni_data['name'])} 처리 실패: {str(e)}")
                session.rollback()
                continue

        session.commit()
        logger.info(f"\n✅ 총 {len(universities_to_process)}개 대학 데이터 준비 완료\n")

        # =============== 2단계: crawl4ai로 교수/연구실 정보 수집 ===============
        logger.info("🔍 [2단계] crawl4ai를 사용한 교수/연구실 정보 수집")
        logger.info("-" * 70)

        await crawler.initialize()

        # 처음 2개 대학만 테스트 (전체 확장은 나중에)
        for university in universities_to_process[:2]:
            logger.info(f"\n🎓 {university.name_ko} 크롤링 중...")
            logger.info(f"   🌐 URL: {university.url}")

            # 학과 정보 API에서 조회
            departments_data = api_client.get_departments(university.id)
            logger.info(f"   📚 {departments_data['total']}개 학과 발견")

            # 학과별 크롤링
            for college_data in departments_data.get("colleges", [])[:1]:  # 첫 단과대만
                college_name = college_data.get("college_name_ko", college_data.get("college_name"))
                logger.info(f"\n   단과대: {college_name}")

                for dept_data in college_data.get("departments", [])[:1]:  # 첫 학과만
                    dept_name = dept_data.get("name_ko", dept_data.get("name"))
                    dept_url = dept_data.get("url", "")

                    logger.info(f"   📖 학과: {dept_name}")

                    if not dept_url:
                        logger.warning(f"      ⚠️  학과 URL 없음, 스킵")
                        continue

                    # 교수 정보 추출
                    professors = await crawler.extract_professors(dept_url, dept_name)
                    logger.info(f"      👨‍🏫 {len(professors)}명의 교수 정보 추출")

                    for prof_data in professors[:2]:  # 처음 2명만
                        logger.info(f"         - {prof_data.get('name', 'Unknown')}")

                    # 연구실 정보 추출
                    labs = await crawler.extract_labs(dept_url, dept_name)
                    logger.info(f"      🔬 {len(labs)}개의 연구실 정보 추출")

        logger.info("\n✅ crawl4ai 크롤링 완료\n")

        # =============== 3단계: 수집된 논문 검증 ===============
        logger.info("📋 [3단계] 수집된 데이터 검증")
        logger.info("-" * 70)

        # DB 통계
        paper_count = session.query(ResearchPaper).count()
        analysis_count = session.query(PaperAnalysis).count()

        logger.info(f"📊 데이터베이스 통계:")
        logger.info(f"   - 총 논문: {paper_count}개")
        logger.info(f"   - 분석된 논문: {analysis_count}개")
        logger.info(f"   - 분석 완료율: {(analysis_count/paper_count*100 if paper_count > 0 else 0):.1f}%")

        logger.info("\n✅ Phase 2 크롤러 파이프라인 완료!")
        logger.info("="*70 + "\n")

        logger.info("📋 다음 단계:")
        logger.info("   1. 모든 대학에 대해 크롤링 확장 (현재 2개만 테스트)")
        logger.info("   2. 수집된 모든 논문에 Ollama 분석 적용 (배치)")
        logger.info("   3. 최종 통계 및 품질 검증")
        logger.info("="*70 + "\n")

    except Exception as e:
        logger.error(f"❌ 파이프라인 실패: {str(e)}")
        import traceback
        traceback.print_exc()

    finally:
        await crawler.close()
        session.close()


if __name__ == "__main__":
    asyncio.run(main())
