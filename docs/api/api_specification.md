# Backend API Specification

**Base URL:** `/api/v1`
**Version:** 1.0.0

## 0. Authentication (인증)

### Kakao Login Callback
*   **Endpoint:** `GET /auth/kakao/callback`
*   **Description:** 카카오 로그인 후 리다이렉트 처리 및 JWT 발급.
*   **Response:** `{"access_token": "...", "token_type": "bearer"}`

## 1. User Management (학생/학부모 관리)

### Register/Update User
*   **Endpoint:** `POST /users/profile`
*   **Description:** 사용자 등록 및 관심사(Interests) 설정.
*   **Request Body:**
    ```json
    {
      "user_id": "kakao_12345",
      "name": "김학생",
      "role": "student",  // or "parent"
      "grade": 2,
      "interests": ["Artificial Intelligence", "Robotics", "Brain Science"],
      "contact_info": {
        "kakao_uuid": "...",
        "notion_email": "student@example.com"
      }
    }
    ```
*   **Response:** `200 OK`

### Get User Profile
*   **Endpoint:** `GET /users/{user_id}`
*   **Description:** 사용자 정보 조회.

---

## 2. Research & Analysis (연구 데이터)

### List Research Papers
*   **Endpoint:** `GET /research`
*   **Description:** 수집된 연구 목록 조회 (필터링 가능).
*   **Query Params:**
    *   `university`: (Optional) "KAIST", "SNU"
    *   `topic`: (Optional) "Computer Vision"
    *   `limit`: 10
*   **Response:**
    ```json
    {
      "items": [
        {
          "id": "p_101",
          "title": "Efficient Transformer Architecture",
          "university": "KAIST",
          "summary_short": "챗GPT가 전기를 덜 먹게 만드는 기술",
          "date": "2024-05-20"
        }
      ]
    }
    ```

### Get Research Detail (Analysis)
*   **Endpoint:** `GET /research/{paper_id}/analysis`
*   **Description:** 특정 연구의 상세 분석 리포트(LLM 결과) 조회.
*   **Response:**
    ```json
    {
      "paper_id": "p_101",
      "title": "Efficient Transformer Architecture",
      "analysis": {
        "easy_summary": "이 연구는 마치...",
        "career_path": {
          "companies": ["Samsung Electronics", "Naver", "Google"],
          "job_title": "AI Model Optimizer",
          "salary_hint": "6000~7000"
        },
        "action_item": {
          "subject": "Math II",
          "topic": "행렬 연산의 효율성 탐구"
        }
      }
    }
    ```

---

## 3. Recommendation & Reports (큐레이션)

### Generate Personal Report
*   **Endpoint:** `POST /reports/generate`
*   **Description:** 특정 사용자를 위한 맞춤형 리포트 생성 및 Notion/Kakao 발송 트리거.
*   **Request Body:**
    ```json
    {
      "user_id": "kakao_12345",
      "target_date": "2024-05-24"
    }
    ```
*   **Response:**
    ```json
    {
      "status": "success",
      "report_id": "r_999",
      "message": "Report sent to Notion."
    }
    ```

### Get Plan B Suggestions
*   **Endpoint:** `GET /research/{paper_id}/plan-b`
*   **Description:** 특정 연구와 유사한 주제를 가진 타 대학(진입장벽이 다른) 연구 추천.
*   **Logic:** `Similarity > 0.8 AND Target_Univ_Tier > Current_Univ_Tier` (Tier 숫자가 클수록 입결이 낮음)
*   **Response:**
    ```json
    [
      {
        "university": "Hanyang Univ",
        "title": "Lightweight AI Models for Mobile",
        "similarity_score": 0.89
      },
      {
        "university": "Kookmin Univ",
        "title": "Embedded AI Systems",
        "similarity_score": 0.85
      }
    ]
    ```

---

## 4. System & Admin

### Trigger Crawler
*   **Endpoint:** `POST /admin/crawl`
*   **Description:** (관리자용) 수동 크롤링 작업 실행.
*   **Request Body:**
    ```json
    {
      "target": "KAIST_CS",
      "depth": 1
    }
    ```

### Health Check
*   **Endpoint:** `GET /health`
*   **Response:** `{"status": "ok"}`
