# Advanced RAG API - Deployment Guide

Complete guide for deploying the Advanced RAG API in different environments: local development, Docker, and cloud platforms.

---

## Table of Contents

1. [Local Development Setup](#local-development-setup)
2. [Docker Deployment](#docker-deployment)
3. [Cloud Deployment Options](#cloud-deployment-options)
4. [Production Checklist](#production-checklist)
5. [API Usage Examples](#api-usage-examples)
6. [Monitoring & Troubleshooting](#monitoring--troubleshooting)

---

## Local Development Setup

### Prerequisites

- Python 3.10+
- pip or poetry
- Git
- OpenAI API key
- Pinecone API key (optional, for vector search)
- Cohere API key (optional, for reranking)

### Installation Steps

#### 1. Clone Repository

```bash
git clone <repository-url>
cd week3/advanced-rag-system
```

#### 2. Create Virtual Environment

**Linux/macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

#### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

For development (with testing tools):
```bash
pip install -r requirements.txt
pip install pytest pytest-cov black flake8
```

#### 4. Setup Environment Variables

```bash
# Copy example file
cp .env.example .env

# Edit .env with your actual values
# Required:
API_KEY=your-secure-api-key
OPENAI_API_KEY=sk-...
PINECONE_API_KEY=...
PINECONE_ENV=...
PINECONE_INDEX=...

# Optional:
COHERE_API_KEY=...
LOG_LEVEL=INFO
```

#### 5. Run Local Server

```bash
uvicorn src.api:app --reload --port 8000
```

Server will be available at:
- API: `http://localhost:8000`
- Documentation: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

#### 6. Verify Setup

```bash
# Health check
curl http://localhost:8000/health

# Get available strategies
curl -H "X-API-Key: test-key-123" http://localhost:8000/strategies
```

### Development Commands

```bash
# Format code
black src/

# Lint code
flake8 src/

# Run tests
pytest tests/ -v --cov=src

# Check types (with mypy)
mypy src/
```

---

## Docker Deployment

### Quick Start

#### 1. Build Docker Image

```bash
docker build -t rag-api:latest .
```

#### 2. Run Container

```bash
docker run -d \
  --name rag-api \
  -p 8000:8000 \
  --env-file .env \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/logs:/app/logs \
  rag-api:latest
```

#### 3. Check Logs

```bash
docker logs -f rag-api
```

#### 4. Stop Container

```bash
docker stop rag-api
docker rm rag-api
```

### Docker Compose

Recommended for development and production.

#### 1. Create .env File

```bash
cp .env.example .env
# Edit .env with your values
```

#### 2. Start Services

```bash
# Development
docker-compose up

# Production (detached)
docker-compose up -d
```

#### 3. View Logs

```bash
docker-compose logs -f api

# View specific service
docker-compose logs -f db
docker-compose logs -f cache
```

#### 4. Stop Services

```bash
docker-compose down

# Remove volumes (clean everything)
docker-compose down -v
```

### Services Included

- **API**: FastAPI application (port 8000)
- **Database**: PostgreSQL (optional, can use SQLite)
- **Cache**: Redis (optional, for caching)
- **Nginx**: Reverse proxy (optional, for production)

### Environment Variables for Docker

Create `.env` file:

```env
# API
API_KEY=your-secure-key
OPENAI_API_KEY=sk-...
PINECONE_API_KEY=...
PINECONE_ENV=...
PINECONE_INDEX=...

# Database
DATABASE_URL=postgresql://rag_user:password@db:5432/rag_db
POSTGRES_USER=rag_user
POSTGRES_PASSWORD=secure-password
POSTGRES_DB=rag_db

# Logging
LOG_LEVEL=INFO

# Environment
ENVIRONMENT=production
```

---

## Cloud Deployment Options

### Option 1: Railway.app

Railway is the easiest way to deploy - just connect your GitHub repo.

#### 1. Create Railway Account

Visit [railway.app](https://railway.app) and sign up with GitHub.

#### 2. Create New Project

- Click "New Project"
- Select "Deploy from GitHub repo"
- Choose your repository

#### 3. Configure Environment

In Railway dashboard:
- Go to "Variables"
- Add all environment variables from `.env`

```env
API_KEY=your-secure-key
OPENAI_API_KEY=sk-...
PINECONE_API_KEY=...
# ... other variables
```

#### 4. Configure Start Command

In the Railway dashboard, set:
```
uvicorn src.api:app --host 0.0.0.0 --port 8000
```

#### 5. Deploy

Railway will automatically deploy on GitHub push.

**Deployment URL:**
```
https://your-project.railway.app
```

#### 6. View Logs

```bash
railway logs
```

#### 7. Setup Custom Domain

In Railway dashboard:
- Go to "Settings"
- Add custom domain
- Configure DNS records

---

### Option 2: Render.com

Render is a modern cloud platform with generous free tier.

#### 1. Create Render Account

Visit [render.com](https://render.com) and sign up.

#### 2. Create New Web Service

- Click "New +"
- Select "Web Service"
- Connect GitHub repository

#### 3. Configure Service

```
Name: rag-api
Region: Oregon (or nearest)
Branch: main
Runtime: Python
Build Command: pip install -r requirements.txt
Start Command: uvicorn src.api:app --host 0.0.0.0 --port 8000
```

#### 4. Add Environment Variables

- Go to "Environment"
- Add all variables:

```env
API_KEY=your-secure-key
OPENAI_API_KEY=sk-...
PINECONE_API_KEY=...
# ... other variables
```

#### 5. Deploy

Click "Deploy Service" to start deployment.

**Service URL:**
```
https://your-service.onrender.com
```

#### 6. Monitor

- Go to "Logs" tab to view logs
- Set up alerts in "Notifications"

---

### Option 3: AWS Elastic Container Service (ECS)

For larger-scale deployments on AWS.

#### 1. Create ECR Repository

```bash
# Create repository
aws ecr create-repository --repository-name rag-api

# Login to ECR
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com

# Tag and push image
docker build -t rag-api:latest .
docker tag rag-api:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/rag-api:latest
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/rag-api:latest
```

#### 2. Create ECS Cluster

```bash
aws ecs create-cluster --cluster-name rag-api-cluster
```

#### 3. Create Task Definition

Create `task-definition.json`:

```json
{
  "family": "rag-api",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "512",
  "memory": "1024",
  "containerDefinitions": [
    {
      "name": "rag-api",
      "image": "<account-id>.dkr.ecr.us-east-1.amazonaws.com/rag-api:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "hostPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "API_KEY",
          "value": "your-api-key"
        },
        {
          "name": "OPENAI_API_KEY",
          "value": "sk-..."
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/rag-api",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

Register task definition:
```bash
aws ecs register-task-definition --cli-input-json file://task-definition.json
```

#### 4. Create Service

```bash
aws ecs create-service \
  --cluster rag-api-cluster \
  --service-name rag-api-service \
  --task-definition rag-api \
  --desired-count 2 \
  --launch-type FARGATE \
  --load-balancers targetGroupArn=arn:aws:elasticloadbalancing:...,containerName=rag-api,containerPort=8000 \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-xxx],securityGroups=[sg-xxx],assignPublicIp=ENABLED}"
```

---

### Option 4: Google Cloud Run

Serverless deployment on Google Cloud.

#### 1. Install gcloud CLI

```bash
curl https://sdk.cloud.google.com | bash
gcloud init
```

#### 2. Build and Push Image

```bash
# Configure Docker with gcloud
gcloud auth configure-docker

# Build image
docker build -t gcr.io/<project-id>/rag-api:latest .

# Push to Google Container Registry
docker push gcr.io/<project-id>/rag-api:latest
```

#### 3. Deploy to Cloud Run

```bash
gcloud run deploy rag-api \
  --image gcr.io/<project-id>/rag-api:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars API_KEY=your-key,OPENAI_API_KEY=sk-... \
  --memory 1024Mi \
  --timeout 3600s
```

#### 4. Get Service URL

```bash
gcloud run services list
```

---

## Production Checklist

### ✅ Security Configuration

- [ ] Set strong `API_KEY` (minimum 32 characters)
- [ ] Store all secrets in `.env` or cloud secret manager
- [ ] Enable HTTPS/TLS
- [ ] Configure CORS for specific domains
- [ ] Set up rate limiting
- [ ] Use API key authentication
- [ ] Regular security audits
- [ ] Enable request validation and sanitization

### ✅ Environment Variables

```bash
# Verify all required variables are set
API_KEY=<secure-random-key>
OPENAI_API_KEY=<key>
PINECONE_API_KEY=<key>
PINECONE_ENV=<env>
PINECONE_INDEX=<index>
COHERE_API_KEY=<key>
DATABASE_URL=<db-connection>
LOG_LEVEL=WARNING  # Not DEBUG in production
ENVIRONMENT=production
MAX_REQUESTS_PER_MINUTE=10
MAX_QUERY_LENGTH=500
MAX_FILE_SIZE_MB=10
```

### ✅ Monitoring & Logging

- [ ] Enable structured logging
- [ ] Monitor error rates
- [ ] Track performance metrics
- [ ] Set up alerts for slow queries (>30s)
- [ ] Implement log aggregation (e.g., ELK Stack)
- [ ] Regular backup of logs and metrics
- [ ] Monitor disk space and database size

### ✅ Database Configuration

- [ ] Use PostgreSQL for production (not SQLite)
- [ ] Enable automatic backups
- [ ] Set up read replicas for high availability
- [ ] Configure connection pooling
- [ ] Monitor database performance
- [ ] Regular maintenance and vacuum

### ✅ Caching & Performance

- [ ] Enable Redis caching
- [ ] Configure cache TTL
- [ ] Monitor cache hit rates
- [ ] Enable gzip compression
- [ ] CDN for static content
- [ ] Connection pooling

### ✅ Backup & Disaster Recovery

- [ ] Daily automated backups
- [ ] Test backup restoration
- [ ] Keep backups in separate region
- [ ] Document recovery procedures
- [ ] Backup retention policy (30 days minimum)

### ✅ API Gateway / Load Balancing

- [ ] Use reverse proxy (nginx)
- [ ] Load balance across multiple instances
- [ ] SSL/TLS termination
- [ ] Rate limiting at gateway level
- [ ] DDoS protection

### ✅ Scaling Configuration

```yaml
# Auto-scaling rules
min_instances: 2
max_instances: 10
target_cpu_utilization: 70%
target_memory_utilization: 80%
scale_up_threshold: 75%
scale_down_threshold: 25%
```

### ✅ Health & Readiness Checks

```bash
# Health check endpoint
GET /health

# Expected response
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:45.123456"
}
```

### ✅ Incident Response Plan

- [ ] Document on-call procedures
- [ ] Create runbooks for common issues
- [ ] Set up alert channels (Slack, PagerDuty)
- [ ] Regular incident drills
- [ ] Post-incident reviews

---

## API Usage Examples

### cURL Examples

#### 1. Health Check

```bash
curl -X GET http://localhost:8000/health
```

Response:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:45.123456",
  "version": "1.0.0"
}
```

#### 2. List Available Strategies

```bash
curl -X GET http://localhost:8000/strategies \
  -H "X-API-Key: test-key-123"
```

Response:
```json
{
  "strategies": ["basic", "rewritten", "multi_query", "hyde", "hybrid_rerank"],
  "descriptions": {
    "basic": "Simple vector similarity search",
    "rewritten": "Query rewritten by GPT-4 before retrieval",
    ...
  }
}
```

#### 3. Query Documents

```bash
curl -X POST http://localhost:8000/query \
  -H "X-API-Key: test-key-123" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is machine learning?",
    "strategy": "hybrid_rerank",
    "conversation_id": "conv_123",
    "num_results": 5
  }'
```

Response:
```json
{
  "answer": "Machine learning is...",
  "sources": [
    {
      "content": "...",
      "metadata": {...}
    }
  ],
  "metadata": {
    "strategy": "hybrid_rerank",
    "response_time_seconds": 2.345,
    "cost": 0.0045
  },
  "status": "success",
  "timestamp": "2024-01-15T10:30:45.123456"
}
```

#### 4. Upload Documents

```bash
curl -X POST http://localhost:8000/upload \
  -H "X-API-Key: test-key-123" \
  -F "files=@document1.pdf" \
  -F "files=@document2.txt"
```

Response:
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
    },
    {
      "filename": "document2.txt",
      "size_mb": 0.05,
      "content_type": "text/plain",
      "status": "uploaded"
    }
  ],
  "timestamp": "2024-01-15T10:30:45.123456"
}
```

### Python Client Example

```python
import requests
import json

BASE_URL = "http://localhost:8000"
API_KEY = "test-key-123"

class RAGClient:
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url
        self.headers = {"X-API-Key": api_key}
    
    def health_check(self):
        """Check API health"""
        response = requests.get(f"{self.base_url}/health")
        return response.json()
    
    def get_strategies(self):
        """List available strategies"""
        response = requests.get(
            f"{self.base_url}/strategies",
            headers=self.headers
        )
        return response.json()
    
    def query(self, query: str, strategy: str = "hybrid_rerank", num_results: int = 5):
        """Query documents"""
        payload = {
            "query": query,
            "strategy": strategy,
            "num_results": num_results
        }
        response = requests.post(
            f"{self.base_url}/query",
            json=payload,
            headers=self.headers
        )
        return response.json()
    
    def upload(self, file_paths: list):
        """Upload documents"""
        files = [("files", open(path, "rb")) for path in file_paths]
        response = requests.post(
            f"{self.base_url}/upload",
            files=files,
            headers=self.headers
        )
        return response.json()

# Usage
client = RAGClient(BASE_URL, API_KEY)

# Check health
print(client.health_check())

# List strategies
print(client.get_strategies())

# Query
result = client.query("What is machine learning?", strategy="hybrid_rerank")
print(f"Answer: {result['answer']}")
print(f"Sources: {len(result['sources'])} documents")

# Upload
result = client.upload(["doc1.pdf", "doc2.txt"])
print(f"Uploaded: {result['documents_added']} documents")
```

### JavaScript/Fetch Example

```javascript
const BASE_URL = "http://localhost:8000";
const API_KEY = "test-key-123";

class RAGClient {
    constructor(baseUrl, apiKey) {
        this.baseUrl = baseUrl;
        this.headers = {
            "X-API-Key": apiKey,
            "Content-Type": "application/json"
        };
    }

    async healthCheck() {
        const response = await fetch(`${this.baseUrl}/health`);
        return response.json();
    }

    async getStrategies() {
        const response = await fetch(`${this.baseUrl}/strategies`, {
            headers: this.headers
        });
        return response.json();
    }

    async query(query, strategy = "hybrid_rerank", numResults = 5) {
        const payload = {
            query: query,
            strategy: strategy,
            num_results: numResults
        };

        const response = await fetch(`${this.baseUrl}/query`, {
            method: "POST",
            headers: this.headers,
            body: JSON.stringify(payload)
        });

        if (!response.ok) {
            throw new Error(`API error: ${response.statusText}`);
        }

        return response.json();
    }

    async upload(files) {
        const formData = new FormData();
        files.forEach(file => {
            formData.append("files", file);
        });

        const response = await fetch(`${this.baseUrl}/upload`, {
            method: "POST",
            headers: { "X-API-Key": API_KEY },
            body: formData
        });

        return response.json();
    }
}

// Usage
const client = new RAGClient(BASE_URL, API_KEY);

// Check health
client.healthCheck().then(result => console.log(result));

// Query
client.query("What is machine learning?")
    .then(result => {
        console.log(`Answer: ${result.answer}`);
        console.log(`Sources: ${result.sources.length}`);
    })
    .catch(error => console.error(error));

// Upload
const fileInput = document.getElementById('fileInput');
client.upload(fileInput.files)
    .then(result => console.log(`Uploaded: ${result.documents_added} documents`));
```

---

## Monitoring & Troubleshooting

### View Logs

#### Docker
```bash
docker logs -f rag-api
```

#### Docker Compose
```bash
docker-compose logs -f api
```

#### Local
```bash
tail -f logs/app.log
cat logs/errors.log
```

### Common Issues

#### 1. API Key Authentication Failed

```bash
# Error: 401 Unauthorized
# Solution: Make sure X-API-Key header is correct

curl -H "X-API-Key: correct-key" http://localhost:8000/strategies
```

#### 2. Rate Limit Exceeded

```bash
# Error: 429 Too Many Requests
# Solution: Wait before sending more requests, or increase MAX_REQUESTS_PER_MINUTE
```

#### 3. Database Connection Error

```bash
# Check if PostgreSQL is running
docker-compose ps

# View database logs
docker-compose logs db

# Reset database
docker-compose down -v
docker-compose up
```

#### 4. Out of Memory

```bash
# Increase memory in docker-compose.yml
# Or adjust Python garbage collection

# Monitor memory usage
docker stats rag-api
```

#### 5. Slow Queries

Check logs for queries > 30 seconds:
```bash
grep "Slow query" logs/app.log
```

### Performance Optimization

#### 1. Database Indexing

```sql
-- Add indexes for better query performance
CREATE INDEX idx_conversation_id ON conversations(id);
CREATE INDEX idx_query_timestamp ON queries(timestamp);
```

#### 2. Caching Strategy

```python
# Enable Redis caching in production
CACHE_TTL = 3600  # 1 hour
```

#### 3. Load Testing

```bash
# Install locust
pip install locust

# Run load test
locust -f tests/load_test.py --host=http://localhost:8000
```

---

## Support & Resources

- **Documentation**: http://localhost:8000/docs
- **GitHub Issues**: [Report bugs](https://github.com/...)
- **Email**: support@example.com
- **Slack Channel**: #rag-api-support

---

**Last Updated**: January 2024
**Version**: 1.0.0
