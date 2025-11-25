"""
Phase 3 테스트: RAG + LLM 분석 + 추천 엔진

구현 사항:
1. 벡터 스토어 (ChromaDB)
2. RAG 엔진
3. LLM 분석
4. 추천 엔진
"""

import asyncio
import json
import logging
from datetime import datetime

from src.services.vector_store import ChromaVectorStore, EmbeddingService
from src.services.rag_engine import RAGEngine
from src.services.llm_analysis import LLMAnalysisService
from src.services.recommendation_engine import RecommendationEngine

logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'
)
logger = logging.getLogger(__name__)


async def test_phase3():
    """Phase 3 테스트"""

    print("\n" + "="*80)
    print("🚀 Phase 3 테스트: RAG + LLM 분석 + 추천 엔진")
    print("="*80 + "\n")

    # 1️⃣ 벡터 스토어 초기화
    print("📚 벡터 스토어 초기화...")
    embedding_service = EmbeddingService()
    vector_store = ChromaVectorStore(
        collection_name="phase3_test",
        persist_dir="./chroma_db_phase3",
        embedding_service=embedding_service,
    )
    await vector_store.initialize()
    print()

    # 2️⃣ 테스트 논문 데이터 추가
    print("📄 테스트 논문 데이터 추가...")
    test_papers = [
        {
            "id": "paper-1",
            "title": "트랜스포머 모델 최적화: 에너지 효율성 개선",
            "content": """트랜스포머는 현대 AI의 핵심 아키텍처입니다. 이 논문은 자기 주의 메커니즘(self-attention)의 계산 복잡도를 줄이는 방법을 제시합니다. 
            기존 트랜스포머는 O(n²)의 시간 복잡도를 가지고 있어 긴 시퀀스 처리 시 많은 에너지를 소비합니다.
            우리의 방법은 선형 어텐션(linear attention)을 사용하여 O(n) 복잡도로 개선했으며, 실험 결과 에너지 소비를 70% 감소시켰습니다.
            이는 모바일 장치에서 AI 모델을 실행할 때 배터리 수명을 크게 연장시킬 수 있습니다.""",
            "metadata": {
                "university": "KAIST",
                "department": "전자공학과",
                "year": 2024,
            }
        },
        {
            "id": "paper-2",
            "title": "자율주행 자동차의 라이다 센서 융합 기술",
            "content": """자율주행 자동차는 여러 센서를 통합하여 주변 환경을 이해합니다.
            라이다(LiDAR)는 빛을 이용하여 3D 정보를 얻는 핵심 센서입니다.
            이 논문은 라이다와 카메라 데이터를 효율적으로 융합하는 신경망 아키텍처를 제안합니다.
            실제 도로 환경에서 테스트한 결과, 기존 방법 대비 95% 이상의 정확도를 달성했습니다.
            특히 악천후 조건에서의 성능이 크게 개선되어 안전성을 높였습니다.""",
            "metadata": {
                "university": "서울대학교",
                "department": "기계항공공학과",
                "year": 2024,
            }
        },
        {
            "id": "paper-3",
            "title": "mRNA 백신 기술의 최신 발전: 개인맞춤형 치료",
            "content": """mRNA 백신은 COVID-19 이후 각광받은 기술입니다.
            기존 백신과 달리 mRNA는 우리 몸의 세포를 이용하여 항원을 직접 만들게 합니다.
            이 논문은 개인의 유전 정보에 맞춘 맞춤형 mRNA 백신을 개발하는 방법을 제시합니다.
            종양 환자 임상 시험에서 70% 이상의 반응률을 보였으며, 면역 체계를 강화하는 효과가 확인되었습니다.
            이 기술은 암, 에이즈, 말라리아 등 다양한 질병 치료로 확대될 전망입니다.""",
            "metadata": {
                "university": "서울대학교",
                "department": "생명과학부",
                "year": 2024,
            }
        },
    ]

    added = await vector_store.add_batch(test_papers)
    print(f"✅ {added}개 논문 추가됨\n")

    # 3️⃣ RAG 엔진 초기화
    print("🔍 RAG 엔진 초기화...")
    rag_engine = RAGEngine(vector_store)
    print()

    # 4️⃣ 검색 테스트
    print("="*70)
    print("🔍 검색 테스트")
    print("="*70)

    queries = [
        "AI 모델의 에너지 효율",
        "자율주행 센서 기술",
        "질병 치료 기술",
    ]

    search_results = {}
    for query in queries:
        print(f"\n📌 쿼리: {query}")
        rag_result = await rag_engine.retrieve_and_rank(query, top_k=2)
        search_results[query] = rag_result
        print(f"   찾음: {rag_result['context_count']}개 논문")
        for doc in rag_result["context_docs"]:
            print(f"     - {doc['title']} (거리: {doc['distance']:.3f})")

    print()

    # 5️⃣ LLM 분석
    print("="*70)
    print("🧠 LLM 분석")
    print("="*70)

    llm_service = LLMAnalysisService(llm_provider="mock")
    first_query = queries[0]
    rag_result = search_results[first_query]

    print(f"\n📝 {first_query} 분석 중...")
    analysis = await llm_service.analyze_research_paper(rag_result["rag_prompt"])
    print(f"✅ 분석 완료\n")

    print("분석 결과:")
    for key, value in analysis.items():
        if isinstance(value, list):
            print(f"  {key}:")
            for item in value:
                print(f"    - {item}")
        else:
            print(f"  {key}: {value}")

    print()

    # 6️⃣ 추천 엔진
    print("="*70)
    print("💼 추천 엔진")
    print("="*70)

    recommendation_engine = RecommendationEngine()

    print("\n📌 주제: AI 에너지 효율성")
    roadmap = await recommendation_engine.generate_student_roadmap("AI/머신러닝")

    print("\n진로 추천:")
    for career in roadmap["career_paths"]:
        print(f"  - {career['company']}: {career['job']} ({career['salary']})")

    print("\n플랜 B 대학:")
    for uni in roadmap["plan_b_universities"]:
        print(f"  - {uni['university']} {uni['department']}")

    print("\n관련 주제:")
    for topic in roadmap["related_topics"]:
        print(f"  - {topic}")

    print("\n학습 타임라인:")
    for grade, description in roadmap["timeline"].items():
        print(f"  {grade}: {description}")

    print()

    # 7️⃣ 통계
    print("="*70)
    print("📊 최종 통계")
    print("="*70)

    vector_stats = await vector_store.get_stats()
    rag_stats = await rag_engine.get_stats()
    rec_stats = await recommendation_engine.get_stats()

    print(f"\n📚 벡터 스토어:")
    print(f"   문서: {vector_stats['document_count']}개")
    print(f"   모델: {vector_stats['embedding_model']}")

    print(f"\n🔍 RAG 엔진:")
    print(f"   상태: {rag_stats['rag_engine']}")

    print(f"\n💼 추천 엔진:")
    print(f"   대학: {rec_stats['universities_count']}개")
    print(f"   회사: {rec_stats['companies_count']}개")

    # 8️⃣ 결과 저장
    print(f"\n📝 결과 저장...")
    results = {
        "timestamp": datetime.now().isoformat(),
        "phase": "Phase 3",
        "test_results": {
            "vector_store": vector_stats,
            "search_queries": len(search_results),
            "queries": queries,
            "analysis": analysis,
            "recommendations": {
                "career_count": len(roadmap["career_paths"]),
                "universities_count": len(roadmap["plan_b_universities"]),
                "topics_count": len(roadmap["related_topics"]),
            },
        },
    }

    with open("PHASE3_TEST_REPORT.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"✅ 결과 저장 완료: PHASE3_TEST_REPORT.json")

    print("\n" + "="*80)
    print("✅ Phase 3 테스트 완료!")
    print("="*80 + "\n")

    return results


if __name__ == "__main__":
    asyncio.run(test_phase3())
