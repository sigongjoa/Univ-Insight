#!/usr/bin/env python3
"""
API Progressive Disclosure 테스트
실제 API 응답에 쉬운 설명이 포함되는지 확인
"""

import sys
import os
sys.path.append(os.getcwd())

from src.core.database import SessionLocal
from src.domain.models import Department, Professor
from src.api.routes import _get_research_preview
import json

def test_api_progressive_disclosure():
    print("="*80)
    print("🧪 API Progressive Disclosure 테스트")
    print("="*80)
    
    db = SessionLocal()
    
    try:
        # Test 1: Department API
        print("\n[TEST 1] Department API - 교수 목록에 쉬운 설명 포함")
        print("-"*80)
        
        dept = db.query(Department).first()
        if not dept:
            print("❌ Department 데이터 없음")
            return
        
        print(f"학과: {dept.name_ko}")
        print(f"교수 수: {len(dept.professors)}")
        
        for i, prof in enumerate(dept.professors[:3], 1):
            preview = _get_research_preview(prof, db)
            print(f"\n[{i}] {prof.name_ko} 교수")
            print(f"    쉬운 주제: {preview['topic_easy']}")
            print(f"    설명 미리보기: {preview['explanation_preview'][:100]}...")
        
        # Test 2: Professor API simulation
        print("\n\n[TEST 2] Professor API - 상세 연구 설명")
        print("-"*80)
        
        prof = db.query(Professor).first()
        if not prof:
            print("❌ Professor 데이터 없음")
            return
        
        print(f"교수: {prof.name_ko}")
        
        # Simulate API response
        from src.domain.models import PaperAnalysis
        
        research_explanations = []
        for lab in prof.laboratories:
            for paper in lab.papers[:3]:
                analysis = db.query(PaperAnalysis).filter(PaperAnalysis.paper_id == paper.id).first()
                if analysis and analysis.topic_easy:
                    research_explanations.append({
                        "topic_easy": analysis.topic_easy,
                        "topic_technical": analysis.topic_technical,
                        "explanation": analysis.explanation,
                        "paper_title": paper.title
                    })
        
        if research_explanations:
            print(f"\n연구 설명 {len(research_explanations)}개 발견:")
            for i, exp in enumerate(research_explanations, 1):
                print(f"\n[{i}] {exp['topic_easy']}")
                print(f"    전문 용어: {exp['topic_technical']}")
                print(f"    설명: {exp['explanation'][:150]}...")
        else:
            print("⚠️  분석된 연구 없음 - 먼저 분석 파이프라인 실행 필요")
        
        # Test 3: JSON Response Format
        print("\n\n[TEST 3] JSON Response 형식 확인")
        print("-"*80)
        
        sample_response = {
            "id": prof.id,
            "name_ko": prof.name_ko,
            "research_interests": prof.research_interests,
            "research_explanations": research_explanations[:1]  # First one
        }
        
        print(json.dumps(sample_response, ensure_ascii=False, indent=2))
        
        print("\n" + "="*80)
        print("✅ API 테스트 완료!")
        print("="*80)
        
        if research_explanations:
            print("\n✅ Progressive Disclosure가 API 응답에 포함됩니다!")
            print("   - topic_easy: 고등학생이 이해하기 쉬운 제목")
            print("   - explanation: 쉬운 비유와 설명")
            print("   - topic_technical: 전문 용어 (괄호 안)")
        else:
            print("\n⚠️  아직 분석된 데이터가 없습니다.")
            print("   다음 명령어를 실행하세요:")
            print("   wsl .venv_wsl/bin/python3 src/scripts/test_e2e_progressive_disclosure.py")
        
    except Exception as e:
        print(f"\n❌ 오류: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_api_progressive_disclosure()
