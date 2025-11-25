import os
import requests
import logging
from typing import List, Optional, Dict
from src.domain.schemas import UniversityInfo, DepartmentInfo

logger = logging.getLogger(__name__)

class CareerNetClient:
    """
    커리어넷 오픈 API 클라이언트
    문서: https://www.career.go.kr/cnet/front/openapi/openApiMain.do
    """
    
    BASE_URL = "http://www.career.go.kr/cnet/openapi/getOpenApi"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("CAREERNET_API_KEY")
        if not self.api_key:
            logger.warning("CAREERNET_API_KEY is not set. API calls will fail or return mock data.")

    def search_university(self, university_name: str) -> Optional[UniversityInfo]:
        """
        대학명으로 대학 정보 및 학과 목록을 조회합니다.
        """
        if not self.api_key:
            logger.info("No API Key provided. Returning Mock Data.")
            return self._get_mock_data(university_name)

        params = {
            "apiKey": self.api_key,
            "svcType": "api",
            "svcCode": "SCHOOL",
            "contentType": "json",
            "gubun": "univ_list",
            "searchSchulNm": university_name
        }

        try:
            response = requests.get(self.BASE_URL, params=params)
            response.raise_for_status()
            data = response.json()
            
            return self._parse_response(data, university_name)
            
        except Exception as e:
            logger.error(f"Failed to fetch data from CareerNet: {e}")
            return None

    def _parse_response(self, data: Dict, target_name: str) -> Optional[UniversityInfo]:
        """
        API 응답(JSON)을 파싱하여 UniversityInfo 객체로 변환
        """
        try:
            data_list = data.get("dataSearch", {}).get("content", [])
            if not data_list:
                return None

            # 정확도 순 또는 첫 번째 결과 사용
            # 여기서는 단순히 첫 번째 결과를 사용하되, 이름이 유사한지 체크 가능
            univ_data = data_list[0]
            
            # 학과 정보 파싱 (API 응답 구조에 따라 다를 수 있음. 
            # 보통 'facilName'이나 별도 필드에 학과 정보가 있을 수 있음.
            # 여기서는 예시로 'major_list'라고 가정하거나, 별도 API 호출이 필요할 수 있음.
            # *참고*: SCHOOL API는 학교 기본 정보 위주임. 
            # 학과 정보를 위해서는 svcCode='MAJOR' 등을 써야 할 수도 있음.
            # 일단은 학교 정보만이라도 매핑.)
            
            # API 응답 필드 (예시)
            # schoolName: 학교명
            # link: 학교 URL
            # region: 지역
            
            name = univ_data.get("schoolName", target_name)
            link = univ_data.get("link", "")
            region = univ_data.get("region", "")
            
            # 학과 정보가 이 API에 없다면 빈 리스트
            departments = []
            
            return UniversityInfo(
                name=name,
                region=region,
                url=link,
                departments=departments
            )

        except Exception as e:
            logger.error(f"Error parsing response: {e}")
            return None

    def _get_mock_data(self, name: str) -> UniversityInfo:
        """API 키가 없을 때 테스트용 Mock 데이터 반환"""
        return UniversityInfo(
            name=name,
            region="서울",
            url="https://www.snu.ac.kr",
            departments=[
                DepartmentInfo(university_name=name, department_name="컴퓨터공학부", category="공학계열"),
                DepartmentInfo(university_name=name, department_name="기계공학부", category="공학계열"),
                DepartmentInfo(university_name=name, department_name="경영학과", category="사회계열"),
            ]
        )
