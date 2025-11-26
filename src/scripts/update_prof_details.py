
import sys
import os
import re
import asyncio
import json
import ollama
from urllib.parse import urljoin

# Add project root to path
sys.path.append(os.getcwd())

from src.core.database import SessionLocal
from src.domain.models import Professor, Laboratory
from src.services.crawler import UniversityCrawler

async def update_prof_details():
    db = SessionLocal()
    crawler = UniversityCrawler()
    
    try:
        print("🚀 Starting Professor Detail Update...")
        
        # 1. Get Faculty List Page
        list_url = "https://cse.snu.ac.kr/people/faculty"
        print(f"1️⃣ Crawling list page: {list_url}")
        
        try:
            result = await crawler._crawl_async(list_url)
        except Exception as e:
            print(f"❌ Failed to crawl list page: {e}")
            return

        # 2. Parse Links
        content = result.content_raw
        links = re.findall(r'\[(.*?)\]\((.*?)\)', content)
        
        prof_urls = {}
        for text, url in links:
            if "/people/faculty/" in url:
                # Clean name: Remove '교수', '부교수', '조교수', '(...)', spaces
                clean_name = re.sub(r'교수|부교수|조교수|\(.*\)', '', text).strip()
                full_url = url if url.startswith('http') else urljoin("https://cse.snu.ac.kr", url)
                prof_urls[clean_name] = full_url
                print(f"   Found URL for {clean_name}: {full_url}")

        # 3. Update DB and Crawl Details
        profs = db.query(Professor).all()
        print(f"ℹ️ Found {len(profs)} professors in DB.")
        
        for prof in profs:
            # Match by name
            # DB name might be English or Korean. Try both if available.
            # Our previous script saved English names mostly.
            # But the links have Korean names.
            # We need a way to match.
            # Let's try to match by partial string or assume we need to update based on Korean name if available.
            
            # Since we saved English names in 'name' and 'name_ko' in deep_crawl_faculty.py,
            # we might have a mismatch.
            # Let's try to match loosely.
            
            matched_url = None
            for name_key, url in prof_urls.items():
                if name_key in prof.name or (prof.name_ko and name_key in prof.name_ko):
                    matched_url = url
                    break
            
            if not matched_url:
                # Try to find by English name mapping (Mock logic or LLM translation needed ideally)
                # For now, skip if no match
                print(f"⚠️ No URL found for {prof.name}")
                continue
                
            print(f"✅ Updating {prof.name} with URL: {matched_url}")
            prof.profile_url = matched_url
            db.commit()
            
            # 4. Crawl Detail Page
            print(f"   🕷️ Crawling detail page...")
            try:
                detail_result = await crawler._crawl_async(matched_url)
                if not detail_result:
                    print("      Failed to crawl detail page.")
                    continue
                    
                # 5. Extract Details with LLM
                prompt = f"""
                Extract detailed information about the professor from this text.
                
                Text:
                {detail_result.content_raw[:4000]}
                
                Instructions:
                1. Extract Email, Website, Lab Name, Lab Description.
                2. Extract Research Interests (keywords).
                3. Return JSON ONLY.
                
                Output Format:
                {{
                    "email": "...",
                    "website": "...",
                    "lab_name": "...",
                    "lab_description": "...",
                    "research_interests": ["...", "..."]
                }}
                """
                
                response = ollama.chat(model='qwen2:7b', messages=[{'role': 'user', 'content': prompt}])
                resp_content = response['message']['content']
                
                json_match = re.search(r'\{.*\}', resp_content, re.DOTALL)
                if json_match:
                    data = json.loads(json_match.group(0))
                    
                    # Update Professor
                    if data.get('email'): prof.email = data['email']
                    if data.get('website'): prof.profile_url = data['website'] # Or separate website field
                    if data.get('research_interests'): 
                        prof.research_interests = data['research_interests']
                    
                    # Update/Create Lab
                    lab_name = data.get('lab_name')
                    if lab_name and lab_name != "Unknown":
                        # Check if lab exists for this professor
                        lab = db.query(Laboratory).filter(Laboratory.professor_id == prof.id).first()
                        if not lab:
                            import uuid
                            lab = Laboratory(
                                id=str(uuid.uuid4()),
                                professor_id=prof.id,
                                department_id=prof.department_id,
                                name=lab_name,
                                name_ko=lab_name,
                                description=data.get('lab_description')
                            )
                            db.add(lab)
                        else:
                            lab.name = lab_name
                            lab.description = data.get('lab_description')
                            
                    db.commit()
                    print(f"      ✅ Updated details for {prof.name}")
                    
                else:
                    print("      ❌ No JSON in LLM response")

            except Exception as e:
                print(f"      ❌ Error crawling detail: {e}")
                
            # Sleep to be polite
            await asyncio.sleep(1)

    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(update_prof_details())
