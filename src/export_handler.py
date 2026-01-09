"""
Export Handler Module

Provides functionality to export RAG query results to CSV and PDF formats.
Includes Streamlit integration for easy download buttons.

Features:
- CSV export with query, strategy, response time, relevance score, and answer
- PDF export with formatted report using FPDF
- Streamlit download buttons with proper MIME type handling

Author: RAG Learning Journey - Day 17
"""

import csv
import io
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from fpdf import FPDF
import streamlit as st
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ResultExporter:
    """Export RAG query results to CSV and PDF formats."""

    def __init__(self):
        """Initialize the exporter."""
        self.csv_columns = [
            "Query",
            "Timestamp",
            "Strategy",
            "Response Time (s)",
            "Relevance Score",
            "Answer",
        ]

    def export_to_csv(self, results: List[Dict[str, Any]]) -> bytes:
        """
        Export query results to CSV format.

        Args:
            results: List of result dictionaries from RAG queries

        Returns:
            CSV content as bytes

        Raises:
            ValueError: If results list is empty
        """
        if not results:
            raise ValueError("Cannot export empty results list")

        try:
            # Create in-memory CSV
            output = io.StringIO()
            writer = csv.DictWriter(output, fieldnames=self.csv_columns)

            # Write header
            writer.writeheader()

            # Write data rows
            for result in results:
                row = {
                    "Query": result.get("question", ""),
                    "Timestamp": result.get(
                        "timestamp", datetime.now().isoformat()
                    ),
                    "Strategy": result.get("strategy", ""),
                    "Response Time (s)": f"{result.get('processing_time', 0):.3f}",
                    "Relevance Score": f"{result.get('relevance_score', 0):.3f}",
                    "Answer": self._truncate_text(
                        result.get("answer", ""), max_length=500
                    ),
                }
                writer.writerow(row)

            # Convert to bytes
            csv_bytes = output.getvalue().encode("utf-8")
            logger.info(f"CSV export created: {len(results)} rows")
            return csv_bytes

        except Exception as e:
            logger.error(f"Error exporting to CSV: {str(e)}")
            raise

    def export_to_pdf(
        self, results: List[Dict[str, Any]], title: str = "RAG Query Results"
    ) -> bytes:
        """
        Export query results to PDF format using FPDF.

        Args:
            results: List of result dictionaries from RAG queries
            title: Title for the PDF report

        Returns:
            PDF content as bytes

        Raises:
            ValueError: If results list is empty
        """
        if not results:
            raise ValueError("Cannot export empty results list")

        try:
            # Create PDF
            pdf = FPDF()
            pdf.set_auto_page_break(auto=True, margin=15)
            pdf.add_page()

            # Add title
            pdf.set_font("Arial", "B", 16)
            pdf.cell(0, 10, title, ln=True, align="C")
            pdf.ln(5)

            # Add generation timestamp
            pdf.set_font("Arial", "I", 10)
            pdf.cell(0, 8, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True)
            pdf.ln(5)

            # Add results
            for idx, result in enumerate(results, 1):
                # Result header
                pdf.set_font("Arial", "B", 12)
                strategy_safe = self._sanitize_text(result.get('strategy', 'Unknown'))
                pdf.cell(0, 8, f"Result {idx}: {strategy_safe}", ln=True)
                pdf.set_font("Arial", "", 10)

                # Query
                query_text = self._sanitize_text(result.get("question", ""))
                pdf.multi_cell(
                    0, 5, f"Query: {query_text}", border=0, align="L"
                )

                # Metadata
                metrics = [
                    f"Response Time: {result.get('processing_time', 0):.3f}s",
                    f"Relevance Score: {result.get('relevance_score', 0):.3f}",
                ]
                for metric in metrics:
                    pdf.cell(0, 5, metric, ln=True)

                # Answer
                pdf.set_font("Arial", "", 9)
                answer_text = self._truncate_text(
                    result.get("answer", ""), max_length=1000
                )
                answer_safe = self._sanitize_text(answer_text)
                pdf.multi_cell(0, 4, f"Answer: {answer_safe}", border=0, align="L")

                # Add spacing between results
                pdf.ln(3)

                # Add page break if needed
                if pdf.get_y() > 250:
                    pdf.add_page()

            # Convert to bytes - pdf.output() returns bytearray, need to convert to bytes
            pdf_bytes = pdf.output(dest="S")
            if isinstance(pdf_bytes, str):
                pdf_bytes = pdf_bytes.encode("latin-1")
            elif isinstance(pdf_bytes, bytearray):
                pdf_bytes = bytes(pdf_bytes)
            logger.info(f"PDF export created: {len(results)} results")
            return pdf_bytes

        except Exception as e:
            logger.error(f"Error exporting to PDF: {str(e)}")
            raise

    @staticmethod
    def _sanitize_text(text: str) -> str:
        """
        Sanitize text for PDF export by removing/replacing unsupported Unicode characters.

        Args:
            text: Text to sanitize

        Returns:
            Sanitized text safe for Helvetica/Arial fonts
        """
        if not text:
            return ""
        
        # Replace common problematic Unicode characters
        replacements = {
            '"': '"',  # Smart double quote -> straight quote
            '"': '"',  # Smart double quote -> straight quote
            ''': "'",  # Smart single quote -> straight quote
            ''': "'",  # Smart single quote -> straight quote
            '–': '-',  # En dash -> hyphen
            '—': '-',  # Em dash -> hyphen
            '…': '...',  # Ellipsis -> three dots
        }
        
        result = text
        for char, replacement in replacements.items():
            result = result.replace(char, replacement)
        
        # Remove any remaining non-ASCII characters that might cause issues
        result = result.encode('ascii', 'ignore').decode('ascii')
        
        return result

    @staticmethod
    def _truncate_text(text: str, max_length: int = 500) -> str:
        """
        Truncate text to maximum length with ellipsis.

        Args:
            text: Text to truncate
            max_length: Maximum length before truncation

        Returns:
            Truncated text
        """
        if len(text) <= max_length:
            return text
        return text[:max_length] + "..."


def create_download_buttons(
    results: List[Dict[str, Any]],
    container_key: str = "export_buttons",
    csv_filename: str = "rag_results.csv",
    pdf_filename: str = "rag_results.pdf",
) -> None:
    """
    Create Streamlit download buttons for CSV and PDF exports.

    Displays side-by-side buttons in a 2-column layout.

    Args:
        results: List of result dictionaries to export
        container_key: Unique key for the container
        csv_filename: Filename for CSV download
        pdf_filename: Filename for PDF download

    Returns:
        None (modifies Streamlit session state)
    """
    if not results:
        st.warning("No results to export. Run a query first.")
        return

    try:
        exporter = ResultExporter()

        # Create columns for side-by-side buttons
        col1, col2 = st.columns(2)

        # CSV Export Button
        with col1:
            csv_data = exporter.export_to_csv(results)
            st.download_button(
                label="📥 Download as CSV",
                data=csv_data,
                file_name=csv_filename,
                mime="text/csv",
                key=f"{container_key}_csv",
            )

        # PDF Export Button
        with col2:
            pdf_data = exporter.export_to_pdf(results)
            st.download_button(
                label="📄 Download as PDF",
                data=pdf_data,
                file_name=pdf_filename,
                mime="application/pdf",
                key=f"{container_key}_pdf",
            )

        logger.info(f"Export buttons created for {len(results)} results")

    except ValueError as e:
        st.error(f"Export error: {str(e)}")
        logger.error(f"Export error: {str(e)}")
    except Exception as e:
        st.error(f"Unexpected error creating export buttons: {str(e)}")
        logger.error(f"Unexpected export error: {str(e)}")
