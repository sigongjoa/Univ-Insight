import asyncio
import sys
import os
import logging
import random
import uuid
from sqlalchemy.orm import Session

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.core.database import SessionLocal
from src.domain.models import Department, Professor, Laboratory
from src.services.deep_crawler import DeepCrawler

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def process_department(db: Session, crawler: DeepCrawler, dept: Department):
    """
    Process a single department: crawl URL, extract professors, save to DB.
    """
    if not dept.website:
        logger.warning(f"Skipping {dept.name} (No URL)")
        return

    logger.info(f"Processing Department: {dept.name} ({dept.website})")
    
    try:
        # 1. Extract Data
        professors_data = await crawler.extract_professors_from_url(dept.website)
        
        if not professors_data:
            logger.warning(f"No professors found for {dept.name}")
            return

        # 2. Save to DB
        count = 0
        for p_data in professors_data:
            name = p_data.get("name")
            if not name: continue
            
            # Generate ID or check existing
            # Simple ID generation: dept_id + slugified name
            # But name might be Korean, so maybe UUID is safer or hash
            # Let's use UUID for now to avoid collision issues with same names
            
            # Check if professor exists by name in this dept
            existing_prof = db.query(Professor).filter_by(
                department_id=dept.id, 
                name=name
            ).first()
            
            if existing_prof:
                prof = existing_prof
                # Update fields
                prof.email = p_data.get("email")
                prof.research_interests = p_data.get("research_areas", [])
                logger.info(f"  Updated Professor: {name}")
            else:
                prof_id = f"prof-{uuid.uuid4().hex[:8]}"
                prof = Professor(
                    id=prof_id,
                    department_id=dept.id,
                    name=name,
                    name_ko=name, # Assuming extracted name is primary
                    email=p_data.get("email"),
                    research_interests=p_data.get("research_areas", []),
                    title="Professor" # Default
                )
                db.add(prof)
                logger.info(f"  Created Professor: {name}")
            
            db.flush() # Get ID
            
            # Create Lab if lab_name exists
            lab_name = p_data.get("lab_name")
            if lab_name:
                # Check existing lab
                existing_lab = db.query(Laboratory).filter_by(
                    professor_id=prof.id
                ).first()
                
                if not existing_lab:
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
                    logger.info(f"    Created Lab: {lab_name}")
            
            count += 1
            
        db.commit()
        logger.info(f"✅ Saved {count} professors for {dept.name}")

    except Exception as e:
        logger.error(f"Failed to process {dept.name}: {e}")
        db.rollback()

async def main():
    print(">>> [Phase 2-3] Running Deep Crawler for All Departments")
    
    db = SessionLocal()
    crawler = DeepCrawler() # Uses default model (qwen2.5 or configured)
    
    try:
        # Get all departments with URLs
        # Filter out those with 'go.kr' or invalid ones if needed, but Discovery service handled most.
        departments = db.query(Department).filter(Department.website != None).all()
        
        logger.info(f"Found {len(departments)} departments to crawl.")
        
        for dept in departments:
            await process_department(db, crawler, dept)
            
            # Respectful delay
            delay = random.uniform(2.0, 5.0)
            logger.info(f"Sleeping for {delay:.1f}s...")
            await asyncio.sleep(delay)
            
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(main())
