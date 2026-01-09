# Advanced RAG API - Setup & Quick Reference

Complete quick reference for the REST API setup, running, and using the Advanced RAG system.

---

## 📋 Quick Start (5 Minutes)

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env and set your API_KEY and OpenAI credentials
```

### 3. Run API Server

```bash
uvicorn src.api:app --reload --port 8000
```

### 4. Test API

```bash
# Health check
curl http://localhost:8000/health

# View interactive docs
# Open: http://localhost:8000/docs
```

---

## 🔑 API Key Setup

### Generate API Key

```bash
# Generate a secure API key (use in production)
python -c "import secrets; print(secrets.token_hex(32))"
```

### Set API Key in .env

```env
API_KEY=your_generated_key_here
```

### Use API Key in Requests

All endpoints except `/health` require the `X-API-Key` header:

```bash
curl -H "X-API-Key: your_api_key" http://localhost:8000/strategies
```

---

## 📚 API Endpoints

### 1. Health Check

**Endpoint:** `GET /health`

No authentication required.

```bash
curl http://localhost:8000/health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:45.123456",
  "version": "1.0.0"
}
```

---

### 2. List Strategies

**Endpoint:** `GET /strategies`

Requires: `X-API-Key` header

```bash
curl -H "X-API-Key: your_api_key" http://localhost:8000/strategies
```

**Response:**
```json
{
  "strategies": ["basic", "rewritten", "multi_query", "hyde", "hybrid_rerank"],
  "descriptions": {
    "basic": "Simple vector similarity search",
    "rewritten": "Query rewritten by GPT-4 before retrieval",
    "multi_query": "Multiple query variations for broader coverage",
    "hyde": "Hypothetical document embeddings",
    "hybrid_rerank": "Combined hybrid search with semantic reranking"
  }
}
```

---

### 3. Query Documents

**Endpoint:** `POST /query`

Requires: `X-API-Key` header

**Request:**
```json
{
  "query": "What is machine learning?",
  "strategy": "hybrid_rerank",
  "num_results": 5,
  "conversation_id": "optional_conv_id"
}
```

**Query Parameters:**
- `query` (required): Search query (max 500 characters)
- `strategy` (optional): Retrieval strategy
  - `basic`: Simple vector search (fastest)
  - `rewritten`: Query rewriting with GPT-4
  - `multi_query`: Multiple variations
  - `hyde`: Hypothetical documents
  - `hybrid_rerank`: Best results (slowest, most accurate)
- `num_results` (optional): Number of results (1-20, default 5)
- `conversation_id` (optional): For context preservation

**Example:**
```bash
curl -X POST http://localhost:8000/query \
  -H "X-API-Key: your_api_key" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is machine learning?",
    "strategy": "hybrid_rerank",
    "num_results": 5
  }'
```

**Response:**
```json
{
  "answer": "Machine learning is a subset of artificial intelligence...",
  "sources": [
    {
      "content": "...",
      "metadata": {
        "filename": "document.pdf",
        "page": 1
      }
    }
  ],
  "metadata": {
    "strategy": "hybrid_rerank",
    "num_results": 5,
    "response_time_seconds": 2.345,
    "conversation_id": null,
    "cost": 0.0045
  },
  "status": "success",
  "timestamp": "2024-01-15T10:30:45.123456"
}
```

---

### 4. Upload Documents

**Endpoint:** `POST /upload`

Requires: `X-API-Key` header

Supported formats: PDF, TXT, DOCX (max 10MB each)

**Example:**
```bash
curl -X POST http://localhost:8000/upload \
  -H "X-API-Key: your_api_key" \
  -F "files=@document1.pdf" \
  -F "files=@document2.txt"
```

**Response:**
```json
{
  "status": "success",
  "documents_added": 2,
  "file_details": [
    {
      "filename": "document1.pdf",
      "size_mb": 1.5,
      "content_type": "application/pdf",
      "status": "uploaded"
    }
  ],
  "timestamp": "2024-01-15T10:30:45.123456"
}
```

---

## 🐳 Docker Setup

### Run with Docker

**Build:**
```bash
docker build -t rag-api:latest .
```

**Run:**
```bash
docker run -d \
  --name rag-api \
  -p 8000:8000 \
  --env-file .env \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/logs:/app/logs \
  rag-api:latest
```

**View logs:**
```bash
docker logs -f rag-api
```

---

### Docker Compose (Recommended)

**Start:**
```bash
docker-compose up -d
```

**Stop:**
```bash
docker-compose down
```

**View logs:**
```bash
docker-compose logs -f api
```

Services:
- API (port 8000)
- PostgreSQL (database)
- Redis (cache)

---

## 📊 Monitoring

### View Logs

**Real-time logs:**
```bash
tail -f logs/app.log
```

**Error logs:**
```bash
cat logs/errors.log
```

**Metrics:**
```bash
cat logs/metrics.json
```

### Log Format

Logs are in JSON format for easy parsing:

```json
{
  "timestamp": "2024-01-15T10:30:45.123456",
  "level": "INFO",
  "logger": "rag_api",
  "message": "Query processed successfully (2.34s)",
  "module": "api",
  "function": "query_documents",
  "strategy": "hybrid_rerank",
  "response_time": 2.34
}
```

---

## ⚙️ Configuration Files

### Environment Variables (.env)

```env
# API Authentication
API_KEY=your_secure_api_key_here

# API Settings
MAX_REQUESTS_PER_MINUTE=10
MAX_QUERY_LENGTH=500
MAX_FILE_SIZE_MB=10

# Keys
OPENAI_API_KEY=sk-...
PINECONE_API_KEY=...
PINECONE_ENV=...
PINECONE_INDEX=...
COHERE_API_KEY=...

# Logging
LOG_LEVEL=INFO
LOG_DIR=logs

# Database
DATABASE_URL=sqlite:///./data/rag.db

# Server
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
ENVIRONMENT=development
```

---

## 🔒 Security

### Rate Limiting

- **Limit:** 10 requests per minute per API key
- **Burst:** Up to 20 requests allowed with backoff
- **Status Code:** 429 Too Many Requests when exceeded

### Input Validation

- **Query length:** Max 500 characters
- **File size:** Max 10MB per file
- **File types:** PDF, TXT, DOCX only

### API Key Security

✅ Store API key in `.env` file
✅ Never commit `.env` to version control
✅ Use strong, random API keys (32+ characters)
✅ Rotate keys regularly
✅ Use environment variables or secret manager in production

---

## 🧪 Testing

### Verify Setup

```bash
python verify_api.py
```

This script checks:
- Configuration files
- Required packages
- API running
- Health check
- Authentication
- Available strategies

### Manual Testing

```bash
# Test 1: Health check
curl http://localhost:8000/health

# Test 2: Strategies (requires API key)
curl -H "X-API-Key: test-key-123" http://localhost:8000/strategies

# Test 3: Query (requires API key)
curl -X POST http://localhost:8000/query \
  -H "X-API-Key: test-key-123" \
  -H "Content-Type: application/json" \
  -d '{"query": "test"}'

# Test 4: Rate limiting
# Make 11 requests in quick succession and observe 429 response
```

---

## 📖 Interactive Documentation

Access the interactive API documentation:

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
- **OpenAPI JSON:** http://localhost:8000/openapi.json

These provide:
- Complete endpoint documentation
- Request/response schemas
- "Try it out" functionality
- Example requests and responses

---

## 🚀 Deployment

For cloud deployment options, see [DEPLOYMENT.md](DEPLOYMENT.md):

- **Local Development:** uvicorn + SQLite
- **Docker:** Single container
- **Docker Compose:** Multi-service (API, DB, Cache)
- **Railway:** Simple cloud deployment
- **Render:** Modern cloud platform
- **AWS ECS:** Enterprise-scale deployment
- **Google Cloud Run:** Serverless option

---

## 🐛 Troubleshooting

### API Won't Start

**Error:** `Address already in use: ('0.0.0.0', 8000)`

**Solution:**
```bash
# Find process using port 8000
lsof -i :8000

# Kill process
kill -9 <PID>

# Or use different port
uvicorn src.api:app --port 8001
```

### 401 Unauthorized

**Error:** `"API key required. Provide X-API-Key header"`

**Solution:** Add `X-API-Key` header to your request

```bash
curl -H "X-API-Key: your_api_key" http://localhost:8000/strategies
```

### 429 Too Many Requests

**Error:** `"Rate limit exceeded. Max 10 requests per minute"`

**Solution:** Wait before sending more requests, or increase `MAX_REQUESTS_PER_MINUTE` in `.env`

### Database Connection Error

**Error:** `"Failed to connect to database"`

**Solution:**
```bash
# Check if PostgreSQL is running (if using docker-compose)
docker-compose ps

# Reset database
docker-compose down -v
docker-compose up
```

### Slow Queries

**Check logs:**
```bash
grep "Slow query" logs/app.log
```

**Improve performance:**
1. Use `basic` strategy for faster responses
2. Reduce `num_results`
3. Enable caching (Redis)
4. Check database indexes

---

## 📞 Support

- **API Docs:** http://localhost:8000/docs
- **Deployment Guide:** [DEPLOYMENT.md](DEPLOYMENT.md)
- **README:** [README.md](README.md)
- **Issues:** Check logs in `logs/app.log`

---

## 📋 File Structure

```
advanced-rag-system/
├── src/
│   ├── api.py                 # FastAPI application
│   ├── logger_config.py       # Logging configuration
│   ├── monitoring.py          # Metrics & monitoring
│   ├── rag_pipeline.py        # RAG orchestration
│   └── ...                    # Other RAG modules
├── config/
│   ├── nginx.conf             # Production nginx config
│   └── settings.py
├── logs/
│   ├── app.log               # Application logs
│   ├── errors.log            # Error logs
│   └── metrics.json          # Metrics
├── data/
│   └── (uploaded documents)
├── .env.example              # Environment template
├── Dockerfile                # Docker image
├── docker-compose.yml        # Multi-service setup
├── DEPLOYMENT.md             # Deployment guide
├── API_SETUP.md              # This file
├── README.md                 # Project overview
└── requirements.txt          # Python dependencies
```

---

**Last Updated:** January 2024
**Version:** 1.0.0
