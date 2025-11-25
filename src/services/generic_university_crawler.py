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

        professors = self._extract_professor_info(html)
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

        labs = self._extract_lab_info(html)
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

        papers = self._extract_paper_info(html)
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

    def _extract_professor_info(self, html: str) -> List[Dict]:
        """
        HTML에서 교수 정보 패턴 추출

        일반적인 패턴:
        - "Prof. Name" 또는 "교수"
        - 이메일 주소
        - 사무실/오피스 위치
        """
        professors = []

        try:
            # 이메일 패턴으로 교수 찾기
            email_pattern = r'\b([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,})\b'
            emails = re.findall(email_pattern, html)

            for email in emails:
                # 이메일 앞뒤의 텍스트에서 이름 추출
                email_pos = html.find(email)
                if email_pos == -1:
                    continue

                # 이메일 앞 300자 범위에서 이름 찾기
                context_start = max(0, email_pos - 300)
                context = html[context_start:email_pos + len(email) + 100]

                # 이름 패턴 (여러 형식 지원)
                name_patterns = [
                    r'(?:Prof\.|Professor|Dr\.|교수)\s+([A-Za-z0-9\s&-]+?)(?:\<|<|email|\()',
                    r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s*(?:\(|<|email)',
                ]

                name = None
                for pattern in name_patterns:
                    match = re.search(pattern, context, re.IGNORECASE)
                    if match:
                        name = match.group(1).strip()
                        break

                if name and len(name) > 2 and len(name) < 50:
                    professors.append({
                        "name": name,
                        "email": email,
                        "extracted_from": "email_pattern"
                    })

        except Exception as e:
            logger.error(f"❌ 교수 정보 추출 실패: {e}")

        # 중복 제거
        unique_professors = []
        seen_emails = set()
        for prof in professors:
            if prof["email"] not in seen_emails:
                unique_professors.append(prof)
                seen_emails.add(prof["email"])

        return unique_professors[:50]  # 최대 50명

    def _extract_lab_info(self, html: str) -> List[Dict]:
        """
        HTML에서 연구실 정보 패턴 추출

        일반적인 패턴:
        - "Lab", "Laboratory", "Research Group"
        - "연구실", "실험실"
        """
        labs = []

        try:
            # 연구실 관련 키워드 찾기
            lab_keywords = [
                "laboratory",
                "research group",
                "research center",
                "lab",
                "연구실",
                "연구 그룹",
                "연구센터",
                "실험실",
            ]

            for keyword in lab_keywords:
                # 키워드를 포함하는 문장 찾기
                pattern = rf'(?:[^.!?\n]{{0,100}}){re.escape(keyword)}[^.!?\n]{{0,200}}'
                matches = re.finditer(pattern, html, re.IGNORECASE)

                for match in matches:
                    text = match.group(0).strip()
                    if len(text) > 10 and len(text) < 500:
                        labs.append({
                            "description": text[:200],
                            "keyword": keyword,
                            "extracted_from": "keyword_pattern"
                        })

        except Exception as e:
            logger.error(f"❌ 연구실 정보 추출 실패: {e}")

        return labs[:20]  # 최대 20개

    def _extract_paper_info(self, html: str) -> List[Dict]:
        """
        HTML에서 논문 정보 패턴 추출

        일반적인 패턴:
        - "Title: ...", "Journal: ...", "Year: ..."
        - 인용 형식 (Conference, Journal 등)
        """
        papers = []

        try:
            # 연도 패턴 (1900-2099)
            year_pattern = r'\b(19|20)\d{2}\b'

            # 논문 제목 같은 패턴 (대문자로 시작하는 긴 문장)
            title_pattern = r'(?:Title|title|Title:|TITLE:)\s*"?([^"\n]+?)(?:"|$)'

            # 제목 찾기
            title_matches = re.finditer(title_pattern, html)
            for match in title_matches:
                title = match.group(1).strip()
                if len(title) > 5 and len(title) < 300:
                    papers.append({
                        "title": title,
                        "extracted_from": "title_pattern"
                    })

            # 제목 패턴이 없으면, 일반적인 긴 텍스트로 추정
            if not papers:
                # 문장 단위로 분리하고, 제목 같은 문장 찾기
                sentences = re.split(r'[.!?\n]+', html)
                for sentence in sentences:
                    text = re.sub(r'<[^>]+>', '', sentence).strip()  # HTML 태그 제거
                    if (len(text) > 20 and
                        len(text) < 300 and
                        text[0].isupper() and
                        text.count(' ') > 2):
                        papers.append({
                            "title": text,
                            "extracted_from": "sentence_pattern"
                        })

        except Exception as e:
            logger.error(f"❌ 논문 정보 추출 실패: {e}")

        return papers[:30]  # 최대 30개

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
