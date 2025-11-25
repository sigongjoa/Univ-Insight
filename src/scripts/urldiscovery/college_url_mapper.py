
import sqlite3
from typing import Dict, List
from bs4 import BeautifulSoup
import asyncio
import os
import sys
from datetime import datetime

# 프로젝트 루트를 sys.path에 추가
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

try:
    from crawl4ai import AsyncWebCrawler
except ImportError:
    AsyncWebCrawler = None

class CollegeURLMapper:
    """
    각 대학 웹사이트에서 학과 URL을 `crawl4ai`를 사용하여 비동기적으로 자동 추출하고 DB를 업데이트합니다.
    """

    UNIVERSITY_PATTERNS = {
        "서울대학교": {
            "base_url": "https://www.snu.ac.kr",
            "colleges_path": "/academics/departments",
            "css_selector": "div.department-item a"
        },
        "KAIST": {
            "base_url": "https://www.kaist.ac.kr",
            "colleges_path": "/kr/academics/undergraduate/",
            "css_selector": "div.item-box a"
        },
    }

    def __init__(self, db_path: str):
        self.db_path = db_path
        if not AsyncWebCrawler:
            raise ImportError("crawl4ai is not installed. Please install it with 'pip install crawl4ai'")

    async def _fetch_page_content(self, url: str) -> str:
        """주어진 URL의 페이지를 crawl4ai로 가져와 HTML 콘텐츠를 반환합니다."""
        try:
            async with AsyncWebCrawler(verbose=False) as crawler:
                result = await crawler.arun(url=url, timeout=30, wait_until="networkidle")
                if result.success:
                    return result.html
                else:
                    print(f"❌ crawl4ai fetch 실패 ({url}): {result.error_message}")
                    return ""
        except Exception as e:
            print(f"❌ crawl4ai 실행 중 오류 발생 ({url}): {e}")
            return ""

    async def map_university_urls(self, university_name: str) -> List[Dict]:
        """
        특정 대학의 학과 URL을 비동기적으로 매핑합니다.
        """
        pattern = self.UNIVERSITY_PATTERNS.get(university_name)
        if not pattern:
            print(f"⚠️ '{university_name}'에 대한 정의된 패턴이 없습니다. 스킵합니다.")
            return []

        base_url = pattern["base_url"]
        colleges_url = base_url + pattern["colleges_path"]
        css_selector = pattern["css_selector"]

        print(f"🔍 '{university_name}'의 학과 URL을 '{colleges_url}'에서 탐색 중...")
        html_content = await self._fetch_page_content(colleges_url)
        if not html_content:
            print(f"✅ '{university_name}'에서 콘텐츠를 가져오지 못했습니다.")
            return []

        soup = BeautifulSoup(html_content, 'html.parser')
        departments = []

        for link in soup.select(css_selector):
            dept_name = link.get_text(strip=True)
            dept_url = link.get("href", "")

            if dept_url:
                if not dept_url.startswith("http"):
                    import requests.compat
                    dept_url = requests.compat.urljoin(base_url, dept_url)
                
                departments.append({"name": dept_name, "url": dept_url})
        
        print(f"✅ '{university_name}'에서 {len(departments)}개의 학과 URL 발견.")
        return departments

    async def _update_database_async(self):
        """
        DB의 crawl_targets 테이블을 비동기적으로 업데이트합니다.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT DISTINCT university_name FROM crawl_targets WHERE status IN ('Ready', 'URLFound')")
        universities_to_process = [row[0] for row in cursor.fetchall()]
        print(f"🔄 총 {len(universities_to_process)}개 대학의 URL을 업데이트합니다.")

        tasks = [self.map_university_urls(name) for name in universities_to_process]
        results = await asyncio.gather(*tasks)

        updated_count = 0
        for university_name, departments in zip(universities_to_process, results):
            if not departments:
                continue
            
            for dept in departments:
                cursor.execute("""
                    UPDATE crawl_targets
                    SET department_url = ?, status = 'URLFound', updated_at = ?
                    WHERE university_name = ? AND (department_name = ? OR department_name_ko = ?) AND department_url IS NULL
                """, (dept["url"], datetime.now(), university_name, dept["name"], dept["name"]))
                if cursor.rowcount > 0:
                    updated_count += cursor.rowcount
            conn.commit()

        conn.close()
        print(f"🎉 총 {updated_count}개의 학과 URL이 DB에 업데이트되었습니다.")

    def update_database(self):
        """
        비동기 데이터베이스 업데이트 작업을 실행하기 위한 동기 래퍼입니다.
        """
        asyncio.run(self._update_database_async())
