
import sys
import os

# Add project root to path
sys.path.append(os.getcwd())

from src.core.database import engine, Base
from src.domain.models import Report, ReportPaper, ReportProfessor

def reset_tables():
    print("🔄 Resetting Report tables...")
    try:
        ReportProfessor.__table__.drop(engine, checkfirst=True)
        ReportPaper.__table__.drop(engine, checkfirst=True)
        Report.__table__.drop(engine, checkfirst=True)
        
        # Create all tables (will only create missing ones)
        Base.metadata.create_all(engine)
        print("✅ Report tables reset successfully.")
    except Exception as e:
        print(f"❌ Error resetting tables: {e}")

if __name__ == "__main__":
    reset_tables()
