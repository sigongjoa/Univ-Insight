#!/usr/bin/env python3
"""
HTML 직접 파싱으로 교수 정보 추출
LLM 대신 BeautifulSoup 사용
"""

import asyncio
import sys
import os
sys.path.append(os.getcwd())

from crawl4ai import AsyncWebCrawler
from bs4 import BeautifulSoup
import re

async def extract_professors_from_html():
    print("="*80)
    print("🔍 HTML 파싱으로 교수 정보 추출")
    print("="*80)
    
    test_url = "https://cba.snu.ac.kr/research/faculty/professor"
    
    print(f"\n[STEP 1] 페이지 크롤링: {test_url}")
    
    async with AsyncWebCrawler(verbose=True) as crawler:
        result = await crawler.arun(url=test_url)
        
        if not result.success:
            print(f"❌ 크롤링 실패")
            return
        
        print(f"✅ 크롤링 성공")
        
        # Parse HTML
        soup = BeautifulSoup(result.html, 'html.parser')
        
        print(f"\n[STEP 2] HTML 구조 분석...")
        
        # Find all text containing professor-like patterns
        all_text = soup.get_text()
        
        # Look for Korean names (2-4 characters)
        korean_name_pattern = r'[가-힣]{2,4}'
        potential_names = re.findall(korean_name_pattern, all_text)
        
        print(f"   발견된 한글 단어: {len(potential_names)}개")
        print(f"   예시: {potential_names[:20]}")
        
        # Look for email patterns
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        emails = re.findall(email_pattern, all_text)
        
        print(f"\n   발견된 이메일: {len(emails)}개")
        print(f"   예시: {emails[:5]}")
        
        # Find specific HTML structures
        print(f"\n[STEP 3] HTML 요소 분석...")
        
        # Try common professor list structures
        structures_to_try = [
            ('div', {'class': 'professor'}),
            ('div', {'class': 'faculty'}),
            ('div', {'class': 'member'}),
            ('li', {'class': 'professor'}),
            ('tr', {}),  # Table rows
            ('div', {'class': re.compile('prof|faculty|member', re.I)}),
        ]
        
        for tag, attrs in structures_to_try:
            elements = soup.find_all(tag, attrs)
            if elements:
                print(f"   ✅ 발견: <{tag}> with {attrs} - {len(elements)}개")
                
                # Show first element
                if elements:
                    print(f"      첫 번째 요소:")
                    print(f"      {str(elements[0])[:200]}...")
        
        # Try to find tables
        tables = soup.find_all('table')
        print(f"\n   테이블: {len(tables)}개")
        
        if tables:
            print(f"   첫 번째 테이블:")
            print(f"   {str(tables[0])[:500]}...")
        
        # Look for links with professor names
        links = soup.find_all('a', href=True)
        print(f"\n   링크: {len(links)}개")
        
        prof_links = []
        for link in links:
            text = link.get_text().strip()
            # Korean names are usually 2-4 characters
            if re.match(r'^[가-힣]{2,4}$', text):
                prof_links.append({
                    'name': text,
                    'url': link.get('href')
                })
        
        print(f"   교수 이름으로 보이는 링크: {len(prof_links)}개")
        for i, prof in enumerate(prof_links[:10], 1):
            print(f"      {i}. {prof['name']}: {prof['url']}")
        
        # Save HTML for manual inspection
        with open('docs/reports/cba_faculty_page.html', 'w', encoding='utf-8') as f:
            f.write(result.html)
        
        print(f"\n✅ HTML 저장: docs/reports/cba_faculty_page.html")
        print(f"   이 파일을 브라우저에서 열어 구조를 확인하세요.")

if __name__ == "__main__":
    asyncio.run(extract_professors_from_html())
