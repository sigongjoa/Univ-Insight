#!/usr/bin/env python3
"""
서울대 조직도 기반 계층적 크롤링
1. 조직도에서 단과대 목록 추출
2. 각 단과대 홈페이지 크롤링
3. 학과 목록 추출
4. 교수진 정보 크롤링
"""

import asyncio
import sys
import os
sys.path.append(os.getcwd())

from crawl4ai import AsyncWebCrawler
from bs4 import BeautifulSoup
from src.core.database import SessionLocal
from src.domain.models import University, College, Department, Professor, Laboratory
from src.services.deep_crawler import DeepCrawler
import json
import uuid
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def crawl_organization_page():
    """조직도 페이지에서 단과대 목록 추출"""
    org_url = "https://www.snu.ac.kr/about/overview/organization/sub_organ"
    
    async with AsyncWebCrawler(verbose=True) as crawler:
        result = await crawler.arun(url=org_url)
        
        if not result.success:
            logger.error(f"조직도 크롤링 실패: {result.error_message}")
            return []
        
        logger.info("✅ 조직도 페이지 크롤링 성공")
        
        soup = BeautifulSoup(result.html, 'html.parser')
        
        # Find college links
        colleges = []
        
        # Look for links containing college-related keywords
        for link in soup.find_all('a', href=True):
            text = link.get_text().strip()
            href = link.get('href')
            
            # Filter for colleges (단과대학)
            if any(keyword in text for keyword in ['대학', '학부']) and len(text) < 20:
                # Skip generic links
                if text in ['대학', '학부', '대학원']:
                    continue
                
                # Build full URL
                if href.startswith('http'):
                    url = href
                elif href.startswith('/'):
                    url = 'https://www.snu.ac.kr' + href
                else:
                    continue
                
                colleges.append({
                    'name_ko': text,
                    'name': text,  # Will translate later
                    'url': url
                })
        
        # Remove duplicates
        seen = set()
        unique_colleges = []
        for college in colleges:
            if college['name_ko'] not in seen:
                seen.add(college['name_ko'])
                unique_colleges.append(college)
        
        logger.info(f"✅ {len(unique_colleges)}개 단과대 발견")
        for i, college in enumerate(unique_colleges, 1):
            logger.info(f"   {i}. {college['name_ko']}: {college['url']}")
        
        return unique_colleges

async def crawl_college_departments(college_url, college_name):
    """단과대 홈페이지에서 학과 목록 추출"""
    async with AsyncWebCrawler(verbose=True) as crawler:
        result = await crawler.arun(url=college_url)
        
        if not result.success:
            logger.error(f"{college_name} 크롤링 실패: {result.error_message}")
            return []
        
        soup = BeautifulSoup(result.html, 'html.parser')
        
        departments = []
        dept_keywords = ['학과', '학부', 'department', 'dept']
        
        for link in soup.find_all('a', href=True):
            text = link.get_text().strip()
            href = link.get('href')
            
            # Check if it's a department link
            if any(keyword in text.lower() for keyword in dept_keywords):
                if len(text) > 50 or len(text) < 3:
                    continue
                
                # Build full URL
                if href.startswith('http'):
                    url = href
                elif href.startswith('/'):
                    # Use college domain
                    from urllib.parse import urlparse
                    parsed = urlparse(college_url)
                    url = f"{parsed.scheme}://{parsed.netloc}{href}"
                else:
                    continue
                
                departments.append({
                    'name_ko': text,
                    'name': text,
                    'url': url
                })
        
        # Remove duplicates
        seen = set()
        unique_depts = []
        for dept in departments:
            if dept['name_ko'] not in seen:
                seen.add(dept['name_ko'])
                unique_depts.append(dept)
        
        logger.info(f"   → {len(unique_depts)}개 학과 발견")
        
        return unique_depts

async def crawl_department_faculty(dept_url, dept_name):
    """학과 페이지에서 교수진 페이지 찾기 및 크롤링"""
    # Try common faculty page patterns
    faculty_patterns = [
        '/faculty',
        '/professor',
        '/people',
        '/members',
        '/교수진',
        '/구성원'
    ]
    
    from urllib.parse import urlparse, urljoin
    parsed = urlparse(dept_url)
    base_url = f"{parsed.scheme}://{parsed.netloc}"
    
    async with AsyncWebCrawler(verbose=True) as crawler:
        # First, try to find faculty link on department page
        result = await crawler.arun(url=dept_url)
        
        if result.success:
            soup = BeautifulSoup(result.html, 'html.parser')
            
            # Look for faculty links
            for link in soup.find_all('a', href=True):
                text = link.get_text().strip().lower()
                href = link.get('href')
                
                if any(pattern in text for pattern in ['교수', 'faculty', 'professor', '구성원']):
                    faculty_url = urljoin(base_url, href)
                    logger.info(f"   → 교수진 페이지 발견: {faculty_url}")
                    
                    # Use DeepCrawler to extract professors
                    deep_crawler = DeepCrawler(model_name="qwen2:7b")
                    professors = await deep_crawler.extract_professors_from_url(faculty_url)
                    
                    return professors, faculty_url
        
        # If not found, try common patterns
        for pattern in faculty_patterns:
            test_url = base_url + pattern
            logger.info(f"   시도: {test_url}")
            
            result = await crawler.arun(url=test_url)
            if result.success:
                logger.info(f"   → 교수진 페이지 발견: {test_url}")
                
                deep_crawler = DeepCrawler(model_name="qwen2:7b")
                professors = await deep_crawler.extract_professors_from_url(test_url)
                
                if professors:
                    return professors, test_url
    
    return [], None

async def save_to_database(colleges_data):
    """크롤링 결과를 데이터베이스에 저장"""
    db = SessionLocal()
    
    try:
        # Get or create SNU
        uni = db.query(University).filter(University.name.like("%Seoul%National%")).first()
        if not uni:
            uni = University(
                id="snu",
                name="Seoul National University",
                name_ko="서울대학교",
                url="https://www.snu.ac.kr"
            )
            db.add(uni)
            db.flush()
        
        for college_data in colleges_data:
            # Create or update college
            college_id = f"snu-{college_data['name_ko'][:3]}-{uuid.uuid4().hex[:4]}"
            college = College(
                id=college_id,
                university_id=uni.id,
                name=college_data['name'],
                name_ko=college_data['name_ko']
            )
            db.add(college)
            db.flush()
            
            logger.info(f"✅ 저장: {college_data['name_ko']}")
            
            # Save departments
            for dept_data in college_data.get('departments', []):
                dept_id = f"dept-{uuid.uuid4().hex[:8]}"
                dept = Department(
                    id=dept_id,
                    college_id=college.id,
                    name=dept_data['name'],
                    name_ko=dept_data['name_ko'],
                    website=dept_data.get('url')
                )
                db.add(dept)
                db.flush()
                
                # Save professors
                for prof_data in dept_data.get('professors', []):
                    prof_id = f"prof-{uuid.uuid4().hex[:8]}"
                    prof = Professor(
                        id=prof_id,
                        department_id=dept.id,
                        name=prof_data.get('name', ''),
                        name_ko=prof_data.get('name', ''),
                        email=prof_data.get('email'),
                        research_interests=prof_data.get('research_areas', []),
                        title="Professor"
                    )
                    db.add(prof)
                    
                    # Create lab if exists
                    lab_name = prof_data.get('lab_name')
                    if lab_name:
                        lab_id = f"lab-{uuid.uuid4().hex[:8]}"
                        lab = Laboratory(
                            id=lab_id,
                            professor_id=prof.id,
                            department_id=dept.id,
                            name=lab_name,
                            name_ko=lab_name,
                            research_areas=prof.research_interests
                        )
                        db.add(lab)
        
        db.commit()
        logger.info("✅ 데이터베이스 저장 완료")
        
    except Exception as e:
        logger.error(f"❌ 데이터베이스 저장 실패: {e}")
        db.rollback()
    finally:
        db.close()

async def main():
    print("="*80)
    print("🕷️ 서울대 조직도 기반 전체 크롤링")
    print("="*80)
    
    # Step 1: 조직도에서 단과대 목록 추출
    print("\n[STEP 1] 조직도에서 단과대 목록 추출...")
    colleges = await crawl_organization_page()
    
    if not colleges:
        print("❌ 단과대 목록을 찾을 수 없습니다.")
        return
    
    # Step 2: 각 단과대 크롤링 (처음 3개만 테스트)
    print(f"\n[STEP 2] 단과대 크롤링 (처음 3개)...")
    
    colleges_data = []
    
    for i, college in enumerate(colleges[:3], 1):
        print(f"\n[{i}/{min(3, len(colleges))}] {college['name_ko']}")
        print(f"   URL: {college['url']}")
        
        # Crawl departments
        departments = await crawl_college_departments(college['url'], college['name_ko'])
        
        college['departments'] = []
        
        # Crawl first 2 departments
        for j, dept in enumerate(departments[:2], 1):
            print(f"   [{j}] {dept['name_ko']}")
            
            # Crawl faculty
            professors, faculty_url = await crawl_department_faculty(dept['url'], dept['name_ko'])
            
            dept['professors'] = professors
            dept['faculty_url'] = faculty_url
            
            if professors:
                print(f"      ✅ {len(professors)}명 교수 발견")
            
            college['departments'].append(dept)
        
        colleges_data.append(college)
        
        # Delay between colleges
        await asyncio.sleep(2)
    
    # Step 3: Save to database
    print("\n[STEP 3] 데이터베이스 저장...")
    await save_to_database(colleges_data)
    
    # Save JSON
    output_file = "docs/reports/snu_full_crawl_result.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(colleges_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 결과 저장: {output_file}")
    
    print("\n" + "="*80)
    print("✅ 크롤링 완료!")
    print("="*80)

if __name__ == "__main__":
    asyncio.run(main())
