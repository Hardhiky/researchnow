# ResearchNow API Documentation 

Complete API documentation for the ResearchNow backend.

**Base URL**: `http://localhost:8000/api/v1`  
**Production URL**: `https://api.researchnow.app/api/v1`

---

## Table of Contents

1. [Authentication](#authentication)
2. [Papers API](#papers-api)
3. [Search API](#search-api)
4. [Summaries API](#summaries-api)
5. [Sources API](#sources-api)
6. [Users API](#users-api)
7. [Error Handling](#error-handling)
8. [Rate Limiting](#rate-limiting)

---

## Authentication

Currently, most endpoints are **publicly accessible**. For authenticated endpoints (bookmarks, collections), include an API key:

```bash
curl -H "X-API-Key: your_api_key" \
  https://api.researchnow.app/api/v1/protected-endpoint
```

---

## Papers API

### Get Papers (Paginated)

```http
GET /api/v1/papers
```

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `page` | integer | 1 | Page number |
| `page_size` | integer | 20 | Items per page (max 100) |
| `sort_by` | string | publication_date | Sort field |
| `sort_order` | string | desc | Sort order (asc/desc) |
| `open_access_only` | boolean | false | Filter open access papers |
| `has_full_text` | boolean | false | Filter papers with full text |

**Example Request:**

```bash
curl "http://localhost:8000/api/v1/papers?page=1&page_size=20&open_access_only=true"
```

**Example Response:**

```json
{
  "papers": [
    {
      "id": 1,
      "doi": "10.48550/arXiv.1706.03762",
      "arxiv_id": "1706.03762",
      "title": "Attention Is All You Need",
      "abstract": "The dominant sequence transduction models...",
      "authors": ["Ashish Vaswani", "Noam Shazeer", "Niki Parmar"],
      "publication_date": "2017-06-12",
      "publication_year": 2017,
      "journal": "NeurIPS",
      "fields_of_study": ["Computer Science", "Machine Learning"],
      "citation_count": 85420,
      "is_open_access": true,
      "pdf_url": "https://arxiv.org/pdf/1706.03762.pdf",
      "html_url": "https://arxiv.org/abs/1706.03762",
      "has_full_text": true,
      "primary_source": "arxiv"
    }
  ],
  "total": 1542,
  "page": 1,
  "page_size": 20,
  "has_next": true,
  "has_prev": false
}
```

---

### Get Paper by ID

```http
GET /api/v1/papers/{paper_id}
```

**Example Request:**

```bash
curl "http://localhost:8000/api/v1/papers/1"
```

**Example Response:**

```json
{
  "id": 1,
  "doi": "10.48550/arXiv.1706.03762",
  "arxiv_id": "1706.03762",
  "title": "Attention Is All You Need",
  "abstract": "The dominant sequence transduction models...",
  "authors": ["Ashish Vaswani", "Noam Shazeer"],
  "publication_date": "2017-06-12",
  "publication_year": 2017,
  "journal": "NeurIPS",
  "fields_of_study": ["Computer Science", "Machine Learning"],
  "keywords": ["transformer", "attention", "neural networks"],
  "citation_count": 85420,
  "reference_count": 42,
  "influential_citation_count": 12534,
  "is_open_access": true,
  "pdf_url": "https://arxiv.org/pdf/1706.03762.pdf",
  "html_url": "https://arxiv.org/abs/1706.03762",
  "has_full_text": true,
  "summary_available": true,
  "primary_source": "arxiv",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

---

### Get Paper by DOI

```http
GET /api/v1/papers/doi/{doi}
```

**Example Request:**

```bash
curl "http://localhost:8000/api/v1/papers/doi/10.48550/arXiv.1706.03762"
```

---

### Get Paper by arXiv ID

```http
GET /api/v1/papers/arxiv/{arxiv_id}
```

**Example Request:**

```bash
curl "http://localhost:8000/api/v1/papers/arxiv/1706.03762"
```

---

### Get Paper Citations

```http
GET /api/v1/papers/{paper_id}/citations
```

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `page` | integer | 1 | Page number |
| `page_size` | integer | 20 | Items per page |

**Example Request:**

```bash
curl "http://localhost:8000/api/v1/papers/1/citations?page=1&page_size=20"
```

---

### Get Paper References

```http
GET /api/v1/papers/{paper_id}/references
```

**Example Request:**

```bash
curl "http://localhost:8000/api/v1/papers/1/references"
```

---

### Get Related Papers

```http
GET /api/v1/papers/{paper_id}/related
```

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `limit` | integer | 10 | Max results (max 50) |
| `method` | string | semantic | Recommendation method |

**Methods:**
- `semantic` - Vector similarity
- `citations` - Similar citation patterns
- `co-citations` - Frequently cited together

**Example Request:**

```bash
curl "http://localhost:8000/api/v1/papers/1/related?limit=10&method=semantic"
```

---

### Get Trending Papers

```http
GET /api/v1/papers/trending/
```

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `days` | integer | 7 | Time window (1-30) |
| `field` | string | null | Field of study filter |
| `limit` | integer | 20 | Max results |

**Example Request:**

```bash
curl "http://localhost:8000/api/v1/papers/trending/?days=7&limit=20"
```

---

### Get Recent Papers

```http
GET /api/v1/papers/recent/
```

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `field` | string | null | Field of study filter |
| `source` | string | null | Source filter (arxiv, pubmed, etc.) |
| `limit` | integer | 20 | Max results |

**Example Request:**

```bash
curl "http://localhost:8000/api/v1/papers/recent/?field=Computer%20Science&limit=20"
```

---

### Get Popular Papers

```http
GET /api/v1/papers/popular/
```

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `time_period` | string | all | Time period (week, month, year, all) |
| `field` | string | null | Field of study filter |
| `limit` | integer | 20 | Max results |

**Example Request:**

```bash
curl "http://localhost:8000/api/v1/papers/popular/?time_period=year&limit=20"
```

---

## Search API

### Search Papers

```http
GET /api/v1/search
```

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `q` | string | required | Search query |
| `page` | integer | 1 | Page number |
| `page_size` | integer | 20 | Items per page |
| `field` | string | null | Field of study filter |
| `year_from` | integer | null | Publication year from |
| `year_to` | integer | null | Publication year to |
| `open_access_only` | boolean | false | Filter open access |
| `sort_by` | string | relevance | Sort field |

**Example Request:**

```bash
curl "http://localhost:8000/api/v1/search?q=machine+learning&field=Computer+Science&year_from=2020&open_access_only=true"
```

**Example Response:**

```json
{
  "results": [
    {
      "id": 1,
      "title": "Deep Learning for Natural Language Processing",
      "authors": ["John Doe", "Jane Smith"],
      "abstract": "We present a novel approach...",
      "publication_year": 2021,
      "citation_count": 1234,
      "relevance_score": 0.95,
      "highlights": [
        "We present a novel <mark>machine learning</mark> approach",
        "Our method achieves state-of-the-art results"
      ]
    }
  ],
  "total": 45123,
  "page": 1,
  "page_size": 20,
  "query": "machine learning",
  "filters": {
    "field": "Computer Science",
    "year_from": 2020,
    "open_access_only": true
  }
}
```

---

### Semantic Search

```http
POST /api/v1/search/semantic
```

**Request Body:**

```json
{
  "query": "How do transformers work in neural networks?",
  "limit": 10,
  "min_score": 0.7
}
```

**Example Request:**

```bash
curl -X POST "http://localhost:8000/api/v1/search/semantic" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "How do transformers work in neural networks?",
    "limit": 10
  }'
```

**Example Response:**

```json
{
  "results": [
    {
      "id": 1,
      "title": "Attention Is All You Need",
      "similarity_score": 0.92,
      "abstract": "The dominant sequence transduction models..."
    }
  ],
  "total": 10,
  "query": "How do transformers work in neural networks?"
}
```

---

### Search Suggestions

```http
GET /api/v1/search/suggestions
```

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `q` | string | Partial query |
| `limit` | integer | Max suggestions (default 5) |

**Example Request:**

```bash
curl "http://localhost:8000/api/v1/search/suggestions?q=machine+lear&limit=5"
```

**Example Response:**

```json
{
  "suggestions": [
    "machine learning",
    "machine learning algorithms",
    "machine learning applications",
    "machine learning theory",
    "machine learning for nlp"
  ]
}
```

---

## Summaries API

### Get Paper Summary

```http
GET /api/v1/papers/{paper_id}/summary
```

**Example Request:**

```bash
curl "http://localhost:8000/api/v1/papers/1/summary"
```

**Example Response:**

```json
{
  "id": 1,
  "paper_id": 1,
  "executive_summary": "This paper introduces the Transformer architecture, which relies entirely on attention mechanisms and eliminates recurrent layers, achieving superior performance on translation tasks.",
  "detailed_summary": "The paper presents a novel neural network architecture called the Transformer that relies entirely on self-attention mechanisms to compute representations of input and output sequences. Unlike previous models that use recurrent or convolutional layers, the Transformer allows for significantly more parallelization and can reach state-of-the-art results in translation quality after training for as little as twelve hours on eight GPUs.",
  "simplified_summary": "Imagine trying to translate a sentence from English to French. Old methods looked at one word at a time, which was slow. This paper introduces a new way called 'Transformers' that can look at all words at once, making it much faster and more accurate. It's like reading the whole sentence before translating, rather than word by word.",
  "key_findings": [
    "Transformers eliminate the need for recurrent layers in sequence modeling",
    "Self-attention mechanisms can capture long-range dependencies more effectively",
    "The model achieves SOTA results on WMT translation tasks",
    "Training is significantly faster due to increased parallelization"
  ],
  "main_claims": [
    "Attention mechanisms alone are sufficient for sequence transduction",
    "The proposed architecture is more parallelizable than RNN-based models",
    "Transformers generalize better to longer sequences"
  ],
  "methodology_summary": "The authors propose a sequence-to-sequence model based entirely on attention mechanisms. The architecture uses stacked self-attention and point-wise fully connected layers for both encoder and decoder. Multi-head attention allows the model to jointly attend to information from different representation subspaces.",
  "results_summary": "The Transformer achieves 28.4 BLEU on WMT 2014 English-to-German translation, improving over existing best results by over 2 BLEU. On WMT 2014 English-to-French translation, the model achieves a BLEU score of 41.8 after training for 3.5 days on 8 GPUs.",
  "limitations": [
    "Computational cost increases quadratically with sequence length",
    "Limited evaluation on tasks beyond translation",
    "Requires large amounts of training data"
  ],
  "highlights": [
    "Revolutionary architecture that eliminates recurrence",
    "Achieves state-of-the-art translation results",
    "Enables massively parallel training",
    "Foundation for modern NLP models like BERT and GPT"
  ],
  "research_questions": [
    "Can attention mechanisms alone replace recurrent layers?",
    "How does self-attention compare to RNNs for long sequences?"
  ],
  "auto_tags": [
    "transformer",
    "attention mechanism",
    "neural machine translation",
    "deep learning",
    "nlp"
  ],
  "difficulty_level": "advanced",
  "reading_time_minutes": 25,
  "model_used": "llama2:70b",
  "quality_score": 0.92,
  "status": "completed",
  "created_at": "2024-01-15T10:35:00Z"
}
```

---

### Generate Summary

```http
POST /api/v1/papers/{paper_id}/summary
```

**Request Body:**

```json
{
  "model": "llama",
  "regenerate": false
}
```

**Models:**
- `llama` - Llama 70B (recommended)
- `aella` - AELLA-Qwen

**Example Request:**

```bash
curl -X POST "http://localhost:8000/api/v1/papers/1/summary" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "llama",
    "regenerate": false
  }'
```

**Response:** Same as Get Summary endpoint

---

### Submit Summary Feedback

```http
POST /api/v1/papers/{paper_id}/feedback
```

**Request Body:**

```json
{
  "helpful": true,
  "comment": "Great summary, very clear!"
}
```

**Example Request:**

```bash
curl -X POST "http://localhost:8000/api/v1/papers/1/feedback" \
  -H "Content-Type: application/json" \
  -d '{
    "helpful": true,
    "comment": "Very helpful summary"
  }'
```

**Example Response:**

```json
{
  "message": "Feedback submitted successfully"
}
```

---

## Sources API

### Get Available Sources

```http
GET /api/v1/sources
```

**Example Request:**

```bash
curl "http://localhost:8000/api/v1/sources"
```

**Example Response:**

```json
{
  "sources": [
    {
      "id": "arxiv",
      "name": "arXiv",
      "description": "Open access preprint repository",
      "paper_count": 2000000,
      "has_full_text": true,
      "is_active": true,
      "last_sync": "2024-01-15T08:00:00Z"
    },
    {
      "id": "pubmed",
      "name": "PubMed Central",
      "description": "Biomedical and life sciences literature",
      "paper_count": 6000000,
      "has_full_text": true,
      "is_active": true,
      "last_sync": "2024-01-15T07:30:00Z"
    },
    {
      "id": "semantic_scholar",
      "name": "Semantic Scholar",
      "description": "AI-powered research tool",
      "paper_count": 200000000,
      "has_full_text": false,
      "is_active": true,
      "last_sync": "2024-01-15T09:00:00Z"
    }
  ]
}
```

---

### Get Source Statistics

```http
GET /api/v1/sources/{source_id}/stats
```

**Example Request:**

```bash
curl "http://localhost:8000/api/v1/sources/arxiv/stats"
```

**Example Response:**

```json
{
  "source_id": "arxiv",
  "total_papers": 2000000,
  "papers_with_full_text": 2000000,
  "recent_papers_24h": 543,
  "recent_papers_7d": 3821,
  "most_common_fields": [
    "Computer Science",
    "Physics",
    "Mathematics"
  ],
  "last_sync": "2024-01-15T08:00:00Z",
  "sync_status": "healthy"
}
```

---

## Users API

### Create Anonymous User (Optional)

```http
POST /api/v1/users/anonymous
```

**Example Response:**

```json
{
  "user_id": 123,
  "anonymous_id": "anon_abc123xyz",
  "is_anonymous": true,
  "created_at": "2024-01-15T10:00:00Z"
}
```

---

### Get User Bookmarks

```http
GET /api/v1/users/me/bookmarks
```

**Headers:** `X-API-Key: your_api_key`

**Example Response:**

```json
{
  "bookmarks": [
    {
      "id": 1,
      "paper_id": 1,
      "paper_title": "Attention Is All You Need",
      "notes": "Important for my research",
      "tags": ["transformer", "must-read"],
      "created_at": "2024-01-15T09:00:00Z"
    }
  ],
  "total": 15
}
```

---

### Add Bookmark

```http
POST /api/v1/users/me/bookmarks
```

**Request Body:**

```json
{
  "paper_id": 1,
  "notes": "Important for my research",
  "tags": ["transformer", "must-read"]
}
```

---

### Get User Collections

```http
GET /api/v1/users/me/collections
```

**Example Response:**

```json
{
  "collections": [
    {
      "id": 1,
      "name": "Machine Learning Papers",
      "description": "My ML reading list",
      "paper_count": 23,
      "is_public": false,
      "created_at": "2024-01-10T10:00:00Z"
    }
  ]
}
```

---

## Error Handling

All errors follow this format:

```json
{
  "error": "error_code",
  "message": "Human-readable error message",
  "detail": "Additional details (only in debug mode)",
  "status_code": 400
}
```

### Common Error Codes

| Code | Status | Description |
|------|--------|-------------|
| `paper_not_found` | 404 | Paper doesn't exist |
| `invalid_parameter` | 400 | Invalid query parameter |
| `rate_limit_exceeded` | 429 | Too many requests |
| `unauthorized` | 401 | Authentication required |
| `forbidden` | 403 | Insufficient permissions |
| `internal_error` | 500 | Server error |
| `service_unavailable` | 503 | Service temporarily down |

**Example Error Response:**

```json
{
  "error": "paper_not_found",
  "message": "Paper with ID 99999 not found",
  "status_code": 404
}
```

---

## Rate Limiting

**Default Limits:**
- **Per Minute**: 60 requests
- **Per Hour**: 1000 requests

**Headers:**

```
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1705315200
```

**Rate Limit Exceeded Response:**

```json
{
  "error": "rate_limit_exceeded",
  "message": "Rate limit exceeded. Try again in 30 seconds.",
  "retry_after": 30,
  "status_code": 429
}
```

---

## Pagination

All list endpoints support pagination with consistent parameters:

- `page` - Page number (starting from 1)
- `page_size` - Items per page (default 20, max 100)

**Response includes:**

```json
{
  "results": [...],
  "total": 1000,
  "page": 1,
  "page_size": 20,
  "has_next": true,
  "has_prev": false
}
```

---

## Sorting

Supported sort fields:
- `publication_date` (default)
- `citation_count`
- `title`
- `relevance` (for search)

**Example:**

```bash
curl "http://localhost:8000/api/v1/papers?sort_by=citation_count&sort_order=desc"
```

---

## Filtering

Common filters across endpoints:

| Filter | Type | Description |
|--------|------|-------------|
| `field` | string | Field of study |
| `year_from` | integer | Min publication year |
| `year_to` | integer | Max publication year |
| `open_access_only` | boolean | Only OA papers |
| `has_full_text` | boolean | Only papers with full text |
| `source` | string | Source filter (arxiv, pubmed, etc.) |

---

## SDK Examples

### Python

```python
import requests

BASE_URL = "http://localhost:8000/api/v1"

# Search papers
response = requests.get(f"{BASE_URL}/search", params={
    "q": "machine learning",
    "page_size": 10,
    "open_access_only": True
})
papers = response.json()

# Get paper summary
paper_id = papers["results"][0]["id"]
summary = requests.get(f"{BASE_URL}/papers/{paper_id}/summary").json()

print(summary["simplified_summary"])
```

### JavaScript/TypeScript

```javascript
const BASE_URL = "http://localhost:8000/api/v1";

// Search papers
const searchPapers = async (query) => {
  const response = await fetch(
    `${BASE_URL}/search?q=${encodeURIComponent(query)}&page_size=10`
  );
  return response.json();
};

// Get paper summary
const getPaperSummary = async (paperId) => {
  const response = await fetch(`${BASE_URL}/papers/${paperId}/summary`);
  return response.json();
};

// Usage
const papers = await searchPapers("machine learning");
const summary = await getPaperSummary(papers.results[0].id);
console.log(summary.simplified_summary);
```

### cURL

```bash
# Search papers
curl "http://localhost:8000/api/v1/search?q=machine+learning&page_size=10"

# Get paper by ID
curl "http://localhost:8000/api/v1/papers/1"

# Get paper summary
curl "http://localhost:8000/api/v1/papers/1/summary"

# Generate new summary
curl -X POST "http://localhost:8000/api/v1/papers/1/summary" \
  -H "Content-Type: application/json" \
  -d '{"model": "llama"}'
```

---

## Webhooks (Coming Soon)

Subscribe to events:
- `paper.created` - New paper added
- `summary.completed` - Summary generated
- `paper.updated` - Paper metadata updated

---

## GraphQL API (Coming Soon)

GraphQL endpoint will be available at:
```
POST /api/v1/graphql
```

---

## WebSocket API (Coming Soon)

Real-time updates:
```
ws://localhost:8000/api/v1/ws
```

---

## Support

- **Documentation**: https://docs.researchnow.app
- **Issues**: https://github.com/yourusername/ResearchNow/issues
- **Email**: api-support@researchnow.app

---

## Changelog

### v1.0.0 (2024-01-15)
- Initial API release
- Paper search and retrieval
- AI summarization
- Multiple source support

---

**Happy coding! **