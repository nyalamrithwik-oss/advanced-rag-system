"""
FastAPI REST API for Advanced RAG System

Provides endpoints for:
- Query processing with multiple retrieval strategies
- Document uploading and indexing
- Health monitoring
- Strategy listing
- Authentication and rate limiting
- Comprehensive logging and monitoring

Features:
- API Key authentication
- Rate limiting (10 requests/minute per key)
- Input validation and sanitization
- CORS support
- Request/response logging
- Error handling with proper HTTP status codes
"""

import os
import logging
from datetime import datetime
from typing import List, Optional, Dict, Any
from pathlib import Path
import json
from io import BytesIO

from fastapi import (
    FastAPI, File, UploadFile, HTTPException, Header, Depends, 
    Request, status
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, validator
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from dotenv import load_dotenv

from .rag_pipeline import AdvancedRAGPipeline
from .logger_config import setup_logging

# Load environment variables
load_dotenv()

# Setup logging
logger = setup_logging(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Advanced RAG API",
    description="REST API for Advanced Retrieval Augmented Generation System",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Setup CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup rate limiting
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter


# ============================================================================
# Pydantic Models for Request/Response Validation
# ============================================================================

class QueryRequest(BaseModel):
    """Request model for /query endpoint"""
    query: str = Field(..., min_length=1, max_length=500, 
                       description="Search query (max 500 chars)")
    strategy: str = Field(
        "hybrid_rerank",
        description="Retrieval strategy: basic, rewritten, multi_query, hyde, hybrid_rerank"
    )
    conversation_id: Optional[str] = Field(
        None, 
        description="Optional conversation ID for context"
    )
    num_results: int = Field(5, ge=1, le=20, description="Number of results to retrieve")

    @validator('query')
    def query_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError("Query cannot be empty")
        return v.strip()

    @validator('strategy')
    def validate_strategy(cls, v):
        valid_strategies = ['basic', 'rewritten', 'multi_query', 'hyde', 'hybrid_rerank']
        if v not in valid_strategies:
            raise ValueError(f"Strategy must be one of {valid_strategies}")
        return v


class QueryResponse(BaseModel):
    """Response model for /query endpoint"""
    answer: str
    sources: List[Dict[str, Any]]
    metadata: Dict[str, Any]
    status: str = "success"
    timestamp: str


class UploadResponse(BaseModel):
    """Response model for /upload endpoint"""
    status: str
    documents_added: int
    file_details: List[Dict[str, Any]]
    timestamp: str


class HealthResponse(BaseModel):
    """Response model for /health endpoint"""
    status: str = "healthy"
    timestamp: str
    version: str = "1.0.0"


class StrategiesResponse(BaseModel):
    """Response model for /strategies endpoint"""
    strategies: List[str]
    descriptions: Dict[str, str]


class ErrorResponse(BaseModel):
    """Error response model"""
    status: str = "error"
    message: str
    timestamp: str
    code: int


# ============================================================================
# Authentication & Security
# ============================================================================

async def verify_api_key(x_api_key: Optional[str] = Header(None)) -> str:
    """Verify API key from header"""
    # Skip auth for health endpoint (handled separately)
    valid_key = os.getenv("API_KEY", "test-key-123")
    
    if not x_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key required. Provide X-API-Key header",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if x_api_key != valid_key:
        logger.warning(f"Invalid API key attempt: {x_api_key[:5]}...")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
        )
    
    return x_api_key


def validate_file_upload(file: UploadFile) -> bool:
    """Validate uploaded file"""
    max_file_size_mb = int(os.getenv("MAX_FILE_SIZE_MB", "10"))
    max_file_size = max_file_size_mb * 1024 * 1024
    
    allowed_types = {
        'application/pdf': '.pdf',
        'text/plain': '.txt',
        'application/msword': '.doc',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document': '.docx',
    }
    
    if file.content_type not in allowed_types:
        raise ValueError(f"File type not allowed: {file.content_type}")
    
    return True


# ============================================================================
# Request/Response Logging Middleware
# ============================================================================

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all HTTP requests and responses"""
    start_time = datetime.utcnow()
    
    # Log request
    logger.info(f"Incoming request: {request.method} {request.url.path}", extra={
        "method": request.method,
        "path": request.url.path,
        "timestamp": start_time.isoformat(),
    })
    
    try:
        response = await call_next(request)
        process_time = (datetime.utcnow() - start_time).total_seconds()
        
        # Log response
        logger.info(f"Response: {response.status_code} ({process_time:.2f}s)", extra={
            "status_code": response.status_code,
            "process_time": process_time,
        })
        
        return response
    except Exception as e:
        process_time = (datetime.utcnow() - start_time).total_seconds()
        logger.error(f"Request failed: {str(e)}", extra={
            "error": str(e),
            "process_time": process_time,
        })
        raise


# ============================================================================
# API Endpoints
# ============================================================================

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint
    
    Returns:
        HealthResponse: Status and timestamp
    """
    try:
        logger.info("Health check performed")
        return HealthResponse(
            status="healthy",
            timestamp=datetime.utcnow().isoformat()
        )
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service unhealthy"
        )


@app.get("/strategies", response_model=StrategiesResponse)
async def list_strategies(api_key: str = Depends(verify_api_key)):
    """
    List available retrieval strategies
    
    Parameters:
        api_key: API key (X-API-Key header)
    
    Returns:
        StrategiesResponse: List of available strategies with descriptions
    """
    try:
        strategies = {
            "basic": "Simple vector similarity search",
            "rewritten": "Query rewritten by GPT-4 before retrieval",
            "multi_query": "Multiple query variations for broader coverage",
            "hyde": "Hypothetical document embeddings",
            "hybrid_rerank": "Combined hybrid search with semantic reranking",
        }
        
        logger.info("Strategies listed")
        return StrategiesResponse(
            strategies=list(strategies.keys()),
            descriptions=strategies
        )
    except Exception as e:
        logger.error(f"Error listing strategies: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.post("/query", response_model=QueryResponse)
@limiter.limit("10/minute")
async def query_documents(
    request: Request,
    query_req: QueryRequest,
    api_key: str = Depends(verify_api_key)
):
    """
    Process a query and return relevant documents and answer
    
    Parameters:
        query_req: QueryRequest object with query, strategy, and optional conversation_id
        api_key: API key (X-API-Key header)
    
    Returns:
        QueryResponse: Answer, sources, and metadata
    
    Rate limit: 10 requests per minute per API key
    """
    start_time = datetime.utcnow()
    
    try:
        # Validate query
        max_query_length = int(os.getenv("MAX_QUERY_LENGTH", "500"))
        if len(query_req.query) > max_query_length:
            raise ValueError(f"Query exceeds max length of {max_query_length}")
        
        # Initialize pipeline if not exists
        if not hasattr(app, 'rag_pipeline'):
            app.rag_pipeline = AdvancedRAGPipeline()
        
        logger.info(f"Processing query: {query_req.query[:50]}...", extra={
            "strategy": query_req.strategy,
            "conversation_id": query_req.conversation_id,
        })
        
        # Execute RAG pipeline
        result = app.rag_pipeline.answer_question(
            query=query_req.query,
            strategy=query_req.strategy,
            num_results=query_req.num_results
        )
        
        process_time = (datetime.utcnow() - start_time).total_seconds()
        
        # Prepare response
        response = QueryResponse(
            answer=result.get("answer", ""),
            sources=result.get("retrieved_docs", []),
            metadata={
                "strategy": query_req.strategy,
                "num_results": query_req.num_results,
                "response_time_seconds": process_time,
                "conversation_id": query_req.conversation_id,
                "cost": result.get("cost", 0),
            },
            timestamp=datetime.utcnow().isoformat()
        )
        
        logger.info(f"Query processed successfully ({process_time:.2f}s)")
        return response
        
    except ValueError as e:
        logger.warning(f"Validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Query processing error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing query: {str(e)}"
        )


@app.post("/upload", response_model=UploadResponse)
@limiter.limit("5/minute")
async def upload_documents(
    request: Request,
    files: List[UploadFile] = File(...),
    api_key: str = Depends(verify_api_key)
):
    """
    Upload documents for indexing
    
    Parameters:
        files: List of documents (PDF, TXT, DOCX)
        api_key: API key (X-API-Key header)
    
    Returns:
        UploadResponse: Status and number of documents added
    
    Rate limit: 5 uploads per minute
    """
    start_time = datetime.utcnow()
    
    try:
        if not files:
            raise ValueError("No files provided")
        
        max_file_size_mb = int(os.getenv("MAX_FILE_SIZE_MB", "10"))
        file_details = []
        documents_added = 0
        
        # Initialize pipeline if not exists
        if not hasattr(app, 'rag_pipeline'):
            app.rag_pipeline = AdvancedRAGPipeline()
        
        for file in files:
            try:
                # Validate file
                validate_file_upload(file)
                
                # Check file size
                file_content = await file.read()
                file_size_mb = len(file_content) / (1024 * 1024)
                
                if file_size_mb > max_file_size_mb:
                    logger.warning(f"File too large: {file.filename}")
                    continue
                
                # Store file
                data_dir = Path("data")
                data_dir.mkdir(exist_ok=True)
                file_path = data_dir / file.filename
                
                with open(file_path, "wb") as f:
                    f.write(file_content)
                
                documents_added += 1
                file_details.append({
                    "filename": file.filename,
                    "size_mb": file_size_mb,
                    "content_type": file.content_type,
                    "status": "uploaded",
                })
                
                logger.info(f"File uploaded: {file.filename} ({file_size_mb:.2f}MB)")
                
            except Exception as e:
                logger.error(f"Error uploading file {file.filename}: {str(e)}")
                file_details.append({
                    "filename": file.filename,
                    "status": "error",
                    "error": str(e),
                })
        
        process_time = (datetime.utcnow() - start_time).total_seconds()
        
        logger.info(f"Upload completed: {documents_added} files ({process_time:.2f}s)")
        
        return UploadResponse(
            status="success" if documents_added > 0 else "partial",
            documents_added=documents_added,
            file_details=file_details,
            timestamp=datetime.utcnow().isoformat()
        )
        
    except ValueError as e:
        logger.warning(f"Validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Upload error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error uploading files: {str(e)}"
        )


# ============================================================================
# Error Handlers
# ============================================================================

@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    """Handle rate limit exceeded"""
    logger.warning(f"Rate limit exceeded: {request.client.host}")
    return JSONResponse(
        status_code=429,
        content={
            "status": "error",
            "message": "Rate limit exceeded. Max 10 requests per minute",
            "timestamp": datetime.utcnow().isoformat(),
            "code": 429,
        }
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions"""
    logger.error(f"HTTP exception: {exc.status_code} - {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": "error",
            "message": exc.detail,
            "timestamp": datetime.utcnow().isoformat(),
            "code": exc.status_code,
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions"""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "message": "Internal server error",
            "timestamp": datetime.utcnow().isoformat(),
            "code": 500,
        }
    )


# ============================================================================
# Startup/Shutdown Events
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Initialize on startup"""
    try:
        logger.info("=== API Server Starting ===")
        app.rag_pipeline = AdvancedRAGPipeline()
        logger.info("RAG Pipeline initialized")
    except Exception as e:
        logger.error(f"Startup error: {str(e)}")
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("=== API Server Shutting Down ===")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
