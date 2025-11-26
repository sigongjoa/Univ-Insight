#!/usr/bin/env python3
"""
LLM 교수 정보 추출 디버깅
실제 응답을 확인하고 문제 파악
"""

import asyncio
import sys
import os
sys.path.append(os.getcwd())

from crawl4ai import AsyncWebCrawler
import ollama
import json
import re

async def debug_llm_extraction():
    print("="*80)
    print("🔍 LLM 교수 정보 추출 디버깅")
    print("="*80)
    
    # Test URL: 경영대학 교수진 페이지
    test_url = "https://cba.snu.ac.kr/research/faculty/professor"
    
    print(f"\n[STEP 1] 페이지 크롤링: {test_url}")
    
    async with AsyncWebCrawler(verbose=True) as crawler:
        result = await crawler.arun(url=test_url)
        
        if not result.success:
            print(f"❌ 크롤링 실패: {result.error_message}")
            return
        
        print(f"✅ 크롤링 성공")
        print(f"   Markdown 길이: {len(result.markdown)} chars")
        
        # Show first 1000 chars
        print(f"\n[STEP 2] 페이지 내용 미리보기:")
        print("-"*80)
        print(result.markdown[:1000])
        print("-"*80)
        
        # Prepare content for LLM
        content = result.markdown[:15000]
        
        # Test different prompts
        prompts = [
            # Prompt 1: Very simple
            {
                "name": "Simple Prompt",
                "content": f"""Extract professor names from this text. Return ONLY a JSON array like this:
[{{"name": "Kim Chul-soo"}}, {{"name": "Lee Young-hee"}}]

Text:
{content[:5000]}"""
            },
            
            # Prompt 2: Structured but clear
            {
                "name": "Structured Prompt",
                "content": f"""You are extracting professor information from a university faculty page.

Return ONLY a JSON array. Each object should have:
- name: professor's name
- email: email if found (or null)

Example: [{{"name": "홍길동", "email": "hong@snu.ac.kr"}}, {{"name": "김철수", "email": null}}]

Text:
{content[:8000]}

JSON array:"""
            },
            
            # Prompt 3: Step by step
            {
                "name": "Step-by-step Prompt",
                "content": f"""Task: Find all professors in this text.

Step 1: Look for names (Korean or English)
Step 2: Look for email addresses
Step 3: Return as JSON array

Format: [{{"name": "...", "email": "..."}}, ...]

IMPORTANT: Return ONLY the JSON array, nothing else.

Text:
{content[:8000]}

Your JSON array:"""
            }
        ]
        
        for i, prompt_test in enumerate(prompts, 1):
            print(f"\n[TEST {i}] {prompt_test['name']}")
            print("="*80)
            
            try:
                print("🤖 Sending to LLM (qwen2:7b)...")
                response = ollama.chat(
                    model='qwen2:7b',
                    messages=[{'role': 'user', 'content': prompt_test['content']}]
                )
                
                response_content = response['message']['content']
                
                print(f"\n📝 LLM Response (first 500 chars):")
                print("-"*80)
                print(response_content[:500])
                print("-"*80)
                
                print(f"\n📝 LLM Response (full):")
                print("-"*80)
                print(response_content)
                print("-"*80)
                
                # Try to parse JSON
                print(f"\n🔧 Attempting JSON parse...")
                
                # Clean response
                clean = response_content.strip()
                
                # Remove markdown code blocks
                clean = re.sub(r'```json\s*|\s*```', '', clean)
                
                # Try to find JSON array
                json_match = re.search(r'\[.*\]', clean, re.DOTALL)
                if json_match:
                    clean = json_match.group(0)
                    print(f"✅ Found JSON array pattern")
                else:
                    print(f"❌ No JSON array pattern found")
                
                # Parse
                try:
                    data = json.loads(clean)
                    print(f"✅ JSON Parse Success!")
                    print(f"   Extracted {len(data)} items")
                    
                    if data:
                        print(f"\n   First item: {data[0]}")
                    
                except json.JSONDecodeError as e:
                    print(f"❌ JSON Parse Failed: {e}")
                    print(f"   Attempted to parse: {clean[:200]}...")
                
            except Exception as e:
                print(f"❌ Error: {e}")
                import traceback
                traceback.print_exc()
            
            print("\n" + "="*80)
            
            # Wait between tests
            await asyncio.sleep(2)

if __name__ == "__main__":
    asyncio.run(debug_llm_extraction())
