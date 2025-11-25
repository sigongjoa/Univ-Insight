
import os
import json
from typing import List, Dict
import requests
from tenacity import retry, stop_after_attempt, wait_fixed

# 프로젝트 루트를 기준으로 mock 데이터 경로 설정
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
MOCK_DATA_PATH = os.path.join(project_root, 'tests', 'fixtures', 'mock_career_api_response.json')


class CareerAPIClient:
    """
    커리어넷 오픈 API 클라이언트
    - mock=True일 경우, 실제 API 대신 로컬 mock 데이터를 사용합니다.
    """

    BASE_URL = "https://www.career.go.kr/cnet/openapi/getOpenApi"

    def __init__(self, api_key: str, mock: bool = False):
        if not mock and not api_key:
            raise ValueError("API key is required when not in mock mode.")
        self.api_key = api_key
        self.session = requests.Session()
        self.mock = mock

    def _get_mock_data(self, category: str = None) -> List[Dict]:
        """로컬 mock JSON 파일에서 데이터를 로드합니다."""
        try:
            with open(MOCK_DATA_PATH, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            all_data = data.get("dataSearch", [])
            
            if category:
                return [item for item in all_data if item.get("majorGroup") == category]
            
            return all_data
        except FileNotFoundError:
            print(f"Error: Mock data file not found at {MOCK_DATA_PATH}")
            return []
        except json.JSONDecodeError:
            print(f"Error: Could not decode JSON from {MOCK_DATA_PATH}")
            return []

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
    def search_universities(self, page: int = 1, page_size: int = 100) -> List[Dict]:
        """
        전국 대학 및 학과 정보 조회
        """
        if self.mock:
            # mock 데이터는 페이징을 지원하지 않으므로, 첫 페이지 요청에만 전체 데이터를 반환합니다.
            return self._get_mock_data() if page == 1 else []

        params = {
            "serviceKey": self.api_key,
            "subject": "school",
            "thisPage": page,
            "listSize": page_size,
            "dataType": "json"
        }

        response = self.session.get(self.BASE_URL, params=params)
        response.raise_for_status()

        data = response.json()
        return data.get("dataSearch", [])

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
    def search_by_category(self, category: str, page: int = 1, page_size: int = 100) -> List[Dict]:
        """
        계열별 대학/학과 조회 (예: "공학", "자연과학")
        """
        if self.mock:
            # mock 데이터는 페이징을 지원하지 않으므로, 첫 페이지 요청에만 필터링된 데이터를 반환합니다.
            return self._get_mock_data(category) if page == 1 else []

        params = {
            "serviceKey": self.api_key,
            "subject": "school",
            "majorGroup": category,
            "thisPage": page,
            "listSize": page_size,
            "dataType": "json"
        }

        response = self.session.get(self.BASE_URL, params=params)
        response.raise_for_status()

        return response.json().get("dataSearch", [])

if __name__ == '__main__':
    # Mock 클라이언트 테스트
    print("--- Testing Mock Client ---")
    mock_client = CareerAPIClient(api_key="dummy_key", mock=True)
    
    # 카테고리별 조회
    engineering_seeds = mock_client.search_by_category("공학")
    print(f"Found {len(engineering_seeds)} engineering seeds (mock).")
    assert len(engineering_seeds) > 0
    print(engineering_seeds[0])

    # 전체 조회
    all_seeds = mock_client.search_universities()
    print(f"\nFound {len(all_seeds)} total seeds (mock).")
    assert len(all_seeds) > 0
    print(all_seeds[0])

    # 페이지 2는 비어 있어야 함
    page_2_seeds = mock_client.search_universities(page=2)
    print(f"\nFound {len(page_2_seeds)} seeds on page 2 (mock).")
    assert len(page_2_seeds) == 0
    
    print("\n--- Mock Client Test Passed ---")

    # 실제 클라이언트 테스트 (API 키가 환경 변수에 설정된 경우)
    # REAL_API_KEY = os.getenv("CAREER_API_KEY")
    # if REAL_API_KEY:
    #     print("\n--- Testing Real Client (requires CAREER_API_KEY env var) ---")
    #     real_client = CareerAPIClient(api_key=REAL_API_KEY)
    #     try:
    #         real_seeds = real_client.search_by_category("공학", page_size=5)
    #         print(f"Found {len(real_seeds)} real engineering seeds.")
    #         if real_seeds:
    #             print(real_seeds[0])
    #     except Exception as e:
    #         print(f"Real API client test failed: {e}")

