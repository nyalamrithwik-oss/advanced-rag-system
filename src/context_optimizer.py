"""
Context Optimization Module

Implements context optimization techniques:
- Deduplication: Remove similar/duplicate chunks
- Compression: Reduce context while preserving information
- Query-Aware Optimization: Prioritize query-relevant content

Author: RAG Learning Journey - Day 16
"""

import logging
from typing import List, Tuple
from langchain_openai import OpenAIEmbeddings
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ContextOptimizer:
    """Optimize retrieved context for better LLM performance."""

    def __init__(self, similarity_threshold: float = 0.95):
        """
        Initialize ContextOptimizer.

        Args:
            similarity_threshold: Cosine similarity threshold for deduplication (0-1)
        """
        self.similarity_threshold = similarity_threshold
        self.embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small",
            dimensions=1536,
        )
        logger.info(f"ContextOptimizer initialized with threshold: {similarity_threshold}")

    def deduplicate_chunks(
        self, chunks: List[str], method: str = "cosine"
    ) -> List[str]:
        """
        Remove duplicate or highly similar chunks.

        Uses semantic similarity to identify near-duplicate content.
        This prevents redundancy in the context window.

        Args:
            chunks: List of text chunks
            method: Similarity method ('cosine', 'exact')

        Returns:
            Deduplicated list of chunks
        """
        if len(chunks) <= 1:
            return chunks

        try:
            if method == "exact":
                # Simple exact duplicate removal
                return list(dict.fromkeys(chunks))

            # Semantic deduplication using cosine similarity
            embeddings_list = self.embeddings.embed_documents(chunks)
            embeddings_array = np.array(embeddings_list)

            # Calculate similarity matrix
            similarity_matrix = cosine_similarity(embeddings_array)

            # Identify duplicates
            unique_indices = []
            for i in range(len(chunks)):
                is_duplicate = False
                for j in unique_indices:
                    if similarity_matrix[i][j] > self.similarity_threshold:
                        is_duplicate = True
                        break
                if not is_duplicate:
                    unique_indices.append(i)

            deduplicated = [chunks[i] for i in sorted(unique_indices)]
            logger.info(
                f"Deduplication: {len(chunks)} -> {len(deduplicated)} chunks (removed {len(chunks) - len(deduplicated)})"
            )
            return deduplicated

        except Exception as e:
            logger.error(f"Error in deduplication: {str(e)}")
            return chunks

    def compress_context(self, chunks: List[str], max_tokens: int = 2000) -> str:
        """
        Compress context to fit within token limits.

        Selects the most representative chunks to stay within token budget.
        Uses a simple heuristic: length-weighted selection.

        Args:
            chunks: List of text chunks
            max_tokens: Maximum tokens in compressed context

        Returns:
            Compressed context string
        """
        if not chunks:
            return ""

        try:
            # Rough token estimate: 1 token ≈ 4 characters
            tokens_per_chunk = [len(chunk) / 4 for chunk in chunks]
            total_tokens = sum(tokens_per_chunk)

            # If within limit, return concatenated
            if total_tokens <= max_tokens:
                return "\n\n".join(chunks)

            # Select chunks to fit within budget
            selected_chunks = []
            current_tokens = 0
            for chunk, tokens in sorted(
                zip(chunks, tokens_per_chunk), key=lambda x: len(x[0]), reverse=True
            ):
                if current_tokens + tokens <= max_tokens:
                    selected_chunks.append(chunk)
                    current_tokens += tokens

            logger.info(
                f"Compression: {total_tokens:.0f} -> {current_tokens:.0f} tokens ({len(chunks)} -> {len(selected_chunks)} chunks)"
            )
            return "\n\n".join(selected_chunks)

        except Exception as e:
            logger.error(f"Error in compression: {str(e)}")
            return "\n\n".join(chunks[:5])  # Fallback: first 5 chunks

    def optimize_for_llm(
        self, chunks: List[str], query: str, max_tokens: int = 2000
    ) -> str:
        """
        Optimize context for LLM consumption.

        Pipeline:
        1. Deduplicate similar chunks
        2. Rank by relevance to query
        3. Compress to fit token limit
        4. Add formatting for clarity

        Args:
            chunks: List of retrieved chunks
            query: User query for relevance ranking
            max_tokens: Maximum context tokens

        Returns:
            Optimized context string ready for LLM
        """
        if not chunks:
            return ""

        try:
            # Step 1: Deduplication
            deduplicated = self.deduplicate_chunks(chunks)
            logger.info(f"Step 1 - Deduplication: {len(chunks)} -> {len(deduplicated)}")

            # Step 2: Relevance ranking (simple keyword matching)
            query_keywords = set(query.lower().split())
            scored_chunks = []

            for chunk in deduplicated:
                chunk_keywords = set(chunk.lower().split())
                relevance_score = len(query_keywords.intersection(chunk_keywords))
                scored_chunks.append((chunk, relevance_score))

            # Sort by relevance (descending)
            scored_chunks.sort(key=lambda x: x[1], reverse=True)
            ranked_chunks = [chunk for chunk, _ in scored_chunks]
            logger.info(f"Step 2 - Relevance ranking: ranked {len(ranked_chunks)} chunks")

            # Step 3: Compression
            compressed = self.compress_context(ranked_chunks, max_tokens)
            logger.info(f"Step 3 - Compression: compressed to fit token budget")

            # Step 4: Format for clarity
            formatted = self._format_context(compressed)
            logger.info(f"Step 4 - Formatting: added structure markers")

            return formatted

        except Exception as e:
            logger.error(f"Error in optimization: {str(e)}")
            return "\n\n".join(chunks[:3])  # Fallback

    @staticmethod
    def _format_context(context: str) -> str:
        """
        Add formatting to context for better LLM comprehension.

        Args:
            context: Raw context string

        Returns:
            Formatted context with clear structure
        """
        sections = context.split("\n\n")
        formatted_sections = []

        for i, section in enumerate(sections, 1):
            # Add section markers
            formatted = f"[Source {i}]\n{section}"
            formatted_sections.append(formatted)

        return "\n\n".join(formatted_sections)

    def calculate_compression_ratio(
        self, original_chunks: List[str], optimized_context: str
    ) -> float:
        """
        Calculate compression ratio.

        Args:
            original_chunks: Original list of chunks
            optimized_context: Optimized context string

        Returns:
            Compression ratio (0-1, lower is more compressed)
        """
        original_chars = sum(len(chunk) for chunk in original_chunks)
        optimized_chars = len(optimized_context)

        if original_chars == 0:
            return 1.0

        ratio = optimized_chars / original_chars
        return ratio

    def get_optimization_stats(
        self, original_chunks: List[str], optimized_context: str
    ) -> dict:
        """
        Get detailed statistics about optimization.

        Args:
            original_chunks: Original list of chunks
            optimized_context: Optimized context string

        Returns:
            Dictionary with optimization statistics
        """
        return {
            "original_chunks": len(original_chunks),
            "original_characters": sum(len(chunk) for chunk in original_chunks),
            "original_tokens_estimate": sum(len(chunk) / 4 for chunk in original_chunks),
            "optimized_characters": len(optimized_context),
            "optimized_tokens_estimate": len(optimized_context) / 4,
            "compression_ratio": self.calculate_compression_ratio(
                original_chunks, optimized_context
            ),
        }


if __name__ == "__main__":
    # Example usage
    import os
    from dotenv import load_dotenv

    load_dotenv()

    optimizer = ContextOptimizer(similarity_threshold=0.95)

    # Sample chunks
    sample_chunks = [
        "Focus on value-based selling to establish credibility with B2B clients",
        "Value-based selling is important for building trust with business clients",
        "Use data-driven insights to demonstrate ROI in your sales pitch",
        "Data and metrics help show the return on investment to prospects",
        "Develop multiple touchpoints throughout the sales process",
    ]

    test_query = "How to improve B2B sales?"

    print("--- Original Chunks ---")
    for i, chunk in enumerate(sample_chunks, 1):
        print(f"{i}. {chunk}")

    print("\n--- Deduplicated Chunks ---")
    dedup = optimizer.deduplicate_chunks(sample_chunks)
    for i, chunk in enumerate(dedup, 1):
        print(f"{i}. {chunk}")

    print("\n--- Optimized Context ---")
    optimized = optimizer.optimize_for_llm(sample_chunks, test_query, max_tokens=500)
    print(optimized)

    print("\n--- Optimization Stats ---")
    stats = optimizer.get_optimization_stats(sample_chunks, optimized)
    for key, value in stats.items():
        print(f"{key}: {value}")
