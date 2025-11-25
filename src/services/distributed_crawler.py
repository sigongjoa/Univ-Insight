"""
분산 크롤러 오케스트레이터

주요 기능:
1. 작업 생성 및 스케줄링
2. 워커 풀 관리
3. 자동 스케일링
4. 실시간 모니터링
"""

import asyncio
import logging
from typing import List, Dict, Optional, Tuple
from datetime import datetime

from src.services.task_queue import CrawlTask, get_task_queue, TaskPriority
from src.services.worker_pool import WorkerPool
from src.services.monitoring import (
    get_metrics_collector,
    get_health_checker,
    get_dashboard,
)
from src.database.db import Database

logger = logging.getLogger(__name__)


class DistributedCrawler:
    """분산 크롤러"""

    def __init__(
        self,
        database: Database,
        num_workers: int = 3,
        min_workers: int = 1,
        max_workers: int = 10,
        auto_scale_interval: int = 30,
    ):
        """
        초기화

        Args:
            database: 데이터베이스
            num_workers: 초기 워커 수
            min_workers: 최소 워커 수
            max_workers: 최대 워커 수
            auto_scale_interval: 자동 스케일링 간격 (초)
        """
        self.database = database
        self.task_queue = get_task_queue()
        self.worker_pool = WorkerPool(
            self.task_queue,
            database,
            num_workers=num_workers,
            min_workers=min_workers,
            max_workers=max_workers,
        )

        self.auto_scale_interval = auto_scale_interval
        self.running = False

        # 모니터링
        self.metrics_collector = get_metrics_collector()
        self.health_checker = get_health_checker()
        self.dashboard = get_dashboard()

        logger.info(f"🚀 DistributedCrawler 초기화 (워커={num_workers})")

    async def initialize(self):
        """초기화"""
        await self.worker_pool.initialize()
        logger.info("✅ DistributedCrawler 초기화 완료")

    async def submit_task(
        self,
        url: str,
        university_name: str,
        department_name: str = "",
        priority: int = TaskPriority.NORMAL.value,
        use_cache: bool = True,
        use_ocr: bool = False,
    ) -> str:
        """작업 제출"""
        task = CrawlTask(
            url=url,
            university_name=university_name,
            department_name=department_name,
            priority=priority,
            use_cache=use_cache,
            use_ocr=use_ocr,
        )

        task_id = self.task_queue.enqueue(task)
        logger.info(f"📝 작업 제출: {task_id[:8]}... {university_name}")
        return task_id

    async def submit_bulk(
        self,
        tasks: List[Tuple[str, str, str]]
    ) -> List[str]:
        """대량 작업 제출"""
        task_ids = []
        for url, university_name, department_name in tasks:
            task_id = await self.submit_task(url, university_name, department_name)
            task_ids.append(task_id)

        logger.info(f"📦 {len(task_ids)}개 작업 제출 완료")
        return task_ids

    async def start(self):
        """크롤러 시작"""
        self.running = True
        logger.info("🚀 DistributedCrawler 시작")

        # 워커 풀 시작
        await self.worker_pool.start()

        # 자동 스케일링 시작
        asyncio.create_task(self._auto_scale_loop())

        # 모니터링 시작
        asyncio.create_task(self._monitoring_loop())

    async def stop(self):
        """크롤러 중지"""
        self.running = False
        logger.info("⏹️  DistributedCrawler 중지 중...")
        await self.worker_pool.stop()
        logger.info("✅ DistributedCrawler 중지 완료")

    async def _auto_scale_loop(self):
        """자동 스케일링 루프"""
        logger.info(f"⚙️  자동 스케일링 시작 (간격={self.auto_scale_interval}초)")

        while self.running:
            try:
                await asyncio.sleep(self.auto_scale_interval)
                await self.worker_pool.auto_scale()
            except Exception as e:
                logger.error(f"❌ 자동 스케일링 오류: {e}")

    async def _monitoring_loop(self):
        """모니터링 루프"""
        logger.info("📊 모니터링 시작")

        while self.running:
            try:
                await asyncio.sleep(10)  # 10초마다 대시보드 업데이트

                # 대시보드 데이터 수집
                worker_pool_stats = self.worker_pool.get_stats()
                queue_stats = self.task_queue.get_stats()

                dashboard_data = self.dashboard.get_dashboard_data(
                    worker_pool_stats, queue_stats
                )

                # 필요시 출력 (로깅)
                if queue_stats["pending"] > 0 or queue_stats["running"] > 0:
                    logger.info(
                        f"📊 상태: "
                        f"작업={queue_stats['pending']}대기 "
                        f"{queue_stats['running']}실행 | "
                        f"워커={worker_pool_stats['workers']['active']} | "
                        f"성공률={dashboard_data['metrics']['success_rate']:.1f}%"
                    )

            except Exception as e:
                logger.error(f"❌ 모니터링 오류: {e}")

    def get_task_status(self, task_id: str) -> Optional[str]:
        """작업 상태 조회"""
        return self.task_queue.get_task_status(task_id)

    def get_stats(self) -> Dict:
        """통계 조회"""
        worker_pool_stats = self.worker_pool.get_stats()
        queue_stats = self.task_queue.get_stats()
        metrics = self.metrics_collector.get_current_metrics()

        return {
            "worker_pool": worker_pool_stats,
            "queue": queue_stats,
            "metrics": metrics,
            "timestamp": datetime.now().isoformat(),
        }

    def get_dashboard_data(self) -> Dict:
        """대시보드 데이터"""
        worker_pool_stats = self.worker_pool.get_stats()
        queue_stats = self.task_queue.get_stats()
        return self.dashboard.get_dashboard_data(worker_pool_stats, queue_stats)

    def print_dashboard(self):
        """대시보드 출력"""
        dashboard_data = self.get_dashboard_data()
        self.dashboard.print_dashboard(dashboard_data)
