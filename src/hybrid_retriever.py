"""
Hybrid Retriever Module

Implements hybrid search combining:
- Dense retrieval (Pinecone with embeddings)
- Sparse retrieval (BM25 keyword search)
- Reciprocal Rank Fusion (RRF) for result combination

Author: RAG Learning Journey - Day 16
"""

import logging
from typing import List, Tuple, Dict, Any
import numpy as np
from rank_bm25 import BM25Okapi
from langchain_openai import OpenAIEmbeddings
from pinecone import Pinecone, ServerlessSpec

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class HybridRetriever:
    """Hybrid search combining dense embeddings and sparse keyword matching."""

    def __init__(
        self,
        index_name: str = "advanced-rag",
        api_key: str = None,
        dimension: int = 1536,  # OpenAI embedding dimension
    ):
        """
        Initialize HybridRetriever with Pinecone and BM25.

        Args:
            index_name: Pinecone index name
            api_key: Pinecone API key (uses env variable if not provided)
            dimension: Embedding dimension (default: 1536 for OpenAI)
        """
        self.index_name = index_name
        self.dimension = dimension

        # Initialize Pinecone (Pinecone 3.0+ syntax)
        try:
            self.pc = Pinecone(api_key=api_key) if api_key else Pinecone()
            # Create index if it doesn't exist
            if self.index_name not in self.pc.list_indexes().names():
                self.pc.create_index(
                    name=self.index_name,
                    dimension=dimension,
                    metric="cosine",
                    spec=ServerlessSpec(cloud="aws", region="us-east-1"),
                )
                logger.info(f"Created Pinecone index: {self.index_name}")
            self.index = self.pc.Index(self.index_name)
            logger.info(f"Connected to Pinecone index: {self.index_name}")
        except Exception as e:
            logger.error(f"Failed to initialize Pinecone: {str(e)}")
            self.index = None

        # Initialize embeddings
        self.embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small",  # Using smaller model for efficiency
            dimensions=dimension,
        )

        # BM25 for sparse search
        self.bm25 = None
        self.documents = []  # Store documents for BM25
        self.document_ids = []  # Track document IDs

        logger.info("HybridRetriever initialized successfully")

    def index_documents(
        self, texts: List[str], metadatas: List[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Index documents for both dense and sparse search.

        Args:
            texts: List of document texts
            metadatas: List of metadata dictionaries (optional)
            
        Returns:
            Dictionary with indexing statistics
        """
        if not texts:
            logger.warning("No texts provided for indexing")
            return {"success": False, "total_chunks": 0}

        try:
            # Store documents for BM25
            self.documents = texts
            self.document_ids = list(range(len(texts)))

            # Tokenize for BM25
            tokenized_docs = [doc.split() for doc in texts]
            self.bm25 = BM25Okapi(tokenized_docs)
            logger.info(f"Indexed {len(texts)} documents in BM25")

            # Index in Pinecone for dense search
            indexed_count = 0
            if self.index:
                embeddings_list = self.embeddings.embed_documents(texts)

                # Prepare vectors with metadata
                vectors = []
                for i, (text, embedding) in enumerate(zip(texts, embeddings_list)):
                    vector_id = f"doc_{i}"
                    metadata = metadatas[i] if metadatas else {}
                    metadata["text"] = text
                    vectors.append((vector_id, embedding, metadata))

                # Upsert in batches
                batch_size = 100
                for j in range(0, len(vectors), batch_size):
                    batch = vectors[j : j + batch_size]
                    self.index.upsert(vectors=batch)

                indexed_count = len(vectors)
                logger.info(f"Indexed {len(vectors)} documents in Pinecone")
            else:
                logger.warning("Pinecone index not available, skipping dense indexing")
                indexed_count = len(texts)

            return {
                "success": True,
                "total_chunks": len(texts),
                "indexed_in_pinecone": indexed_count,
                "indexed_in_bm25": len(texts),
            }

        except Exception as e:
            logger.error(f"Error indexing documents: {str(e)}")
            return {"success": False, "total_chunks": len(texts) if texts else 0, "error": str(e)}

    def dense_search(self, query: str, k: int = 5) -> List[Tuple[str, float]]:
        """
        Perform dense search using vector embeddings.

        Args:
            query: Search query
            k: Number of results to return

        Returns:
            List of (document, score) tuples
        """
        if not self.index:
            logger.warning("Pinecone index not available for dense search")
            return []

        try:
            # Embed query
            query_embedding = self.embeddings.embed_query(query)

            # Search Pinecone
            results = self.index.query(
                vector=query_embedding,
                top_k=k,
                include_metadata=True,
            )

            dense_results = []
            for match in results.get("matches", []):
                if "text" in match.get("metadata", {}):
                    text = match["metadata"]["text"]
                    score = match.get("score", 0.0)
                    dense_results.append((text, score))

            logger.info(f"Dense search returned {len(dense_results)} results")
            return dense_results

        except Exception as e:
            logger.error(f"Error in dense search: {str(e)}")
            return []

    def sparse_search(self, query: str, k: int = 5) -> List[Tuple[str, float]]:
        """
        Perform sparse search using BM25 keyword matching.

        Args:
            query: Search query
            k: Number of results to return

        Returns:
            List of (document, score) tuples
        """
        if not self.bm25 or not self.documents:
            logger.warning("BM25 index not available for sparse search")
            return []

        try:
            # Tokenize query
            query_tokens = query.split()

            # BM25 search
            scores = self.bm25.get_scores(query_tokens)

            # Get top k results
            top_indices = np.argsort(scores)[::-1][:k]
            sparse_results = [
                (self.documents[idx], float(scores[idx]))
                for idx in top_indices
                if scores[idx] > 0
            ]

            logger.info(f"Sparse search returned {len(sparse_results)} results")
            return sparse_results

        except Exception as e:
            logger.error(f"Error in sparse search: {str(e)}")
            return []

    @staticmethod
    def reciprocal_rank_fusion(
        dense_results: List[Tuple[str, float]],
        sparse_results: List[Tuple[str, float]],
        k: int = 60,
    ) -> List[Tuple[str, float]]:
        """
        Combine dense and sparse results using Reciprocal Rank Fusion (RRF).

        RRF Formula: score = sum(1 / (k + rank)) across all rankings
        This prevents single ranking from dominating the combined results.

        Args:
            dense_results: Results from dense search
            sparse_results: Results from sparse search
            k: Constant for RRF formula (default: 60)

        Returns:
            Combined and ranked results
        """
        fused_scores = {}

        # Process dense results
        for rank, (text, _) in enumerate(dense_results, 1):
            rrf_score = 1 / (k + rank)
            if text not in fused_scores:
                fused_scores[text] = 0
            fused_scores[text] += rrf_score

        # Process sparse results
        for rank, (text, _) in enumerate(sparse_results, 1):
            rrf_score = 1 / (k + rank)
            if text not in fused_scores:
                fused_scores[text] = 0
            fused_scores[text] += rrf_score

        # Sort by fused score
        fused_results = sorted(fused_scores.items(), key=lambda x: x[1], reverse=True)

        logger.info(f"RRF fusion combined results: {len(fused_results)} unique documents")
        return fused_results

    def hybrid_search(self, query: str, k: int = 5) -> List[Tuple[str, float]]:
        """
        Perform hybrid search combining dense and sparse retrieval.

        Process:
        1. Execute dense search (embeddings)
        2. Execute sparse search (BM25)
        3. Combine using Reciprocal Rank Fusion
        4. Return top k results

        Args:
            query: Search query
            k: Number of results to return

        Returns:
            List of (document, score) tuples
        """
        try:
            # Get dense results
            dense_results = self.dense_search(query, k=k)

            # Get sparse results
            sparse_results = self.sparse_search(query, k=k)

            if not dense_results and not sparse_results:
                logger.warning("No results from either dense or sparse search")
                return []

            # Fuse results
            fused = self.reciprocal_rank_fusion(dense_results, sparse_results, k=60)

            # Return top k
            hybrid_results = fused[:k]

            logger.info(
                f"Hybrid search returned {len(hybrid_results)} results for query: {query}"
            )
            return hybrid_results

        except Exception as e:
            logger.error(f"Error in hybrid search: {str(e)}")
            return []

    def clear_index(self) -> None:
        """Clear all documents from Pinecone index."""
        try:
            if self.index:
                self.index.delete(delete_all=True)
                self.documents = []
                self.document_ids = []
                self.bm25 = None
                logger.info("Index cleared successfully")
        except Exception as e:
            logger.error(f"Error clearing index: {str(e)}")


if __name__ == "__main__":
    # Example usage
    import os
    from dotenv import load_dotenv

    load_dotenv()

    retriever = HybridRetriever()

    # Sample documents
    sample_docs = [
        "Focus on value-based selling to establish credibility with B2B clients",
        "Build long-term relationships by understanding client pain points",
        "Use data-driven insights to demonstrate ROI in your sales pitch",
        "Develop multiple touchpoints throughout the sales process",
        "Leverage case studies and testimonials to build social proof",
    ]

    print("Indexing documents...")
    retriever.index_documents(sample_docs)

    test_query = "How to improve B2B sales techniques?"

    print("\n--- Dense Search ---")
    dense = retriever.dense_search(test_query, k=3)
    for text, score in dense:
        print(f"Score: {score:.3f} | {text[:80]}...")

    print("\n--- Sparse Search ---")
    sparse = retriever.sparse_search(test_query, k=3)
    for text, score in sparse:
        print(f"Score: {score:.3f} | {text[:80]}...")

    print("\n--- Hybrid Search (Dense + Sparse + RRF) ---")
    hybrid = retriever.hybrid_search(test_query, k=3)
    for text, score in hybrid:
        print(f"Score: {score:.3f} | {text[:80]}...")
