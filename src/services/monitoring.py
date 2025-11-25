"""
실시간 모니터링 및 메트릭 서비스

주요 기능:
1. 크롤링 성능 메트릭 수집
2. 워커 상태 모니터링
3. 큐 상태 모니터링
4. 실시간 대시보드 데이터
"""

import logging
import time
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from collections import defaultdict, deque

logger = logging.getLogger(__name__)


class MetricsCollector:
    """메트릭 수집기"""

    def __init__(self, window_size: int = 3600):  # 1시간 윈도우
        """
        초기화

        Args:
            window_size: 메트릭 보관 시간 (초)
        """
        self.window_size = window_size
        self.metrics_history: deque = deque(maxlen=1000)  # 최근 1000개 메트릭

        # 시간별 집계
        self.hourly_stats = defaultdict(lambda: {
            "tasks_processed": 0,
            "tasks_failed": 0,
            "total_time": 0.0,
            "errors": []
        })

        logger.info(f"🚀 MetricsCollector 초기화 (윈도우={window_size}초)")

    def record_task_completion(self, task_id: str, duration: float, success: bool = True, error: str = ""):
        """작업 완료 기록"""
        metric = {
            "timestamp": datetime.now(),
            "task_id": task_id,
            "duration": duration,
            "success": success,
            "error": error,
        }
        self.metrics_history.append(metric)

        # 시간별 집계
        hour = datetime.now().strftime("%Y-%m-%d %H:00")
        if success:
            self.hourly_stats[hour]["tasks_processed"] += 1
            self.hourly_stats[hour]["total_time"] += duration
        else:
            self.hourly_stats[hour]["tasks_failed"] += 1
            if error:
                self.hourly_stats[hour]["errors"].append(error)

    def get_current_metrics(self) -> Dict:
        """현재 메트릭 조회"""
        if not self.metrics_history:
            return self._empty_metrics()

        recent_metrics = list(self.metrics_history)[-100:]  # 최근 100개

        successful = [m for m in recent_metrics if m["success"]]
        failed = [m for m in recent_metrics if not m["success"]]

        return {
            "total_tasks": len(recent_metrics),
            "successful": len(successful),
            "failed": len(failed),
            "success_rate": len(successful) / len(recent_metrics) * 100 if recent_metrics else 0,
            "avg_duration": sum(m["duration"] for m in successful) / len(successful) if successful else 0,
            "min_duration": min(m["duration"] for m in successful) if successful else 0,
            "max_duration": max(m["duration"] for m in successful) if successful else 0,
            "latest_errors": [m["error"] for m in failed[-5:]],
        }

    def get_hourly_stats(self, hours: int = 24) -> Dict:
        """시간별 통계"""
        stats = {}
        for hour_str, hour_data in sorted(self.hourly_stats.items())[-hours:]:
            processed = hour_data["tasks_processed"]
            failed = hour_data["tasks_failed"]
            total = processed + failed

            stats[hour_str] = {
                "processed": processed,
                "failed": failed,
                "total": total,
                "success_rate": processed / total * 100 if total > 0 else 0,
                "avg_duration": hour_data["total_time"] / processed if processed > 0 else 0,
            }

        return stats

    def _empty_metrics(self) -> Dict:
        """빈 메트릭"""
        return {
            "total_tasks": 0,
            "successful": 0,
            "failed": 0,
            "success_rate": 0,
            "avg_duration": 0,
            "min_duration": 0,
            "max_duration": 0,
            "latest_errors": [],
        }


class HealthChecker:
    """건강 상태 확인"""

    def __init__(self):
        """초기화"""
        self.last_check = datetime.now()
        self.status_history: deque = deque(maxlen=100)
        logger.info("🚀 HealthChecker 초기화")

    def check_health(
        self,
        worker_pool_stats: Dict,
        queue_stats: Dict,
        metrics: Dict
    ) -> Dict:
        """건강 상태 확인"""
        health = {
            "timestamp": datetime.now().isoformat(),
            "overall_status": "healthy",
            "components": {}
        }

        # 워커 풀 확인
        worker_status = "healthy"
        if worker_pool_stats["workers"]["active"] == 0:
            worker_status = "critical"
            health["overall_status"] = "critical"
        elif worker_pool_stats["workers"]["active"] < worker_pool_stats["workers"]["min"]:
            worker_status = "degraded"
            if health["overall_status"] == "healthy":
                health["overall_status"] = "degraded"

        health["components"]["workers"] = {
            "status": worker_status,
            "active": worker_pool_stats["workers"]["active"],
            "min": worker_pool_stats["workers"]["min"],
            "max": worker_pool_stats["workers"]["max"],
        }

        # 큐 확인
        queue_status = "healthy"
        queue_full_percent = queue_stats.get("queue_size_percent", 0)
        if queue_full_percent > 90:
            queue_status = "critical"
            health["overall_status"] = "critical"
        elif queue_full_percent > 70:
            queue_status = "degraded"
            if health["overall_status"] == "healthy":
                health["overall_status"] = "degraded"

        health["components"]["queue"] = {
            "status": queue_status,
            "pending": queue_stats["pending"],
            "running": queue_stats["running"],
            "full_percent": queue_full_percent,
        }

        # 메트릭 확인
        metrics_status = "healthy"
        if metrics["success_rate"] < 80:
            metrics_status = "degraded"
            if health["overall_status"] == "healthy":
                health["overall_status"] = "degraded"
        if metrics["success_rate"] < 50:
            metrics_status = "critical"
            health["overall_status"] = "critical"

        health["components"]["metrics"] = {
            "status": metrics_status,
            "success_rate": metrics["success_rate"],
            "failed_count": metrics["failed"],
        }

        self.status_history.append(health)
        return health


class RealtimeDashboard:
    """실시간 대시보드 데이터"""

    def __init__(
        self,
        metrics_collector: MetricsCollector,
        health_checker: HealthChecker
    ):
        """초기화"""
        self.metrics_collector = metrics_collector
        self.health_checker = health_checker
        logger.info("🚀 RealtimeDashboard 초기화")

    def get_dashboard_data(
        self,
        worker_pool_stats: Dict,
        queue_stats: Dict
    ) -> Dict:
        """대시보드 데이터 조회"""
        metrics = self.metrics_collector.get_current_metrics()
        health = self.health_checker.check_health(worker_pool_stats, queue_stats, metrics)
        hourly = self.metrics_collector.get_hourly_stats(hours=24)

        return {
            "timestamp": datetime.now().isoformat(),
            "health": health,
            "metrics": metrics,
            "workers": {
                "active": worker_pool_stats["workers"]["active"],
                "min": worker_pool_stats["workers"]["min"],
                "max": worker_pool_stats["workers"]["max"],
                "stats": worker_pool_stats["workers"]["stats"][:5],  # 상위 5개만
            },
            "queue": {
                "pending": queue_stats["pending"],
                "running": queue_stats["running"],
                "completed": queue_stats["completed"],
                "failed": queue_stats["failed"],
                "total": queue_stats["total"],
            },
            "hourly_stats": hourly,
        }

    def print_dashboard(self, dashboard_data: Dict):
        """대시보드 출력"""
        print("\n" + "="*80)
        print("📊 실시간 크롤링 대시보드")
        print("="*80)

        health = dashboard_data["health"]
        print(f"\n🔹 상태: {health['overall_status'].upper()}")

        metrics = dashboard_data["metrics"]
        print(f"\n📈 메트릭:")
        print(f"   총 작업: {metrics['total_tasks']}")
        print(f"   성공: {metrics['successful']} ({metrics['success_rate']:.1f}%)")
        print(f"   실패: {metrics['failed']}")
        print(f"   평균 시간: {metrics['avg_duration']:.2f}초")

        workers = dashboard_data["workers"]
        print(f"\n👷 워커:")
        print(f"   활성: {workers['active']} (범위: {workers['min']}-{workers['max']})")

        queue = dashboard_data["queue"]
        print(f"\n📋 큐:")
        print(f"   대기: {queue['pending']}")
        print(f"   실행 중: {queue['running']}")
        print(f"   완료: {queue['completed']}")
        print(f"   실패: {queue['failed']}")

        print(f"\n{'='*80}\n")


# 전역 모니터링 인스턴스
_metrics_collector: Optional[MetricsCollector] = None
_health_checker: Optional[HealthChecker] = None
_dashboard: Optional[RealtimeDashboard] = None


def get_metrics_collector() -> MetricsCollector:
    """전역 메트릭 수집기"""
    global _metrics_collector
    if _metrics_collector is None:
        _metrics_collector = MetricsCollector()
    return _metrics_collector


def get_health_checker() -> HealthChecker:
    """전역 건강 상태 확인기"""
    global _health_checker
    if _health_checker is None:
        _health_checker = HealthChecker()
    return _health_checker


def get_dashboard() -> RealtimeDashboard:
    """전역 대시보드"""
    global _dashboard
    if _dashboard is None:
        _dashboard = RealtimeDashboard(get_metrics_collector(), get_health_checker())
    return _dashboard
