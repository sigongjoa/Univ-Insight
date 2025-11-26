#!/usr/bin/env python3
"""
서울대 경영학과 크롤링 및 리포트 생성
"""

import asyncio
import sys
import os
sys.path.append(os.getcwd())

from src.core.database import SessionLocal
from src.domain.models import Department, Professor, Laboratory
from src.services.deep_crawler import DeepCrawler
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def crawl_business_department():
    print("="*80)
    print("🕷️ 서울대 경영학과 크롤링")
    print("="*80)
    
    db = SessionLocal()
    
    try:
        # Find Business Department
        dept = db.query(Department).filter(Department.name_ko.like('%경영%')).first()
        
        if not dept:
            print("❌ 경영학과를 찾을 수 없습니다.")
            return
        
        print(f"\n✅ 학과: {dept.name_ko}")
        print(f"🌐 웹사이트: {dept.website}")
        
        # Use the faculty page directly
        faculty_url = "https://cba.snu.ac.kr/research/faculty/professor"
        print(f"👨‍🏫 교수진 페이지: {faculty_url}")
        
        # Initialize crawler
        crawler = DeepCrawler(model_name="qwen2:7b")
        
        # Crawl
        print(f"\n🕷️ 크롤링 시작...")
        professors_data = await crawler.extract_professors_from_url(faculty_url)
        
        if not professors_data:
            print("❌ 교수 정보를 추출하지 못했습니다.")
            print("\n💡 수동으로 페이지를 확인해보세요:")
            print(f"   {faculty_url}")
            return
        
        print(f"\n✅ {len(professors_data)}명의 교수 정보 추출")
        
        # Save to DB
        import uuid
        saved_count = 0
        
        for p_data in professors_data:
            name = p_data.get("name")
            if not name:
                continue
            
            # Check existing
            existing = db.query(Professor).filter_by(
                department_id=dept.id,
                name=name
            ).first()
            
            if existing:
                print(f"   ⏭️  이미 존재: {name}")
                continue
            
            # Create new professor
            prof_id = f"prof-{uuid.uuid4().hex[:8]}"
            prof = Professor(
                id=prof_id,
                department_id=dept.id,
                name=name,
                name_ko=name,
                email=p_data.get("email"),
                research_interests=p_data.get("research_areas", []),
                title="Professor"
            )
            db.add(prof)
            db.flush()
            
            # Create lab if exists
            lab_name = p_data.get("lab_name")
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
            
            print(f"   ✅ 저장: {name}")
            saved_count += 1
        
        db.commit()
        
        print(f"\n✅ 총 {saved_count}명의 교수 저장 완료")
        
        # Refresh to get updated count
        db.refresh(dept)
        print(f"📊 경영학과 교수 수: {len(dept.professors)}")
        
    except Exception as e:
        print(f"\n❌ 오류: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(crawl_business_department())
