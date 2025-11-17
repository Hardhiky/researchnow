# Getting Started with ResearchNow 🚀

Welcome to **ResearchNow** - an AI-powered platform that makes research papers accessible to everyone!

---

## ⚡ Quick Start (5 minutes)

### Option 1: Automated Setup (Recommended)

```bash
# Clone the repository
git clone https://github.com/yourusername/ResearchNow.git
cd ResearchNow

# Run the quick start script
./quickstart.sh
```

The script will:
- ✅ Check prerequisites (Docker, Docker Compose)
- ✅ Generate secure passwords
- ✅ Start all services
- ✅ Initialize the database
- ✅ Set up AI models
- ✅ Show you where to access the app

After completion, open **http://localhost:3000** in your browser!

---

### Option 2: Manual Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/ResearchNow.git
cd ResearchNow

# Create environment file
cp .env.example .env

# Edit .env with your settings (optional for quick start)
nano .env

# Start all services
docker-compose up -d

# Initialize database
docker-compose exec backend alembic upgrade head

# Pull AI model (choose one)
docker-compose exec ollama ollama pull llama2:7b   # Fast, 4GB
docker-compose exec ollama ollama pull llama2:13b  # Balanced, 8GB
docker-compose exec ollama ollama pull llama2:70b  # Best, 40GB
```

Access the app at **http://localhost:3000**

---

## 🎯 What Can You Do?

### 1. Search Research Papers
- Search across **200+ million papers**
- Filter by field, year, open access
- Semantic search using AI

### 2. Get AI Summaries
- **Executive Summary**: 2-3 sentences
- **Detailed Summary**: Full paragraph
- **Simplified Explanation**: Plain language for everyone
- **Key Findings**: Bullet points of main discoveries

### 3. Explore & Discover
- Browse trending papers
- Find related research
- Explore citation networks
- Save bookmarks and collections

---

## 📱 Platform Overview

### Web Application
**URL**: http://localhost:3000

Features:
- Advanced search interface
- Paper viewer with summaries
- Collections and bookmarks
- Export capabilities
- Responsive design (mobile-friendly)

### Backend API
**URL**: http://localhost:8000/api/v1
**Docs**: http://localhost:8000/api/docs

Features:
- RESTful API
- Automatic documentation
- Rate limiting
- Caching

### Mobile Apps (iOS & Android)
**Location**: `mobile-app/`

Features:
- Native mobile experience
- Offline reading
- Share functionality
- Dark mode
- Biometric authentication

---

## 🔍 Try Your First Search

### Via Web App:
1. Go to http://localhost:3000
2. Enter a search term (e.g., "machine learning")
3. Browse results
4. Click on a paper
5. View the AI-generated summary

### Via API:
```bash
# Search for papers
curl "http://localhost:8000/api/v1/search?q=machine+learning&limit=5"

# Get a specific paper
curl "http://localhost:8000/api/v1/papers/1"

# Get AI summary
curl "http://localhost:8000/api/v1/papers/1/summary"
```

### Via Python:
```python
import requests

BASE_URL = "http://localhost:8000/api/v1"

# Search papers
response = requests.get(f"{BASE_URL}/search", params={
    "q": "quantum computing",
    "limit": 10
})
papers = response.json()

# Get summary of first paper
paper_id = papers["results"][0]["id"]
summary = requests.get(f"{BASE_URL}/papers/{paper_id}/summary").json()

print(summary["simplified_summary"])
```

---

## 🎓 Example Use Cases

### For Students
```
1. Search for "neural networks basics"
2. Read simplified summary
3. Understand key concepts
4. Explore related papers
5. Bookmark for later study
```

### For Researchers
```
1. Advanced search with filters
2. Review executive summaries
3. Find highly-cited papers
4. Explore citation network
5. Export summaries for reference
```

### For Journalists
```
1. Search recent papers on topic
2. Read simplified explanations
3. Verify claims
4. Find expert authors
5. Share credible sources
```

---

## 🛠️ Service URLs

| Service | URL | Credentials |
|---------|-----|-------------|
| Web App | http://localhost:3000 | - |
| API | http://localhost:8000 | - |
| API Docs | http://localhost:8000/api/docs | - |
| RabbitMQ | http://localhost:15672 | guest / guest |
| MinIO | http://localhost:9001 | minioadmin / minioadmin123 |

---

## 📚 Key Concepts

### Paper Sources
ResearchNow aggregates papers from 8 major sources:

**Full-Text Sources** (Open Access):
- **arXiv**: 2M+ papers (CS, Physics, Math)
- **PubMed Central**: 6M+ biomedical papers
- **CORE**: 30-50M university papers
- **DOAJ**: Millions from OA journals
- **S2ORC**: 8M+ full-text papers

**Metadata Sources**:
- **Semantic Scholar**: 200M+ papers
- **Crossref**: Complete DOI registry
- **OpenAlex**: Open scholarly data

### AI Models
- **Llama 70B**: Primary summarization model
- **AELLA-Qwen**: Alternative model
- **Sentence Transformers**: For semantic search

### Summary Types
1. **Executive**: Quick 2-3 sentence overview
2. **Detailed**: Complete paragraph summary
3. **Simplified**: Plain language explanation
4. **Structured**: Methods, results, findings

---

## 🔧 Common Commands

### Docker Commands
```bash
# View logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f backend

# Restart services
docker-compose restart

# Stop services
docker-compose stop

# Stop and remove everything
docker-compose down

# Stop and remove including volumes (database)
docker-compose down -v
```

### Database Commands
```bash
# Access PostgreSQL
docker-compose exec postgres psql -U researchnow -d researchnow

# Run migrations
docker-compose exec backend alembic upgrade head

# Create new migration
docker-compose exec backend alembic revision --autogenerate -m "description"
```

### Backend Commands
```bash
# Access backend shell
docker-compose exec backend bash

# Run Python shell
docker-compose exec backend python

# Run tests
docker-compose exec backend pytest
```

---

## 🐛 Troubleshooting

### Services won't start
```bash
# Check if ports are already in use
sudo lsof -i :8000  # Backend
sudo lsof -i :3000  # Frontend
sudo lsof -i :5432  # PostgreSQL

# Kill conflicting processes or change ports in docker-compose.yml
```

### Database connection errors
```bash
# Restart PostgreSQL
docker-compose restart postgres

# Check PostgreSQL logs
docker-compose logs postgres

# Reset database (WARNING: deletes all data)
docker-compose down -v
docker-compose up -d
```

### AI summarization not working
```bash
# Check if Ollama is running
docker-compose ps ollama

# Check if model is downloaded
docker-compose exec ollama ollama list

# Pull model if missing
docker-compose exec ollama ollama pull llama2:7b

# Check backend logs
docker-compose logs -f backend
```

### Web app shows blank page
```bash
# Check frontend logs
docker-compose logs web-frontend

# Verify API is accessible
curl http://localhost:8000/health

# Restart frontend
docker-compose restart web-frontend
```

---

## 📖 Next Steps

### 1. Explore Documentation
- **Setup Guide**: `docs/SETUP_GUIDE.md` - Complete setup instructions
- **API Documentation**: `docs/API_DOCUMENTATION.md` - API reference
- **Project Overview**: `docs/PROJECT_OVERVIEW.md` - Architecture details

### 2. Configure API Keys
Get free API keys for more features:
- **CORE**: https://core.ac.uk/services/api
- **Semantic Scholar**: https://www.semanticscholar.org/product/api

Add to `.env` file:
```env
CORE_API_KEY=your_key_here
SEMANTIC_SCHOLAR_API_KEY=your_key_here
```

### 3. Customize Settings
Edit `.env` to customize:
- Rate limits
- Cache settings
- AI model preferences
- Search parameters

### 4. Set Up Mobile Apps
```bash
cd mobile-app

# iOS (macOS only)
npm install
cd ios && pod install && cd ..
npm run ios

# Android
npm install
npm run android
```

### 5. Deploy to Production
See `docs/SETUP_GUIDE.md` for:
- Cloud deployment guides
- Security best practices
- Performance optimization
- Monitoring setup

---

## 🤝 Get Help

### Resources
- **Documentation**: `docs/` folder
- **GitHub Issues**: Report bugs and request features
- **API Docs**: http://localhost:8000/api/docs
- **Examples**: `examples/` folder

### Community
- **GitHub Discussions**: Ask questions
- **Email**: support@researchnow.app
- **Twitter**: @ResearchNowApp

---

## 🎉 You're All Set!

Start exploring research papers like never before. Happy researching! 🔬📚

### Quick Links
- 🌐 **Web App**: http://localhost:3000
- 📚 **API Docs**: http://localhost:8000/api/docs
- 📖 **Full Setup Guide**: [docs/SETUP_GUIDE.md](docs/SETUP_GUIDE.md)
- 🏗️ **Architecture**: [docs/PROJECT_OVERVIEW.md](docs/PROJECT_OVERVIEW.md)

---

**Made with ❤️ for researchers, students, and curious minds everywhere.**