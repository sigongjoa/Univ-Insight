"""
데이터베이스 초기화 및 세션 관리

주요 기능:
1. 데이터베이스 연결 관리
2. 세션 팩토리
3. 마이그레이션 및 초기화
"""

import logging
import os
from sqlalchemy import create_engine, event, inspect
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from contextlib import contextmanager

from src.database.models import Base, CrawlTask, CrawlResult, Professor, Paper, CrawlMetrics

logger = logging.getLogger(__name__)


class Database:
    """데이터베이스 관리"""

    def __init__(
        self,
        db_url: str = None,
        echo: bool = False,
        pool_size: int = 20,
        max_overflow: int = 40
    ):
        """
        초기화

        Args:
            db_url: 데이터베이스 URL (기본: SQLite)
            echo: SQL 로깅 여부
            pool_size: 연결 풀 크기
            max_overflow: 풀 오버플로우 허용 수
        """
        if db_url is None:
            # 기본값: SQLite
            db_path = os.getenv("DATABASE_URL", "sqlite:///./univ_insight.db")
            db_url = db_path
        else:
            db_url = db_url

        self.db_url = db_url
        self.echo = echo

        # 데이터베이스 엔진 생성
        if "sqlite" in db_url:
            # SQLite 특수 설정
            self.engine = create_engine(
                db_url,
                connect_args={"check_same_thread": False},
                poolclass=StaticPool,
                echo=echo
            )
            # SQLite 외래키 활성화
            @event.listens_for(self.engine, "connect")
            def set_sqlite_pragma(dbapi_connection, connection_record):
                cursor = dbapi_connection.cursor()
                cursor.execute("PRAGMA foreign_keys=ON")
                cursor.close()
        else:
            # PostgreSQL, MySQL 등
            self.engine = create_engine(
                db_url,
                pool_size=pool_size,
                max_overflow=max_overflow,
                echo=echo
            )

        # 세션 팩토리
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        )

        logger.info(f"🚀 Database 초기화: {db_url[:50]}...")

    def init_db(self):
        """데이터베이스 초기화 (테이블 생성)"""
        logger.info("📊 테이블 생성 중...")
        Base.metadata.create_all(bind=self.engine)
        logger.info("✅ 테이블 생성 완료")

    def get_session(self) -> Session:
        """새로운 세션 획득"""
        return self.SessionLocal()

    @contextmanager
    def session_scope(self):
        """컨텍스트 매니저 세션"""
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"❌ 세션 오류: {e}")
            raise
        finally:
            session.close()

    def drop_db(self):
        """데이터베이스 모두 삭제 (주의: 개발용)"""
        logger.warning("⚠️  모든 테이블 삭제 중...")
        Base.metadata.drop_all(bind=self.engine)
        logger.info("✅ 테이블 삭제 완료")

    def get_db_stats(self) -> dict:
        """데이터베이스 통계"""
        with self.session_scope() as session:
            stats = {
                "tasks_total": session.query(CrawlTask).count(),
                "tasks_pending": session.query(CrawlTask).filter_by(status="pending").count(),
                "tasks_running": session.query(CrawlTask).filter_by(status="running").count(),
                "tasks_completed": session.query(CrawlTask).filter_by(status="completed").count(),
                "tasks_failed": session.query(CrawlTask).filter_by(status="failed").count(),
                "results_total": session.query(CrawlResult).count(),
                "professors_total": session.query(Professor).count(),
                "papers_total": session.query(Paper).count(),
                "metrics_total": session.query(CrawlMetrics).count(),
            }
        return stats

    def close(self):
        """연결 종료"""
        self.engine.dispose()
        logger.info("✅ 데이터베이스 연결 종료")


# 전역 데이터베이스 인스턴스
_db_instance: Database = None


def get_db(db_url: str = None) -> Database:
    """전역 데이터베이스 인스턴스 획득"""
    global _db_instance
    if _db_instance is None:
        _db_instance = Database(db_url=db_url)
    return _db_instance


def init_database(db_url: str = None):
    """데이터베이스 초기화"""
    db = get_db(db_url)
    db.init_db()
    return db
