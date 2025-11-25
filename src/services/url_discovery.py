import logging
import asyncio
from typing import Optional
from duckduckgo_search import DDGS

logger = logging.getLogger(__name__)

class URLDiscoveryService:
    """
    학과 홈페이지 URL을 검색을 통해 찾아내는 서비스.
    DuckDuckGo Search를 사용합니다.
    """

    # 자주 사용되는 학과 URL 매핑 (검색 실패 대비 및 속도 향상)
    KNOWN_URLS = {
        ("서울대학교", "컴퓨터공학부"): "https://cse.snu.ac.kr",
        ("서울대학교", "기계공학부"): "https://mech.snu.ac.kr",
        ("서울대학교", "경영학과"): "https://cba.snu.ac.kr",
        
        # KAIST (DB에는 '컴퓨터공학부' 등으로 저장됨)
        ("KAIST", "전산학부"): "https://cs.kaist.ac.kr",
        ("KAIST", "컴퓨터공학부"): "https://cs.kaist.ac.kr", 
        ("KAIST", "기계공학과"): "https://mech.kaist.ac.kr",
        ("KAIST", "기계공학부"): "https://mech.kaist.ac.kr",
        ("KAIST", "경영공학부"): "https://btm.kaist.ac.kr",
        ("KAIST", "경영학과"): "https://btm.kaist.ac.kr",

        # 연세대학교
        ("연세대학교", "컴퓨터과학과"): "https://cs.yonsei.ac.kr",
        ("연세대학교", "컴퓨터공학부"): "https://cs.yonsei.ac.kr",
        ("연세대학교", "기계공학부"): "https://me.yonsei.ac.kr",
        ("연세대학교", "경영학과"): "https://biz.yonsei.ac.kr",

        # 고려대학교
        ("고려대학교", "컴퓨터학과"): "https://cs.korea.ac.kr",
        ("고려대학교", "컴퓨터공학부"): "https://cs.korea.ac.kr",
        ("고려대학교", "기계공학부"): "https://me.korea.ac.kr",
        ("고려대학교", "경영학과"): "https://biz.korea.ac.kr",
    }

    def __init__(self):
        self.ddgs = DDGS()

    def find_department_url(self, university_name: str, department_name: str) -> Optional[str]:
        """
        대학명과 학과명을 조합하여 검색하고, 가장 유력한 홈페이지 URL을 반환합니다.
        """
        # 1. Known URLs 확인
        # 학과명 매핑 유연성 (컴퓨터공학부 vs 컴퓨터공학과 등) 고려 필요하지만 일단 정확히 매칭
        if (university_name, department_name) in self.KNOWN_URLS:
            logger.info(f"✅ Found in Known URLs: {self.KNOWN_URLS[(university_name, department_name)]}")
            return self.KNOWN_URLS[(university_name, department_name)]

        # 2. 검색 시도
        # site:ac.kr 연산자를 사용하여 대학 사이트만 검색되도록 유도
        query = f"site:ac.kr {university_name} {department_name}"
        logger.info(f"🔍 Searching for: {query}")

        try:
            # DuckDuckGo 검색 (최대 5개 결과)
            results = self.ddgs.text(query, max_results=5)
            
            if not results:
                logger.warning(f"No results found for {query}")
                return None

            # 결과 순회하며 유효한 대학 도메인(.ac.kr, .edu) 찾기
            for res in results:
                url = res.get('href', '')
                title = res.get('title', '')
                
                # 간단한 도메인 필터링
                if '.ac.kr' in url or '.edu' in url or 'snu.ac.kr' in url or 'kaist.ac.kr' in url:
                    logger.info(f"✅ Found Valid URL: {url} ({title})")
                    return url
                
            logger.warning(f"⚠️ No valid academic URL found in top results for {query}. Top result was: {results[0].get('href')}")
            return None # 유효한 URL 없으면 None 반환 (엄격 모드)

        except Exception as e:
            logger.error(f"Search failed for {query}: {e}")
            return None

    async def find_url_async(self, university_name: str, department_name: str) -> Optional[str]:
        """비동기 래퍼 (필요 시 사용)"""
        # DDGS는 동기 라이브러리이므로, 비동기 실행을 위해 run_in_executor 사용 고려 가능
        # 여기서는 간단히 동기 호출
        return self.find_department_url(university_name, department_name)
