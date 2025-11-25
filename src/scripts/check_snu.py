
from src.core.database import SessionLocal
from src.domain.models import University

db = SessionLocal()
u = db.query(University).filter(University.name == "Seoul National University").first()
if u:
    print(f"Found: ID={u.id}, Name={u.name}")
else:
    print("Not found")

u2 = db.query(University).filter(University.id == "seoul-national-university").first()
if u2:
    print(f"Found by ID: ID={u2.id}, Name={u2.name}")
else:
    print("Not found by ID")
db.close()
