
import os
import sys
import sqlite3
import importlib.util
from argparse import ArgumentParser

# 프로젝트 루트를 sys.path에 추가
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

MIGRATIONS_DIR = os.path.join(project_root, 'src', 'scripts', 'migrations')

def find_migrations():
    """마이그레이션 디렉토리에서 마이그레이션 파일들을 찾아서 정렬된 리스트로 반환합니다."""
    files = [f for f in os.listdir(MIGRATIONS_DIR) if f.endswith('.py') and f.startswith(('0', '1', '2', '3', '4', '5', '6', '7', '8', '9'))]
    return sorted(files)

def run_migration(db_path, direction='up'):
    """지정된 데이터베이스에 대해 마이그레이션을 실행합니다."""
    if not os.path.exists(MIGRATIONS_DIR):
        print(f"Error: Migrations directory not found at {MIGRATIONS_DIR}")
        sys.exit(1)

    migrations = find_migrations()
    if not migrations:
        print("No migration files found.")
        return

    print(f"Connecting to database: {db_path}")
    conn = sqlite3.connect(db_path)

    try:
        for migration_file in migrations:
            migration_path = os.path.join(MIGRATIONS_DIR, migration_file)
            
            # 모듈로 동적 로드
            spec = importlib.util.spec_from_file_location(migration_file, migration_path)
            migration_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(migration_module)
            
            target_func = getattr(migration_module, f'migrate_{direction}', None)
            
            if callable(target_func):
                print(f"Running {direction} for {migration_file}...")
                target_func(conn)
                print(f"  -> Done.")
            else:
                print(f"Warning: {direction} function not found in {migration_file}. Skipping.")
    
    except Exception as e:
        print(f"An error occurred: {e}")
        conn.rollback()
    finally:
        conn.close()
        print("Database connection closed.")

def main():
    parser = ArgumentParser(description="Run database migrations.")
    parser.add_argument(
        '--db',
        dest='db_path',
        default='univ_insight.db',
        help="Path to the SQLite database file (default: univ_insight.db)"
    )
    parser.add_argument(
        '--direction',
        choices=['up', 'down'],
        default='up',
        help="Migration direction: 'up' to apply, 'down' to revert (default: up)"
    )
    args = parser.parse_args()

    run_migration(args.db_path, args.direction)

if __name__ == '__main__':
    main()
