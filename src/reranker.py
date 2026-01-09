"""
Reranking Module

Implements document reranking using Cohere API for improved relevance ranking.
Reranking improves the final answer quality by prioritizing the most relevant
documents before passing them to the LLM.

Author: RAG Learning Journey - Day 16
"""

import logging
import os
from typing import List, Dict, Any
from tenacity import retry, stop_after_attempt, wait_exponential
import cohere

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Reranker:
    """Rerank documents using Cohere's rerank-english-v3.0 model."""

    def __init__(self, api_key: str = None, model: str = "rerank-english-v3.0"):
        """
        Initialize Reranker with Cohere client.

        Args:
            api_key: Cohere API key (uses env variable if not provided)
            model: Reranking model to use (default: rerank-english-v3.0)
        """
        # Get API key from parameter or environment variable
        if not api_key:
            api_key = os.getenv('COHERE_API_KEY') or os.getenv('CO_API_KEY')
        
        self.co = cohere.Client(api_key=api_key)
        self.model = model
        logger.info(f"Reranker initialized with model: {model}")

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def rerank_documents(
        self, query: str, documents: List[str], top_n: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Rerank documents based on relevance to the query.

        Uses Cohere's rerank model to assign relevance scores to documents.
        This is more accurate than semantic similarity alone because:
        - Considers semantic matching with query intent
        - Learns from human relevance judgments
        - Better at distinguishing subtle relevance differences

        Args:
            query: Search/ranking query
            documents: List of document texts to rerank
            top_n: Number of top documents to return

        Returns:
            List of dicts with 'document', 'index', and 'score' keys, sorted by relevance
        """
        if not documents:
            logger.warning("No documents provided for reranking")
            return []

        try:
            # Cohere rerank API call
            rerank_results = self.co.rerank(
                model=self.model,
                query=query,
                documents=documents,
                top_n=top_n,
            )

            # Format results
            ranked_documents = []
            for result in rerank_results.results:
                ranked_documents.append(
                    {
                        "document": documents[result.index],
                        "index": result.index,
                        "score": result.relevance_score,
                        "rank": len(ranked_documents) + 1,
                    }
                )

            logger.info(
                f"Reranked {len(documents)} documents to top {len(ranked_documents)}"
            )
            return ranked_documents

        except Exception as e:
            logger.error(f"Error reranking documents: {str(e)}")
            # Fallback: return documents in original order with zero scores
            return [
                {"document": doc, "index": idx, "score": 0.0, "rank": idx + 1}
                for idx, doc in enumerate(documents[:top_n])
            ]

    def rerank_with_metadata(
        self,
        query: str,
        documents: List[Dict[str, Any]],
        top_n: int = 5,
        text_key: str = "text",
    ) -> List[Dict[str, Any]]:
        """
        Rerank documents that include metadata.

        Args:
            query: Search/ranking query
            documents: List of dicts containing document info
            top_n: Number of top documents to return
            text_key: Key in dict containing the document text

        Returns:
            Reranked documents with original metadata preserved
        """
        if not documents:
            logger.warning("No documents provided for reranking")
            return []

        try:
            # Extract text from documents
            texts = [doc.get(text_key, str(doc)) for doc in documents]

            # Call Cohere rerank
            rerank_results = self.co.rerank(
                model=self.model,
                query=query,
                documents=texts,
                top_n=top_n,
            )

            # Reconstruct with original metadata
            ranked_documents = []
            for result in rerank_results.results:
                ranked_doc = documents[result.index].copy()
                ranked_doc["rerank_score"] = result.relevance_score
                ranked_doc["rerank_position"] = len(ranked_documents) + 1
                ranked_documents.append(ranked_doc)

            logger.info(
                f"Reranked {len(documents)} documents with metadata to top {len(ranked_documents)}"
            )
            return ranked_documents

        except Exception as e:
            logger.error(f"Error reranking documents with metadata: {str(e)}")
            # Fallback: return with zero scores
            result = []
            for i, doc in enumerate(documents[:top_n]):
                doc_copy = doc.copy()
                doc_copy["rerank_score"] = 0.0
                doc_copy["rerank_position"] = i + 1
                result.append(doc_copy)
            return result

    def batch_rerank(
        self, queries: List[str], documents: List[str], top_n: int = 5
    ) -> List[List[Dict[str, Any]]]:
        """
        Rerank the same documents for multiple queries.

        Useful for evaluating document quality across different questions.

        Args:
            queries: List of search queries
            documents: List of document texts
            top_n: Number of top documents per query

        Returns:
            List of reranked document lists, one per query
        """
        results = []
        for query in queries:
            ranked = self.rerank_documents(query, documents, top_n)
            results.append(ranked)
        return results

    def get_rerank_explanation(self, document: str, query: str) -> str:
        """
        Generate a brief explanation for why a document is relevant to a query.

        Args:
            document: Document text
            query: Search query

        Returns:
            Brief relevance explanation
        """
        # Simple heuristic: identify matching keywords
        doc_words = set(document.lower().split())
        query_words = set(query.lower().split())
        matching_words = doc_words.intersection(query_words)

        if matching_words:
            return f"Contains query keywords: {', '.join(list(matching_words)[:3])}"
        else:
            return "Semantically related to query topic"


if __name__ == "__main__":
    # Example usage
    import os
    from dotenv import load_dotenv

    load_dotenv()
    api_key = os.getenv("COHERE_API_KEY")

    reranker = Reranker(api_key=api_key)

    # Sample documents
    sample_docs = [
        "Focus on value-based selling to establish credibility with B2B clients",
        "Always start with small talk to build rapport",
        "Use data-driven insights to demonstrate ROI in your pitch",
        "Weather patterns affect seasonal sales in certain regions",
        "Develop multiple touchpoints throughout the sales process",
    ]

    test_query = "What are effective B2B sales techniques?"

    print("--- Reranking Documents ---")
    reranked = reranker.rerank_documents(test_query, sample_docs, top_n=3)

    for result in reranked:
        print(f"\nRank {result['rank']}: Score {result['score']:.3f}")
        print(f"Document: {result['document'][:80]}...")
