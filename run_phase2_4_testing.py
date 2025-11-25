"""
Phase 2.4 테스트: 분산 크롤링 + 데이터베이스 통합 + 모니터링

구현 사항:
1. 분산 작업 큐
2. 워커 풀 기반 병렬 처리
3. SQLAlchemy 데이터베이스 통합
4. 실시간 모니터링 대시보드
5. 자동 스케일링
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import List, Tuple

from src.database.db import init_database, Database
from src.services.distributed_crawler import DistributedCrawler
from src.services.task_queue import get_task_queue, CrawlTask

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='{"timestamp": "%(asctime)s", "level": "%(levelname)s", "message": "%(message)s"}'
)

logger = logging.getLogger(__name__)


async def test_phase2_4():
    """Phase 2.4 테스트"""

    print("\n" + "="*80)
    print("🚀 Phase 2.4 테스트: 분산 크롤링 + DB 통합 + 모니터링")
    print("="*80 + "\n")

    # 1️⃣ 데이터베이스 초기화
    print("📚 데이터베이스 초기화...")
    db = init_database("sqlite:///./test_phase2_4.db")

    # 2️⃣ 분산 크롤러 초기화
    print("🏗️  분산 크롤러 초기화...")
    crawler = DistributedCrawler(
        database=db,
        num_workers=3,
        min_workers=1,
        max_workers=5,
        auto_scale_interval=5,
    )
    await crawler.initialize()

    # 3️⃣ 테스트 데이터 준비
    test_tasks = [
        ("https://engineering.snu.ac.kr/cse", "서울대학교", "컴퓨터학과"),
        ("https://www.kaist.ac.kr/cs", "KAIST", "컴퓨터학과"),
        ("https://cs.korea.ac.kr", "고려대학교", "컴퓨터학과"),
        ("https://www.yonsei.ac.kr/cs", "연세대학교", "컴퓨터학과"),
        ("https://www.sungkyunkwan.ac.kr/cs", "성균관대학교", "컴퓨터학과"),
    ]

    # 4️⃣ 크롤러 시작
    print("🚀 크롤러 시작...")
    await crawler.start()

    # 5️⃣ 작업 제출
    print(f"\n📋 {len(test_tasks)}개 작업 제출 중...")
    task_ids = await crawler.submit_bulk(test_tasks)
    print(f"✅ {len(task_ids)}개 작업 제출 완료\n")

    # 6️⃣ 모니터링
    print("="*70)
    print("📊 실시간 모니터링 (30초)")
    print("="*70)

    monitoring_duration = 30
    check_interval = 5

    for i in range(0, monitoring_duration, check_interval):
        await asyncio.sleep(check_interval)

        stats = crawler.get_stats()
        queue_stats = stats["queue"]

        print(
            f"\n[{i+check_interval}초] "
            f"대기={queue_stats['pending']} "
            f"실행={queue_stats['running']} "
            f"완료={queue_stats['completed']} "
            f"실패={queue_stats['failed']} | "
            f"워커={stats['worker_pool']['workers']['active']}"
        )

    # 7️⃣ 최종 통계
    print("\n" + "="*70)
    print("📈 최종 통계")
    print("="*70)

    final_stats = crawler.get_stats()
    queue_stats = final_stats["queue"]
    metrics = final_stats["metrics"]

    print(f"\n📋 큐 상태:")
    print(f"   대기: {queue_stats['pending']}")
    print(f"   실행: {queue_stats['running']}")
    print(f"   완료: {queue_stats['completed']}")
    print(f"   실패: {queue_stats['failed']}")
    print(f"   총합: {queue_stats['total']}")

    print(f"\n📊 성능 메트릭:")
    print(f"   총 작업: {metrics['total_tasks']}")
    print(f"   성공: {metrics['successful']}")
    print(f"   실패: {metrics['failed']}")
    print(f"   성공률: {metrics['success_rate']:.1f}%")
    print(f"   평균 시간: {metrics['avg_duration']:.2f}초")

    print(f"\n👷 워커 풀:")
    print(f"   활성: {final_stats['worker_pool']['workers']['active']}")
    print(f"   범위: {final_stats['worker_pool']['workers']['min']}-{final_stats['worker_pool']['workers']['max']}")

    # 8️⃣ 데이터베이스 통계
    print(f"\n💾 데이터베이스:")
    db_stats = db.get_db_stats()
    print(f"   작업: {db_stats['tasks_total']}")
    print(f"   결과: {db_stats['results_total']}")
    print(f"   교수: {db_stats['professors_total']}")
    print(f"   논문: {db_stats['papers_total']}")

    # 9️⃣ 크롤러 중지
    print(f"\n⏹️  크롤러 중지...")
    await crawler.stop()

    # 🔟 결과 저장
    print(f"\n📝 결과 저장...")
    results = {
        "timestamp": datetime.now().isoformat(),
        "test_tasks_count": len(test_tasks),
        "queue_stats": queue_stats,
        "metrics": {
            "total_tasks": metrics["total_tasks"],
            "successful": metrics["successful"],
            "failed": metrics["failed"],
            "success_rate": metrics["success_rate"],
            "avg_duration": metrics["avg_duration"],
        },
        "workers": {
            "active": final_stats["worker_pool"]["workers"]["active"],
            "min": final_stats["worker_pool"]["workers"]["min"],
            "max": final_stats["worker_pool"]["workers"]["max"],
        },
        "database": db_stats,
    }

    with open("PHASE2_4_TEST_REPORT.json", "w") as f:
        json.dump(results, f, indent=2)

    print(f"✅ 결과 저장 완료: PHASE2_4_TEST_REPORT.json")

    print("\n" + "="*80)
    print("✅ Phase 2.4 테스트 완료!")
    print("="*80 + "\n")

    return results


if __name__ == "__main__":
    asyncio.run(test_phase2_4())
