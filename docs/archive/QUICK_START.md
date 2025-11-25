# Univ-Insight 계층적 구조 - 빠른 시작 가이드

## ⚡ 5분 안에 시작하기

### 1️⃣ 데이터베이스 초기화 (1분)

```bash
cd /mnt/d/progress/Univ-Insight

# 기존 데이터베이스 삭제
rm -f univ_insight.db

# SNU 데이터 로드
python src/scripts/init_snu_data.py
```

**예상 출력**:
```
✅ University created: 서울대학교
✅ Data Population Complete!

Summary:
  - Universities:    1
  - Colleges:        3
  - Departments:     6
  - Professors:      4
  - Laboratories:    4
  - Lab Members:     3
  - Research Papers: 3
```

---

### 2️⃣ API 서버 시작 (1분)

```bash
python -m src.api.main
```

**또는**:
```bash
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

**예상 출력**:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

---

### 3️⃣ API 문서 확인 (1분)

브라우저에서 열기:
```
http://localhost:8000/docs
```

이 페이지에서 모든 엔드포인트를 테스트할 수 있습니다.

---

### 4️⃣ 첫 번째 API 호출 (1분)

#### 터미널에서:
```bash
# 대학 목록
curl http://localhost:8000/universities

# 서울대 상세정보
curl http://localhost:8000/universities/seoul-national-univ

# 공과대학
curl http://localhost:8000/colleges/snu-college-eng

# 전자정보공학부
curl http://localhost:8000/departments/snu-dept-eecs

# 김성호 교수
curl http://localhost:8000/professors/prof-kim-ai-001

# 비전 딥러닝 연구실
curl http://localhost:8000/laboratories/lab-ai-vision-001
```

#### 또는 Swagger UI에서:
1. `http://localhost:8000/docs` 접속
2. `/universities` 클릭
3. "Try it out" 버튼 클릭
4. "Execute" 버튼 클릭

---

### 5️⃣ 데이터 검증 (1분)

```bash
python test_api_hierarchical.py
```

**예상 출력**:
```
================================================================================
🚀 Testing Hierarchical Navigation API
================================================================================

1️⃣  UNIVERSITIES
  📍 서울대학교 (ID: seoul-national-univ)
     Ranking: #1, Tier: TOP
     Colleges: 3

2️⃣  COLLEGES
  📚 공과대학
     Departments: 3

3️⃣  DEPARTMENTS in 공과대학
  🏛️  전기정보공학부
     Professors: 2

...

📊 SUMMARY STATISTICS
Universities:  1
Colleges:      3
Departments:   6
Professors:    4
Laboratories:  4
Papers:        3

✅ All data loaded successfully!
```

---

## 🗂️ 계층적 네비게이션 구조

```
📍 University (대학)
   ├─ ID: seoul-national-univ
   ├─ Name: Seoul National University / 서울대학교
   └─ GET /universities/{uni_id}
      │
      └─📚 College (단과대)
         ├─ ID: snu-college-eng
         ├─ Name: College of Engineering / 공과대학
         └─ GET /colleges/{college_id}
            │
            └─🏛️ Department (학과)
               ├─ ID: snu-dept-eecs
               ├─ Name: Department of EECS / 전기정보공학부
               └─ GET /departments/{dept_id}
                  │
                  └─👨‍🏫 Professor (교수)
                     ├─ ID: prof-kim-ai-001
                     ├─ Name: Kim Sung-Ho / 김성호
                     ├─ H-Index: 45
                     ├─ Publications: 287
                     └─ GET /professors/{prof_id}
                        │
                        └─🔬 Laboratory (연구실)
                           ├─ ID: lab-ai-vision-001
                           ├─ Name: Vision & DL Lab / 비전 및 딥러닝 연구실
                           ├─ Research Areas: Computer Vision, Deep Learning
                           ├─ Funding: ₩500M (NRF)
                           └─ GET /laboratories/{lab_id}
                              │
                              ├─👤 Lab Members (연구실원)
                              │  ├─ Name: Lee Min-jun / 이민준
                              │  ├─ Role: PhD Student
                              │  └─ Topic: Vision Transformers for Medical Imaging
                              │
                              └─📄 Research Papers (논문)
                                 ├─ Title: Vision Transformers for Medical Image Segmentation
                                 ├─ Authors: [Kim, Lee, Park]
                                 ├─ Year: 2024
                                 ├─ Venue: IEEE TMI
                                 ├─ Citations: 127
                                 └─ GET /papers/{paper_id}/analysis
                                    └─ Career Info
                                       ├─ Technologies: ViT, PyTorch, CUDA
                                       ├─ Skills: Python, Deep Learning
                                       ├─ Career Paths: AI Researcher
                                       ├─ Companies: NVIDIA, Google, Meta
                                       └─ Learning Path: [Step 1, 2, 3, ...]
```

---

## 📡 주요 API 엔드포인트

### 네비게이션

| 엔드포인트 | 설명 | 반환 정보 |
|----------|------|---------|
| `GET /universities` | 대학 목록 | ID, 이름, 순위, 단과대 수 |
| `GET /universities/{uni_id}` | 대학 상세 | 단과대 배열 |
| `GET /colleges/{college_id}` | 단과대 상세 | 학과 배열 |
| `GET /departments/{dept_id}` | 학과 상세 | 교수 배열 |
| `GET /professors/{prof_id}` | 교수 상세 | 연구실 배열, H-Index |
| `GET /laboratories/{lab_id}` | 연구실 상세 | 연구실원, 논문, 프로젝트 |

### 논문 & 분석

| 엔드포인트 | 설명 |
|----------|------|
| `GET /papers` | 논문 목록 (필터: lab_id, topic) |
| `GET /papers/{paper_id}` | 논문 상세 |
| `GET /papers/{paper_id}/analysis` | **진로 분석** (기술, 스킬, 진로, 학습경로) |

---

## 🔍 실제 데이터 예시

### 서울대학교 공과대학 전자정보공학부

#### 교수 정보
- **김성호 (Kim Sung-Ho)**
  - H-Index: 45
  - 논문: 287편
  - 교육: PhD Stanford, Masters SNU
  - 연구: Deep Learning, Computer Vision

- **이재원 (Lee Jae-won)**
  - H-Index: 38
  - 논문: 156편
  - 교육: PhD CMU
  - 연구: Machine Learning, Robotics

#### 연구실 정보
- **비전 및 딥러닝 연구실** (Vision & DL Lab)
  - 교수: 김성호
  - 설립: 2010년
  - 연구실원: 이민준 (PhD), 박지원 (Master)
  - 프로젝트:
    - Medical Image Segmentation using Transformers
    - Vision-based Autonomous Navigation
  - 펀딩: ₩500M (NRF) + Samsung, LG
  - 장비: GPU Cluster (4x A100, 8x RTX 4090)

- **머신러닝 및 로봇틱스 연구실** (ML & Robotics Lab)
  - 교수: 이재원
  - 연구실원: 최수빈 (PhD)
  - 연구: Reinforcement Learning, Robot Control

#### 논문 정보
1. **"Vision Transformers for Medical Image Segmentation"**
   - 저자: Kim, Lee, Park
   - 출판: IEEE TMI 2024
   - 인용: 127회
   - 키워드: Vision Transformer, Medical Imaging, Segmentation

2. **"Deep Reinforcement Learning for Robotic Manipulation"**
   - 저자: Lee, Choi
   - 출판: ICRA 2023
   - 인용: 156회
   - 키워드: RL, Robotics, Deep Learning

---

## 💻 예제 코드

### Python에서 API 사용

```python
import requests

BASE_URL = "http://localhost:8000"

# 대학 조회
unis = requests.get(f"{BASE_URL}/universities").json()
print(f"Total universities: {unis['total_count']}")

# 서울대 조회
snu = requests.get(f"{BASE_URL}/universities/seoul-national-univ").json()
print(f"University: {snu['name_ko']}")
print(f"Colleges: {len(snu['colleges'])}")

# 공과대학 조회
eng_college = requests.get(
    f"{BASE_URL}/colleges/snu-college-eng"
).json()
print(f"College: {eng_college['name_ko']}")
print(f"Departments: {len(eng_college['departments'])}")

# 전자정보공학부 조회
eecs = requests.get(
    f"{BASE_URL}/departments/snu-dept-eecs"
).json()
print(f"Department: {eecs['name_ko']}")
print(f"Professors: {len(eecs['professors'])}")

# 김성호 교수 조회
prof_kim = requests.get(
    f"{BASE_URL}/professors/prof-kim-ai-001"
).json()
print(f"Professor: {prof_kim['name_ko']}")
print(f"H-Index: {prof_kim['h_index']}")
print(f"Labs: {len(prof_kim['laboratories'])}")

# 비전 딥러닝 연구실 조회
lab = requests.get(
    f"{BASE_URL}/laboratories/lab-ai-vision-001"
).json()
print(f"Lab: {lab['name_ko']}")
print(f"Members: {len(lab['members'])}")
print(f"Papers: {len(lab['papers'])}")

# 논문 분석 (진로 정보 포함)
analysis = requests.get(
    f"{BASE_URL}/papers/paper-vision-001/analysis"
).json()
print(f"\n논문 분석:")
print(f"- 기술: {analysis['analysis']['core_technologies']}")
print(f"- 스킬: {analysis['analysis']['required_skills']}")
print(f"- 진로: {analysis['analysis']['career_paths']}")
print(f"- 기업: {analysis['analysis']['recommended_companies']}")
```

### JavaScript/TypeScript에서 API 사용

```typescript
const BASE_URL = "http://localhost:8000";

// 대학 조회
const unis = await fetch(`${BASE_URL}/universities`)
  .then(res => res.json());
console.log(`Total: ${unis.total_count}`);

// 서울대 상세
const snu = await fetch(`${BASE_URL}/universities/seoul-national-univ`)
  .then(res => res.json());
console.log(`${snu.name_ko} - ${snu.colleges.length} 단과대`);

// 공과대학
const college = await fetch(`${BASE_URL}/colleges/snu-college-eng`)
  .then(res => res.json());
college.departments.forEach(dept => {
  console.log(`- ${dept.name_ko} (${dept.professor_count}명)`);
});

// 교수
const professor = await fetch(`${BASE_URL}/professors/prof-kim-ai-001`)
  .then(res => res.json());
console.log(`${professor.name_ko} (H-Index: ${professor.h_index})`);

// 연구실
const lab = await fetch(`${BASE_URL}/laboratories/lab-ai-vision-001`)
  .then(res => res.json());
console.log(`${lab.name_ko}`);
console.log(`연구 분야: ${lab.research_areas.join(", ")}`);
console.log(`프로젝트: ${lab.current_projects.length}개`);

// 논문 분석
const analysis = await fetch(`${BASE_URL}/papers/paper-vision-001/analysis`)
  .then(res => res.json());
console.log("기술:", analysis.analysis.core_technologies);
console.log("진로:", analysis.analysis.career_paths);
```

---

## 🚨 문제 해결

### 포트 이미 사용 중
```bash
# 다른 포트에서 실행
uvicorn src.api.main:app --port 8001
```

### 데이터베이스 오류
```bash
# 데이터베이스 재초기화
rm -f univ_insight.db chroma_db
python src/scripts/init_snu_data.py
```

### 모듈 임포트 오류
```bash
# 가상환경 재설정
source .venv_wsl/bin/activate
pip install -r requirements.txt
```

---

## 📚 더 알아보기

- **API 상세 문서**: `API_REFERENCE.md`
- **검증 보고서**: `SNU_HIERARCHICAL_VERIFICATION.md`
- **구현 요약**: `IMPLEMENTATION_SUMMARY.md`
- **데이터베이스 스키마**: `src/domain/models.py`
- **크롤러 코드**: `src/services/snu_crawler.py`

---

## ✅ 확인 체크리스트

- [ ] 데이터베이스 초기화 완료
- [ ] API 서버 실행 중
- [ ] API 문서 (Swagger) 접속 가능
- [ ] 첫 번째 API 호출 성공
- [ ] 테스트 스크립트 실행 완료
- [ ] 데이터 확인 (1 대학, 3 단과대, 6 학과, 4 교수, 4 연구실, 3 논문)

---

**준비 완료! 🎉**

이제 API를 통해 계층적 데이터를 탐색할 수 있습니다.
