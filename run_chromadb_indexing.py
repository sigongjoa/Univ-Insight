"""
ChromaDB 벡터 저장소에 논문들을 색인(indexing)하는 스크립트

분석된 논문들을 ChromaDB에 저장하여 벡터 검색을 가능하게 합니다.

실행: python run_chromadb_indexing.py
"""

import sys
from datetime import datetime

# SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Domain
from src.domain.models import (
    ResearchPaper, PaperAnalysis
)

# Services
from src.services.vector_store import VectorStore
from src.core.logging import get_logger, setup_logging

# Logging
setup_logging(level="INFO")
logger = get_logger(__name__)

# Database setup
DATABASE_URL = "sqlite:///./univ_insight.db"
engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine)


def index_papers_to_chromadb():
    """분석된 논문들을 ChromaDB에 색인"""
    logger.info("\n" + "="*70)
    logger.info("🗂️ ChromaDB 벡터 저장소 색인 시작")
    logger.info("="*70)

    session = SessionLocal()
    vector_store = VectorStore(
        persist_dir="./chroma_db",
        persist_enabled=True,
        collection_name="research_papers"
    )

    try:
        # 1️⃣ 분석된 논문 조회
        papers_with_analysis = session.query(ResearchPaper).filter(
            ResearchPaper.analysis != None
        ).all()

        if not papers_with_analysis:
            logger.info("❌ 분석된 논문이 없습니다\n")
            return

        logger.info(f"📋 색인할 논문: {len(papers_with_analysis)}개\n")

        # 2️⃣ 기존 벡터 저장소 초기화
        current_count = vector_store.get_collection_count()
        if current_count > 0:
            logger.info(f"🗑️ 기존 벡터 {current_count}개 삭제 중...")
            vector_store.clear_collection()
            logger.info("✅ 기존 데이터 삭제 완료\n")

        # 3️⃣ 각 논문을 벡터 저장소에 추가
        indexed_count = 0
        for idx, paper in enumerate(papers_with_analysis, 1):
            try:
                # 색인할 콘텐츠 준비
                # 제목, 요약, 기술 스택, 기업, 직업 정보 포함
                analysis = paper.analysis

                content = f"""
                Title: {paper.title}

                Summary: {analysis.easy_summary}

                Technologies: {', '.join(analysis.core_technologies[:5])}

                Companies: {', '.join(analysis.recommended_companies[:5])}

                Jobs: {', '.join(analysis.job_roles)}

                Subjects: {', '.join(analysis.recommended_subjects[:5])}
                """.strip()

                # 메타데이터 준비 (ChromaDB는 제한된 타입 지원)
                metadata = {
                    "title": str(paper.title)[:512],  # String
                    "lab_id": str(paper.lab_id),  # String
                    "venue": str(paper.venue or "Unknown")[:256],  # String
                    "publication_year": int(paper.publication_year or 2024),  # Integer
                    "companies": str(",".join(analysis.recommended_companies[:3]))[:256],  # String
                    "jobs": str(",".join(analysis.job_roles))[:256],  # String
                    "technologies": str(",".join(analysis.core_technologies[:5]))[:256],  # String
                    "salary_range": str(analysis.salary_range or "Not specified")[:100],  # String
                    "analysis_model": str(analysis.analysis_model or "Unknown")[:100]  # String
                }

                # 벡터 저장소에 추가
                vector_store.add_embedding(
                    paper_id=paper.id,
                    content=content,
                    metadata=metadata
                )

                indexed_count += 1
                logger.info(f"[{idx}/{len(papers_with_analysis)}] ✅ 색인됨: {paper.title[:60]}...")

            except Exception as e:
                logger.error(f"[{idx}/{len(papers_with_analysis)}] ❌ 색인 실패: {str(e)[:100]}")
                continue

        logger.info("")
        logger.info("="*70)
        logger.info(f"✅ 색인 완료: {indexed_count}/{len(papers_with_analysis)}개 논문")
        logger.info("="*70)

        # 4️⃣ 최종 통계
        final_count = vector_store.get_collection_count()
        logger.info(f"\n📊 벡터 저장소 통계:")
        logger.info(f"   - 색인된 논문: {final_count}개")
        logger.info(f"   - 저장 위치: ./chroma_db")
        logger.info(f"   - 컬렉션명: research_papers")
        logger.info(f"   - 색인 모델: nomic-embed-text (ChromaDB 기본)\n")

    finally:
        session.close()


def test_vector_search():
    """벡터 검색 테스트"""
    logger.info("="*70)
    logger.info("🔍 벡터 검색 테스트")
    logger.info("="*70 + "\n")

    vector_store = VectorStore(
        persist_dir="./chroma_db",
        persist_enabled=True
    )

    # 테스트 쿼리들
    test_queries = [
        "AI and deep learning research",
        "Autonomous vehicles and computer vision",
        "Distributed systems and cloud computing",
        "Job opportunities in technology"
    ]

    for query in test_queries:
        logger.info(f"🔎 검색: '{query}'")

        results = vector_store.search(query, k=3, threshold=0.0)

        if not results:
            logger.info("   ❌ 검색 결과 없음\n")
            continue

        for idx, result in enumerate(results, 1):
            logger.info(f"   [{idx}] {result['id']}")
            logger.info(f"       제목: {result['metadata'].get('title', 'Unknown')[:60]}")
            logger.info(f"       유사도: {result['similarity']:.3f}")
            logger.info(f"       회사: {result['metadata'].get('companies', 'N/A')}")
            logger.info(f"       직업: {result['metadata'].get('jobs', 'N/A')}")

        logger.info("")


def verify_chromadb_status():
    """ChromaDB 상태 확인"""
    logger.info("="*70)
    logger.info("📈 ChromaDB 상태 확인")
    logger.info("="*70 + "\n")

    vector_store = VectorStore(
        persist_dir="./chroma_db",
        persist_enabled=True
    )

    count = vector_store.get_collection_count()

    logger.info(f"✅ 벡터 저장소 상태:")
    logger.info(f"   - 저장소: ChromaDB (Persistent)")
    logger.info(f"   - 위치: ./chroma_db")
    logger.info(f"   - 컬렉션: research_papers")
    logger.info(f"   - 색인된 문서: {count}개")
    logger.info(f"   - 임베딩 모델: nomic-embed-text (기본)")
    logger.info(f"   - 유사도 메트릭: cosine similarity")
    logger.info(f"   - 상태: {'🟢 Ready' if count > 0 else '🔴 Empty'}\n")


if __name__ == "__main__":
    logger.info("\n" + "="*70)
    logger.info("🚀 ChromaDB 벡터 저장소 구축 파이프라인")
    logger.info("="*70)

    # 논문 색인
    index_papers_to_chromadb()

    # 검색 테스트
    test_vector_search()

    # 상태 확인
    verify_chromadb_status()

    logger.info("="*70)
    logger.info("✨ ChromaDB 구축 완료!")
    logger.info("="*70 + "\n")
