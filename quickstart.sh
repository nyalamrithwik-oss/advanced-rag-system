#!/usr/bin/env bash
# Quick Start Script for Advanced RAG API
# This script sets up and runs the API server locally

set -e

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║       Advanced RAG API - Quick Start                           ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Check Python installation
echo "✓ Checking Python installation..."
python --version

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "✓ Creating virtual environment..."
    python -m venv venv
else
    echo "✓ Virtual environment already exists"
fi

# Activate virtual environment
echo "✓ Activating virtual environment..."
source venv/bin/activate || . venv/Scripts/activate

# Install/upgrade dependencies
echo "✓ Installing dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt

# Setup environment file
if [ ! -f ".env" ]; then
    echo "✓ Creating .env file from template..."
    cp .env.example .env
    echo ""
    echo "⚠️  Please edit .env and set your API credentials:"
    echo "   - API_KEY (required)"
    echo "   - OPENAI_API_KEY (required)"
    echo "   - PINECONE_API_KEY, PINECONE_ENV, PINECONE_INDEX (if using Pinecone)"
    echo "   - COHERE_API_KEY (optional, for reranking)"
    echo ""
else
    echo "✓ .env file already exists"
fi

# Run verification
echo "✓ Verifying setup..."
python verify_api.py

echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║  ✅ Setup Complete!                                            ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "To start the API server, run:"
echo ""
echo "  uvicorn src.api:app --reload --port 8000"
echo ""
echo "Then open in your browser:"
echo "  • API: http://localhost:8000"
echo "  • Docs: http://localhost:8000/docs"
echo "  • ReDoc: http://localhost:8000/redoc"
echo ""
