"""
백엔드 E2E 시나리오 테스트
실제 사용 시나리오 기반 테스트

유즈케이스:
1. 대학 탐색 플로우 (University → College → Department → Professor → Lab)
2. 논문 조회 및 분석 결과 확인
3. 벡터 검색 기능
4. 추천 정보 조회
"""

import time
import json
from datetime import datetime
import requests
from typing import Dict, Any, List

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.domain.models import (
    University, College, Department, Professor, Laboratory,
    ResearchPaper, PaperAnalysis
)
from src.core.logging import get_logger, setup_logging
from src.services.vector_store import VectorStore

setup_logging(level="INFO")
logger = get_logger(__name__)

DATABASE_URL = "sqlite:///./univ_insight.db"
engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine)
BASE_URL = "http://localhost:8000/api/v1"


class PerformanceMetrics:
    """성능 측정 클래스"""

    def __init__(self):
        self.metrics: Dict[str, List[float]] = {}

    def record(self, endpoint: str, response_time: float):
        """응답 시간 기록"""
        if endpoint not in self.metrics:
            self.metrics[endpoint] = []
        self.metrics[endpoint].append(response_time)

    def get_stats(self, endpoint: str) -> Dict[str, float]:
        """통계 계산"""
        times = self.metrics.get(endpoint, [])
        if not times:
            return {}

        return {
            "avg": sum(times) / len(times),
            "min": min(times),
            "max": max(times),
            "count": len(times)
        }

    def print_report(self):
        """성능 리포트 출력"""
        logger.info("\n" + "="*70)
        logger.info("📊 성능 분석 결과")
        logger.info("="*70)

        for endpoint in sorted(self.metrics.keys()):
            stats = self.get_stats(endpoint)
            logger.info(f"\n{endpoint}")
            logger.info(f"  평균: {stats['avg']*1000:.2f}ms")
            logger.info(f"  최소: {stats['min']*1000:.2f}ms")
            logger.info(f"  최대: {stats['max']*1000:.2f}ms")
            logger.info(f"  샘플: {stats['count']}개")


class BackendE2ETest:
    """백엔드 E2E 테스트"""

    def __init__(self):
        self.session = SessionLocal()
        self.vector_store = VectorStore(persist_dir="./chroma_db")
        self.metrics = PerformanceMetrics()
        self.test_results = {
            "scenarios": [],
            "performance": {},
            "errors": []
        }

    def api_request(self, method: str, endpoint: str, **kwargs) -> tuple[Any, float]:
        """API 요청 (성능 측정)"""
        url = f"{BASE_URL}{endpoint}"

        start = time.time()
        try:
            if method == "GET":
                response = requests.get(url, timeout=10, **kwargs)
            elif method == "POST":
                response = requests.post(url, timeout=10, **kwargs)
            elif method == "PUT":
                response = requests.put(url, timeout=10, **kwargs)
            else:
                raise ValueError(f"Unsupported method: {method}")

            elapsed = time.time() - start
            self.metrics.record(endpoint, elapsed)

            return response, elapsed
        except Exception as e:
            elapsed = time.time() - start
            self.test_results["errors"].append({
                "endpoint": endpoint,
                "error": str(e),
                "time": elapsed
            })
            raise

    # ======================== 시나리오 1: 계층적 탐색 ========================

    def scenario_1_hierarchical_navigation(self):
        """시나리오 1: 대학 → 단과대학 → 전공 → 교수 → 연구실 탐색"""
        logger.info("\n" + "="*70)
        logger.info("🎯 시나리오 1: 계층적 네비게이션")
        logger.info("(서울대 → 공과대학 → 컴퓨터공학부 → 교수 → 연구실)")
        logger.info("="*70)

        scenario_result = {
            "name": "Hierarchical Navigation",
            "steps": [],
            "success": False,
            "total_time": 0
        }

        start_time = time.time()

        try:
            # 1. 대학 목록 조회
            logger.info("\n[Step 1] 대학 목록 조회")
            resp, elapsed = self.api_request("GET", "/universities")
            assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
            data = resp.json()
            assert len(data["items"]) > 0, "No universities found"
            logger.info(f"✅ {len(data['items'])}개 대학 조회 (응답: {elapsed*1000:.2f}ms)")
            scenario_result["steps"].append({
                "step": "Get Universities",
                "status": "✅",
                "time": elapsed
            })

            # 2. 서울대 상세 조회
            uni_id = data["items"][0]["id"]
            logger.info(f"\n[Step 2] 서울대 상세 조회 (ID: {uni_id})")
            resp, elapsed = self.api_request("GET", f"/universities/{uni_id}")
            assert resp.status_code == 200
            uni_data = resp.json()
            assert len(uni_data["colleges"]) > 0, "No colleges found"
            logger.info(f"✅ {len(uni_data['colleges'])}개 단과대학 조회 (응답: {elapsed*1000:.2f}ms)")
            scenario_result["steps"].append({
                "step": "Get University Details",
                "status": "✅",
                "time": elapsed
            })

            # 3. 공과대학 조회
            college_id = uni_data["colleges"][0]["id"]
            logger.info(f"\n[Step 3] 공과대학 조회 (ID: {college_id})")
            resp, elapsed = self.api_request("GET", f"/colleges/{college_id}")
            assert resp.status_code == 200
            college_data = resp.json()
            assert len(college_data["departments"]) > 0, "No departments found"
            logger.info(f"✅ {len(college_data['departments'])}개 전공 조회 (응답: {elapsed*1000:.2f}ms)")
            scenario_result["steps"].append({
                "step": "Get College Details",
                "status": "✅",
                "time": elapsed
            })

            # 4. 컴퓨터공학부 조회
            dept_id = college_data["departments"][0]["id"]
            logger.info(f"\n[Step 4] 컴퓨터공학부 조회 (ID: {dept_id})")
            resp, elapsed = self.api_request("GET", f"/departments/{dept_id}")
            assert resp.status_code == 200
            dept_data = resp.json()
            professors = dept_data.get("professors", [])
            if professors:
                logger.info(f"✅ {len(professors)}명 교수 조회 (응답: {elapsed*1000:.2f}ms)")
            else:
                logger.info(f"⚠️ 교수 정보 없음 (응답: {elapsed*1000:.2f}ms)")
            scenario_result["steps"].append({
                "step": "Get Department Details",
                "status": "✅",
                "time": elapsed
            })

            # 5. 교수 상세 조회
            if professors:
                prof_id = professors[0]["id"]
                logger.info(f"\n[Step 5] 교수 상세 조회 (ID: {prof_id})")
                resp, elapsed = self.api_request("GET", f"/professors/{prof_id}")
                assert resp.status_code == 200
                prof_data = resp.json()
                labs = prof_data.get("laboratories", [])
                logger.info(f"✅ {len(labs)}개 연구실 조회 (응답: {elapsed*1000:.2f}ms)")
                scenario_result["steps"].append({
                    "step": "Get Professor Details",
                    "status": "✅",
                    "time": elapsed
                })

                # 6. 연구실 조회
                if labs:
                    lab_id = labs[0]["id"]
                    logger.info(f"\n[Step 6] 연구실 상세 조회 (ID: {lab_id})")
                    resp, elapsed = self.api_request("GET", f"/laboratories/{lab_id}")
                    assert resp.status_code == 200
                    logger.info(f"✅ 연구실 정보 조회 완료 (응답: {elapsed*1000:.2f}ms)")
                    scenario_result["steps"].append({
                        "step": "Get Laboratory Details",
                        "status": "✅",
                        "time": elapsed
                    })

            scenario_result["success"] = True
            scenario_result["total_time"] = time.time() - start_time

            logger.info(f"\n✅ 시나리오 1 완료! (총 소요 시간: {scenario_result['total_time']:.2f}초)")
            return scenario_result

        except Exception as e:
            logger.error(f"\n❌ 시나리오 1 실패: {str(e)}")
            scenario_result["total_time"] = time.time() - start_time
            return scenario_result

    # ======================== 시나리오 2: 논문 조회 및 분석 ========================

    def scenario_2_paper_exploration(self):
        """시나리오 2: 논문 목록 조회 → 상세 분석 조회"""
        logger.info("\n" + "="*70)
        logger.info("🎯 시나리오 2: 논문 탐색 및 분석 조회")
        logger.info("(논문 목록 → 상세 분석 → 메타데이터)")
        logger.info("="*70)

        scenario_result = {
            "name": "Paper Exploration",
            "steps": [],
            "success": False,
            "total_time": 0
        }

        start_time = time.time()

        try:
            # 1. 논문 목록 조회
            logger.info("\n[Step 1] 모든 논문 조회")
            resp, elapsed = self.api_request("GET", "/research")
            assert resp.status_code == 200
            papers_data = resp.json()
            papers = papers_data.get("items", [])
            assert len(papers) > 0, "No papers found"
            logger.info(f"✅ {len(papers)}개 논문 조회 (응답: {elapsed*1000:.2f}ms)")
            scenario_result["steps"].append({
                "step": "Get Papers List",
                "status": "✅",
                "time": elapsed
            })

            # 2. 첫 번째 논문 상세 분석 조회
            paper_id = papers[0]["id"]
            logger.info(f"\n[Step 2] 논문 상세 분석 조회 (ID: {paper_id})")
            resp, elapsed = self.api_request("GET", f"/research/{paper_id}/analysis")
            assert resp.status_code == 200
            analysis_data = resp.json()

            # 분석 결과 검증
            assert "easy_summary" in analysis_data, "Missing easy_summary"
            assert "job_roles" in analysis_data, "Missing job_roles"

            logger.info(f"✅ 논문 분석 결과 조회 (응답: {elapsed*1000:.2f}ms)")
            logger.info(f"   - 요약: {analysis_data['easy_summary'][:60]}...")
            logger.info(f"   - 직업: {', '.join(analysis_data['job_roles'][:2])}")
            logger.info(f"   - 기업: {', '.join(analysis_data.get('recommended_companies', [])[:2])}")

            scenario_result["steps"].append({
                "step": "Get Paper Analysis",
                "status": "✅",
                "time": elapsed
            })

            # 3. 다른 논문들도 빠르게 조회
            logger.info(f"\n[Step 3] 나머지 논문 분석 조회 (총 {len(papers)}개)")
            analysis_times = []
            for idx, paper in enumerate(papers[1:], start=2):
                resp, elapsed = self.api_request("GET", f"/research/{paper['id']}/analysis")
                if resp.status_code == 200:
                    analysis_times.append(elapsed)
                    logger.info(f"   [{idx}] {paper.get('title', 'Unknown')[:50]}... ({elapsed*1000:.2f}ms)")

            avg_time = sum(analysis_times) / len(analysis_times) if analysis_times else 0
            logger.info(f"✅ 평균 응답 시간: {avg_time*1000:.2f}ms")

            scenario_result["steps"].append({
                "step": "Get All Papers Analysis",
                "status": "✅",
                "time": avg_time
            })

            scenario_result["success"] = True
            scenario_result["total_time"] = time.time() - start_time

            logger.info(f"\n✅ 시나리오 2 완료! (총 소요 시간: {scenario_result['total_time']:.2f}초)")
            return scenario_result

        except Exception as e:
            logger.error(f"\n❌ 시나리오 2 실패: {str(e)}")
            scenario_result["total_time"] = time.time() - start_time
            return scenario_result

    # ======================== 시나리오 3: 벡터 검색 ========================

    def scenario_3_vector_search(self):
        """시나리오 3: 벡터 검색 기능 테스트"""
        logger.info("\n" + "="*70)
        logger.info("🎯 시나리오 3: 벡터 검색")
        logger.info("(의미 기반 검색 성능 테스트)")
        logger.info("="*70)

        scenario_result = {
            "name": "Vector Search",
            "steps": [],
            "success": False,
            "total_time": 0
        }

        start_time = time.time()

        try:
            # 테스트 쿼리들
            test_queries = [
                "AI and deep learning research",
                "autonomous vehicles",
                "technology companies job",
                "machine learning applications"
            ]

            logger.info(f"\n테스트 쿼리: {len(test_queries)}개")

            search_times = []
            total_results = 0

            for query in test_queries:
                logger.info(f"\n[Query] '{query}'")
                start = time.time()

                try:
                    results = self.vector_store.search(query, k=3)
                    elapsed = time.time() - start
                    search_times.append(elapsed)

                    logger.info(f"   결과: {len(results)}개 (응답: {elapsed*1000:.2f}ms)")
                    for idx, result in enumerate(results[:2], 1):
                        logger.info(f"      [{idx}] {result['metadata'].get('title', 'Unknown')[:50]}")
                        logger.info(f"           유사도: {result['similarity']:.3f}")

                    total_results += len(results)
                except Exception as e:
                    logger.warning(f"   ⚠️ 검색 실패: {str(e)}")

            if search_times:
                avg_search_time = sum(search_times) / len(search_times)
                logger.info(f"\n✅ 평균 검색 시간: {avg_search_time*1000:.2f}ms")
                logger.info(f"   총 결과: {total_results}개")

                scenario_result["steps"].append({
                    "step": "Vector Search",
                    "status": "✅",
                    "time": avg_search_time,
                    "queries": len(test_queries),
                    "results": total_results
                })

                scenario_result["success"] = True

            scenario_result["total_time"] = time.time() - start_time

            logger.info(f"\n✅ 시나리오 3 완료! (총 소요 시간: {scenario_result['total_time']:.2f}초)")
            return scenario_result

        except Exception as e:
            logger.error(f"\n❌ 시나리오 3 실패: {str(e)}")
            scenario_result["total_time"] = time.time() - start_time
            return scenario_result

    def print_results(self):
        """테스트 결과 출력"""
        logger.info("\n" + "="*70)
        logger.info("📋 E2E 테스트 결과 요약")
        logger.info("="*70)

        for scenario in self.test_results["scenarios"]:
            status = "✅ PASS" if scenario["success"] else "❌ FAIL"
            logger.info(f"\n{scenario['name']}: {status}")
            logger.info(f"   소요 시간: {scenario['total_time']:.2f}초")
            logger.info(f"   단계: {len(scenario['steps'])}개")

        # 성능 메트릭
        self.metrics.print_report()

        # 에러 리포트
        if self.test_results["errors"]:
            logger.info("\n" + "="*70)
            logger.info("⚠️ 에러 리포트")
            logger.info("="*70)
            for error in self.test_results["errors"]:
                logger.error(f"\n{error['endpoint']}")
                logger.error(f"   {error['error']}")
                logger.error(f"   응답 시간: {error['time']*1000:.2f}ms")

    def run(self):
        """모든 시나리오 실행"""
        logger.info("\n" + "="*70)
        logger.info("🚀 백엔드 E2E 시나리오 테스트 시작")
        logger.info("="*70)

        try:
            # 시나리오 1 실행
            result1 = self.scenario_1_hierarchical_navigation()
            self.test_results["scenarios"].append(result1)

            # 시나리오 2 실행
            result2 = self.scenario_2_paper_exploration()
            self.test_results["scenarios"].append(result2)

            # 시나리오 3 실행
            result3 = self.scenario_3_vector_search()
            self.test_results["scenarios"].append(result3)

            # 결과 출력
            self.print_results()

            # JSON 저장
            with open("test_results_backend_e2e.json", "w", encoding="utf-8") as f:
                json.dump(self.test_results, f, indent=2, ensure_ascii=False, default=str)
            logger.info("\n✅ 결과 저장: test_results_backend_e2e.json")

        finally:
            self.session.close()


if __name__ == "__main__":
    test = BackendE2ETest()
    test.run()
