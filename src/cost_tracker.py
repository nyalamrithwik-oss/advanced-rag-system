"""
Cost Tracker Module

Tracks API costs for various components used in the RAG system.
Provides cost breakdown, ROI calculation, and Streamlit integration.

Features:
- Track costs for OpenAI embeddings, GPT-4 Turbo, and Cohere reranking
- Calculate ROI based on time saved vs API costs
- Display metrics in Streamlit with proper formatting
- Automatic token estimation based on word count

Pricing (as of 2024):
- OpenAI embeddings: $0.00002 per 1K tokens
- GPT-4 Turbo: $0.01 input, $0.03 output per 1K tokens
- Cohere reranking: $0.001 per query

Author: RAG Learning Journey - Day 17
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import streamlit as st
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class CostBreakdown:
    """Data class for cost breakdown."""
    embeddings_cost: float = 0.0
    llm_input_cost: float = 0.0
    llm_output_cost: float = 0.0
    reranking_cost: float = 0.0
    
    @property
    def total_cost(self) -> float:
        """Calculate total cost."""
        return (
            self.embeddings_cost 
            + self.llm_input_cost 
            + self.llm_output_cost 
            + self.reranking_cost
        )


class CostTracker:
    """Track and calculate API costs for RAG operations."""

    # Pricing configuration (per 1K tokens or per query)
    EMBEDDINGS_COST = 0.00002  # per 1K tokens
    GPT4_INPUT_COST = 0.01  # per 1K tokens
    GPT4_OUTPUT_COST = 0.03  # per 1K tokens
    COHERE_RERANKING_COST = 0.001  # per query
    
    # Estimation constants
    TOKENS_PER_WORD = 1.3  # Average tokens per word for English text
    EMPLOYEE_HOURLY_RATE = 50.0  # USD per hour
    TIME_SAVED_PER_SEARCH = 5 / 60  # 5 minutes in hours

    def __init__(self):
        """Initialize cost tracker."""
        self.costs: List[CostBreakdown] = []
        self.total_queries = 0

    def estimate_tokens(self, text: str) -> int:
        """
        Estimate token count from text.

        Args:
            text: Input text

        Returns:
            Estimated token count
        """
        word_count = len(text.split())
        return int(word_count * self.TOKENS_PER_WORD)

    def calculate_cost(
        self,
        input_text: str,
        output_text: str,
        use_embeddings: bool = True,
        use_reranking: bool = False,
        num_reranking_queries: int = 1,
    ) -> CostBreakdown:
        """
        Calculate API cost for a query.

        Args:
            input_text: Input text (query)
            output_text: Output text (response)
            use_embeddings: Whether embeddings were used
            use_reranking: Whether reranking was used
            num_reranking_queries: Number of reranking queries

        Returns:
            CostBreakdown with detailed cost breakdown
        """
        breakdown = CostBreakdown()

        # Estimate tokens
        input_tokens = self.estimate_tokens(input_text)
        output_tokens = self.estimate_tokens(output_text)

        # Embeddings cost (for retrieved documents)
        if use_embeddings:
            # Assume ~5 documents retrieved with average 300 chars each
            embedding_tokens = self.estimate_tokens("x" * (5 * 300))
            breakdown.embeddings_cost = (
                (embedding_tokens / 1000) * self.EMBEDDINGS_COST
            )

        # LLM cost (GPT-4 Turbo)
        breakdown.llm_input_cost = (input_tokens / 1000) * self.GPT4_INPUT_COST
        breakdown.llm_output_cost = (output_tokens / 1000) * self.GPT4_OUTPUT_COST

        # Reranking cost (Cohere)
        if use_reranking:
            breakdown.reranking_cost = (
                num_reranking_queries * self.COHERE_RERANKING_COST
            )

        self.costs.append(breakdown)
        self.total_queries += 1
        logger.info(f"Cost calculated: ${breakdown.total_cost:.6f}")

        return breakdown

    def calculate_roi(
        self,
        total_cost: float,
        queries_run: int = 1,
    ) -> Dict[str, Any]:
        """
        Calculate ROI based on time saved vs API costs.

        Args:
            total_cost: Total API cost
            queries_run: Number of queries run

        Returns:
            Dictionary with ROI metrics
        """
        # Calculate time saved (5 minutes per search)
        total_time_saved_hours = queries_run * self.TIME_SAVED_PER_SEARCH
        value_created = total_time_saved_hours * self.EMPLOYEE_HOURLY_RATE

        # Calculate ROI
        roi_percentage = (
            ((value_created - total_cost) / total_cost * 100)
            if total_cost > 0 else 0
        )

        return {
            "value_created": value_created,
            "api_cost": total_cost,
            "net_savings": value_created - total_cost,
            "roi_percentage": roi_percentage,
            "time_saved_minutes": total_time_saved_hours * 60,
        }

    def get_total_cost(self) -> float:
        """Get total cost across all tracked queries."""
        return sum(cost.total_cost for cost in self.costs)

    def get_cost_breakdown_by_component(self) -> Dict[str, float]:
        """Get aggregate cost breakdown by component."""
        total_embeddings = sum(c.embeddings_cost for c in self.costs)
        total_llm_input = sum(c.llm_input_cost for c in self.costs)
        total_llm_output = sum(c.llm_output_cost for c in self.costs)
        total_reranking = sum(c.reranking_cost for c in self.costs)

        return {
            "Embeddings": total_embeddings,
            "LLM Input": total_llm_input,
            "LLM Output": total_llm_output,
            "Reranking": total_reranking,
        }

    def display_metrics(
        self,
        st: Any,
        title: str = "💰 Cost Analysis",
    ) -> None:
        """
        Display cost metrics in Streamlit.

        Args:
            st: Streamlit module
            title: Title for the display section

        Returns:
            None (modifies Streamlit session state)
        """
        st.subheader(title)

        total_cost = self.get_total_cost()
        breakdown = self.get_cost_breakdown_by_component()
        roi = self.calculate_roi(total_cost, self.total_queries)

        # Total cost metric
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Cost", f"${total_cost:.4f}")
        with col2:
            st.metric("Queries Run", self.total_queries)
        with col3:
            avg_cost = total_cost / self.total_queries if self.total_queries > 0 else 0
            st.metric("Avg Cost/Query", f"${avg_cost:.4f}")

        # Breakdown
        with st.expander("📊 Cost Breakdown"):
            for component, cost in breakdown.items():
                if cost > 0:
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.write(f"**{component}**")
                    with col2:
                        st.write(f"${cost:.4f}")

        # ROI
        with st.expander("📈 ROI Analysis"):
            st.markdown(f"""
            **Value Created:** ${roi['value_created']:.2f}
            - Time Saved: {roi['time_saved_minutes']:.1f} minutes
            - Employee Rate: ${self.EMPLOYEE_HOURLY_RATE}/hour

            **API Cost:** ${roi['api_cost']:.4f}

            **Net Savings:** ${roi['net_savings']:.2f}

            **ROI Percentage:** {roi['roi_percentage']:.1f}%
            """)

    def reset(self) -> None:
        """Reset all tracked costs."""
        self.costs = []
        self.total_queries = 0
        logger.info("Cost tracker reset")


def get_or_create_tracker() -> CostTracker:
    """
    Get or create a cost tracker in Streamlit session state.

    Returns:
        CostTracker instance
    """
    if "cost_tracker" not in st.session_state:
        st.session_state.cost_tracker = CostTracker()
    return st.session_state.cost_tracker
