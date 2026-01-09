"""
citation_tracker.py

Implements a citation system for RAG answers.
"""
from typing import List, Dict
import re

class CitationTracker:
    """
    Tracks and adds inline citations to generated answers, mapping facts to source chunks.
    """
    def add_citations(self, answer: str, source_chunks: List[Dict]) -> str:
        """
        Adds inline citations to the answer after each major claim, referencing source chunks.
        Also creates a references section at the end.
        Args:
            answer (str): The generated answer text
            source_chunks (List[Dict]): Chunks with metadata (filename, chunk_id, relevance_score, etc.)
        Returns:
            str: Answer with inline citations and references section
        """
        if not answer or not source_chunks:
            return answer
        # Map chunk_id to citation string
        citations = {}
        for chunk in source_chunks:
            meta = chunk.get("metadata", {})
            filename = meta.get("filename", "unknown.txt")
            chunk_id = meta.get("chunk_id", 0)
            score = chunk.get("relevance_score", 0.0)
            citations[chunk_id] = f"[Source: {filename}, Chunk #{chunk_id}, Score: {score:.2f}]"
        # Insert citations after sentences/claims (simple heuristic: after periods)
        sentences = re.split(r'(\.|\!|\?)', answer)
        cited_answer = ""
        used_chunks = set()
        for i in range(0, len(sentences)-1, 2):
            sent = sentences[i].strip()
            punct = sentences[i+1] if i+1 < len(sentences) else ''
            if not sent:
                continue
            # Find most relevant chunk for this sentence
            best_chunk = max(source_chunks, key=lambda c: c.get("relevance_score", 0))
            meta = best_chunk.get("metadata", {})
            chunk_id = meta.get("chunk_id", 0)
            citation = citations.get(chunk_id, "")
            cited_answer += f"{sent}{punct} {citation} "
            used_chunks.add(chunk_id)
        # Add any remaining text
        if len(sentences) % 2 == 1:
            cited_answer += sentences[-1]
        # References section
        references = "\n\nReferences:\n"
        for chunk in source_chunks:
            meta = chunk.get("metadata", {})
            filename = meta.get("filename", "unknown.txt")
            chunk_id = meta.get("chunk_id", 0)
            score = chunk.get("relevance_score", 0.0)
            references += f"- [Source: {filename}, Chunk #{chunk_id}, Score: {score:.2f}]\n"
        return cited_answer.strip() + references
