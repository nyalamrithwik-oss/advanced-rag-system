# 🚀 QUICK REFERENCE - HOW TO USE EVERYTHING

## ⚡ 30-SECOND QUICK START

```bash
# 1. Open Terminal
# 2. Run this command:
cd "C:\Users\nyala\OneDrive\RAG\week3\advanced-rag-system"
$env:OPENAI_API_KEY="your-openai-key"
python -m streamlit run src/app.py

# 3. Open browser: http://localhost:8501
# 4. Start using!
```

---

## 📱 WEB UI WORKFLOW

### To Test ONE Strategy (Page 1):
```
1. Open http://localhost:8501
2. Upload documents (or load sample)
3. Select strategy from dropdown
4. Type question
5. Click "🚀 Execute Query"
6. See answer + metrics + transformation details
7. Click "📊 Download as PDF" to export
```

### To Compare ALL Strategies (Page 2):
```
1. Click "Strategy Comparison" in sidebar
2. Upload documents (or load sample)
3. Type ONE question
4. Click "🚀 Compare All Strategies"
5. See side-by-side results
6. Compare metrics and costs
7. Click "📊 Download as PDF" to export
```

---

## 💾 HOW TO DOWNLOAD FILES

### PDF Export:
```
1. Execute a query (Page 1 or Page 2)
2. Scroll down to "Export Results"
3. Click "📊 Download as PDF"
4. File goes to: C:\Users\YourName\Downloads\
5. Open with: Any PDF reader (Adobe, Chrome, etc.)
```

### CSV Export:
```
1. Execute a query (Page 1 or Page 2)
2. Scroll down to "Export Results"
3. Click "📊 Download as CSV"
4. File goes to: C:\Users\YourName\Downloads\
5. Open with: Excel, Google Sheets, etc.
```

---

## 🎯 5 STRATEGIES EXPLAINED

| Strategy | What It Does | Best For | Cost | Speed |
|----------|------------|----------|------|-------|
| **Basic** | Simple search | Quick tests | Low ✓ | Fast ✓ |
| **Rewritten** | Reformulates query | Better queries | Medium | Medium |
| **Multi-Query** | 3 variations | Comprehensive | Medium | Medium |
| **HyDE** | Generates docs | Specialized queries | High | Slow |
| **Hybrid-Rerank** | ALL techniques | Best quality | High | Slow |

**Recommendation:** Start with "Basic" → try others → compare all 5 on Page 2

---

## 📊 WHAT YOU SEE IN RESULTS

### Generated Answer
- The AI's response to your question
- Based on retrieved documents

### Retrieved Documents
- Click to expand each document
- See relevance score (0-1)
- Higher = more relevant

### Cost Analysis
- Total cost for this query
- Per-query breakdown
- Average cost

### Transformation Details
- **Query Transformations:** How query was rewritten
- **Expanded Queries:** Alternative phrasings
- **HyDE Document:** AI-generated sample document
- **Acronyms:** Expansions of abbreviations
- **Related Terms:** Additional relevant keywords

### Metrics
- Response Time: How long processing took
- Documents Retrieved: Number of sources
- Relevance Score: Overall answer quality

---

## 🔧 API (For Developers)

### Start API:
```bash
cd "C:\Users\nyala\OneDrive\RAG\week3\advanced-rag-system"
$env:PYTHONPATH="$(pwd)"
$env:OPENAI_API_KEY="your-key"
python -m uvicorn src.api:app --reload --port 8000
```

### Access API:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Example API Call:
```bash
curl -X POST http://localhost:8000/query \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is B2B sales?",
    "strategy": "hybrid_rerank",
    "num_results": 5
  }'
```

---

## 📝 DIRECTORY STRUCTURE (What Goes Where)

```
Your Project Root: C:\Users\nyala\OneDrive\RAG\week3\advanced-rag-system\

📂 src/
   ├─ app.py              ← Web UI (Streamlit)
   ├─ api.py              ← REST API (FastAPI)
   ├─ rag_pipeline.py     ← Main logic (5 strategies)
   └─ [other modules]

📂 data/
   └─ Sample documents here

📂 logs/
   ├─ app.log             ← Application logs
   ├─ errors.log          ← Error logs
   └─ metrics.json        ← Performance metrics

📄 test_api.py            ← Run tests: python test_api.py
📄 requirements.txt       ← Python packages
📄 .env                   ← API keys (don't share)
📄 COMPLETE_GUIDE.md      ← Full documentation (you are here)
```

---

## 🧪 TESTING (Verify Everything Works)

```bash
cd "C:\Users\nyala\OneDrive\RAG\week3\advanced-rag-system"
python test_api.py

# Expected: 10/10 tests PASSED ✓
```

Tests check:
- ✅ API is running
- ✅ Authentication works
- ✅ All 5 strategies work
- ✅ Validation works
- ✅ Error handling works

---

## 🐛 TROUBLESHOOTING

### Problem: "Module not found"
```bash
# Solution:
cd "C:\Users\nyala\OneDrive\RAG\week3\advanced-rag-system"
pip install -r requirements.txt
```

### Problem: "OpenAI API error"
```bash
# Solution: Check your API key
$env:OPENAI_API_KEY = "sk-your-actual-key"

# Or update .env file:
# Open .env and set: OPENAI_API_KEY=sk-...
```

### Problem: "Port 8501 already in use"
```bash
# Solution: Kill existing Streamlit
taskkill /F /IM python.exe
# Wait 3 seconds
python -m streamlit run src/app.py
```

### Problem: "Pinecone connection error"
```bash
# Solution: It's optional! Works without Pinecone
# System falls back to in-memory retrieval
# To enable: Update .env with real Pinecone keys
```

---

## 💡 TIPS & TRICKS

**Tip 1: Load sample documents**
- Check "Load sample documents" checkbox
- Use pre-loaded demo data
- Great for testing without uploads

**Tip 2: Adjust retrieval count**
- Slider in sidebar (1-10)
- More docs = better coverage but slower
- Start with 5, adjust as needed

**Tip 3: Enable query expansion**
- Checkbox in sidebar
- Expands queries with related terms
- Better for niche/technical topics

**Tip 4: Export for sharing**
- Download PDF for reports
- Download CSV for analysis
- Keep originals: PDFs auto-name by timestamp

**Tip 5: Monitor costs**
- Look at "Cost Analysis" section
- Compare strategies on Page 2
- API costs vary by strategy complexity

**Tip 6: Use conversation history**
- System remembers previous queries
- Build context for follow-up questions
- Click "Clear History" to reset

---

## 📈 FILES CREATED & MODIFIED IN THIS SESSION

### Created:
✅ `COMPLETE_GUIDE.md` - Full documentation (this file)
✅ `OPENAI_API_FIX.md` - API compatibility fix details

### Modified:
✅ `src/intent_classifier.py` - Updated to new OpenAI API
✅ `src/query_expander.py` - Updated to new OpenAI API

### Already Existing (Built Earlier):
✅ `src/api.py` - REST API (4 endpoints)
✅ `src/app.py` - Streamlit UI (2 pages)
✅ `src/rag_pipeline.py` - Core pipeline (5 strategies)
✅ `test_api.py` - Test suite (10 tests, all passing)
✅ `src/export_handler.py` - CSV & PDF export
✅ And 13+ other core modules

---

## 🎓 KEY CONCEPTS

**RAG (Retrieval Augmented Generation):**
- Combination of document retrieval + AI generation
- Better than pure LLM because uses your documents
- More accurate, less hallucination

**5 Strategies:**
1. **Basic:** Just retrieve and answer
2. **Rewritten:** Better query format
3. **Multi-Query:** Multiple attempts
4. **HyDE:** AI generates example documents
5. **Hybrid-Rerank:** All techniques combined

**Hybrid Search:**
- **Dense (Vector):** Semantic similarity
- **Sparse (BM25):** Keyword matching
- **Combined:** Best of both worlds

**Reranking:**
- Sort results by relevance
- Uses Cohere AI model
- Improves answer quality

**Context Optimization:**
- Remove duplicate information
- Compress long texts
- Format for readability

---

## 🏆 SYSTEM STATUS

**Overall Status: ✅ FULLY OPERATIONAL**

| Component | Status | Port |
|-----------|--------|------|
| Streamlit Web UI | ✅ Working | 8501 |
| FastAPI REST API | ✅ Working | 8000 |
| Query Strategies | ✅ All 5 working | - |
| Document Upload | ✅ Working | - |
| PDF Export | ✅ Working | - |
| CSV Export | ✅ Working | - |
| Authentication | ✅ Working | - |
| Logging | ✅ Working | - |
| Metrics | ✅ Working | - |
| Tests | ✅ 10/10 passing | - |

---

## 🔐 SECURITY NOTES

**API Key Protection:**
- Never commit .env file to git
- Don't share API keys
- Rotate keys regularly
- Use `X-API-Key` header for API calls

**Production Deployment:**
- Use HTTPS/SSL
- Implement user authentication
- Set up rate limiting (already done: 10 req/min)
- Monitor logs regularly
- Use environment variables

---

## 📞 SUPPORT QUICK LINKS

- **Full Documentation:** See [COMPLETE_GUIDE.md](COMPLETE_GUIDE.md)
- **API Setup:** See [API_SETUP.md](API_SETUP.md)
- **Deployment:** See [DEPLOYMENT.md](DEPLOYMENT.md)
- **Main README:** See [README.md](README.md)
- **Run Tests:** `python test_api.py`
- **Check Logs:** `tail -f logs/app.log`

---

## ✨ YOU'RE ALL SET!

Everything is working and ready to use.

**Next Steps:**
1. Start the app (see 30-second quickstart above)
2. Upload documents
3. Ask questions
4. Compare strategies
5. Export results as PDF/CSV
6. Deploy to cloud when ready

**Questions?** Check the Full Guide above or review the code comments.

**Good luck! 🚀**
