"""
작업 큐 서비스 (분산 크롤링용)

주요 기능:
1. 작업 생성 및 큐잉
2. 작업 상태 추적
3. 우선순위 기반 작업 할당
4. 작업 재시도
"""

import logging
import hashlib
import heapq
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class TaskStatus(Enum):
    """작업 상태"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"


class TaskPriority(Enum):
    """작업 우선순위"""
    LOW = -1
    NORMAL = 0
    HIGH = 1
    CRITICAL = 2


@dataclass
class CrawlTask:
    """크롤링 작업"""
    url: str
    university_name: str
    department_name: str = ""
    priority: int = TaskPriority.NORMAL.value
    created_at: datetime = field(default_factory=datetime.now)
    task_id: str = field(default="")
    status: str = field(default="pending")
    retry_count: int = field(default=0)
    max_retries: int = field(default=3)

    # 크롤러 설정
    use_cache: bool = True
    use_ocr: bool = False
    parallel_crawl: bool = False
    timeout_seconds: int = 30

    def __post_init__(self):
        if not self.task_id:
            # URL과 타임스탬프로 고유 ID 생성
            hash_input = f"{self.url}{self.created_at.isoformat()}"
            self.task_id = hashlib.md5(hash_input.encode()).hexdigest()

    def __lt__(self, other):
        """우선순위 큐 비교 (높은 우선순위가 먼저)"""
        if self.priority != other.priority:
            return self.priority > other.priority
        return self.created_at < other.created_at

    def __repr__(self):
        return f"<CrawlTask {self.task_id[:8]}... {self.university_name}>"


class InMemoryTaskQueue:
    """메모리 기반 작업 큐"""

    def __init__(self, max_size: int = 10000):
        """
        초기화

        Args:
            max_size: 최대 큐 크기
        """
        self.max_size = max_size
        self.pending_queue = []  # 우선순위 큐
        self.running_tasks: Dict[str, CrawlTask] = {}  # task_id -> Task
        self.completed_tasks: Dict[str, CrawlTask] = {}  # task_id -> Task
        self.failed_tasks: Dict[str, CrawlTask] = {}  # task_id -> Task
        self.task_registry: Dict[str, CrawlTask] = {}  # task_id -> Task (모든 상태)

        logger.info(f"🚀 InMemoryTaskQueue 초기화 (max_size={max_size})")

    def enqueue(self, task: CrawlTask) -> str:
        """작업 큐에 추가"""
        if len(self.task_registry) >= self.max_size:
            logger.warning(f"⚠️  큐 크기 초과: {len(self.task_registry)}/{self.max_size}")
            return None

        task.status = TaskStatus.PENDING.value
        heapq.heappush(self.pending_queue, task)
        self.task_registry[task.task_id] = task

        logger.info(f"📝 작업 추가: {task.task_id[:8]}... {task.university_name}")
        return task.task_id

    def dequeue(self) -> Optional[CrawlTask]:
        """대기 중인 다음 작업 획득"""
        while self.pending_queue:
            task = heapq.heappop(self.pending_queue)
            if task.status == TaskStatus.PENDING.value:
                task.status = TaskStatus.RUNNING.value
                self.running_tasks[task.task_id] = task
                logger.info(f"🏃 작업 시작: {task.task_id[:8]}... {task.university_name}")
                return task

        return None

    def mark_completed(self, task_id: str) -> bool:
        """작업 완료 표시"""
        if task_id not in self.task_registry:
            logger.warning(f"⚠️  작업을 찾을 수 없음: {task_id}")
            return False

        task = self.task_registry[task_id]
        task.status = TaskStatus.COMPLETED.value

        if task_id in self.running_tasks:
            del self.running_tasks[task_id]

        self.completed_tasks[task_id] = task
        logger.info(f"✅ 작업 완료: {task_id[:8]}...")
        return True

    def mark_failed(self, task_id: str, error: str = "") -> bool:
        """작업 실패 표시"""
        if task_id not in self.task_registry:
            return False

        task = self.task_registry[task_id]

        # 재시도 가능 여부 확인
        if task.retry_count < task.max_retries:
            task.retry_count += 1
            task.status = TaskStatus.RETRYING.value
            heapq.heappush(self.pending_queue, task)
            logger.warning(f"🔄 작업 재시도: {task_id[:8]}... (시도 {task.retry_count}/{task.max_retries})")
            return True
        else:
            task.status = TaskStatus.FAILED.value
            if task_id in self.running_tasks:
                del self.running_tasks[task_id]
            self.failed_tasks[task_id] = task
            logger.error(f"❌ 작업 실패: {task_id[:8]}... {error}")
            return False

    def get_task_status(self, task_id: str) -> Optional[str]:
        """작업 상태 조회"""
        if task_id not in self.task_registry:
            return None
        return self.task_registry[task_id].status

    def get_stats(self) -> Dict:
        """큐 통계"""
        return {
            "pending": len(self.pending_queue),
            "running": len(self.running_tasks),
            "completed": len(self.completed_tasks),
            "failed": len(self.failed_tasks),
            "total": len(self.task_registry),
        }

    def get_queued_tasks(self, limit: int = 10) -> List[CrawlTask]:
        """대기 중인 작업 목록"""
        return [t for t in self.pending_queue[:limit] if t.status == TaskStatus.PENDING.value]

    def get_running_tasks(self) -> List[CrawlTask]:
        """실행 중인 작업 목록"""
        return list(self.running_tasks.values())

    def clear(self):
        """모든 작업 초기화"""
        self.pending_queue.clear()
        self.running_tasks.clear()
        self.completed_tasks.clear()
        self.failed_tasks.clear()
        self.task_registry.clear()
        logger.info("🗑️  모든 작업 초기화")

    def health_check(self) -> Dict:
        """상태 확인"""
        return {
            "status": "healthy",
            "queue_stats": self.get_stats(),
            "queue_size_percent": (len(self.task_registry) / self.max_size) * 100,
        }


# 전역 큐 인스턴스
_queue_instance: Optional[InMemoryTaskQueue] = None


def get_task_queue(max_size: int = 10000) -> InMemoryTaskQueue:
    """전역 작업 큐 인스턴스 획득"""
    global _queue_instance
    if _queue_instance is None:
        _queue_instance = InMemoryTaskQueue(max_size=max_size)
    return _queue_instance
