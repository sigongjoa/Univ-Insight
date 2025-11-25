
import sqlite3

def migrate_up(db_connection):
    """
    analysis_results 테이블 생성
    """
    cursor = db_connection.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS analysis_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            paper_id VARCHAR(36) NOT NULL,
            research_summary TEXT NOT NULL, -- Renamed from summary
            job_title VARCHAR(100),
            salary_hint VARCHAR(100),
            related_companies TEXT, -- JSON stored as TEXT
            action_items TEXT, -- JSON stored as TEXT
            embedding_id VARCHAR(100),
            analyzed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (paper_id) REFERENCES research_papers (id)
        )
    """)
    db_connection.commit()

def migrate_down(db_connection):
    """
    analysis_results 테이블 삭제
    """
    cursor = db_connection.cursor()
    cursor.execute("DROP TABLE IF EXISTS analysis_results")
    db_connection.commit()
