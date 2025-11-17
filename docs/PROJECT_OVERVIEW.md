# ResearchNow - Project Overview 📚🔬

**An AI-powered research paper summarization platform making scientific literature accessible to everyone.**

---

## 🎯 Mission

Transform complex research papers into clear, understandable summaries that anyone can comprehend. Bridge the gap between cutting-edge research and the general public by leveraging AI to simplify scientific communication.

---

## 🌟 Key Features

### 1. **Multi-Source Paper Aggregation**
- **200+ Million Papers** from 8 major sources
- **Full-Text Access**: arXiv, PubMed Central, CORE, DOAJ, S2ORC (~50M papers)
- **Metadata & Abstracts**: Semantic Scholar, Crossref, OpenAlex (200M+ papers)
- **Real-time Sync**: Automatic updates from all sources

### 2. **AI-Powered Summarization**
- **Multiple AI Models**: Llama 70B, AELLA-Qwen
- **Multi-Level Summaries**:
  - Executive Summary (2-3 sentences)
  - Detailed Summary (1 paragraph)
  - Simplified Summary (plain language for non-experts)
  - Section-by-section breakdown (Methods, Results, etc.)
- **Key Information Extraction**:
  - Main findings and claims
  - Research questions and hypotheses
  - Methodology overview
  - Limitations and future work
  - Auto-generated tags and keywords

### 3. **Smart Search & Discovery**
- **Keyword Search**: Traditional full-text search
- **Semantic Search**: Vector-based similarity using embeddings
- **Advanced Filters**: Field, date, citations, open access
- **Recommendations**: Related papers based on content
- **Citation Network**: Explore paper relationships

### 4. **Cross-Platform Access**
- **🌐 Web App**: Responsive Next.js application
- **📱 iOS App**: Native mobile experience
- **🤖 Android App**: Native mobile experience
- **All platforms share unified backend API**

### 5. **User Features** (Optional)
- Bookmarks and collections
- Reading history
- Personalized recommendations
- Collaborative annotations (coming soon)
- Export summaries (PDF, Markdown)

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        CLIENT LAYER                              │
├──────────────────┬──────────────────┬──────────────────────────┤
│   Web Frontend   │   iOS App        │   Android App            │
│   (Next.js)      │   (React Native) │   (React Native)         │
└────────┬─────────┴────────┬─────────┴────────┬─────────────────┘
         │                  │                  │
         └──────────────────┴──────────────────┘
                            │
                    ┌───────▼────────┐
                    │   API Gateway   │
                    │   (FastAPI)     │
                    └───────┬────────┘
                            │
         ┌──────────────────┼──────────────────┐
         │                  │                  │
    ┌────▼─────┐     ┌─────▼──────┐    ┌─────▼──────┐
    │  Paper   │     │    AI      │    │   Search   │
    │Collection│     │Summarizer  │    │  Engine    │
    │ Services │     │  Service   │    │  Service   │
    └────┬─────┘     └─────┬──────┘    └─────┬──────┘
         │                  │                  │
         └──────────────────┼──────────────────┘
                            │
         ┌──────────────────┼──────────────────┐
         │                  │                  │
    ┌────▼─────┐     ┌─────▼──────┐    ┌─────▼──────┐
    │PostgreSQL│     │   Qdrant   │    │   Redis    │
    │(Relational)     │  (Vector)  │    │  (Cache)   │
    └──────────┘     └────────────┘    └────────────┘
         │
    ┌────▼─────┐     ┌────────────┐    ┌────────────┐
    │  MinIO   │     │  RabbitMQ  │    │   Ollama   │
    │(Storage) │     │  (Queue)   │    │ (AI Model) │
    └──────────┘     └────────────┘    └────────────┘
```

---

## 🔧 Technology Stack

### Backend
| Component | Technology | Purpose |
|-----------|-----------|---------|
| API Framework | FastAPI | High-performance async API |
| Database | PostgreSQL 15 | Relational data storage |
| Vector DB | Qdrant | Semantic search embeddings |
| Cache | Redis 7 | High-speed caching |
| Task Queue | Celery + RabbitMQ | Background job processing |
| Storage | MinIO | S3-compatible PDF storage |
| ORM | SQLAlchemy | Database abstraction |

### AI/ML
| Component | Technology | Purpose |
|-----------|-----------|---------|
| Primary Model | Llama 70B | Paper summarization |
| Secondary Model | AELLA-Qwen | Alternative summarization |
| Embeddings | Sentence Transformers | Semantic search vectors |
| Runtime | Ollama / vLLM | Model inference |
| Fallback | OpenAI GPT-4 | Backup option |

### Frontend
| Component | Technology | Purpose |
|-----------|-----------|---------|
| Web Framework | Next.js 14 | React-based web app |
| Mobile Framework | React Native 0.73 | Cross-platform mobile |
| State Management | Zustand | Lightweight state |
| API Client | React Query | Data fetching & caching |
| Styling | Tailwind CSS | Utility-first CSS |
| UI Components | shadcn/ui + React Native Paper | Component libraries |

### DevOps
| Component | Technology | Purpose |
|-----------|-----------|---------|
| Containerization | Docker | Service isolation |
| Orchestration | Docker Compose | Local development |
| CI/CD | GitHub Actions | Automated deployment |
| Monitoring | Prometheus + Grafana | Metrics & dashboards |
| Logging | JSON structured logs | Centralized logging |

---

## 📊 Data Flow

### 1. Paper Ingestion Pipeline
```
External Source (arXiv/PubMed/etc.)
    ↓
API Collector Service
    ↓
Data Validation & Normalization
    ↓
PostgreSQL (Metadata)
    ↓
Full Text Extraction (if available)
    ↓
MinIO (PDF Storage) + PostgreSQL (Text)
    ↓
Embedding Generation
    ↓
Qdrant (Vector Storage)
```

### 2. Summarization Pipeline
```
User Request
    ↓
Backend API
    ↓
Fetch Paper (PostgreSQL + MinIO)
    ↓
AI Summarization Queue (Celery)
    ↓
Llama 70B / AELLA-Qwen
    ↓
Generate Multi-Level Summaries
    ↓
Quality Check
    ↓
Store Summary (PostgreSQL)
    ↓
Return to User
```

### 3. Search Pipeline
```
User Query
    ↓
API Search Endpoint
    ↓
┌─────────────┬─────────────┐
│  Keyword    │  Semantic   │
│  Search     │  Search     │
│ (PostgreSQL)│  (Qdrant)   │
└─────────────┴─────────────┘
    ↓
Merge & Rank Results
    ↓
Apply Filters
    ↓
Cache Results (Redis)
    ↓
Return to User
```

---

## 🔍 Core Components

### 1. Paper Collection Services

**Location**: `backend/services/`

- **ArxivService**: Fetch papers from arXiv API
- **PubMedService**: Access PubMed Central
- **SemanticScholarService**: Query Semantic Scholar
- **CrossrefService**: Get metadata from Crossref
- **OpenAlexService**: Access OpenAlex data
- **COREService**: Fetch from CORE.ac.uk
- **DOAJService**: Query DOAJ journals
- **S2ORCService**: Access Semantic Scholar corpus

Each service handles:
- Rate limiting
- Error handling and retries
- Data normalization
- Incremental updates

### 2. AI Summarization Engine

**Location**: `backend/ai/summarizer.py`

Features:
- Multiple prompt templates for different summary types
- Context-aware summarization (uses paper structure)
- Automatic difficulty level detection
- Quality scoring and validation
- Fallback to alternative models
- Batch processing for efficiency

### 3. Search Engine

**Location**: `backend/api/routes/search.py`

Capabilities:
- Full-text search with PostgreSQL
- Vector similarity search with Qdrant
- Hybrid search combining both methods
- Advanced filtering and faceting
- Result ranking and relevance scoring
- Search suggestions and autocomplete

### 4. Database Models

**Location**: `backend/database/models.py`

Key models:
- **Paper**: Core paper metadata and identifiers
- **FullText**: Complete paper content
- **Summary**: AI-generated summaries
- **Author**: Author information
- **Citation**: Citation relationships
- **User**: User accounts (optional)
- **Bookmark**: Saved papers
- **Collection**: User-organized paper lists

---

## 🚀 Deployment Architecture

### Development
```
Docker Compose (Local)
├── All services on localhost
├── Hot reload enabled
├── Debug mode active
└── Sample data loaded
```

### Production
```
Cloud Provider (AWS/GCP/Azure/DigitalOcean)
├── Backend: Container service (ECS/Cloud Run/App Service)
├── Database: Managed PostgreSQL (RDS/Cloud SQL)
├── Cache: Managed Redis (ElastiCache/MemoryStore)
├── Storage: S3 / Cloud Storage
├── Frontend: Vercel / Netlify / CDN
├── Load Balancer: Nginx / ALB
└── Monitoring: Prometheus + Grafana
```

---

## 📈 Scalability Considerations

### Horizontal Scaling
- **API Servers**: Multiple instances behind load balancer
- **Celery Workers**: Scale workers based on queue depth
- **Database**: Read replicas for query distribution
- **Cache**: Redis cluster for high availability

### Performance Optimizations
- **Caching Strategy**: Multi-level (Redis, CDN, browser)
- **Database Indexing**: Optimized for common queries
- **Connection Pooling**: Efficient database connections
- **Async Processing**: Non-blocking I/O operations
- **Batch Operations**: Bulk inserts and updates

### Cost Optimization
- **Ollama**: Local AI models (no API costs)
- **Open-source stack**: No licensing fees
- **Efficient caching**: Reduced API calls
- **Rate limiting**: Prevent abuse
- **Incremental sync**: Only fetch new papers

---

## 🔐 Security Features

### API Security
- Rate limiting (per IP and per user)
- Input validation and sanitization
- SQL injection prevention (SQLAlchemy ORM)
- XSS protection
- CORS configuration
- Optional API key authentication

### Data Security
- Encrypted connections (HTTPS/TLS)
- Secure password hashing (bcrypt)
- Environment variable management
- No hardcoded secrets
- Regular dependency updates

### Privacy
- Optional anonymous usage
- No user tracking (unless opted in)
- Minimal data collection
- GDPR compliant (if enabled)

---

## 📱 Mobile App Features

### iOS & Android (React Native)
- Native navigation
- Offline reading mode
- PDF viewer integration
- Share functionality
- Push notifications (optional)
- Dark mode support
- Biometric authentication
- Seamless sync with web

---

## 🎨 User Experience

### Design Principles
1. **Simplicity**: Clean, intuitive interface
2. **Speed**: Fast load times, instant search
3. **Accessibility**: WCAG 2.1 compliant
4. **Consistency**: Unified design across platforms
5. **Responsiveness**: Works on all screen sizes

### Key User Flows

**1. New User**
```
Land on homepage → Search/Browse → View paper → Read summary → Bookmark
```

**2. Researcher**
```
Advanced search → Filter results → Compare papers → Export summaries → Cite
```

**3. Student**
```
Topic search → Read simplified summary → Understand concepts → Explore related papers
```

---

## 📊 Metrics & Analytics

### Platform Metrics
- Total papers indexed
- Summaries generated
- Active users
- Search queries
- API calls
- Response times

### Quality Metrics
- Summary quality scores
- User feedback ratings
- Citation accuracy
- Search relevance
- AI model performance

---

## 🛣️ Roadmap

### Phase 1: MVP (Current)
- [x] Core backend API
- [x] Paper collection from 8 sources
- [x] AI summarization
- [x] Web frontend
- [x] Mobile apps (in progress)
- [x] Docker deployment

### Phase 2: Enhancement (Q2 2024)
- [ ] User accounts and authentication
- [ ] Advanced search features
- [ ] Citation graph visualization
- [ ] Browser extensions (Chrome, Firefox)
- [ ] API for developers
- [ ] Multi-language support

### Phase 3: Advanced Features (Q3 2024)
- [ ] Collaborative annotations
- [ ] Reference manager integration (Zotero, Mendeley)
- [ ] Audio summaries (text-to-speech)
- [ ] Video paper explanations
- [ ] Research trends analysis
- [ ] AI-powered research assistant

### Phase 4: Enterprise (Q4 2024)
- [ ] Private deployment options
- [ ] Custom AI model training
- [ ] Advanced analytics
- [ ] Team collaboration features
- [ ] API enterprise tier
- [ ] White-label solutions

---

## 🤝 Contributing

We welcome contributions! Areas where you can help:

1. **Code**: Backend, frontend, mobile
2. **Documentation**: Tutorials, guides, translations
3. **Testing**: Bug reports, feature testing
4. **Design**: UI/UX improvements
5. **Data**: New paper sources, quality checks
6. **Community**: Support, discussions, evangelism

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## 📄 License

MIT License - Free to use, modify, and distribute.

---

## 🙏 Acknowledgments

### Data Sources
- arXiv.org - Open access preprints
- PubMed Central - Biomedical literature
- Semantic Scholar - AI-powered research tool
- CORE - Academic paper aggregator
- OpenAlex - Open catalog of scholarly works
- Crossref - DOI registration agency
- DOAJ - Open access journals

### AI Models
- Meta AI - Llama models
- Alibaba Cloud - Qwen models
- HuggingFace - Model hosting and transformers
- Sentence Transformers - Embedding models

### Open Source
- FastAPI, Next.js, React Native
- PostgreSQL, Redis, RabbitMQ
- Docker, Nginx, and countless others

---

## 📞 Contact & Support

- **Website**: https://researchnow.app
- **Email**: hello@researchnow.app
- **GitHub**: https://github.com/yourusername/ResearchNow
- **Twitter**: @ResearchNowApp
- **Discord**: [Community Server]

---

## 💡 Use Cases

### For Researchers
- Stay updated with latest papers
- Quick literature review
- Find related work
- Share findings with colleagues

### For Students
- Understand complex papers
- Learn new topics quickly
- Prepare for exams
- Write better papers

### For Journalists
- Verify scientific claims
- Understand research findings
- Write accurate science stories
- Find expert sources

### For Curious Minds
- Explore cutting-edge science
- Learn something new daily
- Understand world events
- Make informed decisions

---

## 🎯 Success Metrics

**Target by End of Year 1:**
- 100,000+ monthly active users
- 10 million+ papers indexed
- 1 million+ summaries generated
- 95%+ user satisfaction
- <100ms average search time
- 99.9% API uptime

---

## 🌍 Impact

**Our Goal**: Make scientific knowledge accessible to everyone, regardless of their background or expertise level.

**Vision**: A world where anyone can understand and benefit from cutting-edge research, accelerating innovation and scientific literacy globally.

---

**Built with ❤️ for researchers, students, and curious minds everywhere.**

---

*Last Updated: January 2024*
*Version: 1.0.0*