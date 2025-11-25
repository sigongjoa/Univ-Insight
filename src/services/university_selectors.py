"""
대학별 CSS 선택자 및 추출 패턴 정의

각 대학의 HTML 구조를 분석하여 최적의 CSS 선택자와
추출 패턴을 정의합니다.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class UniversitySelector:
    """대학별 선택자 정의"""
    university_name: str
    university_domain: str

    # 교수 정보 추출 선택자
    professor_selectors: Dict[str, str]      # CSS 선택자
    professor_name_patterns: List[str]       # 정규식 패턴

    # 연구실 정보 추출 선택자
    lab_selectors: Dict[str, str]
    lab_keywords: List[str]

    # 교수 페이지 링크 발견
    professor_link_keywords: List[str]
    professor_link_selectors: Dict[str, str]

    # 추가 설정
    requires_js_rendering: bool = False      # JavaScript 렌더링 필요 여부
    multi_page_crawl: bool = True            # 다중 페이지 크롤링 여부


class UniversitySelectors:
    """대학별 선택자 매핑"""

    # ==================== 서울대학교 ====================
    SEOUL_NATIONAL = UniversitySelector(
        university_name="서울대학교",
        university_domain="snu.ac.kr",

        # 교수 선택자
        professor_selectors={
            "name": ".faculty-list .faculty-member .name, .professor-card .prof-name, .faculty-item h3",
            "email": ".faculty-list .faculty-member .email, a[href^='mailto:'], .contact-email",
            "title": ".faculty-list .faculty-member .title, .prof-title",
            "office": ".faculty-list .faculty-member .office, .office-location",
        },
        professor_name_patterns=[
            r'(?:교수|Prof\.?)\s+([가-힣]{2,5})',  # "교수 이름"
            r'([가-힣]{2,5})\s+(?:교수|부교수|조교수)',  # "이름 교수"
            r'(?:Dr\.|Professor)\s+([A-Za-z\s]+)',
        ],

        # 연구실 선택자
        lab_selectors={
            "name": ".lab-list .lab-item h3, .research-group h3, .lab-name",
            "description": ".lab-list .lab-item .description, .lab-info",
            "members": ".lab-list .lab-item .members, .lab-members",
            "link": ".lab-list .lab-item a[href*='lab'], .lab-link",
        },
        lab_keywords=["laboratory", "lab", "research group", "연구실", "실험실", "연구 그룹"],

        # 교수 페이지 발견
        professor_link_keywords=["faculty", "professor", "people", "교수", "교수소개", "faculty list"],
        professor_link_selectors={
            "faculty_list": "a[href*='faculty'], a[href*='people'], a:contains('Faculty')",
            "professor_link": "a[href*='professor'], a[href*='/prof'], .faculty-link",
        },

        requires_js_rendering=False,
        multi_page_crawl=True,
    )

    # ==================== KAIST ====================
    KAIST = UniversitySelector(
        university_name="KAIST",
        university_domain="kaist.ac.kr",

        # 교수 선택자 (KAIST는 이미지 기반이 많음)
        professor_selectors={
            "name": ".professor-card .prof-name, .faculty-card .name, .prof-list .item h3",
            "email": ".professor-card .email, .contact-info a[href^='mailto:']",
            "title": ".professor-card .title, .prof-title",
            "office": ".professor-card .office, .office-room",
        },
        professor_name_patterns=[
            r'(?:교수|Prof\.?)\s+([가-힣]{2,5})',
            r'([가-힣]{2,5})\s+(?:교수|부교수)',
            r'(?:Dr\.|Prof\.|Professor)\s+([A-Za-z\s]+)',
        ],

        # 연구실 선택자
        lab_selectors={
            "name": ".lab-card .lab-name, .research-lab h3, .laboratory h2",
            "description": ".lab-card .description, .lab-info",
            "link": ".lab-card a[href*='lab'], .lab-link",
        },
        lab_keywords=["laboratory", "lab", "research", "연구실", "실험실"],

        # 교수 페이지 발견
        professor_link_keywords=["faculty", "professor", "people", "교수", "faculty members"],
        professor_link_selectors={
            "faculty_list": "a[href*='faculty'], a[href*='people']",
            "professor_link": ".prof-card a, .professor-link",
        },

        requires_js_rendering=True,  # KAIST는 JavaScript 렌더링 필요할 수 있음
        multi_page_crawl=True,
    )

    # ==================== 고려대학교 ====================
    KOREA_UNIVERSITY = UniversitySelector(
        university_name="고려대학교",
        university_domain="korea.ac.kr",

        # 교수 선택자
        professor_selectors={
            "name": ".professor-list .professor-item .name, .faculty-member h3, .prof-name",
            "email": ".professor-list .professor-item .email, .contact-email, a[href^='mailto:']",
            "title": ".professor-list .professor-item .title, .prof-title, .faculty-rank",
            "office": ".professor-list .professor-item .office, .office-location",
        },
        professor_name_patterns=[
            r'(?:교수|Prof\.?)\s+([가-힣]{2,5})',
            r'([가-힣]{2,5})\s+(?:교수|부교수|조교수)',
            r'(?:Dr\.|Professor)\s+([A-Za-z\s]+)',
        ],

        # 연구실 선택자
        lab_selectors={
            "name": ".lab-list .lab-item .name, .research-lab h3, .laboratory-name",
            "description": ".lab-list .lab-item .description, .lab-info p",
            "members": ".lab-list .lab-item .members, .member-list",
            "link": ".lab-list .lab-item a, .lab-detail-link",
        },
        lab_keywords=["laboratory", "lab", "research", "연구실", "실험실", "lab intro"],

        # 교수 페이지 발견
        professor_link_keywords=["faculty", "professor", "교수", "교수소개", "people"],
        professor_link_selectors={
            "faculty_list": "a[href*='faculty'], a[href*='professor'], a:contains('교수')",
            "professor_link": "a[href*='prof'], .professor-link, .faculty-detail",
        },

        requires_js_rendering=False,
        multi_page_crawl=True,
    )

    # 대학 목록
    UNIVERSITIES = {
        "seoul-national": SEOUL_NATIONAL,
        "kaist": KAIST,
        "korea": KOREA_UNIVERSITY,
        "snu": SEOUL_NATIONAL,  # 별칭
        "korea-university": KOREA_UNIVERSITY,  # 별칭
    }

    @classmethod
    def get_selector(cls, university_id: str) -> Optional[UniversitySelector]:
        """
        대학 ID로 선택자 조회

        Args:
            university_id: 대학 ID (예: "seoul-national", "kaist", "korea")

        Returns:
            UniversitySelector 또는 None
        """
        return cls.UNIVERSITIES.get(university_id.lower())

    @classmethod
    def get_selector_by_domain(cls, domain: str) -> Optional[UniversitySelector]:
        """
        도메인으로 선택자 조회

        Args:
            domain: 도메인 (예: "snu.ac.kr", "kaist.ac.kr")

        Returns:
            UniversitySelector 또는 None
        """
        for selector in cls.UNIVERSITIES.values():
            if selector.university_domain in domain.lower():
                return selector
        return None

    @classmethod
    def list_universities(cls) -> List[Dict]:
        """
        모든 대학 목록 반환

        Returns:
            [{"id": "...", "name": "...", "domain": "..."}, ...]
        """
        return [
            {
                "id": k,
                "name": v.university_name,
                "domain": v.university_domain,
                "requires_js": v.requires_js_rendering,
                "multi_page": v.multi_page_crawl,
            }
            for k, v in cls.UNIVERSITIES.items()
        ]
