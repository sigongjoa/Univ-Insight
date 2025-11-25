
import sqlite3
import asyncio
from datetime import datetime
from typing import List, Dict, Optional
from bs4 import BeautifulSoup
import os
import sys

# 프로젝트 루트를 sys.path에 추가
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

try:
    from crawl4ai import AsyncWebCrawler
except ImportError:
    AsyncWebCrawler = None

class DynamicCrawler:
    """
    Phase 2: DB에 저장된 타겟들을 기반으로 동적 크롤링을 수행합니다.
    교수, 연구실 정보 등을 수집합니다.
    """

    def __init__(self, db_path: str):
        self.db_path = db_path
        if not AsyncWebCrawler:
            raise ImportError("crawl4ai is not installed. Please install it with 'pip install crawl4ai'")

    def get_targets_for_crawl(self, status: str = "URLFound", limit: int = 100) -> List[Dict]:
        """
        DB에서 크롤링할 학과 리스트를 조회합니다.
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, university_name, department_name, department_url
            FROM crawl_targets
            WHERE status = ? AND department_url IS NOT NULL
            LIMIT ?
        """, (status, limit))

        targets = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return targets

    async def _fetch_page_content(self, url: str) -> str:
        """주어진 URL의 페이지를 crawl4ai로 가져와 HTML 콘텐츠를 반환합니다."""
        try:
            async with AsyncWebCrawler(verbose=False) as crawler:
                result = await crawler.arun(url=url, timeout=30, wait_until="networkidle")
                return result.html if result.success else ""
        except Exception:
            return ""

    def _parse_professor_element(self, element: BeautifulSoup) -> Optional[Dict]:
        """교수 정보 요소(element)에서 이름, 직위, 이메일 등을 파싱합니다."""
        try:
            # 일반적인 패턴으로 이름, 직위, 이메일, 연구실 링크 등을 탐색
            name_tag = element.select_one(".prof-name, .name, .professor-name, .prof_nm")
            email_tag = element.select_one("a[href^='mailto:']")
            lab_tag = element.select_one("a[href*='lab'], a[href*='homepage']")

            if not name_tag:
                return None

            return {
                "name": name_tag.get_text(strip=True),
                "email": email_tag.get_text(strip=True) if email_tag else None,
                "website": lab_tag['href'] if lab_tag and lab_tag.has_attr('href') else None,
            }
        except Exception:
            return None

    async def _extract_professors(self, html_content: str, univ_name: str) -> List[Dict]:
        """
        HTML 콘텐츠에서 교수 목록을 추출합니다.
        대학별로 다른 HTML 구조에 대응하기 위해 여러 CSS 선택자를 시도합니다.
        """
        if not html_content:
            return []

        soup = BeautifulSoup(html_content, 'html.parser')
        professors = []
        
        # 대학별 또는 일반적인 교수 목록 선택자
        common_selectors = [
            ".professor_wrap > ul > li",          # 서울대 자연과학대학
            ".prof_list li",                      # 서울대 공과대학 (수정됨)
            "div.faculty-member",                 # 일반적인 패턴
            "div.professor-item",                 # 일반적인 패턴
            "article.professor"                   # 일반적인 패턴
        ]

        for selector in common_selectors:
            elements = soup.select(selector)
            if elements:
                print(f"   -> Found {len(elements)} potential professors with selector '{selector}'")
                for elem in elements:
                    prof_info = self._parse_professor_element(elem)
                    if prof_info and prof_info.get('name'):
                        professors.append(prof_info)
                if professors:
                    break # 교수를 찾았으면 더 이상 다른 선택자를 시도하지 않음
        
        return professors

    async def crawl_department(self, target: Dict) -> Dict:
        """
        개별 학과 페이지에서 교수 정보를 크롤링합니다.
        """
        print(f"   -> Crawling {target['department_url']}...")
        html_content = await self._fetch_page_content(target['department_url'])
        
        if not html_content:
            return {"success": False, "error": "Failed to fetch page content.", "professors": []}

        professors = await self._extract_professors(html_content, target['university_name'])
        
        return {
            "success": True,
            "professors": professors,
            "prof_count": len(professors)
        }

    def _update_target_status(self, target_id: int, status: str, error: Optional[str] = None):
        """크롤링 상태를 DB에 업데이트합니다."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE crawl_targets
            SET status = ?, last_error = ?, updated_at = ?
            WHERE id = ?
        """, (status, error, datetime.now(), target_id))
        conn.commit()
        conn.close()

    async def crawl_all_targets(self):
        """
        모든 타겟 학과에서 크롤링을 실행하고 결과를 DB에 저장합니다.
        """
        targets = self.get_targets_for_crawl(status="URLFound")
        if not targets:
            print("✅ 크롤링할 대상(status='URLFound')이 없습니다.")
            return

        print(f"🎯 총 {len(targets)}개 학과에 대한 크롤링 시작...")
        
        successful_crawls = 0
        total_professors = 0

        for i, target in enumerate(targets, 1):
            print(f"[{i}/{len(targets)}] {target['university_name']} - {target['department_name']}")
            
            result = await self.crawl_department(target)

            if result["success"] and result["prof_count"] > 0:
                successful_crawls += 1
                total_professors += result["prof_count"]
                # TODO: 수집된 교수 정보를 별도의 테이블에 저장하는 로직 추가
                # self.save_professors(target['id'], result['professors'])
                self._update_target_status(target["id"], "Complete")
                print(f"   ✅ 성공: {result['prof_count']}명의 교수 정보 수집")
            elif result["success"]:
                self._update_target_status(target["id"], "NoData")
                print("   ⚠️ 성공했으나 수집된 교수 정보가 없습니다.")
            else:
                self._update_target_status(target["id"], "Failed", result.get("error"))
                print(f"   ❌ 실패: {result.get('error')}")

            await asyncio.sleep(1) # 서버 부하 방지를 위한 딜레이

        print(f"\n🏁 크롤링 완료: {successful_crawls}개 학과 성공, 총 {total_professors}명의 교수 정보 수집.")

    def run(self):
        """비동기 크롤링 작업을 실행하기 위한 동기 래퍼입니다."""
        try:
            asyncio.run(self.crawl_all_targets())
        except RuntimeError as e:
            if "cannot be called from a running event loop" in str(e):
                # 이미 이벤트 루프가 실행 중인 경우 (예: Jupyter notebook)
                # 현재 루프에서 작업을 실행합니다.
                loop = asyncio.get_running_loop()
                loop.create_task(self.crawl_all_targets())
            else:
                raise
