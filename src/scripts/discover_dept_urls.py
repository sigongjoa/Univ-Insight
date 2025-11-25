import sys
import os
import time
import random
from sqlalchemy.orm import Session

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.core.database import SessionLocal
from src.domain.models import Department, University
from src.services.url_discovery import URLDiscoveryService

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def discover_urls():
    """
    DB에 저장된 학과들 중 URL이 없는 학과들의 URL을 검색하여 채워넣습니다.
    """
    db = SessionLocal()
    discovery_service = URLDiscoveryService()
    
    try:
        # 모든 학과 조회 (잘못된 URL 수정 및 Known URL 적용을 위해)
        departments = db.query(Department).all()
        logger.info(f"Found {len(departments)} departments to process.")
        
        for dept in departments:
            # 대학 이름 조회
            # college -> university 관계를 타고 올라가야 함
            # dept.college.university.name
            
            # Lazy loading 주의: session이 열려있으므로 접근 가능
            univ_name = dept.college.university.name_ko
            dept_name = dept.name_ko
            
            logger.info(f"Processing: {univ_name} - {dept_name}")
            
            # 검색
            url = discovery_service.find_department_url(univ_name, dept_name)
            
            if url:
                dept.website = url
                db.add(dept)
                db.commit() # 바로바로 커밋 (중간에 끊겨도 저장되도록)
                logger.info(f"Updated DB: {dept.name} -> {url}")
            else:
                logger.warning(f"Failed to find URL for {dept.name}")
            
            # Rate limiting (너무 빠르면 차단될 수 있음)
            time.sleep(random.uniform(1.0, 3.0))
            
    except Exception as e:
        logger.error(f"Discovery process failed: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    discover_urls()
