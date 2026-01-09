# SETUP & DEPLOYMENT GUIDE

## 🚀 Complete Setup Instructions

### Step 1: Navigate to Project

```powershell
cd C:\Users\nyala\OneDrive\RAG\week3\advanced-rag-system
```

### Step 2: Create Virtual Environment

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### Step 3: Install Dependencies

```powershell
pip install -r requirements.txt
```

This installs:
- LangChain & OpenAI
- Pinecone client (vector database)
- Cohere (reranking)
- Streamlit (web UI)
- BM25 (sparse search)
- pytest (testing)
- And more...

### Step 4: Configure Environment Variables

```powershell
# The .env file is already created as a template
# Edit it with your actual API keys

notepad .env
```

**Required API Keys:**
```
OPENAI_API_KEY=sk-your-key-here
PINECONE_API_KEY=your-pinecone-key
COHERE_API_KEY=your-cohere-key
```

**Optional Configuration:**
```
CHUNK_SIZE=500
CHUNK_OVERLAP=100
LLM_MODEL=gpt-4-turbo-preview
EMBEDDING_MODEL=text-embedding-3-small
RERANKER_MODEL=rerank-english-v3.0
```

### Step 5: Verify Setup

```powershell
python quick_start.py
```

This script will:
- ✅ Check environment variables
- ✅ Verify package imports
- ✅ Test pipeline initialization
- ✅ Show usage instructions

## 🎮 Running the Application

### Option A: Streamlit Web Interface (Recommended)

```powershell
streamlit run src/app.py
```

Access at: **http://localhost:8501**

**Features:**
- 📄 Upload documents (PDF, DOCX, TXT, MD)
- 🔍 Query Playground - Test strategies individually
- 📊 Strategy Comparison - Compare all 5 strategies
- 📊 Interactive charts and results visualization

### Option B: Command Line Testing

Test individual components:

```powershell
# Test Query Transformer
python src/query_transformer.py

# Test Hybrid Retriever
python src/hybrid_retriever.py

# Test Reranker
python src/reranker.py

# Test Context Optimizer
python src/context_optimizer.py

# Test Full Pipeline
python src/rag_pipeline.py
```

### Option C: Run Tests

```powershell
# Run all tests with verbose output
pytest tests/test_pipeline.py -v

# Run specific test class
pytest tests/test_pipeline.py::TestHybridRetriever -v

# Run with coverage report
pytest tests/test_pipeline.py --cov=src --cov-report=html
```

## 📁 Project Structure

```
advanced-rag-system/
├── src/                          # Core implementation
│   ├── query_transformer.py      # Query rewriting, multi-query, HyDE
│   ├── hybrid_retriever.py       # Dense + sparse + RRF fusion
│   ├── reranker.py               # Cohere reranking
│   ├── context_optimizer.py      # Dedup, compression, optimization
│   ├── rag_pipeline.py           # Pipeline orchestration
│   └── app.py                    # Streamlit web UI
├── config/
│   └── settings.py               # Configuration management
├── data/                         # Sample documents
│   ├── sales_strategies.txt
│   ├── objection_handling.txt
│   └── negotiation_tactics.txt
├── tests/
│   └── test_pipeline.py          # Comprehensive tests
├── .env                          # Environment variables
├── requirements.txt              # Dependencies
├── README.md                     # Comprehensive documentation
├── PROJECT_OVERVIEW.md           # Project summary
├── quick_start.py                # Setup verification
└── SETUP.md                      # This file
```

## 🧪 Testing

The project includes comprehensive tests covering:
- ✅ Query transformation (rewriting, multi-query, HyDE)
- ✅ Hybrid retrieval (dense, sparse, RRF fusion)
- ✅ Document reranking
- ✅ Context optimization
- ✅ Full pipeline execution
- ✅ Error handling
- ✅ Component integration
- ✅ End-to-end workflows

**Run tests:**
```powershell
pytest tests/test_pipeline.py -v
```

## 🎯 Available Strategies

1. **basic** - Direct hybrid retrieval (fast, baseline quality)
2. **rewritten** - Query rewriting + retrieval (better clarity)
3. **multi_query** - Multiple query variations (better coverage)
4. **hyde** - Hypothetical documents (handles paraphrasing)
5. **hybrid_rerank** - Full stack with all techniques (best quality)

## 📊 Performance Expectations

| Strategy | Time | Quality |
|----------|------|---------|
| basic | 0.3s | 3/5 |
| rewritten | 0.5s | 3.5/5 |
| multi_query | 0.8s | 4/5 |
| hyde | 1.2s | 3.5/5 |
| hybrid_rerank | 2.1s | 4.5/5 |

## ⚙️ Configuration

### API Keys Setup

1. **OpenAI** (for query transformation & LLM)
   - Get from: https://platform.openai.com/api-keys
   - Required for: Query rewriting, multi-query, HyDE, answer generation

2. **Pinecone** (for vector storage)
   - Get from: https://www.pinecone.io/
   - Required for: Dense embedding search
   - Create serverless index: "advanced-rag"

3. **Cohere** (for reranking)
   - Get from: https://cohere.com/
   - Required for: Document reranking
   - Model: rerank-english-v3.0

### Environment File Example

Create `.env` in project root:
```
OPENAI_API_KEY=sk-...
PINECONE_API_KEY=...
COHERE_API_KEY=...
PINECONE_INDEX_NAME=advanced-rag
CHUNK_SIZE=500
CHUNK_OVERLAP=100
LLM_MODEL=gpt-4-turbo-preview
EMBEDDING_MODEL=text-embedding-3-small
RERANKER_MODEL=rerank-english-v3.0
```

## 🐛 Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'langchain'"

**Solution:**
```powershell
pip install -r requirements.txt
```

### Issue: "OpenAI API key not found"

**Solution:**
1. Check `.env` file has `OPENAI_API_KEY`
2. Verify key is valid (starts with `sk-`)
3. Restart the application

### Issue: "Pinecone index not found"

**Solution:**
1. Check `PINECONE_API_KEY` in `.env`
2. Verify index name matches `PINECONE_INDEX_NAME`
3. Index auto-creates on first use, but ensure API key is valid

### Issue: Low answer quality

**Solution:**
Try the "hybrid_rerank" strategy instead of "basic":
```python
result = pipeline.query(
    question="Your question",
    strategy="hybrid_rerank"  # Full advanced stack
)
```

### Issue: Streamlit session state errors

**Solution:**
```powershell
streamlit run src/app.py --logger.level=debug
```

## 📚 Documentation

- **README.md** - Full project documentation with examples
- **PROJECT_OVERVIEW.md** - Project summary and statistics
- **SETUP.md** - This setup guide
- **Code comments** - Detailed inline documentation

## 🚀 Next Steps

1. **Load Your Documents**
   - Use Streamlit UI to upload PDFs, DOCX, or text files
   - Or use Python API: `pipeline.ingest_documents(file_paths)`

2. **Test Different Strategies**
   - Query Playground page for individual testing
   - Strategy Comparison page for side-by-side analysis

3. **Customize Configuration**
   - Adjust `CHUNK_SIZE`, `CHUNK_OVERLAP` in `.env`
   - Modify similarity threshold for deduplication
   - Configure LLM model and parameters

4. **Extend Functionality**
   - Add custom retrieval methods to `HybridRetriever`
   - Implement custom reranking models in `Reranker`
   - Add new transformation techniques to `QueryTransformer`

## 💡 Usage Examples

### Python API

```python
from src.rag_pipeline import AdvancedRAGPipeline

# Initialize
pipeline = AdvancedRAGPipeline()

# Index documents
pipeline.ingest_documents(["document1.pdf", "document2.txt"])

# Query with different strategies
result = pipeline.query(
    question="What are the best sales techniques?",
    strategy="hybrid_rerank",
    num_results=5
)

print(result["answer"])
print(result["retrieved_docs"])
print(f"Time: {result['processing_time']:.2f}s")
```

### Streamlit UI

1. Open http://localhost:8501
2. Upload documents in sidebar
3. Select strategy from dropdown
4. Enter your question
5. Click "Execute Query"
6. View results with source documents

## 📞 Support

For issues or questions:
1. Check README.md for detailed documentation
2. Review inline code comments
3. Run `python quick_start.py` for verification
4. Check pytest test cases for usage examples

## ✨ Success Indicators

- ✅ `quick_start.py` passes all checks
- ✅ `streamlit run src/app.py` launches without errors
- ✅ `pytest tests/test_pipeline.py -v` shows all tests passing
- ✅ Document upload and query processing work
- ✅ All 5 strategies execute successfully

---

**Project Ready for Production Use! 🎉**

Location: `C:\Users\nyala\OneDrive\RAG\week3\advanced-rag-system`

Day 16 Learning Journey - Advanced RAG Techniques Implementation
