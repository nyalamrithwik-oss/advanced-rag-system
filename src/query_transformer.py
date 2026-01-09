"""
Query Transformation Module

Implements advanced query transformation techniques:
- Query Rewriting: Reformulate queries for better retrieval
- Multi-Query: Generate multiple query variations
- HyDE (Hypothetical Document Embeddings): Generate synthetic documents

Author: RAG Learning Journey - Day 16
"""

import logging
from typing import List
from tenacity import retry, stop_after_attempt, wait_exponential
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.schema import HumanMessage, SystemMessage

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class QueryTransformer:
    """Transform and augment user queries for improved RAG performance."""

    def __init__(self, api_key: str = None, model: str = "gpt-4-turbo-preview"):
        """
        Initialize QueryTransformer with OpenAI client.

        Args:
            api_key: OpenAI API key (uses env variable if not provided)
            model: LLM model to use (default: gpt-4-turbo-preview)
        """
        self.llm = ChatOpenAI(
            api_key=api_key,
            model=model,
            temperature=0.1,  # Low temperature for consistent rewrites
            max_tokens=500,
            request_timeout=30,
        )
        self.model = model
        logger.info(f"QueryTransformer initialized with model: {model}")

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def rewrite_query(self, query: str) -> str:
        """
        Rewrite a query to improve retrieval clarity and specificity.

        Technique: Query Rewriting
        - Adds relevant context
        - Removes ambiguity
        - Improves search term quality

        Args:
            query: Original user query

        Returns:
            Rewritten query optimized for retrieval
        """
        try:
            system_prompt = """You are an expert query optimization specialist. Your task is to rewrite 
user queries to be more specific, clear, and optimized for semantic search.

Guidelines:
- Add context clues if the query seems ambiguous
- Use specific terminology related to the domain
- Expand abbreviations
- Focus on key concepts
- Keep the rewritten query concise but comprehensive"""

            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(
                    content=f"Rewrite this query for optimal retrieval: {query}\n\nProvide ONLY the rewritten query, no explanation."
                ),
            ]

            response = self.llm.invoke(messages)
            rewritten = response.content.strip()

            logger.info(f"Query rewritten: '{query}' -> '{rewritten}'")
            return rewritten

        except Exception as e:
            logger.error(f"Error rewriting query: {str(e)}")
            return query  # Fallback to original query

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def generate_multi_queries(self, query: str, num: int = 3) -> List[str]:
        """
        Generate multiple query variations to improve recall.

        Technique: Multi-Query Retrieval
        - Generates {num} different formulations of the same question
        - Helps retrieve documents that use different terminology
        - Increases chance of finding relevant information

        Args:
            query: Original user query
            num: Number of alternative queries to generate (default: 3)

        Returns:
            List of alternative query formulations
        """
        try:
            system_prompt = f"""You are an expert at generating diverse query variations. 
Your task is to generate {num} different ways to ask the same question.

Guidelines:
- Vary vocabulary and phrasing
- Some queries should be more specific, others more general
- Consider different perspectives or angles
- Each query should be able to retrieve relevant documents independently
- Use technical terms when appropriate"""

            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(
                    content=f"Generate {num} different ways to ask this question: {query}\n\nFormat: Return one query per line, numbered 1-{num}."
                ),
            ]

            response = self.llm.invoke(messages)
            lines = response.content.strip().split("\n")

            queries = []
            for line in lines:
                # Remove numbering and clean up
                cleaned = line.strip()
                if cleaned and not cleaned[0].isdigit():
                    queries.append(cleaned)
                elif cleaned and cleaned[0].isdigit():
                    # Remove leading number and period/dot
                    cleaned = cleaned.split(".", 1)[-1].strip()
                    if cleaned:
                        queries.append(cleaned)

            queries = queries[:num]  # Ensure we return exactly num queries
            logger.info(f"Generated {len(queries)} alternative queries")
            return queries if queries else [query]

        except Exception as e:
            logger.error(f"Error generating multi-queries: {str(e)}")
            return [query]  # Fallback to original query

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def generate_hyde_document(self, query: str) -> str:
        """
        Generate a hypothetical document that would answer the query.

        Technique: HyDE (Hypothetical Document Embeddings)
        - Generates a synthetic document that would contain the answer
        - Uses semantic similarity to find real documents
        - Effective when queries don't match document language

        Args:
            query: User question/query

        Returns:
            Hypothetical document text that would answer the query
        """
        try:
            system_prompt = """You are an expert document generator. Your task is to write a hypothetical 
document that would comprehensively answer the given user question.

Guidelines:
- Write as if you're authoring a detailed response document
- Include relevant context and details
- Use professional language appropriate to the domain
- Make it substantial (200-300 words)
- Focus on directly addressing the question"""

            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(
                    content=f"Write a hypothetical document that comprehensively answers this question: {query}"
                ),
            ]

            response = self.llm.invoke(messages)
            hyde_document = response.content.strip()

            logger.info(f"HyDE document generated ({len(hyde_document.split())} words)")
            return hyde_document

        except Exception as e:
            logger.error(f"Error generating HyDE document: {str(e)}")
            return ""  # Fallback to empty string

    def transform_query(self, query: str, transformation_type: str = "rewrite") -> str:
        """
        Apply a specific transformation to a query.

        Args:
            query: Input query
            transformation_type: Type of transformation - 'rewrite', 'hyde'

        Returns:
            Transformed query
        """
        if transformation_type == "rewrite":
            return self.rewrite_query(query)
        elif transformation_type == "hyde":
            return self.generate_hyde_document(query)
        else:
            logger.warning(f"Unknown transformation type: {transformation_type}")
            return query


if __name__ == "__main__":
    # Example usage
    import os
    from dotenv import load_dotenv

    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")

    transformer = QueryTransformer(api_key=api_key)

    test_query = "What are the best B2B sales techniques?"

    print("\n--- Query Rewriting ---")
    rewritten = transformer.rewrite_query(test_query)
    print(f"Original: {test_query}")
    print(f"Rewritten: {rewritten}")

    print("\n--- Multi-Query Generation ---")
    multi_queries = transformer.generate_multi_queries(test_query, num=3)
    for i, q in enumerate(multi_queries, 1):
        print(f"{i}. {q}")

    print("\n--- HyDE Document Generation ---")
    hyde_doc = transformer.generate_hyde_document(test_query)
    print(f"HyDE Doc (first 300 chars): {hyde_doc[:300]}...")
