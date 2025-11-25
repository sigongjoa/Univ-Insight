"""
워커 풀 서비스 (분산 크롤링 워커)

주요 기능:
1. 워커 풀 생성 및 관리
2. 작업 할당 및 처리
3. 워커 모니터링
4. 자동 스케일링
"""

import asyncio
import logging
import uuid
from typing import Optional, Dict, List, Callable, Awaitable
from datetime import datetime
from dataclasses import dataclass, field

from src.services.task_queue import CrawlTask, InMemoryTaskQueue, TaskStatus
from src.services.multipage_crawler import MultipageCrawler
from src.database.db import Database

logger = logging.getLogger(__name__)


@dataclass
class WorkerStats:
    """워커 통계"""
    worker_id: str
    status: str  # idle, running
    tasks_completed: int = 0
    tasks_failed: int = 0
    total_processing_time: float = 0.0
    current_task: Optional[str] = None
    current_task_start: Optional[datetime] = None

    def get_processing_time(self) -> float:
        """현재 작업 처리 시간"""
        if self.current_task_start:
            return (datetime.now() - self.current_task_start).total_seconds()
        return 0.0

    def __repr__(self):
        return f"<Worker {self.worker_id[:8]}... completed={self.tasks_completed} failed={self.tasks_failed}>"


class Worker:
    """크롤링 워커"""

    def __init__(
        self,
        worker_id: str,
        task_queue: InMemoryTaskQueue,
        database: Database,
        crawler: Optional[MultipageCrawler] = None
    ):
        """
        초기화

        Args:
            worker_id: 워커 ID
            task_queue: 작업 큐
            database: 데이터베이스
            crawler: 크롤러 인스턴스
        """
        self.worker_id = worker_id
        self.task_queue = task_queue
        self.database = database
        self.crawler = crawler or MultipageCrawler()
        self.stats = WorkerStats(worker_id=worker_id, status="idle")
        self.running = False

        logger.info(f"🚀 Worker 초기화: {worker_id}")

    async def initialize(self):
        """워커 초기화 (크롤러 준비)"""
        await self.crawler.initialize()
        logger.info(f"✅ Worker 초기화 완료: {self.worker_id}")

    async def run(self, max_tasks: int = 0):
        """워커 실행"""
        self.running = True
        tasks_processed = 0

        logger.info(f"🏃 Worker 시작: {self.worker_id}")

        while self.running:
            # 작업 획득
            task = self.task_queue.dequeue()
            if not task:
                # 대기 중인 작업 없음
                await asyncio.sleep(1)
                continue

            # 작업 처리
            success = await self._process_task(task)

            # 결과 저장
            if success:
                self.task_queue.mark_completed(task.task_id)
                self.stats.tasks_completed += 1
            else:
                self.task_queue.mark_failed(task.task_id)
                self.stats.tasks_failed += 1

            tasks_processed += 1
            if max_tasks > 0 and tasks_processed >= max_tasks:
                break

        logger.info(f"⏹️  Worker 중지: {self.worker_id}")
        self.running = False

    async def _process_task(self, task: CrawlTask) -> bool:
        """작업 처리"""
        self.stats.status = "running"
        self.stats.current_task = task.task_id
        self.stats.current_task_start = datetime.now()

        try:
            logger.info(f"📝 작업 처리 중: {task.task_id[:8]}... {task.university_name}")

            # 크롤링 수행
            result = await self.crawler.crawl_department(
                task.url,
                task.department_name or task.university_name
            )

            # 결과 저장
            self._save_result(task, result)

            processing_time = (datetime.now() - self.stats.current_task_start).total_seconds()
            self.stats.total_processing_time += processing_time

            logger.info(f"✅ 작업 완료: {task.task_id[:8]}... ({processing_time:.1f}초)")
            return True

        except Exception as e:
            logger.error(f"❌ 작업 처리 오류: {task.task_id[:8]}... {e}")
            return False

        finally:
            self.stats.status = "idle"
            self.stats.current_task = None
            self.stats.current_task_start = None

    def _save_result(self, task: CrawlTask, result: Dict):
        """결과를 데이터베이스에 저장"""
        try:
            with self.database.session_scope() as session:
                # CrawlTask 저장
                from src.database import CrawlTask as DBCrawlTask
                from src.database import CrawlResult

                db_task = DBCrawlTask(
                    id=task.task_id,
                    url=task.url,
                    university_name=task.university_name,
                    department_name=task.department_name,
                    status="completed"
                )
                session.add(db_task)
                session.flush()

                # CrawlResult 저장
                result_id = f"{task.task_id}_{hash(str(result))}"
                db_result = CrawlResult(
                    id=result_id,
                    task_id=task.task_id,
                    url=task.url,
                    university_name=task.university_name,
                    professors_count=result.get("extraction_stats", {}).get("professors_count", 0),
                    papers_count=result.get("extraction_stats", {}).get("papers_count", 0),
                    labs_count=result.get("extraction_stats", {}).get("labs_count", 0),
                    pages_crawled=result.get("extraction_stats", {}).get("pages_crawled", 0),
                )
                session.add(db_result)

        except Exception as e:
            logger.error(f"❌ 결과 저장 오류: {e}")

    async def stop(self):
        """워커 중지"""
        self.running = False
        await self.crawler.close()
        logger.info(f"⏹️  Worker 종료: {self.worker_id}")

    def get_stats(self) -> Dict:
        """통계 반환"""
        return {
            "worker_id": self.worker_id,
            "status": self.stats.status,
            "tasks_completed": self.stats.tasks_completed,
            "tasks_failed": self.stats.tasks_failed,
            "total_processing_time": self.stats.total_processing_time,
            "current_task": self.stats.current_task,
            "current_task_duration": self.stats.get_processing_time(),
        }


class WorkerPool:
    """워커 풀"""

    def __init__(
        self,
        task_queue: InMemoryTaskQueue,
        database: Database,
        num_workers: int = 3,
        min_workers: int = 1,
        max_workers: int = 10
    ):
        """
        초기화

        Args:
            task_queue: 작업 큐
            database: 데이터베이스
            num_workers: 초기 워커 수
            min_workers: 최소 워커 수
            max_workers: 최대 워커 수
        """
        self.task_queue = task_queue
        self.database = database
        self.num_workers = num_workers
        self.min_workers = min_workers
        self.max_workers = max_workers

        self.workers: Dict[str, Worker] = {}
        self.worker_tasks: Dict[str, asyncio.Task] = {}

        logger.info(f"🚀 WorkerPool 초기화 (워커={num_workers}, 범위={min_workers}-{max_workers})")

    async def initialize(self):
        """워커 풀 초기화"""
        for _ in range(self.num_workers):
            await self.add_worker()
        logger.info(f"✅ WorkerPool 초기화 완료 ({len(self.workers)}개 워커)")

    async def add_worker(self) -> str:
        """워커 추가"""
        if len(self.workers) >= self.max_workers:
            logger.warning(f"⚠️  최대 워커 수 도달: {len(self.workers)}/{self.max_workers}")
            return None

        worker_id = f"worker_{uuid.uuid4().hex[:8]}"
        worker = Worker(worker_id, self.task_queue, self.database)
        await worker.initialize()

        self.workers[worker_id] = worker
        logger.info(f"➕ 워커 추가: {worker_id} (총 {len(self.workers)}개)")

        return worker_id

    async def remove_worker(self, worker_id: str) -> bool:
        """워커 제거"""
        if worker_id not in self.workers:
            return False

        worker = self.workers[worker_id]
        await worker.stop()
        del self.workers[worker_id]

        if worker_id in self.worker_tasks:
            del self.worker_tasks[worker_id]

        logger.info(f"➖ 워커 제거: {worker_id} (남은 워커 {len(self.workers)}개)")
        return True

    async def start(self):
        """워커 풀 시작"""
        logger.info(f"🚀 WorkerPool 시작 ({len(self.workers)}개 워커)")

        for worker_id, worker in self.workers.items():
            task = asyncio.create_task(worker.run())
            self.worker_tasks[worker_id] = task

        logger.info("✅ 모든 워커 시작됨")

    async def stop(self):
        """워커 풀 중지"""
        logger.info("⏹️  WorkerPool 중지 중...")

        # 모든 워커 중지
        for worker_id in list(self.workers.keys()):
            await self.remove_worker(worker_id)

        # 작업 완료 대기
        if self.worker_tasks:
            await asyncio.gather(*self.worker_tasks.values(), return_exceptions=True)

        logger.info("✅ WorkerPool 중지 완료")

    async def auto_scale(self):
        """자동 스케일링"""
        stats = self.task_queue.get_stats()
        pending_tasks = stats["pending"]
        active_workers = len(self.workers)

        # 작업/워커 비율 계산
        tasks_per_worker = pending_tasks / max(active_workers, 1)

        logger.info(f"📊 스케일링 분석: {pending_tasks} 작업, {active_workers} 워커, 비율={tasks_per_worker:.1f}")

        # 스케일 업: 작업이 많을 때
        if tasks_per_worker > 5 and active_workers < self.max_workers:
            new_workers_count = min(int(tasks_per_worker / 2), self.max_workers - active_workers)
            for _ in range(new_workers_count):
                await self.add_worker()
            logger.info(f"⬆️  스케일 업: {new_workers_count}개 워커 추가")

        # 스케일 다운: 작업이 적을 때
        elif tasks_per_worker < 1 and active_workers > self.min_workers:
            workers_to_remove = min(active_workers - self.min_workers, int(active_workers * 0.5))
            worker_ids = list(self.workers.keys())[:workers_to_remove]
            for worker_id in worker_ids:
                await self.remove_worker(worker_id)
            logger.info(f"⬇️  스케일 다운: {workers_to_remove}개 워커 제거")

    def get_stats(self) -> Dict:
        """통계 반환"""
        worker_stats = [worker.get_stats() for worker in self.workers.values()]
        queue_stats = self.task_queue.get_stats()

        return {
            "workers": {
                "active": len(self.workers),
                "min": self.min_workers,
                "max": self.max_workers,
                "stats": worker_stats,
            },
            "queue": queue_stats,
            "pool_health": {
                "status": "healthy" if len(self.workers) > 0 else "unhealthy",
                "utilization": sum(w["tasks_completed"] for w in worker_stats) / max(sum(w["tasks_completed"] for w in worker_stats) + sum(w["tasks_failed"] for w in worker_stats), 1),
            }
        }
