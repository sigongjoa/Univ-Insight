#!/usr/bin/env python3
"""
서울대 계층적 크롤링
메인 페이지 → 단과대 → 학과 → 교수진
"""

import asyncio
import sys
import os
sys.path.append(os.getcwd())

from crawl4ai import AsyncWebCrawler
from bs4 import BeautifulSoup
import json

async def crawl_snu_structure():
    print("="*80)
    print("🕷️ 서울대 구조 크롤링")
    print("="*80)
    
    snu_main = "https://www.snu.ac.kr"
    
    async with AsyncWebCrawler(verbose=True) as crawler:
        # Step 1: 메인 페이지
        print("\n[STEP 1] 메인 페이지 크롤링...")
        result = await crawler.arun(url=snu_main)
        
        if not result.success:
            print(f"❌ 메인 페이지 크롤링 실패: {result.error_message}")
            return
        
        print(f"✅ 메인 페이지 크롤링 성공")
        print(f"   HTML 길이: {len(result.html)} chars")
        
        # Parse HTML to find college/department links
        soup = BeautifulSoup(result.html, 'html.parser')
        
        # Find all links
        all_links = soup.find_all('a', href=True)
        print(f"\n   총 링크 수: {len(all_links)}")
        
        # Filter for college/department related links
        college_keywords = ['단과대', 'college', '대학', '학부', 'faculty']
        dept_keywords = ['학과', 'department', '전공']
        
        college_links = []
        for link in all_links:
            href = link.get('href', '')
            text = link.get_text().strip()
            
            # Check if link is related to colleges
            if any(keyword in text.lower() or keyword in href.lower() for keyword in college_keywords):
                if href.startswith('http'):
                    college_links.append({'text': text, 'url': href})
                elif href.startswith('/'):
                    college_links.append({'text': text, 'url': snu_main + href})
        
        print(f"\n✅ 단과대 관련 링크 {len(college_links)}개 발견:")
        for i, link in enumerate(college_links[:20], 1):  # Show first 20
            print(f"   {i}. {link['text']}: {link['url']}")
        
        # Step 2: Try to find organization/structure page
        print("\n[STEP 2] 조직도/구성 페이지 찾기...")
        
        org_keywords = ['조직', 'organization', '구성', 'structure', '단과대학', '학사']
        org_links = []
        
        for link in all_links:
            href = link.get('href', '')
            text = link.get_text().strip()
            
            if any(keyword in text.lower() or keyword in href.lower() for keyword in org_keywords):
                if href.startswith('http'):
                    org_links.append({'text': text, 'url': href})
                elif href.startswith('/'):
                    org_links.append({'text': text, 'url': snu_main + href})
        
        print(f"✅ 조직 관련 링크 {len(org_links)}개 발견:")
        for i, link in enumerate(org_links[:10], 1):
            print(f"   {i}. {link['text']}: {link['url']}")
        
        # Step 3: Crawl a specific college page (example: Engineering)
        print("\n[STEP 3] 공과대학 페이지 크롤링...")
        
        # Known SNU Engineering URL
        eng_url = "https://eng.snu.ac.kr"
        result = await crawler.arun(url=eng_url)
        
        if result.success:
            print(f"✅ 공과대학 페이지 크롤링 성공")
            soup = BeautifulSoup(result.html, 'html.parser')
            
            # Find department links
            dept_links = []
            for link in soup.find_all('a', href=True):
                href = link.get('href', '')
                text = link.get_text().strip()
                
                if any(keyword in text for keyword in dept_keywords):
                    if href.startswith('http'):
                        dept_links.append({'text': text, 'url': href})
                    elif href.startswith('/'):
                        dept_links.append({'text': text, 'url': eng_url + href})
            
            print(f"✅ 학과 링크 {len(dept_links)}개 발견:")
            for i, link in enumerate(dept_links[:15], 1):
                print(f"   {i}. {link['text']}: {link['url']}")
        
        # Save results
        results = {
            "main_url": snu_main,
            "college_links": college_links[:20],
            "org_links": org_links[:10],
            "engineering_dept_links": dept_links[:15] if 'dept_links' in locals() else []
        }
        
        output_file = "docs/reports/snu_crawl_structure.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ 결과 저장: {output_file}")
        
        # Step 4: Recommendations
        print("\n" + "="*80)
        print("📋 다음 단계 추천:")
        print("="*80)
        print("\n1. 단과대 목록 페이지 찾기:")
        print("   - https://www.snu.ac.kr/about/colleges (예상)")
        print("   - 또는 조직도 페이지에서 단과대 목록 추출")
        print("\n2. 각 단과대 홈페이지 크롤링:")
        print("   - 공과대학: https://eng.snu.ac.kr")
        print("   - 경영대학: https://cba.snu.ac.kr")
        print("   - 등등...")
        print("\n3. 각 단과대에서 학과 목록 추출")
        print("\n4. 각 학과에서 교수진 페이지 찾기:")
        print("   - /faculty, /professor, /people 등의 경로")

if __name__ == "__main__":
    asyncio.run(crawl_snu_structure())
