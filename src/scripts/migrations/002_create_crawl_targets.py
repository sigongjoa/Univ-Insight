
import sqlite3

def migrate_up(db_connection):
    """
    crawl_targets 테이블 생성
    """
    cursor = db_connection.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS crawl_targets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            university_id VARCHAR(50),
            university_name VARCHAR(255) NOT NULL,
            university_name_ko VARCHAR(255),
            university_url VARCHAR(512),
            college_id VARCHAR(50),
            college_name VARCHAR(255),
            college_name_ko VARCHAR(255),
            college_url VARCHAR(512),
            department_id VARCHAR(50),
            department_name VARCHAR(255),
            department_name_ko VARCHAR(255),
            department_url VARCHAR(512),
            category VARCHAR(100),
            status VARCHAR(50) DEFAULT 'Ready',
            priority INT DEFAULT 0,
            attempts INT DEFAULT 0,
            last_error TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # 인덱스 생성
    cursor.execute(
        "CREATE INDEX IF NOT EXISTS idx_crawl_status ON crawl_targets(status)"
    )
    cursor.execute(
        "CREATE INDEX IF NOT EXISTS idx_crawl_university ON crawl_targets(university_name)"
    )
    cursor.execute(
        "CREATE INDEX IF NOT EXISTS idx_crawl_category ON crawl_targets(category)"
    )

    db_connection.commit()

def migrate_down(db_connection):
    """
    crawl_targets 테이블 삭제
    """
    cursor = db_connection.cursor()
    cursor.execute("DROP TABLE IF EXISTS crawl_targets")
    db_connection.commit()

if __name__ == '__main__':
    # 간단한 테스트 실행
    db_path = 'univ_insight.db'
    conn = sqlite3.connect(db_path)
    
    print("Running migrate_up...")
    migrate_up(conn)
    print("Table 'crawl_targets' and indexes created.")
    
    # 테이블 정보 확인
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='crawl_targets'")
    print(f"Table exists: {cursor.fetchone() is not None}")
    
    print("\nRunning migrate_down...")
    migrate_down(conn)
    print("Table 'crawl_targets' dropped.")

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='crawl_targets'")
    print(f"Table exists: {cursor.fetchone() is not None}")
    
    conn.close()
