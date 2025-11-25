
import sqlite3

def migrate_up(db_connection):
    """
    research_papers 테이블 생성
    """
    cursor = db_connection.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS research_papers (
            id VARCHAR(36) PRIMARY KEY,
            url VARCHAR(512) UNIQUE NOT NULL,
            title VARCHAR(255) NOT NULL,
            university VARCHAR(50) NOT NULL,
            department VARCHAR(50),
            pub_date DATE,
            content_raw TEXT NOT NULL,
            crawled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    db_connection.commit()

def migrate_down(db_connection):
    """
    research_papers 테이블 삭제
    """
    cursor = db_connection.cursor()
    cursor.execute("DROP TABLE IF EXISTS research_papers")
    db_connection.commit()
