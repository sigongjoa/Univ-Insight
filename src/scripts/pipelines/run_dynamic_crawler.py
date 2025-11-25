
import os
import sys
from argparse import ArgumentParser

# 프로젝트 루트를 sys.path에 추가
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.services.dynamic_crawler import DynamicCrawler

def main():
    """
    커맨드라인 인자를 파싱하여 DynamicCrawler를 실행하는 메인 함수
    """
    parser = ArgumentParser(description="DB에 저장된 타겟 URL들을 기반으로 교수 정보를 동적으로 크롤링합니다.")
    
    parser.add_argument(
        '--db',
        dest='db_path',
        default='univ_insight.db',
        help="SQLite 데이터베이스 파일 경로 (기본값: univ_insight.db)"
    )

    args = parser.parse_args()

    print(f"데이터베이스: {args.db_path}")

    # 1. DynamicCrawler 초기화 및 실행
    crawler = DynamicCrawler(db_path=args.db_path)
    crawler.run()

if __name__ == '__main__':
    main()
