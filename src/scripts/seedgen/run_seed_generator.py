
import os
import sys
from argparse import ArgumentParser

# 프로젝트 루트를 sys.path에 추가
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.services.career_api_client import CareerAPIClient
from src.scripts.seedgen.seed_generator import SeedGenerator

def main():
    """
    커맨드라인 인자를 파싱하여 SeedGenerator를 실행하는 메인 함수
    """
    parser = ArgumentParser(description="커리어넷 API를 통해 크롤링 대상을 수집하여 DB에 저장합니다.")
    
    parser.add_argument(
        '--api-key',
        dest='api_key',
        default=os.getenv("CAREER_API_KEY"),
        help="커리어넷 API 키. 환경변수 CAREER_API_KEY로도 설정 가능합니다."
    )
    parser.add_argument(
        '--categories',
        nargs='+',
        dest='categories',
        default=["공학", "자연과학", "의학", "교육", "인문사회", "예체능"],
        help='수집할 계열 리스트 (예: "공학" "자연과학")'
    )
    parser.add_argument(
        '--db',
        dest='db_path',
        default='univ_insight.db',
        help="SQLite 데이터베이스 파일 경로 (기본값: univ_insight.db)"
    )
    parser.add_argument(
        '--mock',
        action='store_true',
        help="실제 API 대신 로컬 mock 데이터를 사용하여 실행합니다."
    )

    args = parser.parse_args()

    if not args.mock and not args.api_key:
        parser.error("--api-key 인자가 필요합니다 (또는 CAREER_API_KEY 환경변수 설정). --mock 플래그를 사용하면 API 키 없이 실행 가능합니다.")

    print(f"실행 모드: {'Mock' if args.mock else 'Real API'}")
    print(f"데이터베이스: {args.db_path}")
    print(f"대상 계열: {', '.join(args.categories)}")

    # 1. API 클라이언트 초기화
    api_client = CareerAPIClient(api_key=args.api_key, mock=args.mock)

    # 2. SeedGenerator 초기화 및 실행
    seed_generator = SeedGenerator(db_path=args.db_path, api_client=api_client)
    seed_generator.run(categories=args.categories)

if __name__ == '__main__':
    main()
