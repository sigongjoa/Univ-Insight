#!/usr/bin/env python3
"""
경영대학 교수 정보 HTML 파싱
BeautifulSoup로 직접 추출
"""

import asyncio
import sys
import os
sys.path.append(os.getcwd())

from crawl4ai import AsyncWebCrawler
from bs4 import BeautifulSoup
from src.core.database import SessionLocal
from src.domain.models import Department, Professor, Laboratory
import uuid

async def crawl_cba_professors():
    print("="*80)
    print("🕷️ 경영대학 교수 정보 크롤링 (HTML 파싱)")
    print("="*80)
    
    url = "https://cba.snu.ac.kr/research/faculty/professor"
    
    async with AsyncWebCrawler(verbose=True) as crawler:
        result = await crawler.arun(url=url)
        
        if not result.success:
            print("❌ 크롤링 실패")
            return
        
        print("✅ 크롤링 성공")
        
        # Parse HTML
        soup = BeautifulSoup(result.html, 'html.parser')
        
        # Find all professor cards
        prof_cards = soup.find_all('div', class_='pro-cont')
        
        print(f"\n✅ {len(prof_cards)}명의 교수 발견")
        
        professors = []
        
        for card in prof_cards:
            try:
                # Extract name
                name_tag = card.find('strong', class_='font-weight-bold')
                if not name_tag:
                    continue
                
                name = name_tag.get_text().strip()
                
                # Extract major
                major_tag = card.find('span')
                major = major_tag.get_text().strip() if major_tag else ""
                
                # Extract education
                edu_tag = card.find('div', class_='edu')
                education = edu_tag.get_text().strip() if edu_tag else ""
                
                # Extract profile URL
                link_tag = card.find('a', href=True)
                profile_url = ""
                if link_tag:
                    href = link_tag.get('href')
                    if href.startswith('http'):
                        profile_url = href
                    else:
                        profile_url = f"https://cba.snu.ac.kr{href}"
                
                professors.append({
                    'name': name,
                    'name_ko': name,
                    'major': major,
                    'education': education,
                    'profile_url': profile_url,
                    'research_interests': [major] if major else []
                })
                
                print(f"   ✅ {name} ({major})")
                
            except Exception as e:
                print(f"   ❌ 파싱 실패: {e}")
                continue
        
        print(f"\n✅ 총 {len(professors)}명 파싱 완료")
        
        # Save to database
        print("\n[데이터베이스 저장]")
        db = SessionLocal()
        
        try:
            # Find or create department
            dept = db.query(Department).filter(Department.name_ko.like('%경영%')).first()
            
            if not dept:
                print("❌ 경영학과를 찾을 수 없습니다.")
                return
            
            print(f"✅ 학과: {dept.name_ko}")
            
            saved_count = 0
            
            for prof_data in professors:
                # Check if exists
                existing = db.query(Professor).filter_by(
                    department_id=dept.id,
                    name_ko=prof_data['name_ko']
                ).first()
                
                if existing:
                    print(f"   ⏭️  이미 존재: {prof_data['name_ko']}")
                    continue
                
                # Create new professor
                prof_id = f"prof-{uuid.uuid4().hex[:8]}"
                prof = Professor(
                    id=prof_id,
                    department_id=dept.id,
                    name=prof_data['name'],
                    name_ko=prof_data['name_ko'],
                    research_interests=prof_data['research_interests'],
                    education=[prof_data['education']] if prof_data['education'] else [],
                    profile_url=prof_data['profile_url'],
                    title="Professor"
                )
                db.add(prof)
                db.flush()
                
                # Create lab
                if prof_data['major']:
                    lab_id = f"lab-{uuid.uuid4().hex[:8]}"
                    lab = Laboratory(
                        id=lab_id,
                        professor_id=prof.id,
                        department_id=dept.id,
                        name=f"{prof_data['name_ko']} 연구실",
                        name_ko=f"{prof_data['name_ko']} 연구실",
                        research_areas=prof_data['research_interests']
                    )
                    db.add(lab)
                
                print(f"   ✅ 저장: {prof_data['name_ko']}")
                saved_count += 1
            
            db.commit()
            
            print(f"\n✅ 총 {saved_count}명 저장 완료")
            print(f"📊 경영학과 교수 수: {len(dept.professors)}")
            
        except Exception as e:
            print(f"\n❌ 데이터베이스 오류: {e}")
            import traceback
            traceback.print_exc()
            db.rollback()
        finally:
            db.close()

if __name__ == "__main__":
    asyncio.run(crawl_cba_professors())
