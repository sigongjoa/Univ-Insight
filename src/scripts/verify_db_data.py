import sys
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.domain.models import University, College, Department

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.core.database import SessionLocal

def verify_data():
    db = SessionLocal()
    try:
        universities = db.query(University).all()
        print(f"\n>>> [DB Verification] Total Universities: {len(universities)}")
        
        for univ in universities:
            print(f"\n🏫 {univ.name} ({univ.id})")
            print(f"   - URL: {univ.url}")
            print(f"   - Colleges: {len(univ.colleges)}")
            
            for col in univ.colleges:
                print(f"     🏛️ {col.name_ko} ({col.id})")
                print(f"        - Departments: {len(col.departments)}")
                for dept in col.departments:
                    print(f"          • {dept.name} ({dept.id})")
                    print(f"            🔗 {dept.website}")
                    
    finally:
        db.close()

if __name__ == "__main__":
    verify_data()
