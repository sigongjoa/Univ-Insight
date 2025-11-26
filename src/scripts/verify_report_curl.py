
import subprocess
import json
import uuid
import sys
import os

# Add project root to path
sys.path.append(os.getcwd())

from src.core.database import SessionLocal
from src.domain.models import User, Report

def verify_report_curl():
    db = SessionLocal()
    try:
        # 1. Create Test User
        user_id = str(uuid.uuid4())
        user = User(
            id=user_id,
            name="Report Tester",
            interests=["Machine Learning", "AI", "Vision"],
            role="student"
        )
        db.add(user)
        db.commit()
        print(f"✅ Created test user: {user_id} with interests {user.interests}")
        
        # 2. Call Create Report API using curl
        print("🚀 Sending request to generate report...")
        cmd = [
            "curl", "-v", "-X", "POST",
            f"http://127.0.0.1:8001/api/v1/users/{user_id}/reports",
            "-H", "Content-Type: application/json"
        ]
        
        # Run curl
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"❌ Curl failed: {result.stderr}")
            return
            
        print(f"📥 Response: {result.stdout}")
        
        try:
            data = json.loads(result.stdout)
            if data.get("status") == "success":
                print("✅ Report generation successful!")
                print(f"   Report ID: {data.get('report_id')}")
                print(f"   PDF URL: {data.get('pdf_url')}")
                print(f"   Content Preview: {data.get('content')[:100]}...")
                print(f"   Recommendations: {data.get('recommendations')}")
                
                if data.get('pdf_url'):
                    pdf_url = f"http://127.0.0.1:8001{data.get('pdf_url')}"
                    print(f"📥 Downloading PDF from {pdf_url}...")
                    subprocess.run(["curl", "-v", "-O", pdf_url])
            else:
                print("❌ API returned error status.")
        except json.JSONDecodeError:
            print("❌ Failed to parse JSON response.")

    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    verify_report_curl()
