"""
웹 크롤링 응답 캐싱 서비스

주요 기능:
1. URL별 HTML 응답 캐싱
2. 메모리 및 디스크 캐싱 지원
3. TTL (Time To Live) 기반 캐시 만료
4. 자동 캐시 정리
"""

import json
import logging
import hashlib
from pathlib import Path
from typing import Dict, Optional, Tuple
from datetime import datetime, timedelta
import threading

logger = logging.getLogger(__name__)


class CacheService:
    """웹 크롤링 응답 캐싱"""

    def __init__(self, cache_dir: str = ".cache", ttl_hours: int = 24):
        """
        초기화

        Args:
            cache_dir: 캐시 디렉토리 경로
            ttl_hours: 캐시 유효 시간 (시간 단위)
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.ttl_hours = ttl_hours
        self.memory_cache: Dict[str, Tuple[str, datetime]] = {}
        self.lock = threading.RLock()
        logger.info(f"🚀 CacheService 초기화 (TTL={ttl_hours}시간, 경로={cache_dir})")

    def get(self, url: str, use_disk: bool = True) -> Optional[str]:
        """
        캐시에서 데이터 조회

        Args:
            url: 조회할 URL
            use_disk: 디스크 캐시 사용 여부

        Returns:
            캐시된 HTML 또는 None
        """
        cache_key = self._get_cache_key(url)

        # 메모리 캐시 확인
        with self.lock:
            if cache_key in self.memory_cache:
                html, timestamp = self.memory_cache[cache_key]
                if not self._is_expired(timestamp):
                    logger.debug(f"📦 메모리 캐시 hit: {url[:50]}...")
                    return html
                else:
                    del self.memory_cache[cache_key]

        # 디스크 캐시 확인
        if use_disk:
            cache_file = self.cache_dir / f"{cache_key}.json"
            if cache_file.exists():
                try:
                    with open(cache_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)

                    timestamp = datetime.fromisoformat(data['timestamp'])
                    if not self._is_expired(timestamp):
                        html = data['html']
                        # 메모리 캐시에도 저장
                        with self.lock:
                            self.memory_cache[cache_key] = (html, timestamp)
                        logger.debug(f"💾 디스크 캐시 hit: {url[:50]}...")
                        return html
                    else:
                        cache_file.unlink()  # 만료된 캐시 삭제

                except Exception as e:
                    logger.warning(f"   ⚠️  캐시 로드 실패: {e}")

        return None

    def set(self, url: str, html: str, use_disk: bool = True) -> None:
        """
        캐시에 데이터 저장

        Args:
            url: 저장할 URL
            html: 저장할 HTML
            use_disk: 디스크 캐시 사용 여부
        """
        cache_key = self._get_cache_key(url)
        timestamp = datetime.now()

        # 메모리 캐시 저장
        with self.lock:
            self.memory_cache[cache_key] = (html, timestamp)

        # 디스크 캐시 저장
        if use_disk:
            try:
                cache_file = self.cache_dir / f"{cache_key}.json"
                data = {
                    "url": url,
                    "timestamp": timestamp.isoformat(),
                    "html": html,
                    "size": len(html)
                }
                with open(cache_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f)
                logger.debug(f"💾 디스크 캐시 저장: {url[:50]}... ({len(html)} bytes)")
            except Exception as e:
                logger.warning(f"   ⚠️  캐시 저장 실패: {e}")

    def delete(self, url: str) -> None:
        """캐시 삭제"""
        cache_key = self._get_cache_key(url)

        with self.lock:
            if cache_key in self.memory_cache:
                del self.memory_cache[cache_key]

        cache_file = self.cache_dir / f"{cache_key}.json"
        if cache_file.exists():
            cache_file.unlink()

    def clear(self, disk_only: bool = False) -> None:
        """캐시 초기화"""
        if not disk_only:
            with self.lock:
                self.memory_cache.clear()

        # 디스크 캐시 삭제
        for cache_file in self.cache_dir.glob("*.json"):
            cache_file.unlink()

        logger.info("🗑️  캐시 초기화 완료")

    def cleanup_expired(self) -> int:
        """만료된 캐시 정리"""
        expired_count = 0

        # 메모리 캐시 정리
        with self.lock:
            expired_keys = [
                key for key, (_, ts) in self.memory_cache.items()
                if self._is_expired(ts)
            ]
            for key in expired_keys:
                del self.memory_cache[key]
            expired_count += len(expired_keys)

        # 디스크 캐시 정리
        for cache_file in self.cache_dir.glob("*.json"):
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                timestamp = datetime.fromisoformat(data['timestamp'])
                if self._is_expired(timestamp):
                    cache_file.unlink()
                    expired_count += 1
            except Exception as e:
                logger.warning(f"   ⚠️  캐시 파일 정리 실패: {e}")

        logger.info(f"🗑️  {expired_count}개의 만료된 캐시 정리 완료")
        return expired_count

    def get_stats(self) -> Dict:
        """캐시 통계 반환"""
        memory_size = sum(len(html) for html, _ in self.memory_cache.values())
        disk_size = sum(f.stat().st_size for f in self.cache_dir.glob("*.json"))

        return {
            "memory_entries": len(self.memory_cache),
            "memory_size": memory_size,
            "disk_entries": len(list(self.cache_dir.glob("*.json"))),
            "disk_size": disk_size,
            "total_size": memory_size + disk_size,
            "ttl_hours": self.ttl_hours
        }

    # ===================== 내부 메서드 =====================

    def _get_cache_key(self, url: str) -> str:
        """URL을 캐시 키로 변환"""
        return hashlib.md5(url.encode()).hexdigest()

    def _is_expired(self, timestamp: datetime) -> bool:
        """캐시 만료 여부 확인"""
        return datetime.now() - timestamp > timedelta(hours=self.ttl_hours)


# ===================== 전역 캐시 인스턴스 =====================

_global_cache: Optional[CacheService] = None


def get_cache_service(cache_dir: str = ".cache", ttl_hours: int = 24) -> CacheService:
    """전역 캐시 서비스 인스턴스 반환"""
    global _global_cache
    if _global_cache is None:
        _global_cache = CacheService(cache_dir, ttl_hours)
    return _global_cache


# ===================== 사용 예시 =====================

def example_cache():
    """캐시 서비스 예시"""
    cache = CacheService(cache_dir=".cache", ttl_hours=24)

    # 데이터 저장
    cache.set("https://example.com/page", "<html>...</html>")

    # 데이터 조회
    html = cache.get("https://example.com/page")
    print(f"조회 결과: {html[:50] if html else '없음'}...")

    # 통계
    stats = cache.get_stats()
    print(f"캐시 통계: {stats}")

    # 만료된 캐시 정리
    cache.cleanup_expired()


if __name__ == "__main__":
    example_cache()
