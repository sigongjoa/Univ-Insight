"""
crawl4ai 기반 범용 대학 크롤러 (실용 버전)

각 대학마다 별도의 크롤러 클래스를 만들 필요 없이,
crawl4ai의 일반적인 웹 크롤링 기능으로 모든 대학을 지원합니다.

주요 기능:
1. 대학 홈페이지 기본 구조 파악
2. JavaScript 렌더링 지원 (동적 페이지)
3. 링크 추출 및 페이지 매핑
4. 텍스트 기반 정보 추출
"""

import asyncio
import re
import logging
from typing import List, Dict, Optional, Tuple
from datetime import datetime
from urllib.parse import urljoin, urlparse

try:
    from crawl4ai import AsyncWebCrawler, CrawlResult
except ImportError:
    AsyncWebCrawler = None
    CrawlResult = None

from src.services.improved_info_extractor import ImprovedInfoExtractor

logger = logging.getLogger(__name__)


class GenericUniversityCrawler:
    """crawl4ai 기반 범용 대학 크롤러"""

    def __init__(self, use_playwright: bool = True, timeout: int = 15):
        """
        크롤러 초기화

        Args:
            use_playwright: JavaScript 렌더링 지원 여부 (동적 페이지용)
            timeout: 크롤링 타임아웃 (초)
        """
        self.crawler = None
        self.use_playwright = use_playwright
        self.timeout = timeout
        self.session_cache = {}  # URL → HTML 캐시
        logger.info("🚀 GenericUniversityCrawler 초기화")

    async def initialize(self):
        """AsyncWebCrawler 비동기 초기화"""
        if self.crawler is None and AsyncWebCrawler:
            try:
                self.crawler = AsyncWebCrawler(
                    use_playwright=self.use_playwright,
                    ignore_ssl_errors=True
                )
                logger.info("✅ AsyncWebCrawler 초기화 완료")
            except Exception as e:
                logger.error(f"❌ AsyncWebCrawler 초기화 실패: {e}")
                raise

    async def close(self):
        """리소스 정리"""
        if self.crawler:
            try:
                # crawl4ai 버전에 따라 메서드명이 다를 수 있음
                if hasattr(self.crawler, 'aclose'):
                    await self.crawler.aclose()
                elif hasattr(self.crawler, 'close'):
                    await self.crawler.close()
                logger.info("✅ 크롤러 종료")
            except Exception as e:
                logger.warning(f"⚠️  크롤러 종료 중 오류: {e}")

    async def crawl_page(self, url: str) -> Optional[str]:
        """
        페이지 크롤링 및 HTML 반환

        Args:
            url: 크롤링할 URL

        Returns:
            HTML 콘텐츠 또는 None (실패 시)
        """
        if not self.crawler:
            await self.initialize()

        try:
            logger.info(f"   📡 크롤링: {url}")

            result = await asyncio.wait_for(
                self.crawler.arun(
                    url=url,
                    timeout=self.timeout,
                ),
                timeout=self.timeout + 5
            )

            if result.success:
                logger.info(f"   ✅ 크롤링 성공 ({len(result.html)} bytes)")
                return result.html
            else:
                logger.warning(f"   ⚠️  크롤링 실패: {result.error_message}")
                return None

        except asyncio.TimeoutError:
            logger.warning(f"   ⏱️  타임아웃: {url}")
            return None
        except Exception as e:
            logger.error(f"   ❌ 크롤링 오류: {str(e)}")
            return None

    async def find_department_pages(
        self,
        university_url: str,
        department_keywords: List[str]
    ) -> Dict[str, str]:
        """
        대학 홈페이지에서 학과별 페이지 찾기

        Args:
            university_url: 대학 홈페이지 URL
            department_keywords: 학과 검색 키워드 (예: ["computer", "engineering"])

        Returns:
            {department_name: url} 딕셔너리
        """
        logger.info(f"🔍 학과 페이지 검색 중: {university_url}")

        # 1단계: 메인 페이지 크롤링
        html = await self.crawl_page(university_url)
        if not html:
            return {}

        # 2단계: 링크 추출
        links = self._extract_links(html, university_url)
        logger.info(f"   📊 {len(links)}개 링크 추출됨")

        # 3단계: 학과 페이지 필터링
        department_pages = {}
        for link_text, link_url in links:
            link_lower = link_text.lower() + " " + link_url.lower()

            # 학과 키워드 매칭
            for keyword in department_keywords:
                if keyword.lower() in link_lower:
                    # 중복 제거
                    if link_url not in department_pages.values():
                        department_pages[f"{link_text[:30]}"] = link_url
                    break

        logger.info(f"   ✅ {len(department_pages)}개 학과 페이지 발견")
        return department_pages

    async def extract_professors(
        self,
        page_url: str,
        department_name: str = ""
    ) -> List[Dict]:
        """
        학과 페이지에서 교수 정보 추출

        Args:
            page_url: 학과 또는 교수 목록 페이지 URL
            department_name: 학과명 (로깅용)

        Returns:
            교수 정보 리스트
        """
        logger.info(f"🔍 교수 정보 추출 중: {page_url}")

        html = await self.crawl_page(page_url)
        if not html:
            return []

        professors = self._extract_professor_info(html, page_url)
        logger.info(f"   ✅ {len(professors)}명의 교수 정보 추출 완료")

        return professors

    async def extract_labs(
        self,
        page_url: str,
        department_name: str = ""
    ) -> List[Dict]:
        """
        학과 페이지에서 연구실 정보 추출

        Args:
            page_url: 학과 또는 연구실 목록 페이지 URL
            department_name: 학과명

        Returns:
            연구실 정보 리스트
        """
        logger.info(f"🔍 연구실 정보 추출 중: {page_url}")

        html = await self.crawl_page(page_url)
        if not html:
            return []

        labs = self._extract_lab_info(html, page_url)
        logger.info(f"   ✅ {len(labs)}개의 연구실 정보 추출 완료")

        return labs

    async def extract_papers(
        self,
        page_url: str,
        professor_name: str = ""
    ) -> List[Dict]:
        """
        교수 홈페이지에서 논문 정보 추출

        Args:
            page_url: 교수 홈페이지 또는 논문 목록 URL
            professor_name: 교수명

        Returns:
            논문 정보 리스트
        """
        logger.info(f"🔍 논문 정보 추출 중: {page_url}")

        html = await self.crawl_page(page_url)
        if not html:
            return []

        papers = self._extract_paper_info(html, page_url)
        logger.info(f"   ✅ {len(papers)}개의 논문 정보 추출 완료")

        return papers

    # ===================== 텍스트 추출 함수 =====================

    def _extract_links(self, html: str, base_url: str) -> List[Tuple[str, str]]:
        """
        HTML에서 모든 링크 추출

        Returns:
            [(링크 텍스트, 링크 URL), ...] 리스트
        """
        links = []

        try:
            # a 태그 찾기
            link_pattern = r'<a[^>]*href=["\']([^"\']+)["\'][^>]*>([^<]+)</a>'
            matches = re.finditer(link_pattern, html, re.IGNORECASE)

            for match in matches:
                href = match.group(1)
                text = match.group(2).strip()

                if not text or len(text) > 100:  # 너무 긴 텍스트는 제외
                    continue

                # 상대 URL을 절대 URL로 변환
                full_url = urljoin(base_url, href)

                # 외부 링크 제외
                if urlparse(full_url).netloc == urlparse(base_url).netloc:
                    links.append((text, full_url))

        except Exception as e:
            logger.error(f"❌ 링크 추출 실패: {e}")

        return links

    def _extract_professor_info(self, html: str, base_url: str = "") -> List[Dict]:
        """
        HTML에서 교수 정보 추출 (개선된 엔진 사용)

        다층 접근:
        1. 이메일 기반 추출
        2. 직급 키워드 기반
        3. 테이블/리스트 구조 기반
        """
        try:
            extractor = ImprovedInfoExtractor(html, base_url)
            return extractor.extract_professors()
        except Exception as e:
            logger.error(f"❌ 교수 정보 추출 실패: {e}")
            return []

    def _extract_lab_info(self, html: str, base_url: str = "") -> List[Dict]:
        """
        HTML에서 연구실 정보 추출 (개선된 엔진 사용)

        다층 접근:
        1. 키워드 기반 추출
        2. 헤딩 기반 추출
        3. 구조화된 데이터 기반
        """
        try:
            extractor = ImprovedInfoExtractor(html, base_url)
            return extractor.extract_labs()
        except Exception as e:
            logger.error(f"❌ 연구실 정보 추출 실패: {e}")
            return []

    def _extract_paper_info(self, html: str, base_url: str = "") -> List[Dict]:
        """
        HTML에서 논문 정보 추출 (개선된 엔진 사용)

        다층 접근:
        1. 인용 형식 기반 추출
        2. 제목 패턴 기반
        3. 학술 링크 기반
        """
        try:
            extractor = ImprovedInfoExtractor(html, base_url)
            return extractor.extract_papers()
        except Exception as e:
            logger.error(f"❌ 논문 정보 추출 실패: {e}")
            return []

    def _clean_html(self, html: str) -> str:
        """HTML 태그 제거"""
        clean = re.sub(r'<[^>]+>', '', html)
        clean = re.sub(r'\s+', ' ', clean)
        return clean.strip()


# ===================== 사용 예시 =====================

async def example_crawl_snu():
    """서울대학교 크롤링 예시"""
    crawler = GenericUniversityCrawler()
    await crawler.initialize()

    try:
        print("\n" + "="*70)
        print("🎓 서울대학교 컴퓨터공학부 크롤링")
        print("="*70)

        # 1단계: 학과 페이지 찾기
        department_pages = await crawler.find_department_pages(
            university_url="https://www.snu.ac.kr",
            department_keywords=["computer", "engineering", "cse", "컴퓨터"]
        )

        if department_pages:
            print(f"\n📚 찾은 학과 페이지: {len(department_pages)}개")
            for dept_name, dept_url in list(department_pages.items())[:3]:
                print(f"  - {dept_name}: {dept_url}")

            # 첫 번째 학과 페이지에서 교수 정보 추출
            first_dept_url = list(department_pages.values())[0]
            professors = await crawler.extract_professors(first_dept_url, "Computer Science")
            print(f"\n👨‍🏫 추출된 교수: {len(professors)}명")
            for prof in professors[:3]:
                print(f"  - {prof.get('name', 'Unknown')}: {prof.get('email', 'N/A')}")

    finally:
        await crawler.close()

    print("\n" + "="*70)
    print("✨ 크롤링 완료")
    print("="*70 + "\n")


if __name__ == "__main__":
    asyncio.run(example_crawl_snu())
