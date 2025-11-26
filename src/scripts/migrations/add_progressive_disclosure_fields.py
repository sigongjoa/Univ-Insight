"""
Migration script to add Progressive Disclosure fields to PaperAnalysis table
"""

import sys
import os
sys.path.append(os.getcwd())

from sqlalchemy import text
from src.core.database import engine

def migrate():
    print("🔄 Adding Progressive Disclosure fields to paper_analysis table...")
    
    with engine.connect() as conn:
        try:
            # Add new columns
            conn.execute(text("ALTER TABLE paper_analysis ADD COLUMN topic_easy VARCHAR(255)"))
            print("✅ Added topic_easy column")
        except Exception as e:
            print(f"⚠️  topic_easy: {e}")
            
        try:
            conn.execute(text("ALTER TABLE paper_analysis ADD COLUMN topic_technical VARCHAR(255)"))
            print("✅ Added topic_technical column")
        except Exception as e:
            print(f"⚠️  topic_technical: {e}")
            
        try:
            conn.execute(text("ALTER TABLE paper_analysis ADD COLUMN explanation TEXT"))
            print("✅ Added explanation column")
        except Exception as e:
            print(f"⚠️  explanation: {e}")
            
        try:
            conn.execute(text("ALTER TABLE paper_analysis ADD COLUMN reference_link VARCHAR(500)"))
            print("✅ Added reference_link column")
        except Exception as e:
            print(f"⚠️  reference_link: {e}")
            
        try:
            conn.execute(text("ALTER TABLE paper_analysis ADD COLUMN deep_dive JSON"))
            print("✅ Added deep_dive column")
        except Exception as e:
            print(f"⚠️  deep_dive: {e}")
            
        conn.commit()
        
    print("✅ Migration completed!")

if __name__ == "__main__":
    migrate()
