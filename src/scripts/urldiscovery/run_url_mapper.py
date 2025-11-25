
import os
import sys
from argparse import ArgumentParser

# 프로젝트 루트를 sys.path에 추가
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.scripts.urldiscovery.college_url_mapper import CollegeURLMapper

def main():
    """
    커맨드라인 인자를 파싱하여 CollegeURLMapper를 실행하는 메인 함수
    """
    parser = ArgumentParser(description="crawl_targets 테이블의 학과 URL을 웹 스크래핑을 통해 업데이트합니다.")
    
    parser.add_argument(
        '--db',
        dest='db_path',
        default='univ_insight.db',
        help="SQLite 데이터베이스 파일 경로 (기본값: univ_insight.db)"
    )

    args = parser.parse_args()

    print(f"데이터베이스: {args.db_path}")

    # 1. CollegeURLMapper 초기화 및 실행
    mapper = CollegeURLMapper(db_path=args.db_path)
    mapper.update_database()

if __name__ == '__main__':
    main()
