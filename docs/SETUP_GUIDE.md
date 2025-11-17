# ResearchNow - Complete Setup Guide 

This guide will walk you through setting up the complete ResearchNow platform, including backend API, web frontend, and mobile apps.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Quick Start (Docker)](#quick-start-docker)
3. [Manual Setup](#manual-setup)
4. [API Keys Configuration](#api-keys-configuration)
5. [AI Models Setup](#ai-models-setup)
6. [Mobile App Setup](#mobile-app-setup)
7. [Production Deployment](#production-deployment)
8. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Software

- **Docker & Docker Compose** (v20.10+) - Easiest setup method
- **Python 3.11+** - For backend development
- **Node.js 18+** - For web and mobile frontends
- **PostgreSQL 15+** - Database (if not using Docker)
- **Redis 7+** - Caching (if not using Docker)
- **Git** - Version control

### Recommended Hardware

- **Minimum**: 8GB RAM, 4 CPU cores, 50GB storage
- **Recommended**: 16GB RAM, 8 CPU cores, 200GB SSD
- **For AI Models**: NVIDIA GPU with 24GB+ VRAM (for local Llama 70B)

### For Mobile Development

- **iOS**: macOS with Xcode 15+
- **Android**: Android Studio with SDK 33+
- **React Native CLI**: `npm install -g react-native-cli`

---

## Quick Start (Docker)

This is the **fastest way** to get ResearchNow running!

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/ResearchNow.git
cd ResearchNow
```

### 2. Create Environment File

```bash
cp .env.example .env
```

Edit `.env` with your configuration:

```env
# Database
POSTGRES_PASSWORD=your_secure_password

# Redis
REDIS_PASSWORD=your_redis_password

# RabbitMQ
RABBITMQ_USER=researchnow
RABBITMQ_PASSWORD=your_rabbitmq_password

# MinIO
MINIO_ROOT_USER=minioadmin
MINIO_ROOT_PASSWORD=your_minio_password

# API Keys (get these from respective services)
CORE_API_KEY=your_core_api_key
SEMANTIC_SCHOLAR_API_KEY=your_s2_key
PUBMED_EMAIL=your.email@example.com
CROSSREF_EMAIL=your.email@example.com
OPENALEX_EMAIL=your.email@example.com

# Optional: OpenAI (for fallback)
OPENAI_API_KEY=your_openai_key

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 3. Start All Services

```bash
docker-compose up -d
```

This will start:
- PostgreSQL (port 5432)
- Redis (port 6379)
- RabbitMQ (port 5672, Management UI: 15672)
- Qdrant Vector DB (port 6333)
- MinIO Storage (port 9000, Console: 9001)
- Ollama AI (port 11434)
- Backend API (port 8000)
- Celery Workers
- Web Frontend (port 3000)

### 4. Initialize Database

```bash
# Run migrations
docker-compose exec backend alembic upgrade head

# (Optional) Seed with sample data
docker-compose exec backend python scripts/seed_data.py
```

### 5. Pull AI Model (Llama)

```bash
# Download Llama 2 70B (requires ~40GB)
docker-compose exec ollama ollama pull llama2:70b

# Or use smaller model for testing
docker-compose exec ollama ollama pull llama2:13b
```

### 6. Access the Application

- **Web App**: http://localhost:3000
- **API Docs**: http://localhost:8000/api/docs
- **RabbitMQ Management**: http://localhost:15672 (guest/guest)
- **MinIO Console**: http://localhost:9001 (minioadmin/minioadmin123)

### 7. Verify Everything Works

```bash
# Check service health
curl http://localhost:8000/health

# Test paper search
curl "http://localhost:8000/api/v1/search?q=machine+learning&limit=5"
```

---

## Manual Setup

If you prefer not to use Docker, follow these steps:

### Backend Setup

#### 1. Install Python Dependencies

```bash
cd backend

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

#### 2. Install and Configure PostgreSQL

```bash
# Install PostgreSQL (Ubuntu/Debian)
sudo apt-get install postgresql-15

# Create database and user
sudo -u postgres psql
```

```sql
CREATE DATABASE researchnow;
CREATE USER researchnow WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE researchnow TO researchnow;
\q
```

#### 3. Install and Configure Redis

```bash
# Install Redis (Ubuntu/Debian)
sudo apt-get install redis-server

# Start Redis
sudo systemctl start redis-server
sudo systemctl enable redis-server

# Set password (edit /etc/redis/redis.conf)
# Uncomment: requirepass your_redis_password
sudo systemctl restart redis-server
```

#### 4. Install RabbitMQ

```bash
# Install RabbitMQ (Ubuntu/Debian)
sudo apt-get install rabbitmq-server

# Start RabbitMQ
sudo systemctl start rabbitmq-server
sudo systemctl enable rabbitmq-server

# Enable management plugin
sudo rabbitmq-plugins enable rabbitmq_management

# Create user
sudo rabbitmqctl add_user researchnow your_password
sudo rabbitmqctl set_permissions -p / researchnow ".*" ".*" ".*"
```

#### 5. Install Qdrant

```bash
# Using Docker (recommended)
docker run -d -p 6333:6333 -p 6334:6334 \
  -v $(pwd)/qdrant_storage:/qdrant/storage \
  qdrant/qdrant

# Or download binary from https://github.com/qdrant/qdrant/releases
```

#### 6. Install MinIO

```bash
# Download MinIO
wget https://dl.min.io/server/minio/release/linux-amd64/minio
chmod +x minio
sudo mv minio /usr/local/bin/

# Create data directory
mkdir -p ~/minio/data

# Start MinIO
minio server ~/minio/data --console-address ":9001"
```

#### 7. Configure Backend Environment

```bash
cd backend
cp .env.example .env
```

Edit `.env` with your local configuration.

#### 8. Run Database Migrations

```bash
alembic upgrade head
```

#### 9. Start Backend Server

```bash
# Development
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Production
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
```

#### 10. Start Celery Workers

```bash
# In separate terminals:

# Worker
celery -A workers.celery_app worker --loglevel=info --concurrency=4

# Beat (scheduler)
celery -A workers.celery_app beat --loglevel=info
```

### Web Frontend Setup

```bash
cd web-frontend

# Install dependencies
npm install

# Configure environment
cp .env.example .env.local
```

Edit `.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

```bash
# Start development server
npm run dev

# Build for production
npm run build
npm run start
```

### Mobile App Setup

See [Mobile App Setup](#mobile-app-setup) section below.

---

## API Keys Configuration

You'll need API keys from various services to access papers. Most are **free**!

### 1. CORE API Key (Required for CORE.ac.uk)

1. Visit https://core.ac.uk/services/api
2. Register for a free account
3. Request API key
4. Add to `.env`: `CORE_API_KEY=your_key`

### 2. Semantic Scholar (Optional - Higher Rate Limits)

1. Visit https://www.semanticscholar.org/product/api
2. Request API key
3. Add to `.env`: `SEMANTIC_SCHOLAR_API_KEY=your_key`

### 3. PubMed (Required Email)

- No API key needed
- Add your email: `PUBMED_EMAIL=your.email@example.com`
- This gives you access to higher rate limits

### 4. Crossref (Optional - Polite Pool)

- No API key needed
- Add your email: `CROSSREF_EMAIL=your.email@example.com`
- Gets you into "polite pool" with better rate limits

### 5. OpenAlex (Recommended)

- No API key needed
- Add your email: `OPENALEX_EMAIL=your.email@example.com`
- Recommended for better support

### 6. OpenAI (Optional - Fallback)

If local AI models fail:

1. Visit https://platform.openai.com
2. Create account and get API key
3. Add to `.env`: `OPENAI_API_KEY=your_key`

---

## AI Models Setup

### Option 1: Ollama (Recommended - Local)

**Pros**: Free, private, no API costs
**Cons**: Requires GPU with 24GB+ VRAM for 70B model

```bash
# Install Ollama
curl https://ollama.ai/install.sh | sh

# Pull Llama 2 models
ollama pull llama2:70b      # 40GB - Best quality
ollama pull llama2:13b      # 8GB - Good quality
ollama pull llama2:7b       # 4GB - Fast, decent quality

# Test
ollama run llama2:13b "Summarize this: Machine learning is..."
```

Update `.env`:
```env
LLAMA_API_URL=http://localhost:11434
LLAMA_MODEL_NAME=llama2:13b
```

### Option 2: vLLM (Production - Faster)

For better performance with multiple requests:

```bash
pip install vllm

# Start vLLM server
python -m vllm.entrypoints.openai.api_server \
  --model meta-llama/Llama-2-70b-hf \
  --host 0.0.0.0 \
  --port 8080
```

Update `.env`:
```env
LLAMA_API_URL=http://localhost:8080/v1
```

### Option 3: HuggingFace Inference API

**Pros**: No local GPU needed
**Cons**: Costs money, slower

```bash
# Get token from https://huggingface.co/settings/tokens
```

Update `.env`:
```env
HUGGINGFACE_TOKEN=your_token
```

### Option 4: OpenAI (Fallback)

Simplest but costs money:

```env
OPENAI_API_KEY=your_key
OPENAI_MODEL=gpt-4-turbo-preview
```

---

## Mobile App Setup

### iOS Setup (macOS only)

```bash
cd mobile-app

# Install dependencies
npm install

# Install CocoaPods dependencies
cd ios
pod install
cd ..

# Start Metro bundler
npm start

# In another terminal, run iOS app
npm run ios

# Or open in Xcode
open ios/ResearchNow.xcworkspace
```

### Android Setup

```bash
cd mobile-app

# Install dependencies
npm install

# Make sure Android SDK is installed
# Set ANDROID_HOME environment variable

# Start Metro bundler
npm start

# In another terminal, run Android app
npm run android

# Or open in Android Studio
android studio android/
```

### Configure API Endpoint

Edit `mobile-app/src/config.ts`:

```typescript
export const API_URL = __DEV__
  ? 'http://localhost:8000'  // iOS simulator
  : 'http://10.0.2.2:8000';  // Android emulator

// For real device, use your computer's IP:
// export const API_URL = 'http://192.168.1.100:8000';
```

### Building for Release

#### iOS

```bash
cd mobile-app/ios

# Archive app
xcodebuild -workspace ResearchNow.xcworkspace \
  -scheme ResearchNow \
  -configuration Release \
  -archivePath build/ResearchNow.xcarchive \
  archive

# Export IPA
xcodebuild -exportArchive \
  -archivePath build/ResearchNow.xcarchive \
  -exportOptionsPlist exportOptions.plist \
  -exportPath build
```

#### Android

```bash
cd mobile-app/android

# Generate release APK
./gradlew assembleRelease

# APK location: android/app/build/outputs/apk/release/app-release.apk

# Generate AAB (for Play Store)
./gradlew bundleRelease
```

---

## Production Deployment

### Backend Deployment (AWS/DigitalOcean/etc.)

#### 1. Prepare Server

```bash
# Update system
sudo apt-get update && sudo apt-get upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

#### 2. Deploy with Docker

```bash
# Clone repository
git clone https://github.com/yourusername/ResearchNow.git
cd ResearchNow

# Configure production environment
cp .env.example .env
nano .env  # Edit with production values

# Start services
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Initialize database
docker-compose exec backend alembic upgrade head
```

#### 3. Set up Nginx (Reverse Proxy)

```nginx
# /etc/nginx/sites-available/researchnow

server {
    listen 80;
    server_name api.researchnow.app;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

server {
    listen 80;
    server_name researchnow.app www.researchnow.app;

    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/researchnow /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

#### 4. SSL with Let's Encrypt

```bash
sudo apt-get install certbot python3-certbot-nginx
sudo certbot --nginx -d api.researchnow.app -d researchnow.app
```

#### 5. Set up Monitoring

```bash
# Start monitoring stack
docker-compose --profile monitoring up -d

# Access Grafana: http://your-server:3001
# Access Prometheus: http://your-server:9090
```

### Frontend Deployment (Vercel - Easiest)

```bash
cd web-frontend

# Install Vercel CLI
npm i -g vercel

# Deploy
vercel --prod
```

Or deploy to any platform:

```bash
# Build
npm run build

# Deploy the 'out' or '.next' directory
```

### Mobile App Deployment

#### iOS App Store

1. Create app in App Store Connect
2. Archive in Xcode
3. Upload to App Store Connect
4. Submit for review

#### Android Play Store

1. Create app in Play Console
2. Generate signed AAB
3. Upload to Play Console
4. Submit for review

---

## Troubleshooting

### Common Issues

#### Backend won't start

```bash
# Check logs
docker-compose logs backend

# Common fixes:
# 1. Database not ready
docker-compose restart postgres
docker-compose restart backend

# 2. Port already in use
sudo lsof -i :8000
# Kill the process or change port

# 3. Migration issues
docker-compose exec backend alembic upgrade head
```

#### AI summarization failing

```bash
# Check Ollama is running
curl http://localhost:11434/api/version

# Pull model if missing
docker-compose exec ollama ollama pull llama2:13b

# Check logs
docker-compose logs -f backend
```

#### Database connection errors

```bash
# Verify PostgreSQL is running
docker-compose ps postgres

# Check credentials in .env
docker-compose exec postgres psql -U researchnow -d researchnow

# Reset database (WARNING: deletes all data)
docker-compose down -v
docker-compose up -d postgres
docker-compose exec backend alembic upgrade head
```

#### Rate limiting from APIs

```bash
# Add delays in .env
ARXIV_RATE_LIMIT=1
SEMANTIC_SCHOLAR_RATE_LIMIT=10
CROSSREF_RATE_LIMIT=25

# Use API keys for higher limits
# Add to .env as shown in API Keys section
```

#### Out of memory

```bash
# Increase Docker memory
# Docker Desktop: Settings > Resources > Memory (set to 8GB+)

# Use smaller AI model
LLAMA_MODEL_NAME=llama2:7b

# Reduce Celery workers
# In docker-compose.yml: --concurrency=2
```

#### Mobile app can't connect to backend

```bash
# iOS Simulator: Use localhost
# Android Emulator: Use 10.0.2.2
# Real device: Use your computer's IP

# Find your IP
# macOS/Linux: ifconfig | grep inet
# Windows: ipconfig

# Update mobile-app/src/config.ts with your IP
```

### Getting Help

- **GitHub Issues**: https://github.com/yourusername/ResearchNow/issues
- **Discussions**: https://github.com/yourusername/ResearchNow/discussions
- **Email**: support@researchnow.app
- **Discord**: [Coming soon]

---

## Next Steps

1.  **Get Started**: Follow Quick Start guide
2.  **Read API Docs**: Visit http://localhost:8000/api/docs
3.  **Test Search**: Try searching for papers
4.  **Generate Summaries**: Test AI summarization
5.  **Try Mobile App**: Set up iOS/Android app
6.  **Deploy**: Follow production deployment guide

---

## Performance Optimization

### Backend

```python
# config/settings.py

# Increase worker processes
CELERY_WORKER_CONCURRENCY = 8

# Enable query caching
CACHE_ENABLED = True
CACHE_TTL = 3600  # 1 hour

# Database connection pooling
DATABASE_POOL_SIZE = 20
DATABASE_MAX_OVERFLOW = 10
```

### Database

```sql
-- Add indexes for common queries
CREATE INDEX idx_papers_publication_date ON papers(publication_date DESC);
CREATE INDEX idx_papers_citation_count ON papers(citation_count DESC);
CREATE INDEX idx_papers_fields ON papers USING gin(fields_of_study);
CREATE INDEX idx_papers_search ON papers USING gin(search_vector);
```

### Redis

```bash
# Increase max memory in redis.conf
maxmemory 2gb
maxmemory-policy allkeys-lru
```

---

## Security Checklist

- [ ] Change all default passwords
- [ ] Use strong SECRET_KEY
- [ ] Enable HTTPS in production
- [ ] Set up firewall rules
- [ ] Enable rate limiting
- [ ] Regular backups
- [ ] Keep dependencies updated
- [ ] Monitor error logs
- [ ] Use environment variables (never commit secrets)
- [ ] Enable CORS only for trusted domains

---

## Backup Strategy

```bash
# Backup PostgreSQL
docker-compose exec -T postgres pg_dump -U researchnow researchnow > backup.sql

# Backup MinIO (papers)
docker-compose exec minio mc mirror /data /backup

# Backup Qdrant (vectors)
docker cp researchnow-qdrant:/qdrant/storage ./qdrant_backup

# Restore PostgreSQL
cat backup.sql | docker-compose exec -T postgres psql -U researchnow researchnow
```

---

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## License

MIT License - see [LICENSE](../LICENSE) file for details.

---

**Happy researching! ✨**