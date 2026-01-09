# Running the Advanced RAG System - Quick Start Guide

## ⚠️ Important: Use the Entry Point Script

**DO NOT** run: `streamlit run src/app.py` ❌

This will fail with `ModuleNotFoundError: No module named 'src'`

## ✅ Correct Way to Run

### Step 1: Navigate to Project Directory
```powershell
cd C:\Users\nyala\OneDrive\RAG\week3\advanced-rag-system
```

### Step 2: Activate Virtual Environment
```powershell
# Windows PowerShell
.\.venv\Scripts\Activate.ps1

# If you get execution policy error, run:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Step 3: Verify Setup (Optional but Recommended)
```powershell
python verify_imports.py
```

Expected output:
```
✅ Package initialization - OK
✅ RAG Pipeline - OK
✅ Query Transformer - OK
...
✅ ALL IMPORTS SUCCESSFUL!
```

### Step 4: Run the Application
```powershell
streamlit run app_wrapper.py
```

Or:
```powershell
python -m streamlit run app_wrapper.py
```

The app will open in your browser at: `http://localhost:8501`

## 📚 What Was Fixed

### The Problem
Files in `src/` directory were using absolute imports:
```python
# ❌ BROKEN
from src.rag_pipeline import AdvancedRAGPipeline
```

### The Solution
Changed to relative imports:
```python
# ✅ FIXED
from .rag_pipeline import AdvancedRAGPipeline
```

### Entry Point Script
Created `app_wrapper.py` that:
1. Sets up `sys.path` correctly
2. Imports the app module
3. Handles all path issues automatically

## 🔍 Understanding the Fix

```
week3/advanced-rag-system/
├── src/                           # Python package
│   ├── __init__.py                # Makes it a package
│   ├── app.py                     # Uses: from .rag_pipeline
│   ├── api.py                     # Uses: from .rag_pipeline
│   ├── rag_pipeline.py            # Uses: from .query_transformer
│   └── ... other modules
│
├── app_wrapper.py                 # ← RUN THIS with streamlit
└── verify_imports.py              # Check imports work
```

**How it works:**
1. `streamlit run app_wrapper.py` is called
2. `app_wrapper.py` adds project root to `sys.path`
3. Python finds `src` package
4. `src/app.py` uses relative imports (`.rag_pipeline`)
5. Everything works! ✅

## 🚨 Troubleshooting

### Issue: Still getting `ModuleNotFoundError`
**Solution:** Make sure you're running from the project root and using `app_wrapper.py`:
```powershell
# ❌ Wrong
streamlit run src/app.py

# ✅ Correct
streamlit run app_wrapper.py
```

### Issue: Environment Variables Not Loading
The app loads `.env` file automatically. Make sure it exists in the project root:
```
week3/advanced-rag-system/.env
```

Check if `.env` has required keys:
```
OPENAI_API_KEY=your-key-here
PINECONE_API_KEY=your-key-here
COHERE_API_KEY=your-key-here
```

### Issue: Virtual Environment Not Activated
Check if your prompt shows `(.venv)`:
```powershell
# ✅ Correct (shows .venv)
(.venv) PS C:\Users\nyala\OneDrive\RAG\week3\advanced-rag-system>

# ❌ Wrong (no .venv)
PS C:\Users\nyala\OneDrive\RAG\week3\advanced-rag-system>
```

Activate it:
```powershell
.\.venv\Scripts\Activate.ps1
```

## 📋 Files Created/Modified

### Created:
- ✅ `app_wrapper.py` - Entry point for Streamlit (recommended)
- ✅ `streamlit_app.py` - Alternative entry point
- ✅ `verify_imports.py` - Import verification script
- ✅ `IMPORT_FIX_SUMMARY.md` - Detailed fix documentation
- ✅ `RUN_INSTRUCTIONS.md` - This file

### Modified:
- ✅ `src/app.py` - Relative imports
- ✅ `src/api.py` - Relative imports
- ✅ `src/rag_pipeline.py` - Relative imports
- ✅ `src/logger_config.py` - Documentation updated
- ✅ `src/monitoring.py` - Documentation updated

## 🔗 Related Documentation

See also:
- `IMPORT_FIX_SUMMARY.md` - Technical details of the fix
- `README.md` - General project information
- `ARCHITECTURE.md` - System architecture
- `API_SETUP.md` - API configuration

## ✨ Next Steps

1. ✅ Verify imports: `python verify_imports.py`
2. ✅ Check environment: Make sure `.env` is configured
3. ✅ Run the app: `streamlit run app_wrapper.py`
4. 🌐 Open browser: Should auto-open at `http://localhost:8501`
5. 📊 Try the query playground or strategy comparison

## 💡 Key Takeaways

| Do | Don't |
|----|-------|
| Use `streamlit run app_wrapper.py` | Use `streamlit run src/app.py` |
| Use relative imports in `src/` | Use absolute `src.` imports in `src/` |
| Add to sys.path in entry script | Rely on Python to find src automatically |
| Run from project root | Run from src/ directory |

---

**Status:** ✅ Fixed and Ready to Run
**Last Updated:** January 9, 2026
