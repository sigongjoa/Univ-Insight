"""
FastAPI REST API v2 (Phase 2.5)

분산 크롤링 시스템을 위한 RESTful 엔드포인트

주요 엔드포인트:
1. /tasks - 작업 관리
2. /status - 상태 조회
3. /results - 결과 조회
4. /workers - 워커 관리
5. /metrics - 메트릭
"""

import logging
from typing import List, Dict, Optional
from datetime import datetime

from fastapi import FastAPI, HTTPException, Depends, Query, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from src.database.db import get_db, Database
from src.services.distributed_crawler import DistributedCrawler
from src.services.task_queue import CrawlTask, TaskPriority
from src.services.redis_queue import get_redis_queue

logger = logging.getLogger(__name__)


# ===================== Pydantic 모델 =====================

class TaskSubmitRequest(BaseModel):
    """작업 제출 요청"""
    url: str
    university_name: str
    department_name: str = ""
    priority: int = TaskPriority.NORMAL.value
    use_cache: bool = True
    use_ocr: bool = False


class BulkTaskSubmitRequest(BaseModel):
    """대량 작업 제출 요청"""
    tasks: List[TaskSubmitRequest]


class TaskStatusResponse(BaseModel):
    """작업 상태 응답"""
    task_id: str
    status: str
    university_name: str
    url: str
    created_at: str


class QueueStatsResponse(BaseModel):
    """큐 통계 응답"""
    pending: int
    running: int
    completed: int
    failed: int
    total: int


class WorkerStatsResponse(BaseModel):
    """워커 통계 응답"""
    worker_id: str
    status: str
    tasks_completed: int
    tasks_failed: int
    current_task: Optional[str]


class HealthResponse(BaseModel):
    """건강 상태 응답"""
    status: str
    timestamp: str
    components: Dict


# ===================== FastAPI 앱 설정 =====================

def create_app(db: Database, crawler: DistributedCrawler) -> FastAPI:
    """FastAPI 앱 생성"""
    app = FastAPI(
        title="Univ-Insight API v2",
        description="분산 대학 논문 크롤링 시스템",
        version="2.0.0"
    )

    # CORS 설정
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 인증 의존성
    async def verify_api_key(x_api_key: str = Header(None)):
        """API 키 검증 (선택사항)"""
        if x_api_key is None:
            # 개발 모드에서는 선택사항
            return "default"
        # TODO: 실제 API 키 검증 로직
        return x_api_key

    # ===================== 작업 엔드포인트 =====================

    @app.post("/api/v2/tasks", response_model=Dict)
    async def submit_task(
        request: TaskSubmitRequest,
        api_key: str = Depends(verify_api_key)
    ):
        """
        새로운 작업 제출

        - **url**: 크롤링할 URL
        - **university_name**: 대학 이름
        - **priority**: 우선순위 (-1: 낮음, 0: 보통, 1: 높음, 2: 긴급)
        """
        try:
            task_id = await crawler.submit_task(
                url=request.url,
                university_name=request.university_name,
                department_name=request.department_name,
                priority=request.priority,
                use_cache=request.use_cache,
                use_ocr=request.use_ocr,
            )

            logger.info(f"📝 작업 제출 (API): {task_id}")

            return {
                "task_id": task_id,
                "status": "pending",
                "created_at": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"❌ 작업 제출 실패: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    @app.post("/api/v2/tasks/bulk", response_model=Dict)
    async def submit_bulk_tasks(
        request: BulkTaskSubmitRequest,
        api_key: str = Depends(verify_api_key)
    ):
        """
        대량 작업 제출

        최대 1000개까지 한 번에 제출 가능
        """
        if len(request.tasks) > 1000:
            raise HTTPException(
                status_code=400,
                detail="최대 1000개까지만 제출 가능합니다"
            )

        try:
            tasks = [
                (t.url, t.university_name, t.department_name)
                for t in request.tasks
            ]

            task_ids = await crawler.submit_bulk(tasks)

            logger.info(f"📦 대량 작업 제출 (API): {len(task_ids)}개")

            return {
                "submitted": len(task_ids),
                "task_ids": task_ids,
                "created_at": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"❌ 대량 작업 제출 실패: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    # ===================== 상태 엔드포인트 =====================

    @app.get("/api/v2/tasks/{task_id}", response_model=TaskStatusResponse)
    async def get_task_status(
        task_id: str,
        api_key: str = Depends(verify_api_key)
    ):
        """작업 상태 조회"""
        try:
            status = crawler.get_task_status(task_id)

            if status is None:
                raise HTTPException(status_code=404, detail="작업을 찾을 수 없습니다")

            return {
                "task_id": task_id,
                "status": status,
                "university_name": "Unknown",
                "url": "Unknown",
                "created_at": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"❌ 상태 조회 실패: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    # ===================== 통계 엔드포인트 =====================

    @app.get("/api/v2/stats", response_model=Dict)
    async def get_stats(api_key: str = Depends(verify_api_key)):
        """전체 통계 조회"""
        try:
            stats = crawler.get_stats()
            return stats

        except Exception as e:
            logger.error(f"❌ 통계 조회 실패: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/api/v2/queue", response_model=QueueStatsResponse)
    async def get_queue_stats(api_key: str = Depends(verify_api_key)):
        """큐 통계 조회"""
        try:
            stats = crawler.get_stats()
            queue_stats = stats["queue"]

            return QueueStatsResponse(**queue_stats)

        except Exception as e:
            logger.error(f"❌ 큐 통계 조회 실패: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/api/v2/workers", response_model=Dict)
    async def get_workers(api_key: str = Depends(verify_api_key)):
        """워커 목록 조회"""
        try:
            stats = crawler.get_stats()
            workers = stats["worker_pool"]["workers"]["stats"]

            return {
                "active": len(workers),
                "workers": workers,
            }

        except Exception as e:
            logger.error(f"❌ 워커 조회 실패: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    # ===================== 대시보드 엔드포인트 =====================

    @app.get("/api/v2/dashboard", response_model=Dict)
    async def get_dashboard(api_key: str = Depends(verify_api_key)):
        """실시간 대시보드 데이터"""
        try:
            dashboard = crawler.get_dashboard_data()
            return dashboard

        except Exception as e:
            logger.error(f"❌ 대시보드 조회 실패: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/api/v2/health", response_model=HealthResponse)
    async def health_check(api_key: str = Depends(verify_api_key)):
        """건강 상태 확인"""
        try:
            stats = crawler.get_stats()
            health = {
                "status": "healthy" if stats["worker_pool"]["workers"]["active"] > 0 else "unhealthy",
                "timestamp": datetime.now().isoformat(),
                "components": {
                    "database": "ok",
                    "queue": f"{stats['queue']['pending']} pending",
                    "workers": f"{stats['worker_pool']['workers']['active']} active",
                }
            }
            return health

        except Exception as e:
            logger.error(f"❌ 건강 상태 확인 실패: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    # ===================== 제어 엔드포인트 =====================

    @app.post("/api/v2/control/start")
    async def start_crawler(api_key: str = Depends(verify_api_key)):
        """크롤러 시작"""
        try:
            if not crawler.running:
                await crawler.start()
            return {
                "status": "started",
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.post("/api/v2/control/stop")
    async def stop_crawler(api_key: str = Depends(verify_api_key)):
        """크롤러 중지"""
        try:
            if crawler.running:
                await crawler.stop()
            return {
                "status": "stopped",
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    # ===================== 헬스 체크 =====================

    @app.get("/health")
    async def root_health():
        """기본 헬스 체크"""
        return {"status": "ok"}

    return app
