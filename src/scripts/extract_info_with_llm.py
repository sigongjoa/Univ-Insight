
import sys
import os
import json
import re
import uuid
import ollama
from datetime import datetime

# Add project root to path
sys.path.append(os.getcwd())

from src.core.database import SessionLocal
from src.domain.models import ResearchPaper, Professor, Laboratory, Department, University

def extract_info():
    db = SessionLocal()
    try:
        print("🚀 Starting Information Extraction with LLM (Ollama)...")

        # 1. Get Crawled Data
        # We look for papers with 'cse.snu.ac.kr' in URL
        paper = db.query(ResearchPaper).filter(ResearchPaper.url.like("%cse.snu.ac.kr%")).order_by(ResearchPaper.crawled_at.desc()).first()
        
        if not paper:
            print("❌ No crawled paper found. Please run the crawler first.")
            return

        print(f"ℹ️ Found crawled data: {paper.title}")
        print(f"   URL: {paper.url}")
        print(f"   Content Length: {len(paper.full_text)} chars")

        # 2. Prepare LLM Prompt
        # Limit content length to fit context window (approx 4000 chars)
        content_snippet = paper.full_text[:4000]
        
        prompt = f"""
        You are an intelligent information extractor.
        Your task is to extract structured information about Professors and Laboratories from the following University webpage content.

        Input Content:
        {content_snippet}...

        Instructions:
        1. Identify any Professors mentioned (name, email, research interests).
        2. Identify any Laboratories mentioned (name, description).
        3. If specific details are missing, use "Unknown" or leave empty.
        4. Extract at least 3 professors and 1 laboratory if possible.

        Output Format:
        You MUST return ONLY a valid JSON object with the following structure:
        {{
            "professors": [
                {{
                    "name": "Professor Name",
                    "email": "email@snu.ac.kr",
                    "research_area": "Research Area"
                }}
            ],
            "laboratories": [
                {{
                    "name": "Lab Name",
                    "description": "Lab Description"
                }}
            ]
        }}
        """

        print("⏳ Sending request to Ollama (qwen2:7b)...")
        response = ollama.chat(model='qwen2:7b', messages=[
            {
                'role': 'user',
                'content': prompt,
            },
        ])
        
        content = response['message']['content']
        print("📥 Received response from LLM")
        
        # 3. Parse JSON
        try:
            # Find JSON block
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                data = json.loads(json_str)
            else:
                print("❌ Failed to find JSON in response")
                print(f"Response: {content[:500]}...")
                return

            print(f"✅ Extracted Data: {len(data.get('professors', []))} professors, {len(data.get('laboratories', []))} labs")

            # 4. Save to DB
            # Ensure University, College, and Department exist
            uni_id = "seoul-national-univ"
            college_id = "snu-eng" # Mock college ID
            dept_id = "snu-cse" # Mock department ID
            
            from src.domain.models import College

            # Check/Create College
            # First try by ID
            college = db.query(College).filter(College.id == college_id).first()
            if not college:
                # Try by name and university_id
                college = db.query(College).filter(
                    College.university_id == uni_id,
                    College.name == "College of Engineering"
                ).first()
                
            if not college:
                college = College(
                    id=college_id,
                    university_id=uni_id,
                    name="College of Engineering",
                    name_ko="공과대학",
                    description="Engineering college"
                )
                db.add(college)
                db.flush()
                print(f"   Created College: {college.name_ko}")
            else:
                print(f"   Using existing College: {college.name_ko} ({college.id})")
                college_id = college.id # Use the existing ID

            # Check/Create Department
            dept = db.query(Department).filter(Department.id == dept_id).first()
            if not dept:
                # Try by name and college_id
                dept = db.query(Department).filter(
                    Department.college_id == college_id,
                    Department.name == "Computer Science and Engineering"
                ).first()

            if not dept:
                dept = Department(
                    id=dept_id,
                    college_id=college_id,  # Link to College, not University
                    name="Computer Science and Engineering",
                    name_ko="컴퓨터공학부",
                    website="https://cse.snu.ac.kr"
                )
                db.add(dept)
                db.flush()
                print(f"   Created Department: {dept.name_ko}")
            else:
                print(f"   Using existing Department: {dept.name_ko} ({dept.id})")
                dept_id = dept.id # Use existing ID

            # Save Professors
            saved_professors = []
            for prof_data in data.get('professors', []):
                # Ensure research_interests is a list
                interests = prof_data.get('research_area', [])
                if isinstance(interests, str):
                    interests = [interests]
                
                prof = Professor(
                    id=str(uuid.uuid4()),
                    department_id=dept_id,
                    name=prof_data.get('name'),
                    name_ko=prof_data.get('name'), # Use English name for Korean name temporarily
                    email=prof_data.get('email'),
                    research_interests=interests
                )
                db.add(prof)
                saved_professors.append(prof)
                print(f"   Saved Professor: {prof.name} ({prof.research_interests})")

            # Save Labs
            # Link to the first professor found (Mock logic for now)
            first_prof_id = saved_professors[0].id if saved_professors else None
            
            if first_prof_id:
                for lab_data in data.get('laboratories', []):
                    lab = Laboratory(
                        id=str(uuid.uuid4()),
                        department_id=dept_id,
                        professor_id=first_prof_id, # Link to first professor
                        name=lab_data.get('name'),
                        name_ko=lab_data.get('name'), # Use English name
                        description=lab_data.get('description')
                    )
                    db.add(lab)
                    print(f"   Saved Lab: {lab.name} (Linked to Prof: {saved_professors[0].name})")
            else:
                print("⚠️ No professors found to link laboratories to.")

            db.commit()
            print("\n🎉 Information extraction and storage complete!")

        except json.JSONDecodeError:
            print("❌ Failed to parse JSON response")
            print(f"Response: {content}")

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    extract_info()
