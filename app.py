"""
Advanced RAG System - Streamlit Web Application

Multi-page Streamlit app demonstrating advanced RAG techniques:
- Page 1: Query Playground - Test different strategies
- Page 2: Strategy Comparison - Compare all strategies

Author: RAG Learning Journey - Day 16
"""

import streamlit as st
import time
from pathlib import Path
import pandas as pd
import plotly.express as px
from rag_pipeline import AdvancedRAGPipeline
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="Advanced RAG System",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS
st.markdown(
    """
    <style>
    .main {
        padding: 0rem 1rem;
    }
    .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
        font-size: 1.25rem;
    }
    .metric-box {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .retrieved-doc {
        background-color: #e8f4f8;
        padding: 0.75rem;
        border-left: 4px solid #0066cc;
        margin: 0.5rem 0;
        border-radius: 0.25rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# Initialize session state
@st.cache_resource
def get_pipeline():
    """Initialize RAG pipeline (cached for performance)."""
    return AdvancedRAGPipeline()


def load_sample_documents():
    """Load sample documents for demo."""
    data_dir = Path("data")
    documents = []
    files = []

    if data_dir.exists():
        for file_path in data_dir.glob("*.txt"):
            try:
                with open(file_path, "r") as f:
                    documents.append(f.read())
                    files.append(str(file_path))
            except Exception as e:
                st.warning(f"Error loading {file_path}: {str(e)}")

    return documents, files


def page_query_playground():
    """Page 1: Query Playground"""
    st.title("🔍 Query Playground")
    st.markdown("Test different RAG strategies on your documents")

    with st.sidebar:
        st.header("⚙️ Configuration")

        # Document upload section
        st.subheader("📄 Documents")
        uploaded_files = st.file_uploader(
            "Upload documents (PDF, DOCX, TXT, MD)",
            type=["pdf", "docx", "txt", "md"],
            accept_multiple_files=True,
        )

        # Load sample documents option
        if st.checkbox("Load sample documents"):
            sample_docs, sample_files = load_sample_documents()
            if sample_docs:
                st.success(f"Loaded {len(sample_docs)} sample documents")
                # Index sample documents
                pipeline = get_pipeline()
                with st.spinner("Indexing sample documents..."):
                    stats = pipeline.retriever.index_documents(sample_docs)
                st.info(f"Indexed {stats.get('total_chunks', 0)} chunks")

        # Strategy selector
        st.subheader("🎯 Strategy")
        strategy = st.selectbox(
            "Select RAG strategy:",
            [
                "basic",
                "rewritten",
                "multi_query",
                "hyde",
                "hybrid_rerank",
            ],
            format_func=lambda x: {
                "basic": "Basic (Direct retrieval)",
                "rewritten": "Query Rewriting",
                "multi_query": "Multi-Query Generation",
                "hyde": "HyDE (Hypothetical Documents)",
                "hybrid_rerank": "Hybrid + Reranking (Full Stack)",
            }.get(x, x),
        )

        # Results per page
        num_results = st.slider("Number of retrieved documents", 1, 10, 5)

    # Main content area
    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("❓ Your Question")
        query = st.text_area(
            "Enter your question:",
            placeholder="e.g., What are the best B2B sales techniques?",
            height=100,
            label_visibility="collapsed",
        )

    with col2:
        st.subheader("📊 Strategy Info")
        strategy_info = {
            "basic": "Direct retrieval without transformation. Fast baseline.",
            "rewritten": "Rewrites query for clarity. Improves specificity.",
            "multi_query": "Generates multiple query variations. Better coverage.",
            "hyde": "Creates hypothetical documents. Handles paraphrasing.",
            "hybrid_rerank": "Full stack with all techniques. Best quality.",
        }
        st.info(strategy_info.get(strategy, ""))

    # Process query
    if st.button("🚀 Execute Query", type="primary", use_container_width=True):
        if not query:
            st.error("Please enter a question")
        else:
            pipeline = get_pipeline()

            with st.spinner(f"Processing with {strategy} strategy..."):
                result = pipeline.query(query, strategy=strategy, num_results=num_results)

            # Display results
            st.success("✅ Query processed successfully!")

            # Metrics row
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Processing Time", f"{result['processing_time']:.2f}s")
            with col2:
                st.metric("Documents Retrieved", result.get("num_retrieved", 0))
            with col3:
                st.metric("Strategy Used", strategy.title().replace("_", " "))
            with col4:
                confidence = (
                    min(result.get("num_retrieved", 0) * 20, 100)
                    if result.get("num_retrieved")
                    else 0
                )
                st.metric("Confidence", f"{confidence}%")

            # Answer section
            st.subheader("💡 Generated Answer")
            st.markdown(result["answer"])

            # Retrieved documents section
            st.subheader("📚 Retrieved Documents")
            retrieved = result.get("retrieved_docs", [])

            if retrieved:
                for i, (doc, score) in enumerate(retrieved, 1):
                    with st.expander(
                        f"📖 Document {i} (Score: {score:.3f})", expanded=(i == 1)
                    ):
                        st.write(doc)
            else:
                st.info("No documents retrieved")

            # Additional info
            st.subheader("🔬 Transformation Details")
            col1, col2 = st.columns(2)

            with col1:
                if "transformed_query" in result:
                    st.write("**Transformed Query:**")
                    st.code(result["transformed_query"])

            with col2:
                if "hyde_document" in result:
                    st.write("**HyDE Document (excerpt):**")
                    st.text(result["hyde_document"])

                if "queries_used" in result:
                    st.write("**Queries Used:**")
                    for q in result["queries_used"]:
                        st.write(f"- {q}")


def page_strategy_comparison():
    """Page 2: Strategy Comparison"""
    st.title("📊 Strategy Comparison")
    st.markdown("Compare all RAG strategies on the same query")

    with st.sidebar:
        st.header("⚙️ Configuration")

        # Load sample documents
        if st.checkbox("Load sample documents for comparison"):
            sample_docs, sample_files = load_sample_documents()
            if sample_docs:
                st.success(f"Loaded {len(sample_docs)} sample documents")
                pipeline = get_pipeline()
                with st.spinner("Indexing documents..."):
                    stats = pipeline.retriever.index_documents(sample_docs)
                st.info(f"Indexed {stats.get('total_chunks', 0)} chunks")

    # Query input
    st.subheader("❓ Test Query")
    query = st.text_area(
        "Enter a question to test all strategies:",
        placeholder="e.g., What are the best B2B sales techniques?",
        height=100,
        label_visibility="collapsed",
    )

    # Comparison button
    if st.button("🔄 Compare All Strategies", type="primary", use_container_width=True):
        if not query:
            st.error("Please enter a question")
        else:
            pipeline = get_pipeline()
            strategies = ["basic", "rewritten", "multi_query", "hyde", "hybrid_rerank"]

            # Run all strategies
            results = {}
            progress_bar = st.progress(0)

            with st.spinner("Running all strategies..."):
                for idx, strategy in enumerate(strategies):
                    result = pipeline.query(query, strategy=strategy, num_results=5)
                    results[strategy] = result
                    progress_bar.progress((idx + 1) / len(strategies))

            # Comparison table
            st.subheader("📈 Results Comparison")

            comparison_data = []
            for strategy in strategies:
                result = results[strategy]
                comparison_data.append(
                    {
                        "Strategy": strategy.title().replace("_", " "),
                        "Processing Time (s)": round(result["processing_time"], 3),
                        "Documents Retrieved": result.get("num_retrieved", 0),
                        "Answer Length": len(result["answer"]),
                        "Quality Rating": "⭐" * min(5, max(1, 3 + (result.get("num_retrieved", 0) // 2))),
                    }
                )

            df = pd.DataFrame(comparison_data)
            st.dataframe(df, use_container_width=True)

            # Charts
            col1, col2 = st.columns(2)

            with col1:
                # Processing time comparison
                fig_time = px.bar(
                    df,
                    x="Strategy",
                    y="Processing Time (s)",
                    title="Processing Time by Strategy",
                    color="Processing Time (s)",
                    color_continuous_scale="RdYlGn_r",
                )
                fig_time.update_layout(showlegend=False)
                st.plotly_chart(fig_time, use_container_width=True)

            with col2:
                # Documents retrieved comparison
                fig_docs = px.bar(
                    df,
                    x="Strategy",
                    y="Documents Retrieved",
                    title="Documents Retrieved by Strategy",
                    color="Documents Retrieved",
                    color_continuous_scale="Blues",
                )
                fig_docs.update_layout(showlegend=False)
                st.plotly_chart(fig_docs, use_container_width=True)

            # Detailed comparison
            st.subheader("🔍 Detailed Results")

            for strategy in strategies:
                with st.expander(
                    f"**{strategy.upper()}** - {results[strategy]['processing_time']:.2f}s",
                    expanded=False,
                ):
                    result = results[strategy]

                    # Answer
                    st.write("**Generated Answer:**")
                    st.markdown(result["answer"])

                    # Retrieved documents
                    st.write("**Retrieved Documents:**")
                    retrieved = result.get("retrieved_docs", [])
                    for i, (doc, score) in enumerate(retrieved[:3], 1):
                        st.write(f"{i}. (Score: {score:.3f}) {doc[:100]}...")

                    # Transformation info
                    if "transformed_query" in result:
                        st.write(f"**Transformed Query:** {result['transformed_query']}")


# Main app
def main():
    """Main application"""
    st.sidebar.title("🎯 Advanced RAG System")
    st.sidebar.markdown("Day 16 Learning Project - Production RAG Techniques")

    # Page navigation
    page = st.sidebar.radio(
        "Select Page:",
        ["🔍 Query Playground", "📊 Strategy Comparison"],
    )

    if page == "🔍 Query Playground":
        page_query_playground()
    else:
        page_strategy_comparison()

    # Sidebar footer
    st.sidebar.markdown("---")
    st.sidebar.markdown(
        """
    **Architecture:**
    - Query Transformer (Rewriting, Multi-Query, HyDE)
    - Hybrid Retriever (Dense + Sparse + RRF)
    - Reranker (Cohere)
    - Context Optimizer (Dedup, Compression)
    """
    )


if __name__ == "__main__":
    main()
