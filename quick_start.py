"""
Quick Start Guide - Advanced RAG System

Run this file to verify your setup and test the system.

Author: RAG Learning Journey - Day 16
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

def check_environment():
    """Check if environment is properly configured."""
    print("\n" + "="*60)
    print("🔍 ENVIRONMENT CHECK")
    print("="*60)
    
    load_dotenv()
    
    required_keys = [
        "OPENAI_API_KEY",
        "PINECONE_API_KEY", 
        "COHERE_API_KEY",
    ]
    
    all_present = True
    for key in required_keys:
        value = os.getenv(key)
        if value:
            display = f"{value[:10]}***" if len(value) > 10 else "***"
            print(f"✅ {key}: {display}")
        else:
            print(f"❌ {key}: NOT SET")
            all_present = False
    
    return all_present

def test_imports():
    """Test that all modules can be imported."""
    print("\n" + "="*60)
    print("📦 IMPORT CHECK")
    print("="*60)
    
    modules_to_test = [
        "langchain",
        "pinecone",
        "cohere",
        "streamlit",
        "rank_bm25",
        "sklearn",
    ]
    
    all_imported = True
    for module in modules_to_test:
        try:
            __import__(module)
            print(f"✅ {module}")
        except ImportError as e:
            print(f"❌ {module}: {str(e)}")
            all_imported = False
    
    return all_imported

def test_pipeline():
    """Test basic pipeline functionality."""
    print("\n" + "="*60)
    print("🧪 PIPELINE TEST")
    print("="*60)
    
    try:
        from src.rag_pipeline import AdvancedRAGPipeline
        
        print("Initializing pipeline...")
        pipeline = AdvancedRAGPipeline()
        print("✅ Pipeline initialized")
        
        # Index sample data
        print("\nIndexing sample documents...")
        sample_docs = [
            "Focus on value-based selling to establish credibility",
            "Use data-driven insights to demonstrate ROI",
            "Develop multiple touchpoints in sales process",
        ]
        pipeline.retriever.index_documents(sample_docs)
        print(f"✅ Indexed {len(sample_docs)} documents")
        
        # Test basic query
        print("\nTesting basic query...")
        result = pipeline.query(
            "What is value-based selling?",
            strategy="basic",
            num_results=2
        )
        print(f"✅ Query processed in {result['processing_time']:.2f}s")
        print(f"   Answer: {result['answer'][:100]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Pipeline test failed: {str(e)}")
        return False

def show_usage_instructions():
    """Show how to use the system."""
    print("\n" + "="*60)
    print("📖 USAGE INSTRUCTIONS")
    print("="*60)
    
    instructions = """
1. RUN STREAMLIT WEB APP:
   ► streamlit run src/app.py
   ► Open browser: http://localhost:8501
   
2. TEST IN PYTHON:
   ► python -c "from src.rag_pipeline import AdvancedRAGPipeline; ..."
   ► Or: python quick_start.py
   
3. RUN UNIT TESTS:
   ► pytest tests/test_pipeline.py -v
   
4. COMPONENT EXAMPLES:
   ► Query Transformer: python src/query_transformer.py
   ► Hybrid Retriever: python src/hybrid_retriever.py
   ► Reranker: python src/reranker.py
   ► Context Optimizer: python src/context_optimizer.py
   ► RAG Pipeline: python src/rag_pipeline.py

5. PROJECT STRUCTURE:
   src/
   ├── query_transformer.py    # Query rewriting, multi-query, HyDE
   ├── hybrid_retriever.py     # Dense + sparse + RRF fusion
   ├── reranker.py             # Cohere reranking
   ├── context_optimizer.py    # Dedup, compression, optimization
   ├── rag_pipeline.py         # Full orchestration
   └── app.py                  # Streamlit web UI
   
   data/
   ├── sales_strategies.txt    # Sample sales document
   ├── objection_handling.txt  # Objection handling guide
   └── negotiation_tactics.txt # Negotiation strategies

6. CONFIGURE:
   ► Edit .env with your API keys
   ► Check config/settings.py for defaults
"""
    
    print(instructions)

def show_strategies_info():
    """Show information about available strategies."""
    print("\n" + "="*60)
    print("🎯 AVAILABLE STRATEGIES")
    print("="*60)
    
    strategies = {
        "basic": {
            "description": "Direct hybrid retrieval",
            "speed": "Fast ⚡",
            "quality": "3/5 ⭐⭐⭐",
            "best_for": "Quick answers, baseline"
        },
        "rewritten": {
            "description": "Query rewriting + retrieval",
            "speed": "Medium ⚡⚡",
            "quality": "3.5/5 ⭐⭐⭐",
            "best_for": "Ambiguous questions"
        },
        "multi_query": {
            "description": "Multiple query variations + aggregation",
            "speed": "Slower ⚡⚡⚡",
            "quality": "4/5 ⭐⭐⭐⭐",
            "best_for": "Comprehensive coverage"
        },
        "hyde": {
            "description": "Hypothetical document embeddings",
            "speed": "Slow ⚡⚡⚡",
            "quality": "3.5/5 ⭐⭐⭐",
            "best_for": "Paraphrase handling"
        },
        "hybrid_rerank": {
            "description": "Full stack - all techniques combined",
            "speed": "Slowest ⚡⚡⚡⚡",
            "quality": "4.5/5 ⭐⭐⭐⭐",
            "best_for": "Maximum quality"
        }
    }
    
    for name, info in strategies.items():
        print(f"\n{name.upper()}")
        print(f"  Description: {info['description']}")
        print(f"  Speed: {info['speed']}")
        print(f"  Quality: {info['quality']}")
        print(f"  Best for: {info['best_for']}")

def main():
    """Run all checks."""
    print("\n")
    print("╔" + "="*58 + "╗")
    print("║" + " "*58 + "║")
    print("║" + "  ADVANCED RAG SYSTEM - SETUP VERIFICATION".center(58) + "║")
    print("║" + "  Day 16 Learning Journey".center(58) + "║")
    print("║" + " "*58 + "║")
    print("╚" + "="*58 + "╝")
    
    # Run checks
    env_ok = check_environment()
    imports_ok = test_imports()
    
    if env_ok and imports_ok:
        pipeline_ok = test_pipeline()
    else:
        pipeline_ok = False
        print("\n⚠️  Skipping pipeline test (missing dependencies)")
    
    # Show usage
    show_strategies_info()
    show_usage_instructions()
    
    # Summary
    print("\n" + "="*60)
    print("✅ SETUP SUMMARY")
    print("="*60)
    
    checks = [
        ("Environment Variables", env_ok),
        ("Required Packages", imports_ok),
        ("Pipeline Functionality", pipeline_ok),
    ]
    
    all_ok = all(status for _, status in checks)
    
    for check_name, status in checks:
        symbol = "✅" if status else "❌"
        print(f"{symbol} {check_name}")
    
    if all_ok:
        print("\n🎉 All checks passed! System is ready.")
        print("\n🚀 Next step: Run streamlit app:")
        print("   ► streamlit run src/app.py")
    else:
        print("\n⚠️  Some checks failed. Please:")
        print("   1. Install missing packages: pip install -r requirements.txt")
        print("   2. Configure .env with API keys")
        print("   3. Run this script again")
    
    print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    main()
