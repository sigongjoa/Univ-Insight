"""
Redis 기반 분산 작업 큐

주요 기능:
1. 다중 머신 간 작업 공유
2. 우선순위 기반 스케줄링
3. 작업 상태 중앙 관리
4. 자동 재시도 및 실패 처리
"""

import json
import logging
import hashlib
from typing import Optional, Dict, List
from datetime import datetime, timedelta
import asyncio

try:
    import aioredis
    from aioredis import Redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    logging.warning("⚠️  aioredis 미설치 - Redis 기능 사용 불가")

from src.services.task_queue import CrawlTask, TaskStatus, TaskPriority

logger = logging.getLogger(__name__)


class RedisTaskQueue:
    """Redis 기반 분산 작업 큐"""

    def __init__(
        self,
        redis_url: str = "redis://localhost:6379/0",
        ttl_hours: int = 24,
        fallback_to_memory: bool = True
    ):
        """
        초기화

        Args:
            redis_url: Redis 연결 URL
            ttl_hours: 작업 TTL (시간)
            fallback_to_memory: Redis 미연결 시 메모리 폴백
        """
        self.redis_url = redis_url
        self.ttl_hours = ttl_hours
        self.fallback_to_memory = fallback_to_memory
        self.redis: Optional[Redis] = None
        self.memory_fallback = {} if fallback_to_memory else None

        # Redis 키 프리픽스
        self.prefix = "crawl:"
        self.queue_key = f"{self.prefix}queue"
        self.task_key = f"{self.prefix}task:"
        self.result_key = f"{self.prefix}result:"

        logger.info(f"🚀 RedisTaskQueue 초기화 ({redis_url})")

    async def connect(self):
        """Redis 연결"""
        if not REDIS_AVAILABLE:
            logger.warning("⚠️  Redis 사용 불가 - 메모리 모드로 폴백")
            return

        try:
            self.redis = await aioredis.create_redis_pool(self.redis_url)
            logger.info("✅ Redis 연결 성공")
        except Exception as e:
            logger.error(f"❌ Redis 연결 실패: {e}")
            if self.fallback_to_memory:
                logger.warning("⚠️  메모리 모드로 폴백")
            else:
                raise

    async def disconnect(self):
        """Redis 연결 해제"""
        if self.redis:
            self.redis.close()
            await self.redis.wait_closed()
            logger.info("✅ Redis 연결 해제")

    async def enqueue(self, task: CrawlTask) -> str:
        """작업 큐에 추가"""
        task_json = self._serialize_task(task)

        if self.redis:
            try:
                # 작업 저장
                await self.redis.set(
                    f"{self.task_key}{task.task_id}",
                    task_json,
                    expire=int(self.ttl_hours * 3600)
                )

                # 우선순위 큐에 추가
                await self.redis.zadd(
                    self.queue_key,
                    -task.priority,  # 음수로 하면 높은 우선순위 먼저
                    task.task_id
                )

                logger.info(f"📝 작업 추가 (Redis): {task.task_id[:8]}...")
                return task.task_id

            except Exception as e:
                logger.error(f"❌ Redis 저장 실패: {e}")
                if self.fallback_to_memory:
                    return self._enqueue_memory(task, task_json)
                raise
        else:
            return self._enqueue_memory(task, task_json)

    def _enqueue_memory(self, task: CrawlTask, task_json: str) -> str:
        """메모리에 작업 저장 (폴백)"""
        self.memory_fallback[task.task_id] = {
            "task": task,
            "json": task_json,
            "priority": -task.priority
        }
        logger.info(f"📝 작업 추가 (메모리): {task.task_id[:8]}...")
        return task.task_id

    async def dequeue(self, worker_id: str = "default") -> Optional[CrawlTask]:
        """다음 작업 획득"""
        if self.redis:
            try:
                # 우선순위 가장 높은 작업 획득
                result = await self.redis.zrange(self.queue_key, 0, 0)
                if not result:
                    return None

                task_id = result[0].decode() if isinstance(result[0], bytes) else result[0]

                # 작업 로드
                task_json = await self.redis.get(f"{self.task_key}{task_id}")
                if not task_json:
                    # 큐에서 제거
                    await self.redis.zrem(self.queue_key, task_id)
                    return None

                task = self._deserialize_task(task_json)
                task.status = TaskStatus.RUNNING.value

                # 워커 정보 저장
                await self.redis.hset(
                    f"{self.prefix}running:{task_id}",
                    "worker_id", worker_id,
                    "started_at", datetime.now().isoformat()
                )

                # 큐에서 제거
                await self.redis.zrem(self.queue_key, task_id)

                logger.info(f"🏃 작업 시작: {task_id[:8]}... (워커: {worker_id})")
                return task

            except Exception as e:
                logger.error(f"❌ Redis 작업 획득 실패: {e}")
                if self.fallback_to_memory:
                    return self._dequeue_memory()
                return None
        else:
            return self._dequeue_memory()

    def _dequeue_memory(self) -> Optional[CrawlTask]:
        """메모리에서 작업 획득 (폴백)"""
        if not self.memory_fallback:
            return None

        # 우선순위 가장 높은 작업 찾기
        best_task_id = min(
            self.memory_fallback.keys(),
            key=lambda k: self.memory_fallback[k]["priority"]
        )

        task = self.memory_fallback[best_task_id]["task"]
        del self.memory_fallback[best_task_id]

        return task

    async def mark_completed(self, task_id: str) -> bool:
        """작업 완료 표시"""
        if self.redis:
            try:
                await self.redis.set(
                    f"{self.prefix}completed:{task_id}",
                    datetime.now().isoformat(),
                    expire=int(self.ttl_hours * 3600)
                )
                await self.redis.delete(f"{self.prefix}running:{task_id}")
                await self.redis.delete(f"{self.task_key}{task_id}")
                logger.info(f"✅ 작업 완료: {task_id[:8]}...")
                return True
            except Exception as e:
                logger.error(f"❌ 작업 완료 표시 실패: {e}")
                return False
        return True

    async def mark_failed(self, task_id: str, error: str = "") -> bool:
        """작업 실패 표시"""
        if self.redis:
            try:
                await self.redis.hset(
                    f"{self.prefix}failed:{task_id}",
                    "error", error,
                    "timestamp", datetime.now().isoformat()
                )
                await self.redis.delete(f"{self.prefix}running:{task_id}")
                logger.error(f"❌ 작업 실패: {task_id[:8]}... {error}")
                return True
            except Exception as e:
                logger.error(f"❌ 작업 실패 표시 실패: {e}")
                return False
        return True

    async def get_task_status(self, task_id: str) -> Optional[str]:
        """작업 상태 조회"""
        if self.redis:
            try:
                # 실행 중 확인
                if await self.redis.exists(f"{self.prefix}running:{task_id}"):
                    return TaskStatus.RUNNING.value

                # 완료 확인
                if await self.redis.exists(f"{self.prefix}completed:{task_id}"):
                    return TaskStatus.COMPLETED.value

                # 실패 확인
                if await self.redis.exists(f"{self.prefix}failed:{task_id}"):
                    return TaskStatus.FAILED.value

                # 큐에 있는지 확인
                if await self.redis.zrank(self.queue_key, task_id) is not None:
                    return TaskStatus.PENDING.value

                return None

            except Exception as e:
                logger.error(f"❌ 상태 조회 실패: {e}")
                return None
        return None

    async def get_stats(self) -> Dict:
        """큐 통계"""
        if self.redis:
            try:
                pending = await self.redis.zcard(self.queue_key)
                running = await self.redis.dbsize()  # 근사값
                return {
                    "pending": pending,
                    "running": running,
                    "completed": 0,  # 추적 필요
                    "failed": 0,      # 추적 필요
                    "total": pending + running,
                }
            except Exception as e:
                logger.error(f"❌ 통계 조회 실패: {e}")
                return {"error": str(e)}
        return {}

    async def health_check(self) -> Dict:
        """건강 상태 확인"""
        if not self.redis:
            return {
                "status": "unhealthy",
                "reason": "Redis not available"
            }

        try:
            await self.redis.ping()
            return {
                "status": "healthy",
                "redis_connected": True,
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "redis_connected": False,
                "error": str(e)
            }

    def _serialize_task(self, task: CrawlTask) -> str:
        """작업을 JSON으로 직렬화"""
        return json.dumps({
            "task_id": task.task_id,
            "url": task.url,
            "university_name": task.university_name,
            "department_name": task.department_name,
            "priority": task.priority,
            "created_at": task.created_at.isoformat(),
            "status": task.status,
            "retry_count": task.retry_count,
            "max_retries": task.max_retries,
            "use_cache": task.use_cache,
            "use_ocr": task.use_ocr,
            "parallel_crawl": task.parallel_crawl,
            "timeout_seconds": task.timeout_seconds,
        })

    def _deserialize_task(self, task_json) -> CrawlTask:
        """JSON에서 작업으로 역직렬화"""
        if isinstance(task_json, bytes):
            task_json = task_json.decode()

        data = json.loads(task_json)

        return CrawlTask(
            url=data["url"],
            university_name=data["university_name"],
            department_name=data.get("department_name", ""),
            priority=data.get("priority", 0),
            task_id=data["task_id"],
            status=data.get("status", TaskStatus.PENDING.value),
            retry_count=data.get("retry_count", 0),
            max_retries=data.get("max_retries", 3),
            use_cache=data.get("use_cache", True),
            use_ocr=data.get("use_ocr", False),
            parallel_crawl=data.get("parallel_crawl", False),
            timeout_seconds=data.get("timeout_seconds", 30),
        )


# 전역 Redis 큐 인스턴스
_redis_queue_instance: Optional[RedisTaskQueue] = None


async def get_redis_queue(redis_url: str = None) -> RedisTaskQueue:
    """전역 Redis 큐 인스턴스"""
    global _redis_queue_instance
    if _redis_queue_instance is None:
        _redis_queue_instance = RedisTaskQueue(
            redis_url=redis_url or "redis://localhost:6379/0"
        )
        await _redis_queue_instance.connect()
    return _redis_queue_instance
