"""
커리어넷 오픈 API를 사용하여 대학/학과/전공 정보 수집

API 문서: https://www.career.go.kr/openapi
"""

import requests
import json
from typing import List, Dict, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class CareerAPIClient:
    """커리어넷 오픈 API 클라이언트"""

    BASE_URL = "https://www.career.go.kr/openapi"

    # Mock API Key (실제 사용 시 환경변수에서 로드)
    API_KEY = "test_key_phase2"

    def __init__(self, api_key: Optional[str] = None):
        """
        CareerAPIClient 초기화

        Args:
            api_key: 커리어넷 API 키 (없으면 기본값 사용)
        """
        self.api_key = api_key or self.API_KEY
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "UnivInsight/Phase2 (University Research Crawler)"
        })

    def get_universities(self, page: int = 1, per_page: int = 100) -> Dict:
        """전국 대학 목록 조회"""
        logger.info(f"📚 대학 목록 조회 (페이지: {page}, 개수: {per_page})")
        return self._mock_universities(page, per_page)

    def get_departments(self, university_id: str, page: int = 1, per_page: int = 100) -> Dict:
        """특정 대학의 학과 정보 조회"""
        logger.info(f"📚 학과 정보 조회 (대학: {university_id})")
        return self._mock_departments(university_id, page, per_page)

    def get_majors(self, department_id: str) -> Dict:
        """학과의 전공 정보 조회"""
        logger.info(f"📚 전공 정보 조회 (학과: {department_id})")
        return self._mock_majors(department_id)

    # ============ Mock 데이터 (테스트용) ============

    def _mock_universities(self, page: int = 1, per_page: int = 100) -> Dict:
        """Mock 대학 데이터 (실제 API 호출 시 대체)"""

        universities = [
            {
                "id": "snu-001",
                "name": "Seoul National University",
                "name_ko": "서울대학교",
                "location": "Seoul, Gwanak-gu",
                "url": "https://www.snu.ac.kr",
                "type": "national",
                "established_year": 1946
            },
            {
                "id": "kaist-001",
                "name": "Korea Advanced Institute of Science and Technology",
                "name_ko": "한국과학기술원",
                "location": "Daejeon, Yuseong-gu",
                "url": "https://www.kaist.ac.kr",
                "type": "national",
                "established_year": 1971
            },
            {
                "id": "korea-001",
                "name": "Korea University",
                "name_ko": "고려대학교",
                "location": "Seoul, Seongbuk-gu",
                "url": "https://www.korea.ac.kr",
                "type": "private",
                "established_year": 1905
            },
        ]

        # 페이지네이션
        total = len(universities)
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page

        return {
            "total": total,
            "page": page,
            "per_page": per_page,
            "total_pages": (total + per_page - 1) // per_page,
            "universities": universities[start_idx:end_idx]
        }

    def _mock_departments(self, university_id: str, page: int = 1, per_page: int = 100) -> Dict:
        """Mock 학과 데이터"""

        departments_by_uni = {
            "snu-001": [
                {
                    "id": "snu-college-001",
                    "college_name": "College of Engineering",
                    "college_name_ko": "공과대학",
                    "departments": [
                        {
                            "id": "snu-cse-001",
                            "name": "Department of Computer Science and Engineering",
                            "name_ko": "컴퓨터공학부",
                            "url": "https://engineering.snu.ac.kr/cse",
                            "field": "Computer Science"
                        },
                    ]
                },
            ],
            "kaist-001": [
                {
                    "id": "kaist-college-001",
                    "college_name": "School of Computing",
                    "college_name_ko": "전산학부",
                    "departments": [
                        {
                            "id": "kaist-cs-001",
                            "name": "Department of Computer Science",
                            "name_ko": "컴퓨터과학과",
                            "url": "https://www.kaist.ac.kr/cs",
                            "field": "Computer Science"
                        },
                    ]
                }
            ]
        }

        depts = departments_by_uni.get(university_id, [])

        return {
            "university_id": university_id,
            "total": len(depts),
            "page": page,
            "colleges": depts
        }

    def _mock_majors(self, department_id: str) -> Dict:
        """Mock 전공 데이터"""

        majors_data = {
            "snu-cse-001": [
                {
                    "id": "major-cse-001",
                    "name": "Computer Science",
                    "name_ko": "컴퓨터과학",
                    "description": "Data structures, algorithms, databases, systems"
                },
            ],
        }

        majors = majors_data.get(department_id, [])

        return {
            "department_id": department_id,
            "majors": majors,
            "total": len(majors)
        }


if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO)

    client = CareerAPIClient()

    print("\n📚 대학 목록:")
    unis = client.get_universities()
    for uni in unis["universities"]:
        print(f"  - {uni['name_ko']} ({uni['url']})")

    print("\n📚 학과 정보:")
    depts = client.get_departments("snu-001")
    for college in depts["colleges"]:
        print(f"  - {college['college_name_ko']}")
        for dept in college["departments"]:
            print(f"    ├─ {dept['name_ko']} ({dept['url']})")
