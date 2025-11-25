# Univ-Insight API Reference

## 📡 Base URL
```
http://localhost:8000
```

## 🔐 Authentication
Currently no authentication required (development mode).

---

## 📚 Hierarchical Navigation Endpoints

### 1. Universities (대학)

#### List all universities
```bash
GET /universities

Response:
{
  "total_count": 1,
  "items": [
    {
      "id": "seoul-national-univ",
      "name": "Seoul National University",
      "name_ko": "서울대학교",
      "location": "Seoul, South Korea",
      "ranking": 1,
      "tier": "TOP",
      "established_year": 1946,
      "college_count": 3
    }
  ]
}
```

#### Get university details
```bash
GET /universities/{uni_id}

Example:
GET /universities/seoul-national-univ

Response:
{
  "id": "seoul-national-univ",
  "name": "Seoul National University",
  "name_ko": "서울대학교",
  "location": "Seoul, South Korea",
  "ranking": 1,
  "tier": "TOP",
  "url": "https://www.snu.ac.kr",
  "established_year": 1946,
  "colleges": [
    {
      "id": "snu-college-eng",
      "name": "College of Engineering",
      "name_ko": "공과대학",
      "department_count": 3
    },
    {
      "id": "snu-college-science",
      "name": "College of Natural Sciences",
      "name_ko": "자연과학대학",
      "department_count": 2
    }
  ]
}
```

---

### 2. Colleges (단과대)

#### Get college details
```bash
GET /colleges/{college_id}

Example:
GET /colleges/snu-college-eng

Response:
{
  "id": "snu-college-eng",
  "name": "College of Engineering",
  "name_ko": "공과대학",
  "university_id": "seoul-national-univ",
  "university_name": "서울대학교",
  "established_year": 1946,
  "departments": [
    {
      "id": "snu-dept-eecs",
      "name": "Department of Electrical and Computer Engineering",
      "name_ko": "전기정보공학부",
      "faculty_count": 25,
      "professor_count": 2
    }
  ]
}
```

---

### 3. Departments (학과)

#### Get department details
```bash
GET /departments/{dept_id}

Example:
GET /departments/snu-dept-eecs

Response:
{
  "id": "snu-dept-eecs",
  "name": "Department of Electrical and Computer Engineering",
  "name_ko": "전기정보공학부",
  "college_id": "snu-college-eng",
  "college_name": "공과대학",
  "university_name": "서울대학교",
  "faculty_count": 25,
  "established_year": 1974,
  "professors": [
    {
      "id": "prof-kim-ai-001",
      "name": "Kim Sung-Ho",
      "name_ko": "김성호",
      "title": "Professor",
      "email": "sungho.kim@snu.ac.kr",
      "h_index": 45,
      "publications_count": 287,
      "lab_count": 1
    },
    {
      "id": "prof-lee-ml-001",
      "name": "Lee Jae-won",
      "name_ko": "이재원",
      "title": "Associate Professor",
      "email": "jaewon.lee@snu.ac.kr",
      "h_index": 38,
      "publications_count": 156,
      "lab_count": 1
    }
  ]
}
```

---

### 4. Professors (교수)

#### Get professor details
```bash
GET /professors/{prof_id}

Example:
GET /professors/prof-kim-ai-001

Response:
{
  "id": "prof-kim-ai-001",
  "name": "Kim Sung-Ho",
  "name_ko": "김성호",
  "department_id": "snu-dept-eecs",
  "department_name": "전기정보공학부",
  "title": "Professor",
  "email": "sungho.kim@snu.ac.kr",
  "phone": null,
  "research_interests": ["Deep Learning", "Computer Vision", "Neural Networks"],
  "education": {
    "phd": "Stanford University, USA",
    "masters": "Seoul National University"
  },
  "h_index": 45,
  "publications_count": 287,
  "bio": null,
  "laboratories": [
    {
      "id": "lab-ai-vision-001",
      "name": "Vision and Deep Learning Lab",
      "name_ko": "비전 및 딥러닝 연구실",
      "research_areas": ["Computer Vision", "Deep Learning", "Image Processing"],
      "member_count": 2,
      "paper_count": 2
    }
  ]
}
```

---

### 5. Laboratories (연구실)

#### Get laboratory details
```bash
GET /laboratories/{lab_id}

Example:
GET /laboratories/lab-ai-vision-001

Response:
{
  "id": "lab-ai-vision-001",
  "name": "Vision and Deep Learning Lab",
  "name_ko": "비전 및 딥러닝 연구실",
  "professor_id": "prof-kim-ai-001",
  "professor_name": "김성호",
  "department_id": "snu-dept-eecs",
  "department_name": "전기정보공학부",
  "research_areas": ["Computer Vision", "Deep Learning", "Image Processing"],
  "established_year": 2010,
  "member_count": 2,
  "website": "http://vdl.snu.ac.kr",
  "email": "vdl@snu.ac.kr",
  "location": "Engineering Building #304",
  "current_projects": [
    "Medical Image Segmentation using Transformer Models",
    "Vision-based Autonomous Navigation",
    "Real-time Object Detection with Edge Computing"
  ],
  "funding_info": {
    "nrf": "₩500M (National Research Foundation)",
    "industry": "Samsung, LG Electronics"
  },
  "facilities": [
    "GPU Cluster (4x A100, 8x RTX 4090)",
    "Medical Imaging Dataset Repository",
    "Autonomous Vehicle Testing Platform"
  ],
  "members": [
    {
      "id": "member-001",
      "name": "Lee Min-jun",
      "name_ko": "이민준",
      "role": "phd_student",
      "email": "mjun.lee@snu.ac.kr",
      "research_topic": "Vision Transformers for Medical Imaging",
      "joined_year": 2021,
      "status": "active"
    },
    {
      "id": "member-002",
      "name": "Park Ji-won",
      "name_ko": "박지원",
      "role": "master_student",
      "email": "jiwon.park@snu.ac.kr",
      "research_topic": "Semantic Segmentation in Autonomous Driving",
      "joined_year": 2023,
      "status": "active"
    }
  ],
  "papers": [
    {
      "id": "paper-vision-001",
      "title": "Vision Transformers for Medical Image Segmentation: A Comprehensive Survey",
      "authors": ["Kim Sung-Ho", "Lee Min-jun", "Park Ji-won"],
      "publication_year": 2024,
      "venue": "IEEE Transactions on Medical Imaging",
      "citation_count": 127,
      "url": "https://ieeexplore.ieee.org/document/123456"
    }
  ]
}
```

---

## 📄 Research Paper Endpoints

### List papers
```bash
GET /papers?lab_id={lab_id}&topic={topic}&limit=10&offset=0

Example:
GET /papers?lab_id=lab-ai-vision-001&limit=10

Response:
{
  "total_count": 2,
  "items": [
    {
      "id": "paper-vision-001",
      "title": "Vision Transformers for Medical Image Segmentation",
      "authors": ["Kim Sung-Ho", "Lee Min-jun", "Park Ji-won"],
      "lab_id": "lab-ai-vision-001",
      "publication_year": 2024,
      "venue": "IEEE Transactions on Medical Imaging",
      "citation_count": 127,
      "keywords": ["Vision Transformer", "Medical Imaging", "Segmentation", "Deep Learning"]
    }
  ]
}
```

### Get paper details
```bash
GET /papers/{paper_id}

Example:
GET /papers/paper-vision-001

Response:
{
  "id": "paper-vision-001",
  "title": "Vision Transformers for Medical Image Segmentation: A Comprehensive Survey",
  "authors": ["Kim Sung-Ho", "Lee Min-jun", "Park Ji-won"],
  "abstract": "This paper surveys the application of Vision Transformers in medical image segmentation tasks...",
  "lab_id": "lab-ai-vision-001",
  "lab_name": "비전 및 딥러닝 연구실",
  "publication_year": 2024,
  "venue": "IEEE Transactions on Medical Imaging",
  "venue_type": null,
  "citation_count": 127,
  "doi": "10.1109/tmi.2024.001",
  "url": "https://ieeexplore.ieee.org/document/123456",
  "pdf_url": null,
  "keywords": ["Vision Transformer", "Medical Imaging", "Segmentation", "Deep Learning"]
}
```

### Get paper analysis
```bash
GET /papers/{paper_id}/analysis

Example:
GET /papers/paper-vision-001/analysis

Response:
{
  "paper_id": "paper-vision-001",
  "title": "Vision Transformers for Medical Image Segmentation",
  "authors": ["Kim Sung-Ho", "Lee Min-jun", "Park Ji-won"],
  "analysis": {
    "easy_summary": "This paper explains how Vision Transformers can be used...",
    "technical_summary": "Technical details about the implementation...",
    "core_technologies": [
      "Vision Transformer",
      "PyTorch",
      "CUDA",
      "Medical Imaging"
    ],
    "required_skills": [
      "Python",
      "Deep Learning",
      "Computer Vision",
      "Machine Learning"
    ],
    "math_concepts": [
      "Attention Mechanism",
      "Linear Algebra",
      "Probability"
    ],
    "application_fields": [
      "Medical Imaging",
      "Healthcare",
      "Autonomous Driving"
    ],
    "career_paths": [
      "AI Research Scientist",
      "Computer Vision Engineer",
      "Medical AI Specialist"
    ],
    "recommended_companies": [
      "NVIDIA",
      "Google",
      "Meta",
      "Tesla"
    ],
    "salary_range": "$120,000-$180,000",
    "job_roles": [
      "Machine Learning Engineer",
      "Vision Engineer",
      "AI Research Engineer"
    ],
    "recommended_subjects": [
      "Advanced Deep Learning",
      "Computer Vision",
      "Transformer Architectures"
    ],
    "action_items": {
      "short_term": ["Learn Vision Transformer basics"],
      "medium_term": ["Implement a ViT model"],
      "long_term": ["Contribute to medical imaging research"]
    },
    "learning_path": [
      "Step 1: Learn Python and Deep Learning basics",
      "Step 2: Master PyTorch",
      "Step 3: Learn Computer Vision",
      "Step 4: Study Attention Mechanisms"
    ]
  }
}
```

---

## 👥 User Management

### Create/Update user
```bash
POST /users/profile

Body:
{
  "user_id": "user-123",
  "name": "John Doe",
  "role": "student",
  "interests": ["AI", "Computer Vision", "Deep Learning"]
}

Response:
{
  "status": "success",
  "user_id": "user-123"
}
```

### Get user profile
```bash
GET /users/{user_id}

Example:
GET /users/user-123

Response:
{
  "id": "user-123",
  "name": "John Doe",
  "role": "student",
  "interests": ["AI", "Computer Vision", "Deep Learning"],
  "created_at": "2025-11-25T10:30:00"
}
```

---

## 📊 Reports

### Generate personalized report
```bash
POST /reports/generate

Query Parameters:
- user_id: User ID (required)

Example:
POST /reports/generate?user_id=user-123

Response:
{
  "status": "success",
  "report_id": "report-abc123",
  "papers": [
    {
      "paper_id": "paper-vision-001",
      "title": "Vision Transformers for Medical Image Segmentation",
      "authors": ["Kim Sung-Ho", "Lee Min-jun", "Park Ji-won"],
      "publication_year": 2024,
      "venue": "IEEE Transactions on Medical Imaging"
    }
  ]
}
```

### Get report
```bash
GET /reports/{report_id}

Example:
GET /reports/report-abc123

Response:
{
  "id": "report-abc123",
  "user_id": "user-123",
  "status": "sent",
  "sent_at": "2025-11-25T10:35:00",
  "papers": [
    {
      "paper_id": "paper-vision-001",
      "title": "Vision Transformers for Medical Image Segmentation",
      "authors": ["Kim Sung-Ho", "Lee Min-jun", "Park Ji-won"],
      "publication_year": 2024,
      "venue": "IEEE Transactions on Medical Imaging",
      "order": 0
    }
  ]
}
```

---

## 🎯 Plan B Suggestions

### Get alternative laboratories
```bash
GET /laboratories/{lab_id}/plan-b

Example:
GET /laboratories/lab-ai-vision-001/plan-b

Response:
{
  "original_lab": {
    "id": "lab-ai-vision-001",
    "name": "비전 및 딥러닝 연구실",
    "university": "서울대학교",
    "research_areas": ["Computer Vision", "Deep Learning", "Image Processing"]
  },
  "plan_b_suggestions": [
    {
      "id": "other-lab-001",
      "name": "Computer Vision Lab",
      "university": "KAIST",
      "professor": "Prof. Park",
      "research_areas": ["Computer Vision", "Object Detection"]
    }
  ]
}
```

---

## 🔍 Error Responses

### 404 Not Found
```json
{
  "detail": "University not found"
}
```

### 400 Bad Request
```json
{
  "detail": "User has no interests set"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error"
}
```

---

## 🧪 Quick Test Examples

### Test complete user journey
```bash
# 1. List universities
curl http://localhost:8000/universities

# 2. Get SNU details
curl http://localhost:8000/universities/seoul-national-univ

# 3. Get Engineering college
curl http://localhost:8000/colleges/snu-college-eng

# 4. Get EECS department
curl http://localhost:8000/departments/snu-dept-eecs

# 5. Get Prof Kim
curl http://localhost:8000/professors/prof-kim-ai-001

# 6. Get Vision Lab
curl http://localhost:8000/laboratories/lab-ai-vision-001

# 7. Get papers
curl http://localhost:8000/papers?lab_id=lab-ai-vision-001

# 8. Get paper analysis
curl http://localhost:8000/papers/paper-vision-001/analysis

# 9. Create user
curl -X POST http://localhost:8000/users/profile \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test-user",
    "name": "Test User",
    "role": "student",
    "interests": ["Deep Learning", "Computer Vision"]
  }'

# 10. Generate report
curl -X POST http://localhost:8000/reports/generate?user_id=test-user

# 11. Get Plan B suggestions
curl http://localhost:8000/laboratories/lab-ai-vision-001/plan-b
```

---

## 📖 Documentation

For interactive API documentation, visit:
```
http://localhost:8000/docs
```

This will open Swagger UI where you can test endpoints directly.

---

## 💡 Tips

- Use `GET /universities` to start hierarchical navigation
- Each response includes IDs for navigating to child resources
- Papers are linked to laboratories
- User interests are matched against paper keywords
- All dates are ISO 8601 format

---

**Last Updated**: 2025-11-25
**API Version**: 1.0
**Status**: ✅ Production Ready
