# ResearchNow 📚🔬

A comprehensive research paper summarization platform that makes scientific literature accessible to everyone. Built with AI-powered summarization using Llama 70B and AELLA-Qwen models.

## 🌟 Features

- **Multi-Source Paper Collection**: Aggregates papers from 200+ million sources
  - Full-text from arXiv, PubMed Central, CORE, DOAJ, S2ORC
  - Metadata + abstracts from Semantic Scholar, Crossref, OpenAlex
  
- **AI-Powered Summarization**: Converts complex research into plain language
  - Simplified summaries for non-experts
  - Key highlights and findings
  - Methods and results breakdown
  - Important claims extraction

- **Cross-Platform Access**:
  - 🌐 Responsive Web Application
  - 📱 Native iOS App
  - 🤖 Native Android App

- **Smart Search & Discovery**:
  - Semantic search using vector embeddings
  - Filter by field, date, citations
  - Trending papers
  - Personalized recommendations

## 🏗️ Architecture

```
ResearchNow/
├── backend/              # Python/FastAPI backend
│   ├── api/             # REST API endpoints
│   ├── services/        # Paper collection services
│   ├── ai/              # AI summarization models
│   ├── database/        # Database models & migrations
│   └── workers/         # Background job workers
│
├── web-frontend/        # React/Next.js web app
│   ├── components/      # Reusable UI components
│   ├── pages/          # Next.js pages
│   ├── hooks/          # Custom React hooks
│   └── services/       # API client services
│
├── mobile-app/          # React Native mobile app
│   ├── src/
│   │   ├── screens/    # App screens
│   │   ├── components/ # UI components
│   │   ├── navigation/ # Navigation config
│   │   └── services/   # API services
│   ├── ios/            # iOS-specific code
│   └── android/        # Android-specific code
│
└── docs/               # Documentation
    ├── api/            # API documentation
    ├── deployment/     # Deployment guides
    └── architecture/   # Architecture diagrams
```

## 🚀 Tech Stack

### Backend
- **Framework**: FastAPI (Python 3.11+)
- **Database**: PostgreSQL (relational data) + Qdrant (vector embeddings)
- **Cache**: Redis
- **Task Queue**: Celery + RabbitMQ
- **AI Models**: 
  - Llama 70B (via Ollama or vLLM)
  - AELLA-Qwen
- **Storage**: MinIO (S3-compatible) for PDFs

### Web Frontend
- **Framework**: Next.js 14 (React 18)
- **Styling**: Tailwind CSS + shadcn/ui
- **State Management**: Zustand
- **API Client**: Axios + React Query

### Mobile Apps
- **Framework**: React Native 0.73+
- **Navigation**: React Navigation
- **State Management**: Zustand
- **UI Components**: React Native Paper

## 📦 Data Sources

### Full-Text Sources (Legal/Open Access)
1. **arXiv** - ~2M papers (CS, Math, Physics)
2. **PubMed Central OA** - ~6M biomedical papers
3. **CORE** - ~30-50M papers from university repositories
4. **DOAJ** - Millions from 20,000+ OA journals
5. **S2ORC** - ~8.1M full-text papers (Semantic Scholar)

### Metadata + Abstract Sources
1. **Semantic Scholar API** - Massive coverage, free
2. **Crossref API** - DOI registry for all publishers
3. **OpenAlex** - Open alternative to Google Scholar

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL 15+
- Redis 7+
- Docker & Docker Compose (recommended)

### Quick Start with Docker

```bash
# Clone the repository
git clone https://github.com/yourusername/ResearchNow.git
cd ResearchNow

# Start all services
docker-compose up -d

# The services will be available at:
# - Backend API: http://localhost:8000
# - Web Frontend: http://localhost:3000
# - Admin Dashboard: http://localhost:8000/admin
```

### Manual Setup

#### Backend Setup
```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your configuration

# Run database migrations
alembic upgrade head

# Start the server
uvicorn main:app --reload
```

#### Web Frontend Setup
```bash
cd web-frontend

# Install dependencies
npm install

# Set up environment variables
cp .env.example .env.local
# Edit .env.local with your API endpoint

# Start development server
npm run dev
```

#### Mobile App Setup
```bash
cd mobile-app

# Install dependencies
npm install

# iOS setup (macOS only)
cd ios && pod install && cd ..

# Run on iOS
npm run ios

# Run on Android
npm run android
```

## 🔑 API Keys Required

To use all features, you'll need API keys from:

1. **Semantic Scholar** - Free, no key required
2. **Crossref** - Free, polite pool access (optional email)
3. **CORE** - Free API key (register at core.ac.uk)
4. **OpenAlex** - Free, no key required (email recommended)
5. **AI Models** - Local Ollama or API keys for hosted services

Add these to your `.env` file:
```env
CORE_API_KEY=your_core_api_key
SEMANTIC_SCHOLAR_API_KEY=optional
OPENAI_API_KEY=optional_for_fallback
HUGGINGFACE_TOKEN=optional_for_models
```

## 📊 Database Schema

### Main Tables
- **papers**: Paper metadata, DOI, title, authors
- **full_texts**: Full paper content (for OA papers)
- **abstracts**: Paper abstracts
- **summaries**: AI-generated summaries
- **keywords**: Extracted keywords and tags
- **citations**: Citation relationships
- **authors**: Author information
- **sources**: Data source tracking

## 🤖 AI Summarization Pipeline

1. **Paper Ingestion**: Download/extract paper content
2. **Preprocessing**: Clean and structure text
3. **Section Extraction**: Identify abstract, methods, results, conclusions
4. **Summarization**: Generate multi-level summaries
   - Executive summary (2-3 sentences)
   - Detailed summary (1 paragraph)
   - Section-by-section breakdown
   - Key findings and claims
5. **Simplification**: Convert technical language to plain English
6. **Quality Check**: Validate summary accuracy
7. **Storage**: Save with metadata and embeddings

## 🔍 Search Features

- **Keyword Search**: Traditional text search
- **Semantic Search**: Vector similarity using embeddings
- **Filter Options**:
  - Publication date range
  - Field of study
  - Citation count
  - Open access only
  - Journal/conference
- **Sort Options**:
  - Relevance
  - Most cited
  - Most recent
  - Trending

## 📱 Mobile App Features

- Clean, intuitive interface
- Offline reading mode
- Bookmark papers
- Share summaries
- Dark mode support
- Push notifications for saved topics
- PDF viewer integration

## 🌐 Web App Features

- Responsive design (mobile, tablet, desktop)
- Advanced search filters
- User accounts and preferences
- Reading history
- Collections/folders
- Export summaries (PDF, Markdown)
- Browser extension integration

## 🔐 Security & Privacy

- No user tracking beyond anonymous analytics
- Optional user accounts (no email required)
- API rate limiting
- Input validation and sanitization
- Secure API key storage
- HTTPS enforced in production

## 📈 Performance

- **API Response Time**: < 200ms (cached)
- **Summarization Time**: 10-30 seconds per paper
- **Search Results**: < 1 second for 100M+ papers
- **Concurrent Users**: Scales horizontally
- **CDN**: CloudFlare for static assets

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](docs/CONTRIBUTING.md) for guidelines.

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Write tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Data Sources**: arXiv, PubMed, Semantic Scholar, CORE, OpenAlex
- **AI Models**: Meta AI (Llama), Qwen team
- **Open Source Community**: All the amazing libraries we use

## 📞 Contact & Support

- **Issues**: GitHub Issues
- **Discussions**: GitHub Discussions
- **Email**: support@researchnow.app
- **Twitter**: @ResearchNowApp

## 🗺️ Roadmap

- [x] Core paper collection system
- [x] Basic summarization pipeline
- [x] Web frontend MVP
- [ ] Mobile apps (iOS/Android)
- [ ] Citation graph visualization
- [ ] Collaborative annotations
- [ ] API for developers
- [ ] Browser extensions (Chrome, Firefox)
- [ ] Integration with reference managers (Zotero, Mendeley)
- [ ] Multi-language support
- [ ] Audio summaries (text-to-speech)
- [ ] Video paper explanations

## ⭐ Star History

If you find this project useful, please consider giving it a star!

---

**Made with ❤️ for researchers, students, and curious minds everywhere.**