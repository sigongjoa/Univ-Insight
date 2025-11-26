# 서울대 조직도 기반 크롤링 - 최종 보고서

**날짜**: 2025-11-26  
**상태**: 구조 파악 완료, LLM 추출 개선 필요

---

## ✅ 완료된 작업

### 1. 조직도 페이지 발견
- URL: `https://www.snu.ac.kr/about/overview/organization/sub_organ`
- 43개 단과대/대학원 목록 추출 성공

### 2. 주요 단과대 URL 확인
- 공과대학: `https://eng.snu.ac.kr`
- 경영대학: `https://cba.snu.ac.kr`
- 자연과학대학: `https://science.snu.ac.kr`
- 인문대학: `https://humanities.snu.ac.kr`
- 사회과학대학: `https://social.snu.ac.kr`

### 3. 크롤링 구조 확립
```
조직도 페이지
  ↓
단과대 목록 추출
  ↓
각 단과대 홈페이지
  ↓
학과 목록 추출
  ↓
각 학과 홈페이지
  ↓
교수진 페이지 찾기
  ↓
LLM으로 교수 정보 추출
```

---

## ⚠️ 발견된 문제

### LLM JSON 추출 실패
- **증상**: LLM이 빈 응답 또는 비-JSON 응답 반환
- **원인**: 
  1. 프롬프트가 너무 복잡
  2. 페이지 내용에 교수 정보가 없음 (잘못된 페이지)
  3. LLM 모델 문제 (qwen2:7b)

### 해결 방안
1. **직접 URL 지정**: 알려진 단과대 URL 사용
2. **프롬프트 단순화**: JSON 구조를 더 명확하게
3. **HTML 파싱 우선**: LLM 전에 BeautifulSoup로 1차 필터링
4. **MockLLM 사용**: 테스트용으로 먼저 구조 검증

---

## 📋 다음 단계

### 1단계: 알려진 URL로 직접 크롤링
```python
known_colleges = [
    {"name_ko": "공과대학", "url": "https://eng.snu.ac.kr"},
    {"name_ko": "경영대학", "url": "https://cba.snu.ac.kr"},
    {"name_ko": "자연과학대학", "url": "https://science.snu.ac.kr"},
]

for college in known_colleges:
    # 학과 목록 페이지 찾기
    # 각 학과의 교수진 페이지 크롤링
```

### 2단계: HTML 파싱 개선
```python
# BeautifulSoup로 교수 정보 직접 추출
soup = BeautifulSoup(html, 'html.parser')

# 교수 이름 찾기
professors = soup.find_all('div', class_='professor')

# LLM은 보조 수단으로만 사용
```

### 3단계: 점진적 확장
1. 공과대학 1개 학과 완벽 크롤링
2. 전체 공과대학 확장
3. 다른 단과대로 확장

---

## 🎯 즉시 실행 가능한 작업

### 경영대학 교수진 크롤링
```bash
# 경영대학 교수진 페이지
https://cba.snu.ac.kr/research/faculty/professor

# 이 페이지를 직접 크롤링하면 교수 목록 확보 가능
```

### 공과대학 학과별 크롤링
```bash
# 컴퓨터공학부
https://cse.snu.ac.kr/faculty

# 전기정보공학부  
https://ee.snu.ac.kr/faculty

# 기계공학부
https://me.snu.ac.kr/faculty
```

---

## 💡 권장 사항

1. **LLM 의존도 낮추기**: HTML 구조 파싱 우선
2. **수동 URL 리스트 작성**: 주요 학과 URL 미리 정리
3. **단계별 검증**: 각 단계마다 결과 확인
4. **에러 핸들링 강화**: LLM 실패 시 fallback 전략

---

**작성**: 2025-11-26 14:48 KST
