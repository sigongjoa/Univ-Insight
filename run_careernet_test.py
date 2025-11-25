import sys
import os
import logging

# 프로젝트 루트를 sys.path에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.services.careernet_client import CareerNetClient

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    print(">>> [Phase 2] CareerNet API Client Test")
    
    # 1. 클라이언트 초기화 (API 키 없이 -> Mock 모드)
    client = CareerNetClient()
    
    target_univ = "서울대학교"
    print(f"\n>>> Searching for: {target_univ}...")
    
    # 2. 대학 정보 조회
    univ_info = client.search_university(target_univ)
    
    if univ_info:
        print(f"\n✅ Found University: {univ_info.name}")
        print(f"   - Region: {univ_info.region}")
        print(f"   - URL: {univ_info.url}")
        print(f"   - Departments ({len(univ_info.departments)}):")
        for dept in univ_info.departments:
            print(f"     * {dept.department_name} ({dept.category})")
    else:
        print("\n❌ University not found.")

if __name__ == "__main__":
    main()
