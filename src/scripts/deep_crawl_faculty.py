
import sys
import os
import json
import re
import uuid
import asyncio
import ollama
from datetime import datetime

# Add project root to path
sys.path.append(os.getcwd())

from src.core.database import SessionLocal
from src.domain.models import Professor, Department
from src.services.crawler import UniversityCrawler

async def deep_crawl_faculty():
    db = SessionLocal()
    try:
        print("🚀 Starting Deep Crawl for Faculty Information...")
        
        # Target URL: SNU CSE Faculty Page
        target_url = "https://cse.snu.ac.kr/people/faculty"
        print(f"Target URL: {target_url}")

        # 1. Crawl the page
        crawler = UniversityCrawler()
        
        try:
            # Call async method directly since we are already in an event loop
            result = await crawler._crawl_async(target_url)
        except Exception as e:
            print(f"❌ Crawl failed: {e}")
            return

        if not result:
            print("❌ No result from crawler.")
            return

        print(f"✅ Successfully crawled. Content length: {len(result.content_raw)} chars")
        
        # 2. Extract Info using LLM
        # Split content if too large (naive splitting)
        # For qwen2:7b, context is usually 4k-8k. Let's process in chunks of 3000 chars with overlap
        
        content = result.content_raw
        chunk_size = 3000
        overlap = 200
        
        chunks = []
        for i in range(0, len(content), chunk_size - overlap):
            chunks.append(content[i:i + chunk_size])
            
        print(f"ℹ️ Split content into {len(chunks)} chunks for processing.")
        
        all_professors = []
        
        for i, chunk in enumerate(chunks):
            print(f"   Processing chunk {i+1}/{len(chunks)}...")
            
            prompt = f"""
            You are an information extractor.
            Extract Professor information from the following text (part of a university faculty list).
            
            Text:
            {chunk}
            
            Instructions:
            1. Find all professors listed.
            2. Extract Name, Email, and Research Areas (or Major).
            3. Ignore students, staff, or general text.
            4. Return JSON ONLY.
            
            Output Format:
            {{
                "professors": [
                    {{ "name": "Name", "email": "Email", "research_area": "Area" }}
                ]
            }}
            """
            
            try:
                response = ollama.chat(model='qwen2:7b', messages=[{'role': 'user', 'content': prompt}])
                resp_content = response['message']['content']
                
                json_match = re.search(r'\{.*\}', resp_content, re.DOTALL)
                if json_match:
                    data = json.loads(json_match.group(0))
                    profs = data.get('professors', [])
                    all_professors.extend(profs)
                    print(f"      Found {len(profs)} professors in this chunk.")
                else:
                    print("      No JSON found in response.")
            except Exception as e:
                print(f"      Error processing chunk: {e}")

        print(f"✅ Total professors found: {len(all_professors)}")
        
        # 3. Save to DB
        # Get Department
        dept = db.query(Department).filter(Department.name.like("%Computer Science%")).first()
        if not dept:
            print("❌ Department not found. Run previous script first.")
            return
            
        print(f"ℹ️ Saving to Department: {dept.name_ko}")
        
        saved_count = 0
        for prof_data in all_professors:
            name = prof_data.get('name')
            if not name or len(name) < 2 or "Professor" in name: # Simple filter
                continue
                
            # Check duplicate
            exists = db.query(Professor).filter(Professor.department_id == dept.id, Professor.name == name).first()
            if exists:
                continue

            interests = prof_data.get('research_area', [])
            if isinstance(interests, str):
                interests = [interests]

            prof = Professor(
                id=str(uuid.uuid4()),
                department_id=dept.id,
                name=name,
                name_ko=name,
                email=prof_data.get('email'),
                research_interests=interests
            )
            db.add(prof)
            saved_count += 1
            
        db.commit()
        print(f"🎉 Saved {saved_count} new professors to DB!")

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(deep_crawl_faculty())
