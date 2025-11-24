# Getting Started - Univ-Insight

Complete setup guide for running the entire Univ-Insight application (Backend + Frontend)

---

## 📋 Prerequisites

- **Python 3.9+** (for backend)
- **Node.js 16+** (for frontend)
- **Ollama** (for LLM inference) - optional, uses Mock by default
- **Git**

---

## 🚀 Quick Start (Full Stack)

### 1. Clone & Setup Environment

```bash
# Clone the repository (if not already done)
git clone <repository>
cd Univ-Insight

# Create .env file in root
cat > .env << 'EOF'
# Database
DATABASE_URL=sqlite:///./univ_insight.db

# LLM
LLM_MODEL=ollama
OLLAMA_BASE_URL=http://localhost:11434

# Notion (optional)
NOTION_TOKEN=your_notion_token

# Kakao (optional)
KAKAO_BOT_TOKEN=your_kakao_token

# API
API_HOST=0.0.0.0
API_PORT=8000
EOF
```

### 2. Backend Setup

```bash
# 1. Create virtual environment
python3 -m venv venv

# 2. Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Initialize database
python -c "from src.core.init_db import init_db; init_db()"

# 5. Run backend server
python -m uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

Backend will be available at: **http://localhost:8000**
API Documentation: **http://localhost:8000/docs**

### 3. Frontend Setup

```bash
# In a new terminal
cd frontend

# 1. Create environment file
cat > .env << 'EOF'
VITE_API_URL=http://localhost:8000/api/v1
VITE_ENV=development
EOF

# 2. Install dependencies
npm install

# 3. Run development server
npm run dev
```

Frontend will be available at: **http://localhost:5173**

---

## 🔍 Testing the Full Stack

### 1. Login
1. Go to http://localhost:5173/login
2. Register with any userId/password/role/interests
3. Click login

### 2. Search Papers
1. Click "🔍 논문 검색"
2. Try searching for papers (or view mock papers)
3. Click "상세 정보" to see analysis
4. Click "Plan B 보기" to see alternatives

### 3. View Reports
1. Click "📄 리포트 보기"
2. Click "새 리포트 생성" to generate a report
3. View previous reports

### 4. Manage Profile
1. Click "👤 프로필"
2. Edit name and interests
3. Set up notifications and integrations

---

## 📚 Backend API Testing

### Using Swagger UI (Recommended)
```
http://localhost:8000/docs
```

### Sample API Calls

**1. Create User**
```bash
curl -X POST http://localhost:8000/api/v1/users \
  -H "Content-Type: application/json" \
  -d '{
    "id": "user123",
    "name": "John Doe",
    "role": "student",
    "interests": ["AI", "ML"]
  }'
```

**2. List Papers**
```bash
curl http://localhost:8000/api/v1/research/papers?limit=10
```

**3. Get Paper Analysis**
```bash
curl http://localhost:8000/api/v1/research/papers/{paper_id}/analysis
```

**4. Get Plan B Suggestions**
```bash
curl http://localhost:8000/api/v1/research/papers/{paper_id}/plan-b
```

**5. Generate Report**
```bash
curl -X POST http://localhost:8000/api/v1/reports/generate?user_id=user123
```

---

## 🧪 Verify Installation

### Backend Verification
```bash
# Run E2E verification script
python main_mock.py
```

Expected output:
- Database tables created
- Papers crawled and analyzed
- Recommendations generated
- ✅ End-to-end test passed

### Frontend Verification
```bash
cd frontend

# Check TypeScript types
npm run lint

# Build frontend
npm run build
```

Expected output:
- No TypeScript errors
- Successful build

---

## 📁 Project Structure

```
Univ-Insight/
├── src/                          # Backend source
│   ├── api/                      # FastAPI endpoints
│   ├── core/                     # Config & database
│   ├── domain/                   # Data models
│   └── services/                 # Business logic
│
├── frontend/                     # React frontend
│   ├── src/
│   │   ├── pages/               # 6 main pages
│   │   ├── services/            # API client
│   │   ├── store/               # State management
│   │   └── types/               # TypeScript definitions
│   └── package.json             # Frontend dependencies
│
├── tests/                        # Test suite
├── requirements.txt              # Backend dependencies
├── main_mock.py                 # E2E verification
└── README.md                    # Project overview
```

---

## 🔧 Development

### Add a New Backend Endpoint

1. Create endpoint in `src/api/routes.py`:
```python
@router.get("/example")
def example_endpoint(db: Session = Depends(get_db)):
    return {"message": "Hello"}
```

2. Test at http://localhost:8000/docs

### Add a New Frontend Page

1. Create component in `src/pages/`:
```typescript
export default function NewPage() {
  return <div>New Page</div>
}
```

2. Add route in `src/App.tsx`:
```typescript
<Route path="/newpage" element={<NewPage />} />
```

---

## 🐛 Troubleshooting

### Backend Issues

**Database Error: "already exists"**
```bash
# Delete old database and reinitialize
rm univ_insight.db
python -c "from src.core.init_db import init_db; init_db()"
```

**Port 8000 already in use**
```bash
# Use different port
python -m uvicorn src.api.main:app --port 9000
```

**Ollama not found**
- Uses Mock LLM by default
- To use real Ollama: `ollama serve` in another terminal

### Frontend Issues

**Port 5173 already in use**
```bash
npm run dev -- --port 5174
```

**API connection failed**
- Check backend is running: `http://localhost:8000/health`
- Check .env VITE_API_URL is correct
- Check CORS in backend is enabled

**TypeScript errors**
```bash
npm run lint
```

---

## 📖 Documentation

- **Backend:** See `IMPLEMENTATION_COMPLETE.md`
- **Frontend:** See `FRONTEND_IMPLEMENTATION_COMPLETE.md`
- **Architecture:** See `docs/` directory
- **API Spec:** See `docs/api/api_specification.md`

---

## 🚀 Deployment

### Docker Setup (Coming Soon)

```bash
# Build images
docker-compose up -d

# Access at:
# - Frontend: http://localhost:80
# - API: http://localhost:8000/api/v1
```

### Environment Variables

Create `.env.production`:
```
DATABASE_URL=postgresql://user:password@db/univ_insight
API_HOST=0.0.0.0
API_PORT=8000
LLM_MODEL=ollama
NOTION_TOKEN=xxx
KAKAO_BOT_TOKEN=xxx
```

---

## 💡 Tips

1. **Keep both servers running** - Open two terminals for backend and frontend
2. **Check browser console** - View API errors and logs
3. **Use Swagger UI** - Test API endpoints at /docs
4. **Use mock data** - Frontend works without backend (graceful fallback)
5. **Database persists** - User data saved between runs

---

## ✅ Checklist for Success

- [ ] Backend running at http://localhost:8000
- [ ] Frontend running at http://localhost:5173
- [ ] Can login at /login
- [ ] Can search papers at /research
- [ ] Can view reports at /reports
- [ ] Can edit profile at /profile
- [ ] API working at /api/v1/*
- [ ] No console errors

---

## 🎯 Next Steps

1. **Run E2E tests:** `python main_mock.py`
2. **Test full flow:** Login → Search → View Details → Plan B → Profile
3. **Check API docs:** http://localhost:8000/docs
4. **Review code:** Check implementation files

---

## 📞 Support

For issues or questions:
1. Check TROUBLESHOOTING section above
2. Review documentation files
3. Check API spec: `/docs`
4. Check console logs

---

**Happy coding! 🚀**
