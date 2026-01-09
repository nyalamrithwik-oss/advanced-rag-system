"""
Verification Script for Advanced RAG System

This script verifies that all imports work correctly after the fixes.
Run this before running the Streamlit app.

Usage:
    python verify_imports.py
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def verify_imports():
    """Verify that all critical modules can be imported."""
    print("\n" + "="*60)
    print("🔍 VERIFYING IMPORTS FOR ADVANCED RAG SYSTEM")
    print("="*60 + "\n")
    
    modules_to_test = [
        ("src.__init__", "Package initialization"),
        ("src.rag_pipeline", "RAG Pipeline"),
        ("src.query_transformer", "Query Transformer"),
        ("src.hybrid_retriever", "Hybrid Retriever"),
        ("src.reranker", "Reranker"),
        ("src.context_optimizer", "Context Optimizer"),
        ("src.cost_tracker", "Cost Tracker"),
        ("src.citation_tracker", "Citation Tracker"),
        ("src.export_handler", "Export Handler"),
        ("src.chart_generator", "Chart Generator"),
        ("src.logger_config", "Logger Config"),
        ("src.monitoring", "Monitoring"),
    ]
    
    failed = []
    passed = []
    
    for module_name, description in modules_to_test:
        try:
            __import__(module_name)
            print(f"✅ {description:<30} - OK")
            passed.append(module_name)
        except ImportError as e:
            print(f"❌ {description:<30} - FAILED: {str(e)}")
            failed.append((module_name, str(e)))
        except Exception as e:
            print(f"⚠️  {description:<30} - ERROR: {str(e)}")
            failed.append((module_name, str(e)))
    
    print("\n" + "="*60)
    print(f"RESULTS: {len(passed)} passed, {len(failed)} failed")
    print("="*60 + "\n")
    
    if failed:
        print("❌ FAILED MODULES:\n")
        for module_name, error in failed:
            print(f"  {module_name}:")
            print(f"    {error}\n")
        return False
    else:
        print("✅ ALL IMPORTS SUCCESSFUL!")
        print("\nYou can now run the Streamlit app:")
        print("  streamlit run app_wrapper.py")
        print("\nOr from the terminal:")
        print("  python -m streamlit run app_wrapper.py")
        return True

if __name__ == "__main__":
    success = verify_imports()
    sys.exit(0 if success else 1)
