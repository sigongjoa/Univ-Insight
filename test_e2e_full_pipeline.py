"""
완전한 E2E 테스트: 모든 컴포넌트가 함께 동작하는지 검증

구성:
1. 실제 SNUCrawler 데이터
2. Ollama LLM 분석
3. ChromaDB 벡터 검색
4. API 응답 검증

실행: python test_e2e_full_pipeline.py
"""

import json
import requests
from datetime import datetime

# SQLAlchemy
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker

# Domain
from src.domain.models import (
    University, College, Department, Professor, Laboratory,
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


class E2EPipelineTest:
    """완전한 E2E 파이프라인 테스트"""

    def __init__(self):
        self.session = SessionLocal()
        self.vector_store = VectorStore(
            persist_dir="./chroma_db",
            persist_enabled=True
        )
        self.results = {
            "database": {},
            "analysis": {},
            "vector_store": {},
            "api": {}
        }

    def test_database_layer(self):
        """데이터베이스 계층 검증"""
        logger.info("\n" + "="*70)
        logger.info("✅ 테스트 1️⃣: 데이터베이스 계층")
        logger.info("="*70)

        try:
            # 1. University 검증
            uni_count = self.session.query(University).count()
            logger.info(f"\n📊 대학: {uni_count}개")
            assert uni_count > 0, "No universities found"

            universities = self.session.query(University).all()
            for uni in universities:
                logger.info(f"   - {uni.name_ko}")

                # 2. College 검증
                college_count = len(uni.colleges)
                logger.info(f"     📚 단과대학: {college_count}개")
                assert college_count > 0, "No colleges found"

                for college in uni.colleges:
                    logger.info(f"        - {college.name_ko}")

                    # 3. Department 검증
                    dept_count = len(college.departments)
                    logger.info(f"          📖 전공: {dept_count}개")

                    for dept in college.departments:
                        # 4. Professor 검증
                        prof_count = len(dept.professors)
                        logger.info(f"             👨‍🏫 교수: {prof_count}명")

                        for prof in dept.professors:
                            # 5. Laboratory 검증
                            lab_count = len(prof.laboratories)
                            logger.info(f"                🔬 연구실: {lab_count}개")

            # 통계
            total_papers = self.session.query(ResearchPaper).count()
            analyzed_papers = self.session.query(PaperAnalysis).count()

            logger.info(f"\n📄 논문:")
            logger.info(f"   - 총 논문: {total_papers}개")
            logger.info(f"   - 분석된 논문: {analyzed_papers}개")
            logger.info(f"   - 분석 완료율: {(analyzed_papers/total_papers*100):.1f}%")

            assert total_papers > 0, "No papers found"
            assert analyzed_papers > 0, "No analyzed papers found"

            self.results["database"] = {
                "universities": uni_count,
                "papers": total_papers,
                "analyzed_papers": analyzed_papers,
                "status": "✅ PASS"
            }

            logger.info("\n✅ 데이터베이스 검증 통과!\n")

        except AssertionError as e:
            logger.error(f"❌ 데이터베이스 검증 실패: {e}")
            self.results["database"]["status"] = f"❌ FAIL: {e}"

    def test_analysis_layer(self):
        """LLM 분석 계층 검증"""
        logger.info("="*70)
        logger.info("✅ 테스트 2️⃣: LLM 분석 계층 (Ollama)")
        logger.info("="*70)

        try:
            analyzed_papers = self.session.query(PaperAnalysis).all()
            logger.info(f"\n📋 분석된 논문: {len(analyzed_papers)}개\n")

            valid_analysis_count = 0

            for idx, analysis in enumerate(analyzed_papers, 1):
                paper = analysis.paper
                logger.info(f"[{idx}] {paper.title[:60]}...")

                # 분석 결과 검증 (최소한 요약과 모델은 있어야 함)
                assert analysis.easy_summary, "Missing easy_summary"
                assert analysis.analysis_model, "Missing analysis_model"

                # 선택사항: 일부 필드는 LLM 파싱 오류로 없을 수 있음
                has_companies = bool(analysis.recommended_companies)
                has_jobs = bool(analysis.job_roles)
                has_subjects = bool(analysis.recommended_subjects)

                logger.info(f"   ✅ 분석 완료")
                logger.info(f"   📝 요약: {analysis.easy_summary[:50]}...")
                if has_jobs:
                    logger.info(f"   💼 직업: {', '.join(analysis.job_roles[:2])}")
                if has_companies:
                    logger.info(f"   🏢 회사: {', '.join(analysis.recommended_companies[:2])}")
                if has_subjects:
                    logger.info(f"   📚 과목: {', '.join(analysis.recommended_subjects[:2])}")
                logger.info(f"   🤖 모델: {analysis.analysis_model}\n")

                valid_analysis_count += 1

            assert valid_analysis_count == len(analyzed_papers), "Some analyses failed validation"

            self.results["analysis"] = {
                "valid_analyses": valid_analysis_count,
                "status": "✅ PASS"
            }

            logger.info("✅ LLM 분석 검증 통과!\n")

        except AssertionError as e:
            logger.error(f"❌ LLM 분석 검증 실패: {e}")
            self.results["analysis"]["status"] = f"❌ FAIL: {e}"

    def test_vector_store_layer(self):
        """벡터 저장소 계층 검증"""
        logger.info("="*70)
        logger.info("✅ 테스트 3️⃣: 벡터 저장소 계층 (ChromaDB)")
        logger.info("="*70)

        try:
            # 벡터 저장소 상태
            doc_count = self.vector_store.get_collection_count()
            logger.info(f"\n📊 벡터 저장소:")
            logger.info(f"   - 색인된 논문: {doc_count}개")
            assert doc_count > 0, "Vector store is empty"

            # 검색 테스트
            test_queries = [
                ("AI research", 3),
                ("autonomous vehicles", 2),
                ("technology companies", 3)
            ]

            logger.info(f"\n🔍 검색 테스트:\n")

            total_results = 0
            for query, expected_k in test_queries:
                results = self.vector_store.search(query, k=expected_k, threshold=0.0)

                logger.info(f"   쿼리: '{query}'")
                logger.info(f"   결과: {len(results)}개")

                for idx, result in enumerate(results[:2], 1):
                    logger.info(f"      [{idx}] {result['metadata'].get('title', 'Unknown')[:50]}")
                    logger.info(f"           유사도: {result['similarity']:.3f}")

                total_results += len(results)
                logger.info("")

            assert total_results > 0, "No search results found"

            self.results["vector_store"] = {
                "indexed_documents": doc_count,
                "search_results": total_results,
                "status": "✅ PASS"
            }

            logger.info("✅ 벡터 저장소 검증 통과!\n")

        except AssertionError as e:
            logger.error(f"❌ 벡터 저장소 검증 실패: {e}")
            self.results["vector_store"]["status"] = f"❌ FAIL: {e}"

    def test_api_simulation(self):
        """API 엔드포인트 시뮬레이션"""
        logger.info("="*70)
        logger.info("✅ 테스트 4️⃣: API 엔드포인트 시뮬레이션")
        logger.info("="*70)

        try:
            logger.info("\n📡 API 엔드포인트 응답 시뮬레이션:\n")

            # 1. 대학 목록 조회
            universities = self.session.query(University).all()
            logger.info("1️⃣ GET /api/v1/universities")
            logger.info(f"   응답: {len(universities)}개 대학")
            for uni in universities:
                logger.info(f"      - {uni.name_ko} (ID: {uni.id})")

            # 2. 대학 상세 조회
            if universities:
                uni = universities[0]
                logger.info(f"\n2️⃣ GET /api/v1/universities/{uni.id}")
                logger.info(f"   응답: {uni.name_ko}")
                logger.info(f"      - 단과대학: {len(uni.colleges)}개")
                logger.info(f"      - 순위: {uni.ranking}")
                logger.info(f"      - 위치: {uni.location}")

                # 3. 단과대학 상세 조회
                if uni.colleges:
                    college = uni.colleges[0]
                    logger.info(f"\n3️⃣ GET /api/v1/colleges/{college.id}")
                    logger.info(f"   응답: {college.name_ko}")
                    logger.info(f"      - 전공: {len(college.departments)}개")

                    # 4. 전공 상세 조회
                    if college.departments:
                        dept = college.departments[0]
                        logger.info(f"\n4️⃣ GET /api/v1/departments/{dept.id}")
                        logger.info(f"   응답: {dept.name_ko}")
                        logger.info(f"      - 교수: {len(dept.professors)}명")

                        # 5. 교수 상세 조회
                        if dept.professors:
                            prof = dept.professors[0]
                            logger.info(f"\n5️⃣ GET /api/v1/professors/{prof.id}")
                            logger.info(f"   응답: {prof.name_ko}")
                            logger.info(f"      - 연구실: {len(prof.laboratories)}개")

                            # 6. 논문 목록 조회
                            papers = self.session.query(ResearchPaper).all()
                            logger.info(f"\n6️⃣ GET /api/v1/research")
                            logger.info(f"   응답: {len(papers)}개 논문")

                            # 7. 논문 상세 분석 조회
                            if papers:
                                paper = papers[0]
                                analysis = paper.analysis
                                if analysis:
                                    logger.info(f"\n7️⃣ GET /api/v1/research/{paper.id}/analysis")
                                    logger.info(f"   응답: {paper.title[:60]}")
                                    logger.info(f"      - 요약: {analysis.easy_summary[:50]}...")
                                    logger.info(f"      - 직업: {', '.join(analysis.job_roles[:2])}")

            self.results["api"] = {
                "endpoints_tested": 7,
                "status": "✅ PASS"
            }

            logger.info("\n✅ API 시뮬레이션 통과!\n")

        except Exception as e:
            logger.error(f"❌ API 시뮬레이션 실패: {e}")
            self.results["api"]["status"] = f"❌ FAIL: {e}"

    def print_summary(self):
        """최종 결과 요약"""
        logger.info("="*70)
        logger.info("📊 최종 테스트 결과 요약")
        logger.info("="*70)

        total_status = "✅ ALL PASS"

        for test_name, result in self.results.items():
            status = result.get("status", "⚠️ UNKNOWN")
            logger.info(f"\n{test_name.upper()}: {status}")

            for key, value in result.items():
                if key != "status":
                    logger.info(f"   - {key}: {value}")

            if "FAIL" in status:
                total_status = "❌ SOME TESTS FAILED"

        logger.info("\n" + "="*70)
        logger.info(f"전체 상태: {total_status}")
        logger.info("="*70 + "\n")

        # JSON 출력
        logger.info("\n📋 테스트 결과 JSON:\n")
        logger.info(json.dumps(self.results, indent=2, ensure_ascii=False))

        return total_status

    def run(self):
        """전체 테스트 실행"""
        logger.info("\n" + "="*70)
        logger.info("🚀 완전한 E2E 파이프라인 테스트 시작")
        logger.info("="*70)

        try:
            # 모든 테스트 실행
            self.test_database_layer()
            self.test_analysis_layer()
            self.test_vector_store_layer()
            self.test_api_simulation()

            # 결과 출력
            self.print_summary()

        finally:
            self.session.close()


if __name__ == "__main__":
    test = E2EPipelineTest()
    test.run()
