# Quick Start Script for Advanced RAG API (Windows PowerShell)
# This script sets up and runs the API server locally

Write-Host "`n╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║       Advanced RAG API - Quick Start (Windows)                ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan

# Check Python installation
Write-Host "✓ Checking Python installation..." -ForegroundColor Green
python --version

# Create virtual environment if it doesn't exist
if (!(Test-Path "venv")) {
    Write-Host "✓ Creating virtual environment..." -ForegroundColor Green
    python -m venv venv
} else {
    Write-Host "✓ Virtual environment already exists" -ForegroundColor Green
}

# Activate virtual environment
Write-Host "✓ Activating virtual environment..." -ForegroundColor Green
& .\venv\Scripts\Activate.ps1

# Install/upgrade dependencies
Write-Host "✓ Installing dependencies..." -ForegroundColor Green
python -m pip install --upgrade pip
pip install -q -r requirements.txt

# Setup environment file
if (!(Test-Path ".env")) {
    Write-Host "✓ Creating .env file from template..." -ForegroundColor Green
    Copy-Item ".env.example" ".env"
    Write-Host ""
    Write-Host "⚠️  Please edit .env and set your API credentials:" -ForegroundColor Yellow
    Write-Host "   - API_KEY (required)" -ForegroundColor Yellow
    Write-Host "   - OPENAI_API_KEY (required)" -ForegroundColor Yellow
    Write-Host "   - PINECONE_API_KEY, PINECONE_ENV, PINECONE_INDEX (if using Pinecone)" -ForegroundColor Yellow
    Write-Host "   - COHERE_API_KEY (optional, for reranking)" -ForegroundColor Yellow
    Write-Host ""
} else {
    Write-Host "✓ .env file already exists" -ForegroundColor Green
}

# Run verification
Write-Host "✓ Verifying setup..." -ForegroundColor Green
python verify_api.py

Write-Host ""
Write-Host "╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║  ✅ Setup Complete!                                            ║" -ForegroundColor Green
Write-Host "╚════════════════════════════════════════════════════════════════╝`n" -ForegroundColor Green

Write-Host "To start the API server, run:" -ForegroundColor Cyan
Write-Host ""
Write-Host "  uvicorn src.api:app --reload --port 8000" -ForegroundColor Yellow
Write-Host ""
Write-Host "Then open in your browser:" -ForegroundColor Cyan
Write-Host "  • API: http://localhost:8000" -ForegroundColor Yellow
Write-Host "  • Docs: http://localhost:8000/docs" -ForegroundColor Yellow
Write-Host "  • ReDoc: http://localhost:8000/redoc" -ForegroundColor Yellow
Write-Host ""
