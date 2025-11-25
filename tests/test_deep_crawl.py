import asyncio
import sys
import os
import logging

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.services.deep_crawler import DeepCrawler

logging.basicConfig(level=logging.INFO)

async def main():
    print(">>> [Phase 2-3] Deep Crawler Test")
    
    # 테스트 대상: KAIST 전산학부 (이미 URL Discovery로 찾은 URL)
    target_url = "https://cs.kaist.ac.kr/people/view?type=faculty" 
    # 주의: 실제 리스트 페이지 URL은 메인 페이지와 다를 수 있음. 
    # 일단 메인 페이지나 사람 목록 페이지를 타겟팅해야 함.
    # KAIST CS의 경우 /people/view?type=faculty 가 교수진 목록임.
    # Discovery가 찾아준건 메인(https://cs.kaist.ac.kr)일 수 있으므로, 
    # 실제로는 "Faculty" 링크를 찾는 로직이 추가로 필요하지만, 
    # 여기서는 데모를 위해 직접 교수진 페이지를 입력해봄.
    
    # 만약 메인 페이지라면 LLM이 "Faculty" 링크를 찾아내게 하는게 Best.
    # 일단 테스트를 위해 직접 URL 지정.
    
    crawler = DeepCrawler(model_name="llama2:latest") # User env has llama2
    
    print(f"\n>>> Crawling: {target_url}")
    professors = await crawler.extract_professors_from_url(target_url)
    
    print(f"\n>>> Extracted {len(professors)} Professors:")
    for p in professors[:5]: # Show top 5
        print(f"   👨‍🏫 {p.get('name')} ({p.get('email')})")
        print(f"       Lab: {p.get('lab_name')}")
        print(f"       Areas: {p.get('research_areas')}")
        print("---")

if __name__ == "__main__":
    asyncio.run(main())
