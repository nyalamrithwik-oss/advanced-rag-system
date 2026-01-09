"""
chunking_strategies.py

Implements advanced chunking strategies for RAG systems.

Dependencies: spacy (for sentence detection)
"""
from typing import List, Dict
import re

try:
    import spacy
    nlp = spacy.load('en_core_web_sm')
except Exception:
    nlp = None

class ChunkingStrategy:
    """
    Provides multiple intelligent chunking strategies for text documents.
    Each method returns a list of dicts with chunk text and metadata.
    """

    @staticmethod
    def semantic_chunk(text: str) -> List[Dict]:
        """
        Splits text into semantically meaningful chunks using sentence boundaries.
        Uses spaCy for sentence detection. Each chunk is a sentence with metadata.
        Handles empty or very short text.
        Returns:
            List[Dict]: [{"text": str, "metadata": {"chunk_id": int, "start_char": int, "end_char": int}}]
        """
        if not text or not text.strip():
            return []
        if nlp is None:
            raise ImportError("spaCy and the 'en_core_web_sm' model are required for semantic chunking.")
        doc = nlp(text)
        chunks = []
        for i, sent in enumerate(doc.sents):
            chunk = {
                "text": sent.text,
                "metadata": {
                    "chunk_id": i,
                    "start_char": sent.start_char,
                    "end_char": sent.end_char
                }
            }
            chunks.append(chunk)
        return chunks

    @staticmethod
    def recursive_chunk(text: str) -> List[Dict]:
        """
        Recursively splits text respecting document structure: sections → paragraphs → sentences.
        Returns chunks with metadata. Handles empty or very short text.
        Returns:
            List[Dict]: [{"text": str, "metadata": {"chunk_id": int, "start_char": int, "end_char": int}}]
        """
        if not text or not text.strip():
            return []
        if nlp is None:
            raise ImportError("spaCy and the 'en_core_web_sm' model are required for recursive chunking.")
        # Split by sections (simple heuristic: lines with === or --- or ##)
        section_pattern = re.compile(r"(^\s*(#|=|-){2,}.*$)", re.MULTILINE)
        sections = section_pattern.split(text)
        chunks = []
        chunk_id = 0
        pos = 0
        for section in sections:
            if not section.strip():
                pos += len(section)
                continue
            # Split by paragraphs (double newlines)
            paragraphs = [p for p in section.split('\n\n') if p.strip()]
            for para in paragraphs:
                para_start = text.find(para, pos)
                para_end = para_start + len(para)
                doc = nlp(para)
                for sent in doc.sents:
                    chunk = {
                        "text": sent.text,
                        "metadata": {
                            "chunk_id": chunk_id,
                            "start_char": sent.start_char + para_start,
                            "end_char": sent.end_char + para_start
                        }
                    }
                    chunks.append(chunk)
                    chunk_id += 1
                pos = para_end
        return chunks

    @staticmethod
    def sliding_window_chunk(text: str, window_size: int = 500, overlap: int = 100) -> List[Dict]:
        """
        Splits text into overlapping windows of fixed character size.
        Each chunk is window_size chars, overlapping by 'overlap'.
        Handles edge cases (empty, short text).
        Returns:
            List[Dict]: [{"text": str, "metadata": {"chunk_id": int, "start_char": int, "end_char": int}}]
        """
        if not text or not text.strip():
            return []
        chunks = []
        length = len(text)
        chunk_id = 0
        start = 0
        while start < length:
            end = min(start + window_size, length)
            chunk = {
                "text": text[start:end],
                "metadata": {
                    "chunk_id": chunk_id,
                    "start_char": start,
                    "end_char": end
                }
            }
            chunks.append(chunk)
            if end == length:
                break
            start += window_size - overlap
            chunk_id += 1
        return chunks
