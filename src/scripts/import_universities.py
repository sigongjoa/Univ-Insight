
import csv
import os
import sys
from datetime import datetime
from sqlalchemy.orm import Session
from src.core.database import SessionLocal, engine
from src.domain.models import University, Base

# Ensure we can import from src
sys.path.append(os.getcwd())

def generate_id(english_name):
    if not english_name:
        return None
    # Simple slugification: lowercase, replace spaces/special chars with hyphens
    return english_name.lower().strip().replace(' ', '-').replace(',', '').replace('.', '').replace('(', '').replace(')', '')

def parse_year(date_str):
    if not date_str:
        return None
    try:
        # Format seems to be YYYY-MM-DD based on previous file view
        return int(date_str.split('-')[0])
    except:
        return None

def import_universities(csv_path: str, db: Session):
    print(f"Importing from {csv_path}...")
    
    if not os.path.exists(csv_path):
        print(f"Error: File {csv_path} not found.")
        return

    count = 0
    with open(csv_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            if i == 0:
                print(f"First row keys: {list(row.keys())}")
            # CSV columns: 학교명,학교 영문명,본분교구분명,대학구분명,학교구분명,설립형태구분명,시도코드,시도명,소재지도로명주소,소재지지번주소,도로명우편번호,소재지우편번호,홈페이지주소,대표전화번호,대표팩스번호,설립일자,기준연도,데이터기준일자,제공기관코드,제공기관명
            
            # Filter: We probably only want "본교" (Main Campus) or maybe all? 
            # Let's include all for now, but maybe distinguish them later if needed.
            # actually, let's just import everything.

            name_en = row.get('학교 영문명')
            name_ko = row.get('학교명')
            
            if not name_en or not name_ko:
                continue

            uni_id = generate_id(name_en)
            
            # Check if exists by ID
            existing = db.query(University).filter(University.id == uni_id).first()
            
            # Check if exists by Name (to avoid unique constraint violation)
            if not existing:
                existing = db.query(University).filter(University.name == name_en).first()

            if existing:
                # Update? Or skip. Let's update basic info.
                existing.location = row.get('소재지도로명주소')
                existing.url = row.get('홈페이지주소')
                existing.established_year = parse_year(row.get('설립일자'))
            else:
                uni = University(
                    id=uni_id,
                    name=name_en,
                    name_ko=name_ko,
                    location=row.get('소재지도로명주소'),
                    url=row.get('홈페이지주소'),
                    established_year=parse_year(row.get('설립일자'))
                )
                db.add(uni)
            
            try:
                db.flush()
                count += 1
            except Exception as e:
                db.rollback()
                print(f"Error processing {name_ko} ({name_en}): {e}")
                continue
            
    db.commit()
    print(f"Successfully processed {count} universities.")

if __name__ == "__main__":
    # Create tables if they don't exist
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        csv_file = "전국대학및전문대학정보표준데이터.csv"
        import_universities(csv_file, db)
    finally:
        db.close()
