"""
다중 페이지 크롤링 엔진

학과 페이지 → 교수 링크 발견 → 개별 교수 페이지 → 논문/정보 추출
"""

import asyncio
import logging
from typing import List, Dict, Set, Optional, Tuple
from datetime import datetime

from src.services.generic_university_crawler import GenericUniversityCrawler
from src.services.improved_info_extractor import ImprovedInfoExtractor

logger = logging.getLogger(__name__)


class MultipageCrawler:
    """다중 페이지 크롤링을 지원하는 크롤러"""

    def __init__(self, max_depth: int = 3, max_professors_per_dept: int = 10):
        """
        초기화

        Args:
            max_depth: 최대 크롤링 깊이 (1=학과페이지, 2=교수링크, 3=개별교수페이지)
            max_professors_per_dept: 부서당 최대 교수 수
        """
        self.crawler = GenericUniversityCrawler()
        self.max_depth = max_depth
        self.max_professors_per_dept = max_professors_per_dept
        self.visited_urls: Set[str] = set()
        self.start_time = None

    async def initialize(self):
        """크롤러 초기화"""
        await self.crawler.initialize()
        self.start_time = datetime.now()
        logger.info("🚀 MultipageCrawler 초기화 완료")

    async def close(self):
        """리소스 정리"""
        await self.crawler.close()
        elapsed = (datetime.now() - self.start_time).total_seconds()
        logger.info(f"✅ 크롤러 종료 (소요 시간: {elapsed:.1f}초)")

    async def crawl_department(
        self,
        dept_url: str,
        dept_name: str = ""
    ) -> Dict:
        """
        학과 페이지 크롤링 (다중 페이지)

        단계:
        1. 학과 페이지에서 교수 정보 + 링크 추출
        2. 교수 링크 발견
        3. 개별 교수 페이지 크롤링
        4. 논문 정보 추출

        Args:
            dept_url: 학과 페이지 URL
            dept_name: 학과명

        Returns:
            {
                "department": "...",
                "url": "...",
                "professors": [...],
                "labs": [...],
                "papers": [...],
                "pages_crawled": 3,
                "extraction_stats": {...}
            }
        """
        logger.info(f"\n{'='*70}")
        logger.info(f"📚 {dept_name} 다중 페이지 크롤링 시작")
        logger.info(f"{'='*70}")

        result = {
            "department": dept_name,
            "url": dept_url,
            "professors": [],
            "labs": [],
            "papers": [],
            "professor_pages": [],
            "pages_crawled": 0,
            "extraction_stats": {}
        }

        # 방문 체크
        if dept_url in self.visited_urls:
            logger.warning(f"⚠️  이미 방문한 URL: {dept_url}")
            return result

        self.visited_urls.add(dept_url)

        try:
            # 단계 1: 학과 페이지 크롤링
            logger.info(f"\n🔍 [단계 1] 학과 페이지 분석: {dept_url}")
            html = await self.crawler.crawl_page(dept_url)

            if not html or self.crawler._is_error_page(html):
                logger.warning(f"❌ 학과 페이지 크롤링 실패")
                return result

            result["pages_crawled"] += 1

            # 정보 추출
            extractor = ImprovedInfoExtractor(html, dept_url, dept_url)

            # 학과 페이지에서 직접 추출
            result["professors"].extend(extractor.extract_professors())
            result["labs"].extend(extractor.extract_labs())
            result["papers"].extend(extractor.extract_papers())

            # 단계 2: 교수 페이지 링크 발견
            logger.info(f"\n🔗 [단계 2] 교수 페이지 링크 발견")
            professor_links = extractor.extract_professor_links()

            if professor_links:
                logger.info(f"   ✅ {len(professor_links)}개 교수 페이지 링크 발견")
                result["professor_pages"] = professor_links

                # 단계 3: 개별 교수 페이지 크롤링 (최대 max_professors_per_dept개)
                if self.max_depth >= 2:
                    logger.info(f"\n📄 [단계 3] 개별 교수 페이지 크롤링 (최대 {self.max_professors_per_dept}개)")

                    for prof_link in professor_links[:self.max_professors_per_dept]:
                        prof_url = prof_link.get("url", "")
                        prof_text = prof_link.get("text", "")

                        if prof_url in self.visited_urls:
                            continue

                        logger.info(f"   📖 크롤링: {prof_text} ({prof_url})")

                        try:
                            prof_html = await self.crawler.crawl_page(prof_url)

                            if prof_html and not self.crawler._is_error_page(prof_html):
                                self.visited_urls.add(prof_url)
                                result["pages_crawled"] += 1

                                prof_extractor = ImprovedInfoExtractor(
                                    prof_html, prof_url, prof_url
                                )

                                # 교수 페이지에서 논문 추출
                                papers = prof_extractor.extract_papers()
                                if papers:
                                    result["papers"].extend(papers)
                                    logger.info(f"      📚 {len(papers)}개 논문 추출")

                                # 교수 페이지에서 추가 정보
                                profs = prof_extractor.extract_professors()
                                if profs:
                                    result["professors"].extend(profs)

                        except Exception as e:
                            logger.warning(f"   ⚠️  {prof_text} 크롤링 실패: {e}")

                        # 속도 제한 (1초 간격)
                        await asyncio.sleep(1)

            else:
                logger.info(f"   ℹ️  교수 페이지 링크를 찾을 수 없음")

        except Exception as e:
            logger.error(f"❌ 다중 페이지 크롤링 중 오류: {e}")

        # 통계 계산
        result["extraction_stats"] = {
            "professors_count": len(set(p.get("name", "") for p in result["professors"] if p.get("name"))),
            "labs_count": len(set(l.get("name", "") for l in result["labs"] if l.get("name"))),
            "papers_count": len(set(p.get("title", "") for p in result["papers"] if p.get("title"))),
            "total_extracted": len(result["professors"]) + len(result["labs"]) + len(result["papers"]),
            "pages_crawled": result["pages_crawled"],
        }

        logger.info(f"\n{'='*70}")
        logger.info(f"✅ 크롤링 완료 ({result['pages_crawled']}개 페이지)")
        logger.info(f"   👨‍🏫 교수: {result['extraction_stats']['professors_count']}명 (중복 제거)")
        logger.info(f"   🔬 연구실: {result['extraction_stats']['labs_count']}개 (중복 제거)")
        logger.info(f"   📄 논문: {result['extraction_stats']['papers_count']}개 (중복 제거)")
        logger.info(f"{'='*70}\n")

        return result

    async def crawl_multiple_departments(
        self,
        departments: List[Tuple[str, str]]  # [(url, name), ...]
    ) -> List[Dict]:
        """
        여러 학과 동시 크롤링 (순차)

        Args:
            departments: [(url, name), ...] 리스트

        Returns:
            [department_result, ...]
        """
        results = []

        for dept_url, dept_name in departments:
            result = await self.crawl_department(dept_url, dept_name)
            results.append(result)

            # 속도 제한
            await asyncio.sleep(2)

        return results


# ===================== 사용 예시 =====================

async def example_multipage_crawl():
    """다중 페이지 크롤링 예시"""
    crawler = MultipageCrawler(max_depth=3, max_professors_per_dept=5)
    await crawler.initialize()

    try:
        # 고려대학교 CS 크롤링
        result = await crawler.crawl_department(
            "https://cs.korea.ac.kr",
            "고려대학교 컴퓨터학과"
        )

        print(f"\n📊 결과 요약:")
        print(f"   - 교수: {result['extraction_stats']['professors_count']}명")
        print(f"   - 연구실: {result['extraction_stats']['labs_count']}개")
        print(f"   - 논문: {result['extraction_stats']['papers_count']}개")
        print(f"   - 크롤링 페이지: {result['extraction_stats']['pages_crawled']}개")

    finally:
        await crawler.close()


if __name__ == "__main__":
    asyncio.run(example_multipage_crawl())
