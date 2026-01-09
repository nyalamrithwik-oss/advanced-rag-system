"""
context_manager.py

Implements a context window manager for RAG systems.

Dependencies: tiktoken (for token estimation)
"""
from typing import List, Dict
import logging
import hashlib

try:
    import tiktoken
except ImportError:
    tiktoken = None

class ContextWindowManager:
    """
    Manages context windows for RAG, prioritizing relevant chunks, compressing, and tracking token usage.
    """
    def __init__(self):
        self.logger = logging.getLogger("ContextWindowManager")
        logging.basicConfig(level=logging.INFO)

    def estimate_tokens(self, text: str) -> int:
        """
        Estimates the number of tokens in the text using tiktoken (GPT-4 encoding).
        Returns:
            int: Estimated token count
        """
        if tiktoken is None:
            raise ImportError("tiktoken is required for token estimation.")
        enc = tiktoken.encoding_for_model("gpt-4")
        return len(enc.encode(text))

    def compress_context(self, chunks: List[Dict]) -> List[Dict]:
        """
        Removes duplicate or redundant chunks based on text hash.
        Returns:
            List[Dict]: Compressed list of chunks
        """
        seen = set()
        compressed = []
        for chunk in chunks:
            text_hash = hashlib.md5(chunk["text"].strip().encode("utf-8")).hexdigest()
            if text_hash not in seen:
                compressed.append(chunk)
                seen.add(text_hash)
        self.logger.info(f"Compressed context: {len(chunks)} → {len(compressed)} chunks.")
        return compressed

    def optimize_context(self, chunks: List[Dict], max_tokens: int = 3000) -> List[Dict]:
        """
        Selects the most relevant chunks within the token limit, sorted by relevance_score.
        Tracks token usage and logs details.
        Returns:
            List[Dict]: Optimized list of chunks
        """
        if not chunks:
            return []
        # Remove duplicates
        chunks = self.compress_context(chunks)
        # Sort by relevance_score (descending)
        sorted_chunks = sorted(chunks, key=lambda c: c.get("relevance_score", 0), reverse=True)
        selected = []
        total_tokens = 0
        for chunk in sorted_chunks:
            chunk_tokens = self.estimate_tokens(chunk["text"])
            if total_tokens + chunk_tokens > max_tokens:
                break
            selected.append(chunk)
            total_tokens += chunk_tokens
        self.logger.info(f"Token usage: {total_tokens}/{max_tokens} tokens for {len(selected)} chunks.")
        return selected
