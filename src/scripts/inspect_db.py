
from src.core.database import SessionLocal
from src.domain.models import University

db = SessionLocal()
unis = db.query(University).all()
for u in unis:
    print(f"ID: {u.id}, Name: {u.name}")
db.close()
