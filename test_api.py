"""
API Testing Script
Tests all endpoints without needing to run uvicorn separately
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Mock the RAG pipeline for testing
class MockRAGPipeline:
    def answer_question(self, query, strategy, num_results):
        return {
            "answer": f"This is a mock answer to: {query}",
            "retrieved_docs": [
                {"content": "Sample document 1", "metadata": {"source": "test.pdf"}},
                {"content": "Sample document 2", "metadata": {"source": "test.txt"}},
            ],
            "cost": 0.01,
        }

# Patch before importing API
sys.modules['src.rag_pipeline'] = type(sys)('src.rag_pipeline')
sys.modules['src.rag_pipeline'].AdvancedRAGPipeline = MockRAGPipeline

# Now we can import the FastAPI app
from src.api import app
from fastapi.testclient import TestClient

# Create test client
client = TestClient(app)

print("=" * 70)
print("🧪 ADVANCED RAG API - ENDPOINT TESTING")
print("=" * 70)
print()

# Test 1: Health Check
print("Test 1: Health Check (GET /health)")
print("-" * 70)
response = client.get("/health")
print(f"Status Code: {response.status_code}")
print(f"Response: {response.json()}")
assert response.status_code == 200
assert response.json()["status"] == "healthy"
print("✅ PASSED\n")

# Test 2: Get Strategies (without auth - should fail)
print("Test 2: Get Strategies WITHOUT API Key (should fail)")
print("-" * 70)
response = client.get("/strategies")
print(f"Status Code: {response.status_code}")
print(f"Response: {response.json()}")
assert response.status_code == 401
print("✅ PASSED (correctly rejected)\n")

# Test 3: Get Strategies (with auth - should succeed)
print("Test 3: Get Strategies WITH API Key (should succeed)")
print("-" * 70)
response = client.get(
    "/strategies",
    headers={"X-API-Key": "test-key-123"}
)
print(f"Status Code: {response.status_code}")
data = response.json()
print(f"Strategies: {data.get('strategies')}")
assert response.status_code == 200
assert "strategies" in data
assert len(data["strategies"]) == 5
print(f"✅ PASSED (found {len(data['strategies'])} strategies)\n")

# Test 4: Query without API key (should fail)
print("Test 4: Query WITHOUT API Key (should fail)")
print("-" * 70)
response = client.post(
    "/query",
    json={"query": "test", "strategy": "basic"}
)
print(f"Status Code: {response.status_code}")
assert response.status_code == 401
print("✅ PASSED (correctly rejected)\n")

# Test 5: Query with invalid strategy (should fail)
print("Test 5: Query with INVALID Strategy (should fail)")
print("-" * 70)
response = client.post(
    "/query",
    json={"query": "test", "strategy": "invalid_strategy"},
    headers={"X-API-Key": "test-key-123"}
)
print(f"Status Code: {response.status_code}")
assert response.status_code == 422  # Validation error
print("✅ PASSED (validation error)\n")

# Test 6: Valid query (should succeed)
print("Test 6: Valid Query Request")
print("-" * 70)
response = client.post(
    "/query",
    json={
        "query": "What is machine learning?",
        "strategy": "hybrid_rerank",
        "num_results": 5
    },
    headers={"X-API-Key": "test-key-123"}
)
print(f"Status Code: {response.status_code}")
data = response.json()
print(f"Answer: {data.get('answer')[:50]}...")
print(f"Sources: {len(data.get('sources', []))} documents")
print(f"Metadata: {data.get('metadata')}")
assert response.status_code == 200
assert "answer" in data
assert "sources" in data
assert "metadata" in data
print("✅ PASSED\n")

# Test 7: Query with conversation ID
print("Test 7: Query with Conversation ID")
print("-" * 70)
response = client.post(
    "/query",
    json={
        "query": "follow-up question",
        "strategy": "basic",
        "conversation_id": "conv_12345"
    },
    headers={"X-API-Key": "test-key-123"}
)
print(f"Status Code: {response.status_code}")
data = response.json()
assert response.status_code == 200
assert data["metadata"]["conversation_id"] == "conv_12345"
print("✅ PASSED\n")

# Test 8: Upload without API key (should fail)
print("Test 8: Upload WITHOUT API Key (should fail)")
print("-" * 70)
response = client.post("/upload")
print(f"Status Code: {response.status_code}")
assert response.status_code == 401
print("✅ PASSED (correctly rejected)\n")

# Test 9: Upload without files (should fail)
print("Test 9: Upload WITHOUT Files (should fail)")
print("-" * 70)
response = client.post(
    "/upload",
    headers={"X-API-Key": "test-key-123"}
)
print(f"Status Code: {response.status_code}")
assert response.status_code == 422  # Validation error
print("✅ PASSED (validation error)\n")

# Test 10: All valid strategies
print("Test 10: Test All Valid Strategies")
print("-" * 70)
strategies = ["basic", "rewritten", "multi_query", "hyde", "hybrid_rerank"]
for strategy in strategies:
    response = client.post(
        "/query",
        json={
            "query": "test query",
            "strategy": strategy,
            "num_results": 3
        },
        headers={"X-API-Key": "test-key-123"}
    )
    assert response.status_code == 200
    print(f"  ✓ {strategy}: PASSED")
print("✅ ALL STRATEGIES PASSED\n")

# Summary
print("=" * 70)
print("✅ ALL TESTS PASSED!")
print("=" * 70)
print()
print("📊 Test Summary:")
print("  • Health Check: ✓")
print("  • Authentication: ✓ (401 when missing)")
print("  • Strategy Listing: ✓")
print("  • Query Processing: ✓")
print("  • Input Validation: ✓")
print("  • All 5 Strategies: ✓")
print("  • Error Handling: ✓")
print()
print("🚀 API is ready for production!")
print()
