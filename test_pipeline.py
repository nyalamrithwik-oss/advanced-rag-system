"""
Test Suite for Advanced RAG System

Comprehensive testing for all RAG components:
- Query Transformer
- Hybrid Retriever
- Reranker
- Context Optimizer
- Full RAG Pipeline

Author: RAG Learning Journey - Day 16
"""

import pytest
import logging
from typing import List
from unittest.mock import patch, MagicMock
from src.query_transformer import QueryTransformer
from src.hybrid_retriever import HybridRetriever
from src.reranker import Reranker
from src.context_optimizer import ContextOptimizer
from src.rag_pipeline import AdvancedRAGPipeline

logging.basicConfig(level=logging.INFO)


class TestQueryTransformer:
    """Test QueryTransformer component."""

    @pytest.fixture
    def transformer(self):
        """Initialize transformer for testing."""
        return QueryTransformer()

    def test_rewrite_query_returns_string(self, transformer):
        """Test that query rewriting returns a string."""
        query = "B2B sales techniques"
        result = transformer.rewrite_query(query)
        assert isinstance(result, str)
        assert len(result) > 0

    def test_generate_multi_queries_returns_list(self, transformer):
        """Test that multi-query generation returns a list."""
        query = "What are sales strategies?"
        result = transformer.generate_multi_queries(query, num=3)
        assert isinstance(result, list)
        assert len(result) > 0

    def test_generate_hyde_document_returns_string(self, transformer):
        """Test that HyDE generation returns a string."""
        query = "Best sales techniques"
        result = transformer.generate_hyde_document(query)
        assert isinstance(result, str)


class TestHybridRetriever:
    """Test HybridRetriever component."""

    @pytest.fixture
    def retriever(self):
        """Initialize retriever for testing."""
        return HybridRetriever()

    def test_indexing_documents(self, retriever):
        """Test document indexing."""
        docs = [
            "Document about sales",
            "Document about pricing",
            "Document about negotiation",
        ]
        retriever.index_documents(docs)

        assert retriever.documents == docs
        assert retriever.bm25 is not None

    def test_sparse_search_returns_results(self, retriever):
        """Test sparse search functionality."""
        docs = [
            "Focus on value-based selling",
            "Understand client needs",
            "Demonstrate ROI clearly",
        ]
        retriever.index_documents(docs)

        results = retriever.sparse_search("value selling", k=2)
        assert isinstance(results, list)
        assert len(results) > 0

    def test_hybrid_search_combines_results(self, retriever):
        """Test hybrid search combination."""
        docs = [
            "Value-based selling approach",
            "Multi-threading in sales",
            "ROI demonstration techniques",
        ]
        retriever.index_documents(docs)

        results = retriever.hybrid_search("sales value", k=3)
        assert isinstance(results, list)
        # Should return results from hybrid combination
        assert len(results) <= 3

    def test_reciprocal_rank_fusion(self):
        """Test RRF fusion algorithm."""
        dense = [
            ("Document A", 0.9),
            ("Document B", 0.8),
            ("Document C", 0.7),
        ]
        sparse = [
            ("Document C", 2.5),
            ("Document A", 2.0),
            ("Document D", 1.5),
        ]

        fused = HybridRetriever.reciprocal_rank_fusion(dense, sparse, k=60)

        assert len(fused) > 0
        # Document A and C should have high scores (appear in both rankings)
        doc_texts = [doc for doc, _ in fused]
        assert "Document A" in doc_texts


class TestReranker:
    """Test Reranker component."""

    @pytest.fixture
    def reranker(self):
        """Initialize reranker for testing."""
        return Reranker()

    def test_rerank_documents_returns_list(self, reranker):
        """Test that reranking returns a list."""
        query = "B2B sales techniques"
        docs = [
            "Value-based selling approach",
            "Understanding client needs",
            "ROI demonstration",
        ]

        result = reranker.rerank_documents(query, docs, top_n=2)
        assert isinstance(result, list)

    def test_rerank_with_metadata(self, reranker):
        """Test reranking with metadata preservation."""
        query = "Sales strategy"
        docs = [
            {"text": "Value-based selling", "source": "doc1"},
            {"text": "ROI demonstration", "source": "doc2"},
        ]

        result = reranker.rerank_with_metadata(query, docs, top_n=2, text_key="text")
        assert isinstance(result, list)
        if result:
            assert "source" in result[0]  # Metadata preserved

    def test_batch_rerank(self, reranker):
        """Test batch reranking."""
        queries = ["sales technique", "negotiation skills"]
        docs = ["Value-based selling", "Negotiation tactics", "ROI demonstration"]

        result = reranker.batch_rerank(queries, docs, top_n=2)
        assert isinstance(result, list)
        assert len(result) == 2


class TestContextOptimizer:
    """Test ContextOptimizer component."""

    @pytest.fixture
    def optimizer(self):
        """Initialize optimizer for testing."""
        return ContextOptimizer(similarity_threshold=0.95)

    def test_deduplication(self, optimizer):
        """Test chunk deduplication."""
        chunks = [
            "Value-based selling is important",
            "Value-based selling is very important",  # Very similar
            "ROI demonstration techniques",
        ]

        dedup = optimizer.deduplicate_chunks(chunks, method="exact")
        assert len(dedup) >= 2  # At least non-exact duplicates

    def test_compression(self, optimizer):
        """Test context compression."""
        chunks = [
            "This is a long document " * 50,
            "Another document " * 50,
            "Short one",
        ]

        compressed = optimizer.compress_context(chunks, max_tokens=100)
        assert isinstance(compressed, str)
        # Compressed should be shorter than original
        original_tokens = sum(len(c) / 4 for c in chunks)
        compressed_tokens = len(compressed) / 4
        assert compressed_tokens <= original_tokens

    def test_optimize_for_llm(self, optimizer):
        """Test full optimization pipeline."""
        chunks = [
            "Value-based selling focuses on client ROI",
            "Understanding needs is critical",
            "ROI demonstration is key",
        ]
        query = "sales value ROI"

        optimized = optimizer.optimize_for_llm(chunks, query, max_tokens=1000)
        assert isinstance(optimized, str)
        assert len(optimized) > 0

    def test_get_optimization_stats(self, optimizer):
        """Test optimization statistics calculation."""
        chunks = ["Chunk 1", "Chunk 2", "Chunk 3"]
        context = "Optimized context"

        stats = optimizer.get_optimization_stats(chunks, context)
        assert "original_chunks" in stats
        assert "compression_ratio" in stats
        assert isinstance(stats["compression_ratio"], float)


class TestAdvancedRAGPipeline:
    """Test complete RAG Pipeline."""

    @pytest.fixture
    def pipeline(self):
        """Initialize pipeline for testing."""
        return AdvancedRAGPipeline()

    def test_pipeline_initialization(self, pipeline):
        """Test pipeline initializes all components."""
        assert pipeline.query_transformer is not None
        assert pipeline.retriever is not None
        assert pipeline.reranker is not None
        assert pipeline.context_optimizer is not None
        assert pipeline.llm is not None

    def test_document_chunking(self):
        """Test text chunking utility."""
        text = "This is a long document. " * 100
        chunks = AdvancedRAGPipeline._chunk_text(text, chunk_size=100, overlap=20)

        assert isinstance(chunks, list)
        assert len(chunks) > 1
        # Verify overlap
        if len(chunks) > 1:
            assert len(chunks[0]) + len(chunks[-1]) > len(text) / 2

    def test_query_basic_strategy(self, pipeline):
        """Test basic query strategy."""
        # Index documents first
        docs = ["Sales strategy", "ROI focus", "Client value"]
        pipeline.retriever.index_documents(docs)

        result = pipeline.query("What is sales?", strategy="basic")

        assert "answer" in result
        assert "retrieved_docs" in result
        assert "processing_time" in result
        assert result["strategy"] == "basic"

    def test_query_all_strategies(self, pipeline):
        """Test that all strategies execute without error."""
        docs = ["Document 1", "Document 2", "Document 3"]
        pipeline.retriever.index_documents(docs)

        strategies = ["basic", "rewritten", "multi_query", "hyde", "hybrid_rerank"]

        for strategy in strategies:
            result = pipeline.query("test query", strategy=strategy)
            assert "answer" in result
            assert result["strategy"] == strategy
            assert "processing_time" in result

    def test_error_handling(self, pipeline):
        """Test error handling in pipeline."""
        # Query without indexed documents
        result = pipeline.query("test query", strategy="basic")

        # Should not crash, should return gracefully
        assert isinstance(result, dict)
        assert "answer" in result


# Integration Tests
class TestIntegration:
    """Integration tests across components."""

    def test_end_to_end_pipeline(self):
        """Test complete pipeline execution."""
        pipeline = AdvancedRAGPipeline()

        # Index documents
        docs = [
            "Value-based selling focuses on ROI",
            "Understanding client needs is important",
            "Demonstrate clear business value",
        ]
        pipeline.retriever.index_documents(docs)

        # Query with different strategies
        results = {}
        for strategy in ["basic", "hybrid_rerank"]:
            result = pipeline.query("How to improve sales?", strategy=strategy)
            results[strategy] = result

        # Verify results
        assert len(results) == 2
        for strategy, result in results.items():
            assert isinstance(result, dict)
            assert "answer" in result
            assert result["strategy"] == strategy

    def test_component_compatibility(self):
        """Test that all components work together."""
        transformer = QueryTransformer()
        retriever = HybridRetriever()
        reranker = Reranker()
        optimizer = ContextOptimizer()

        # Index documents
        docs = ["Test document 1", "Test document 2"]
        retriever.index_documents(docs)

        query = "test"

        # Transform query
        rewritten = transformer.rewrite_query(query)
        assert isinstance(rewritten, str)

        # Retrieve
        retrieved = retriever.hybrid_search(rewritten, k=2)
        assert isinstance(retrieved, list)

        # Rerank
        if retrieved:
            doc_texts = [doc for doc, _ in retrieved]
            reranked = reranker.rerank_documents(query, doc_texts, top_n=2)
            assert isinstance(reranked, list)

        # Optimize
        if retrieved:
            optimized = optimizer.optimize_for_llm(doc_texts, query)
            assert isinstance(optimized, str)


if __name__ == "__main__":
    # Run tests with: pytest tests/test_pipeline.py -v
    pytest.main([__file__, "-v"])
