import sys
import os
import logging
import uuid
import re

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.core.database import SessionLocal, init_db
from src.domain.models import University, College, Department, UniversityTier
from src.services.careernet_client import CareerNetClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def slugify(text: str) -> str:
    """
    Simple slugify function for ID generation.
    e.g., "Seoul National University" -> "seoul-national-university"
    e.g., "서울대학교" -> "seoul-national-university" (Manual mapping preferred)
    For Korean, we might just use a UUID or a transliteration if needed, 
    but for now let's use a simple mapping or UUID for unknown ones.
    """
    # Basic English slugify
    text = text.lower()
    text = re.sub(r'[^a-z0-9가-힣]+', '-', text)
    text = text.strip('-')
    return text

# Manual mapping for major universities to keep IDs clean
UNIV_ID_MAP = {
    "서울대학교": "seoul-national-univ",
    "KAIST": "kaist",
    "연세대학교": "yonsei-univ",
    "고려대학교": "korea-univ",
    "포항공과대학교": "postech",
    "성균관대학교": "skku",
    "한양대학교": "hanyang-univ"
}

def get_univ_id(name: str) -> str:
    return UNIV_ID_MAP.get(name, f"univ-{slugify(name)}")

def sync_data():
    """
    Syncs University and Department data from CareerNet API (or Mock) to DB.
    """
    db = SessionLocal()
    client = CareerNetClient()
    
    # Target Universities
    targets = ["서울대학교", "KAIST", "연세대학교", "고려대학교"]
    
    try:
        # Ensure tables exist
        init_db()
        
        for univ_name in targets:
            logger.info(f"Syncing {univ_name}...")
            
            # 1. Fetch Data
            info = client.search_university(univ_name)
            if not info:
                logger.warning(f"Could not find info for {univ_name}")
                continue
                
            # 2. Upsert University
            univ_id = get_univ_id(info.name)
            
            univ = db.query(University).filter_by(id=univ_id).first()
            if not univ:
                univ = University(
                    id=univ_id,
                    name=info.name,
                    name_ko=info.name, # Assuming input name is KO
                    url=info.url,
                    location=info.region,
                    tier=UniversityTier.TOP # Default to TOP for these targets
                )
                db.add(univ)
                logger.info(f"Created University: {univ.name}")
            else:
                # Update fields if needed
                univ.url = info.url
                univ.location = info.region
                logger.info(f"Updated University: {univ.name}")
            
            db.flush() # To get univ.id if generated (though we set it manually)
            
            # 3. Process Departments
            # Group by Category to create Colleges
            # Map: Category -> College Object
            college_map = {}
            
            for dept_info in info.departments:
                category = dept_info.category or "General"
                
                # College ID: univ_id + category slug
                # e.g., seoul-national-univ-col-engineering
                cat_slug = slugify(category)
                # English mapping for categories could be better, but using slug for now
                # "공학계열" -> "gonghak-gyeyeol" (Not pretty, but functional)
                # Better: Map "공학계열" -> "engineering"
                
                CAT_MAP = {
                    "공학계열": "engineering",
                    "자연계열": "natural-science",
                    "의학계열": "medicine",
                    "인문계열": "humanities",
                    "사회계열": "social-sciences",
                    "교육계열": "education",
                    "예체능계열": "arts-sports"
                }
                cat_eng = CAT_MAP.get(category, cat_slug)
                
                college_id = f"{univ_id}-col-{cat_eng}"
                
                if college_id not in college_map:
                    # Check DB
                    college = db.query(College).filter_by(id=college_id).first()
                    if not college:
                        college = College(
                            id=college_id,
                            university_id=univ.id,
                            name=f"College of {category}", # Placeholder English name
                            name_ko=f"{category} 대학", # Placeholder Korean name
                        )
                        db.add(college)
                        logger.info(f"  Created College: {college.name_ko}")
                    college_map[college_id] = college
                
                college = college_map[college_id]
                
                # Upsert Department
                # ID: univ_id + dept slug
                dept_slug = slugify(dept_info.department_name)
                dept_id = f"{univ_id}-dept-{dept_slug}"
                
                dept = db.query(Department).filter_by(id=dept_id).first()
                if not dept:
                    dept = Department(
                        id=dept_id,
                        college_id=college.id,
                        name=dept_info.department_name, # Use KO name for both for now if EN unknown
                        name_ko=dept_info.department_name,
                        description=f"{dept_info.department_name} at {univ.name}"
                    )
                    db.add(dept)
                    logger.info(f"    Created Dept: {dept.name}")
                else:
                    pass # Already exists
            
        db.commit()
        logger.info("Sync completed successfully!")
        
    except Exception as e:
        logger.error(f"Sync failed: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    sync_data()
