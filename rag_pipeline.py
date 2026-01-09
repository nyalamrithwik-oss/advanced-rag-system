"""
Advanced RAG Pipeline Module

Orchestrates all components (query transformation, hybrid retrieval,
reranking, context optimization) into a complete RAG system.

Supports multiple strategies:
- Basic: Simple retrieval
- Rewritten: With query rewriting
- Multi-Query: Multiple reformulations
- HyDE: Hypothetical document embeddings
- Hybrid-Rerank: Full advanced stack

Author: RAG Learning Journey - Day 16
"""

import logging
import time
from typing import List, Dict, Any
from pathlib import Path
import PyPDF2
from docx import Document
from query_transformer import QueryTransformer
from hybrid_retriever import HybridRetriever
from reranker import Reranker
from context_optimizer import ContextOptimizer
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AdvancedRAGPipeline:
    """Orchestrate advanced RAG techniques for question answering."""

    def __init__(self):
        """Initialize all RAG components."""
        try:
            self.query_transformer = QueryTransformer()
            self.retriever = HybridRetriever()
            self.reranker = Reranker()
            self.context_optimizer = ContextOptimizer()
            self.llm = ChatOpenAI(
                model="gpt-4-turbo-preview",
                temperature=0.7,
                max_tokens=1000,
            )
            logger.info("AdvancedRAGPipeline initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing pipeline: {str(e)}")
            raise

    def ingest_documents(self, file_paths: List[str]) -> Dict[str, Any]:
        """
        Process and index documents from various file types.

        Supports: PDF, DOCX, TXT, MD

        Args:
            file_paths: List of file paths to ingest

        Returns:
            Dictionary with ingestion statistics
        """
        documents = []
        metadatas = []
        stats = {"total_files": len(file_paths), "successful": 0, "failed": 0}

        for file_path in file_paths:
            try:
                path = Path(file_path)
                content = None

                # Extract text based on file type
                if path.suffix.lower() == ".pdf":
                    content = self._extract_pdf(file_path)
                elif path.suffix.lower() == ".docx":
                    content = self._extract_docx(file_path)
                elif path.suffix.lower() in [".txt", ".md"]:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                else:
                    logger.warning(f"Unsupported file type: {path.suffix}")
                    stats["failed"] += 1
                    continue

                if content:
                    # Split into chunks
                    chunks = self._chunk_text(content, chunk_size=500, overlap=100)
                    documents.extend(chunks)
                    metadatas.extend(
                        [{"source": path.name, "chunk_index": i}
                         for i in range(len(chunks))]
                    )
                    stats["successful"] += 1
                    logger.info(
                        f"Ingested {path.name}: {len(chunks)} chunks from {len(content)} chars"
                    )

            except Exception as e:
                logger.error(f"Error ingesting {file_path}: {str(e)}")
                stats["failed"] += 1

        # Index documents
        if documents:
            self.retriever.index_documents(documents, metadatas)
            stats["total_chunks"] = len(documents)
            logger.info(f"Ingestion complete: {stats}")

        return stats

    @staticmethod
    def _extract_pdf(file_path: str) -> str:
        """Extract text from PDF file."""
        text = []
        try:
            with open(file_path, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    text.append(page.extract_text())
            return "\n\n".join(text)
        except Exception as e:
            logger.error(f"Error extracting PDF: {str(e)}")
            return ""

    @staticmethod
    def _extract_docx(file_path: str) -> str:
        """Extract text from DOCX file."""
        try:
            doc = Document(file_path)
            text = [paragraph.text for paragraph in doc.paragraphs]
            return "\n\n".join(text)
        except Exception as e:
            logger.error(f"Error extracting DOCX: {str(e)}")
            return ""

    @staticmethod
    def _chunk_text(
        text: str, chunk_size: int = 500, overlap: int = 100
    ) -> List[str]:
        """
        Split text into overlapping chunks.

        Args:
            text: Input text
            chunk_size: Size of each chunk (characters)
            overlap: Overlap between chunks

        Returns:
            List of text chunks
        """
        chunks = []
        start = 0
        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]
            if chunk.strip():
                chunks.append(chunk)
            start = end - overlap
        return chunks if chunks else [text]

    def query(
        self,
        question: str,
        strategy: str = "hybrid_rerank",
        num_results: int = 5,
    ) -> Dict[str, Any]:
        """
        Execute RAG pipeline with specified strategy.

        Strategies:
        - 'basic': Direct retrieval
        - 'rewritten': With query rewriting
        - 'multi_query': Multiple reformulations
        - 'hyde': Hypothetical document embeddings
        - 'hybrid_rerank': Full advanced stack

        Args:
            question: User question
            strategy: Strategy to use
            num_results: Number of retrieved documents

        Returns:
            Dictionary with answer, retrieved docs, and metadata
        """
        start_time = time.time()

        try:
            # Select strategy
            if strategy == "basic":
                result = self._strategy_basic(question, num_results)
            elif strategy == "rewritten":
                result = self._strategy_rewritten(question, num_results)
            elif strategy == "multi_query":
                result = self._strategy_multi_query(question, num_results)
            elif strategy == "hyde":
                result = self._strategy_hyde(question, num_results)
            elif strategy == "hybrid_rerank":
                result = self._strategy_hybrid_rerank(question, num_results)
            else:
                logger.warning(f"Unknown strategy: {strategy}")
                result = self._strategy_basic(question, num_results)

            # Add metadata
            result["strategy"] = strategy
            result["processing_time"] = time.time() - start_time
            result["question"] = question

            logger.info(
                f"Query processed in {result['processing_time']:.2f}s using {strategy}"
            )
            return result

        except Exception as e:
            logger.error(f"Error in query processing: {str(e)}")
            return {
                "question": question,
                "answer": f"Error processing query: {str(e)}",
                "retrieved_docs": [],
                "strategy": strategy,
                "processing_time": time.time() - start_time,
                "error": str(e),
            }

    def _strategy_basic(self, question: str, num_results: int) -> Dict[str, Any]:
        """Basic retrieval without transformation."""
        retrieved = self.retriever.hybrid_search(question, k=num_results)
        docs = [doc for doc, score in retrieved]

        answer = self._generate_answer(question, docs)

        return {
            "answer": answer,
            "retrieved_docs": retrieved,
            "num_retrieved": len(retrieved),
        }

    def _strategy_rewritten(self, question: str, num_results: int) -> Dict[str, Any]:
        """Retrieval with query rewriting."""
        rewritten = self.query_transformer.rewrite_query(question)
        retrieved = self.retriever.hybrid_search(rewritten, k=num_results)
        docs = [doc for doc, score in retrieved]

        answer = self._generate_answer(question, docs)

        return {
            "answer": answer,
            "retrieved_docs": retrieved,
            "num_retrieved": len(retrieved),
            "transformed_query": rewritten,
        }

    def _strategy_multi_query(self, question: str, num_results: int) -> Dict[str, Any]:
        """Retrieval with multiple query reformulations."""
        multi_queries = self.query_transformer.generate_multi_queries(
            question, num=3
        )

        all_docs = {}
        for query in multi_queries:
            retrieved = self.retriever.hybrid_search(query, k=num_results)
            for doc, score in retrieved:
                if doc not in all_docs:
                    all_docs[doc] = 0
                all_docs[doc] += score

        # Sort by combined score
        sorted_docs = sorted(all_docs.items(), key=lambda x: x[1], reverse=True)
        retrieved = sorted_docs[:num_results]
        docs = [doc for doc, _ in retrieved]

        answer = self._generate_answer(question, docs)

        return {
            "answer": answer,
            "retrieved_docs": retrieved,
            "num_retrieved": len(retrieved),
            "queries_used": multi_queries,
        }

    def _strategy_hyde(self, question: str, num_results: int) -> Dict[str, Any]:
        """Retrieval using HyDE (Hypothetical Document Embeddings)."""
        hyde_doc = self.query_transformer.generate_hyde_document(question)
        retrieved = self.retriever.hybrid_search(hyde_doc, k=num_results)
        docs = [doc for doc, score in retrieved]

        answer = self._generate_answer(question, docs)

        return {
            "answer": answer,
            "retrieved_docs": retrieved,
            "num_retrieved": len(retrieved),
            "hyde_document": hyde_doc[:200] + "...",
        }

    def _strategy_hybrid_rerank(
        self, question: str, num_results: int
    ) -> Dict[str, Any]:
        """Full advanced stack: Query rewriting + Hybrid search + Reranking + Optimization."""
        # Query rewriting
        rewritten = self.query_transformer.rewrite_query(question)

        # Hybrid retrieval
        retrieved = self.retriever.hybrid_search(rewritten, k=num_results * 2)
        docs_for_rerank = [doc for doc, _ in retrieved]

        # Reranking
        reranked = self.reranker.rerank_documents(
            question, docs_for_rerank, top_n=num_results
        )
        docs = [item["document"] for item in reranked]

        # Context optimization
        optimized_context = self.context_optimizer.optimize_for_llm(
            docs, question, max_tokens=2000
        )

        # Generate answer
        answer = self._generate_answer(question, docs, optimized_context)

        return {
            "answer": answer,
            "retrieved_docs": [(doc, score["score"]) for doc, score in zip(docs, reranked)],
            "num_retrieved": len(docs),
            "transformed_query": rewritten,
            "reranked": True,
            "context_compressed": True,
        }

    def _generate_answer(
        self, question: str, docs: List[str], context: str = None
    ) -> str:
        """
        Generate answer using LLM with retrieved context.

        Args:
            question: User question
            docs: Retrieved documents
            context: Pre-optimized context (optional)

        Returns:
            Generated answer
        """
        if not docs:
            return "No relevant documents found to answer this question."

        try:
            # Use provided context or create from docs
            if context is None:
                context = "\n\n".join(docs)

            system_prompt = """You are an expert assistant. Answer the user's question based on 
the provided context. Be concise, specific, and cite the relevant context when possible.

If the context doesn't contain information to answer the question, say so clearly."""

            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(
                    content=f"Context:\n{context}\n\nQuestion: {question}\n\nProvide a clear, concise answer."
                ),
            ]

            response = self.llm.invoke(messages)
            return response.content

        except Exception as e:
            logger.error(f"Error generating answer: {str(e)}")
            return f"Error generating answer: {str(e)}"

    def clear_index(self) -> None:
        """Clear all indexed documents."""
        self.retriever.clear_index()
        logger.info("Index cleared")


if __name__ == "__main__":
    # Example usage
    import os
    from dotenv import load_dotenv

    load_dotenv()

    pipeline = AdvancedRAGPipeline()

    # Sample documents for testing (can also use ingest_documents)
    sample_docs = [
        "Focus on value-based selling to establish credibility with B2B clients",
        "Use data-driven insights to demonstrate ROI in your sales pitch",
        "Develop multiple touchpoints throughout the sales process",
        "Build long-term relationships by understanding client pain points",
        "Leverage case studies and testimonials to build social proof",
    ]

    pipeline.retriever.index_documents(sample_docs)

    test_question = "What are the best B2B sales techniques?"

    print("\n=== Testing Different Strategies ===\n")

    for strategy in ["basic", "rewritten", "hybrid_rerank"]:
        print(f"\n--- Strategy: {strategy.upper()} ---")
        result = pipeline.query(test_question, strategy=strategy)
        print(f"Answer: {result['answer'][:150]}...")
        print(f"Time: {result['processing_time']:.2f}s")
        print(f"Docs Retrieved: {result['num_retrieved']}")
