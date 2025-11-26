# Phase 2 Progressive Disclosure Implementation Report

**날짜**: 2025-11-26  
**작성자**: Antigravity AI  
**프로젝트**: Univ-Insight - Phase 2 Progressive Disclosure

---

## 📋 개요

Phase 2에서는 **점진적 공개(Progressive Disclosure)** UX 전략을 적용하여 고교생 타겟에게 최적화된 리포트 시스템을 구현했습니다. 기본 내용은 누구나 이해하기 쉽게 보여주되, 관심 있는 사람에게만 깊이 있는 정보로 가는 문(링크)을 열어주는 방식입니다.

---

## 🎯 핵심 목표

1. **쉬운 설명 + 전문 용어** 병기 구조
2. **심화 탐구 섹션** 분리 (키워드, 추천 자료, 관련 개념)
3. **기존 프로세스 통합** (크롤링 → 분석 → 리포트 생성)
4. **E2E 검증** 완료

---

## 🛠️ 구현 내용

### 1. 데이터 모델 확장

#### 1.1 Pydantic Schema (`src/domain/schemas.py`)
```python
class DeepDive(BaseModel):
    keywords: List[str]
    recommendations: List[str]
    related_concepts: List[str]

class AnalysisResult(BaseModel):
    paper_id: str
    topic_easy: str              # "인공지능의 눈과 입 연결하기"
    topic_technical: str          # "Vision-Language Grounding"
    explanation: str              # 쉬운 설명
    reference_link: str           # 참고 링크
    deep_dive: DeepDive          # 심화 탐구
    career_path: CareerPath
    action_item: ActionItem
```

#### 1.2 Database Model (`src/domain/models.py`)
```python
class PaperAnalysis(Base):
    # Progressive Disclosure Fields (New)
    topic_easy = Column(String(255), nullable=True)
    topic_technical = Column(String(255), nullable=True)
    explanation = Column(Text, nullable=True)
    reference_link = Column(String(500), nullable=True)
    deep_dive = Column(JSON, default=dict, nullable=True)
```

**마이그레이션 실행**:
```bash
wsl .venv_wsl/bin/python3 src/scripts/migrations/add_progressive_disclosure_fields.py
```

---

### 2. LLM 프롬프트 엔지니어링

#### 2.1 프롬프트 수정 (`src/services/llm.py`)

**Before**:
```
"You are an expert education consultant..."
```

**After**:
```
"You are a career mentor for high school students.
Your task is to analyze the following research paper content and create a report 
that is easy to understand but also provides depth for interested students.

Instructions:
1. **Explanation**: Use simple analogies and everyday terms suitable for high school students.
2. **Professionalism**: Put accurate 'academic terms' in parentheses after easy explanations.
3. **Expansion**: Provide 'Deep Dive Keywords' and 'Reference Titles' for further study.
```

#### 2.2 JSON 출력 구조
```json
{
  "topic_easy": "인공지능의 눈과 입 연결하기",
  "topic_technical": "Vision-Language Grounding",
  "explanation": "우리가 강아지 사진을 보고...",
  "reference_link": "Google Scholar Search: Vision-Language Grounding",
  "deep_dive": {
    "keywords": ["Multimodal Learning", "VQA"],
    "recommendations": ["CLIP paper", "ViLT paper"],
    "related_concepts": ["조건부 확률", "벡터의 내적"]
  },
  "career_path": {...},
  "action_item": {...}
}
```

---

### 3. 리포트 템플릿 디자인

#### 3.1 Typst Template (`src/templates/report_template.typ`)

**구조**:
```typst
#for item in data.analysis_results [
  #rect[
    // 1. Title Section
    핵심 기술: #item.topic_easy
    (전문 용어: #item.topic_technical)
    
    // 2. Explanation Section
    🧐 이게 뭔가요?
    #item.explanation
    
    // 3. Deep Dive Section (Progressive Disclosure)
    #rect[
      📚 더 깊이 알아보기 (전문가 자료)
      - 심화 학습 키워드: #item.deep_dive.keywords.join(", ")
      - 추천 자료: #item.deep_dive.recommendations.join(", ")
      - 관련 기초 지식: #item.deep_dive.related_concepts.join(", ")
      - 참고 링크: #link(item.reference_link)
    ]
    
    // 4. Career & Action Plan
    #grid[
      💼 진로 가이드 | 🚀 실행 계획
    ]
  ]
]
```

---

### 4. 기존 프로세스 통합

#### 4.1 분석 파이프라인 수정 (`src/scripts/run_real_analysis_pipeline.py`)

**변경 사항**:
1. `analyze_paper_with_ollama()`: Progressive Disclosure 필드 추출
2. `save_analysis_to_db()`: 새 필드 DB 저장

```python
# Extract Progressive Disclosure fields
return {
    "success": True,
    "data": {
        "topic_easy": analysis_result.topic_easy,
        "topic_technical": analysis_result.topic_technical,
        "explanation": analysis_result.explanation,
        "reference_link": analysis_result.reference_link,
        "deep_dive": {
            "keywords": analysis_result.deep_dive.keywords,
            "recommendations": analysis_result.deep_dive.recommendations,
            "related_concepts": analysis_result.deep_dive.related_concepts
        },
        # ... career_path, action_item
    }
}
```

#### 4.2 리포트 생성 API 수정 (`src/api/routes.py`)

**변경 사항**:
1. 교수별 개별 분석 수행
2. `analysis_results` 배열 생성
3. PDF 생성 시 새 템플릿 데이터 전달

```python
@router.post("/users/{user_id}/reports")
def create_report(user_id: str, db: Session = Depends(get_db)):
    # ... 교수 매칭 로직
    
    analysis_results = []
    for prof, score in top_profs:
        # 논문 찾기 또는 가상 논문 생성
        target_paper = ...
        
        # LLM 분석
        result = llm.analyze(target_paper)
        
        # 결과 저장
        result_dict = result.dict()
        result_dict["professor_name"] = prof.name
        analysis_results.append(result_dict)
    
    # PDF 생성
    report_data = {
        "user_name": user.name,
        "interests": ", ".join(user.interests),
        "report_date": datetime.now().strftime("%Y-%m-%d"),
        "analysis_results": analysis_results  # 새 구조
    }
    pdf_path = pdf_gen.generate(report_data, filename)
```

---

## 🧪 테스트 및 검증

### E2E 테스트 (`src/scripts/test_e2e_progressive_disclosure.py`)

**테스트 시나리오**:
1. ✅ 데이터 준비 (교수 3명 확인)
2. ✅ 논문 분석 (LLM 호출, DB 저장)
3. ✅ 사용자 생성
4. ✅ 리포트 생성 (PDF 생성, DB 저장)
5. ✅ 결과 검증

**실행 결과**:
```
================================================================================
✅ E2E 테스트 완료!
================================================================================

📄 생성된 리포트: docs/reports/E2E_Progressive_Report.pdf
🔍 분석된 논문: 7개
👤 사용자: 테스트 학생 (e2e-test-user)

📊 Progressive Disclosure 필드 확인:
   - topic_easy: Exploring the Future World of Robots
   - topic_technical: Machine Learning, Optimization, Robotics
   - deep_dive keywords: 3 개
```

---

## 📊 결과물

### 생성된 파일

1. **문서**:
   - `docs/phases/PHASE_2_REPORT_DESIGN_STRATEGY.md` - 설계 전략
   - `docs/reports/E2E_Progressive_Report.pdf` - E2E 테스트 리포트
   - `docs/reports/Phase2_Progressive_Report.pdf` - 단독 테스트 리포트

2. **코드**:
   - `src/domain/schemas.py` - DeepDive, AnalysisResult 스키마
   - `src/domain/models.py` - PaperAnalysis 모델 확장
   - `src/services/llm.py` - 프롬프트 및 파싱 로직
   - `src/templates/report_template.typ` - 리포트 템플릿
   - `src/api/routes.py` - 리포트 생성 API
   - `src/scripts/run_real_analysis_pipeline.py` - 분석 파이프라인

3. **테스트**:
   - `src/scripts/test_e2e_progressive_disclosure.py` - E2E 테스트
   - `src/scripts/generate_phase2_report.py` - 단독 테스트
   - `src/scripts/migrations/add_progressive_disclosure_fields.py` - DB 마이그레이션

---

## 🎨 리포트 디자인 특징

### Before (기존)
```
관심 분야: Vision과 연결된 언어의 이해 (Language Grounding with Vision)
이러한 연구는 이미지와 자연어가 어떻게 서로 연결되는지...
```

### After (개선)
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
핵심 기술: 인공지능의 '눈'과 '입' 연결하기
(전문 용어: Vision-Language Grounding)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🧐 이게 뭔가요?
우리가 강아지 사진을 보고 "귀여운 강아지가 잔디에 앉아 있네"라고 말하는 것처럼,
컴퓨터도 사진을 보고 문장으로 설명할 수 있게 만드는 기술입니다.

┌────────────────────────────────────────────────────────────────┐
│ 📚 더 깊이 알아보기 (전문가 자료)                                │
│                                                                │
│ 심화 학습 키워드: Multimodal Learning, VQA, Cross-modal Attention│
│ 추천 자료: CLIP paper, ViLT paper                              │
│ 관련 기초 지식: 조건부 확률(확률과 통계), 벡터의 내적(기하)        │
│ 참고 링크: Google Scholar Search: Vision-Language Grounding    │
└────────────────────────────────────────────────────────────────┘

💼 진로 가이드              │  🚀 실행 계획
- 직업: Multimodal AI      │  - 추천 과목: 수학(기하, 확률)
- 기업: Google, Naver      │  - 탐구 주제: 이미지 캡셔닝 모델 구현
- 연봉: 6,000만 원 이상     │
```

---

## 🔄 프로세스 흐름

```
[사용자] 대학/전공 선택
    ↓
[API] 교수 매칭 (관심사 기반)
    ↓
[LLM] 각 교수의 연구 분석 (Progressive Disclosure)
    ↓
[DB] PaperAnalysis 저장 (topic_easy, topic_technical, deep_dive 등)
    ↓
[PDF] Typst 템플릿으로 리포트 생성
    ↓
[사용자] 리포트 다운로드
```

---

## 📈 성과

1. **UX 개선**: 고교생이 이해하기 쉬운 비유 + 전문가를 위한 심화 정보
2. **확장성**: 기존 시스템과 완벽 통합, 기존 데이터 호환
3. **검증 완료**: E2E 테스트 통과, 실제 PDF 생성 확인
4. **문서화**: 설계 전략, 구현 가이드, 테스트 스크립트 완비

---

## 🚀 다음 단계

1. **프로덕션 배포**: API 서버에 통합
2. **LLM 모델 최적화**: qwen2.5:14b 또는 더 나은 모델 사용
3. **UI 개선**: 웹 인터페이스에서 Progressive Disclosure 적용
4. **피드백 수집**: 실제 고교생 타겟 테스트

---

## 📝 참고 자료

- **설계 문서**: `docs/phases/PHASE_2_REPORT_DESIGN_STRATEGY.md`
- **E2E 테스트**: `src/scripts/test_e2e_progressive_disclosure.py`
- **생성된 리포트**: `docs/reports/E2E_Progressive_Report.pdf`

---

**작성 완료**: 2025-11-26 14:20 KST  
**상태**: ✅ 구현 완료, E2E 테스트 통과
