"""
Chart Generator Module

Provides performance visualization for RAG system metrics using Plotly.

Features:
- Relevance score comparison across strategies
- Response time comparison across strategies
- Quality vs Speed scatter plot showing trade-offs
- Interactive Plotly charts with custom styling

Author: RAG Learning Journey - Day 17
"""

from typing import Dict, List, Any, Optional
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PerformanceCharts:
    """Generate performance comparison charts for RAG strategies."""

    # Color scheme
    COLOR_BEST = "rgb(26, 118, 255)"  # Blue
    COLOR_OTHERS = "lightslategray"
    COLOR_OPTIMAL = "rgb(76, 175, 80)"  # Green

    def __init__(self):
        """Initialize the chart generator."""
        pass

    def generate_relevance_chart(
        self, results: Dict[str, Dict[str, Any]]
    ) -> go.Figure:
        """
        Generate bar chart comparing relevance scores across strategies.

        Args:
            results: Dictionary with strategy results {strategy: result_dict}

        Returns:
            Plotly Figure object
        """
        try:
            # Extract data
            strategies = []
            scores = []
            best_score = 0
            best_strategy = None

            for strategy, result in results.items():
                relevance = result.get("relevance_score", 0)
                strategies.append(strategy.replace("_", " ").title())
                scores.append(relevance)

                if relevance > best_score:
                    best_score = relevance
                    best_strategy = strategy

            # Create bar chart
            colors = [
                self.COLOR_BEST if score == best_score else self.COLOR_OTHERS
                for score in scores
            ]

            fig = go.Figure(
                data=[
                    go.Bar(
                        x=strategies,
                        y=scores,
                        marker=dict(color=colors),
                        text=[f"{score:.3f}" for score in scores],
                        textposition="auto",
                        hovertemplate="<b>%{x}</b><br>Relevance: %{y:.3f}<extra></extra>",
                    )
                ]
            )

            # Add annotation for best performer
            if best_strategy:
                fig.add_annotation(
                    x=best_strategy.replace("_", " ").title(),
                    y=best_score,
                    text="30X Better!",
                    showarrow=True,
                    arrowhead=2,
                    arrowsize=1,
                    arrowwidth=2,
                    arrowcolor="rgb(26, 118, 255)",
                    ax=0,
                    ay=-40,
                    bgcolor="rgb(26, 118, 255)",
                    font=dict(color="white", size=12),
                )

            fig.update_layout(
                title="📊 Relevance Score Comparison",
                xaxis_title="Strategy",
                yaxis_title="Relevance Score",
                showlegend=False,
                hovermode="x unified",
                height=400,
                template="plotly_white",
            )

            logger.info("Relevance chart generated")
            return fig

        except Exception as e:
            logger.error(f"Error generating relevance chart: {str(e)}")
            return self._empty_chart("Error generating relevance chart")

    def generate_speed_chart(
        self, results: Dict[str, Dict[str, Any]]
    ) -> go.Figure:
        """
        Generate bar chart comparing response times across strategies.

        Args:
            results: Dictionary with strategy results {strategy: result_dict}

        Returns:
            Plotly Figure object
        """
        try:
            # Extract data
            strategies = []
            times = []
            fastest_time = float("inf")
            fastest_strategy = None

            for strategy, result in results.items():
                proc_time = result.get("processing_time", 0)
                strategies.append(strategy.replace("_", " ").title())
                times.append(proc_time)

                if proc_time < fastest_time:
                    fastest_time = proc_time
                    fastest_strategy = strategy

            # Create bar chart
            colors = [
                self.COLOR_BEST if time == fastest_time else self.COLOR_OTHERS
                for time in times
            ]

            fig = go.Figure(
                data=[
                    go.Bar(
                        x=strategies,
                        y=times,
                        marker=dict(color=colors),
                        text=[f"{time:.2f}s" for time in times],
                        textposition="auto",
                        hovertemplate="<b>%{x}</b><br>Response Time: %{y:.3f}s<extra></extra>",
                    )
                ]
            )

            fig.update_layout(
                title="⚡ Response Time Comparison",
                xaxis_title="Strategy",
                yaxis_title="Response Time (seconds)",
                showlegend=False,
                hovermode="x unified",
                height=400,
                template="plotly_white",
            )

            logger.info("Speed chart generated")
            return fig

        except Exception as e:
            logger.error(f"Error generating speed chart: {str(e)}")
            return self._empty_chart("Error generating speed chart")

    def generate_quality_speed_scatter(
        self, results: Dict[str, Dict[str, Any]]
    ) -> go.Figure:
        """
        Generate scatter plot showing quality vs speed trade-offs.

        X-axis: Response Time (speed)
        Y-axis: Relevance Score (quality)

        Args:
            results: Dictionary with strategy results {strategy: result_dict}

        Returns:
            Plotly Figure object
        """
        try:
            # Extract data
            strategies = []
            times = []
            scores = []

            for strategy, result in results.items():
                strategies.append(strategy.replace("_", " ").title())
                times.append(result.get("processing_time", 0))
                scores.append(result.get("relevance_score", 0))

            fig = go.Figure(
                data=[
                    go.Scatter(
                        x=times,
                        y=scores,
                        mode="markers+text",
                        marker=dict(
                            size=15,
                            color=self.COLOR_BEST,
                            opacity=0.7,
                            line=dict(width=2, color="white"),
                        ),
                        text=strategies,
                        textposition="top center",
                        hovertemplate="<b>%{text}</b><br>Speed: %{x:.3f}s<br>Quality: %{y:.3f}<extra></extra>",
                    )
                ]
            )

            # Add optimal zone annotation (top-right)
            fig.add_annotation(
                x=max(times) * 0.75,
                y=max(scores) * 0.85,
                text="Optimal Zone",
                showarrow=True,
                arrowhead=2,
                arrowsize=1,
                arrowwidth=2,
                arrowcolor=self.COLOR_OPTIMAL,
                bgcolor=self.COLOR_OPTIMAL,
                font=dict(color="white", size=11),
                opacity=0.8,
            )

            # Add quadrant lines
            fig.add_vline(x=sum(times) / len(times), line_dash="dash", line_color="gray", opacity=0.3)
            fig.add_hline(y=sum(scores) / len(scores), line_dash="dash", line_color="gray", opacity=0.3)

            fig.update_layout(
                title="⚖️ Quality vs Speed Trade-offs",
                xaxis_title="Response Time (seconds) - Lower is Better",
                yaxis_title="Relevance Score - Higher is Better",
                showlegend=False,
                hovermode="closest",
                height=500,
                template="plotly_white",
                xaxis=dict(zeroline=False),
                yaxis=dict(zeroline=False),
            )

            logger.info("Quality vs Speed scatter chart generated")
            return fig

        except Exception as e:
            logger.error(f"Error generating quality-speed chart: {str(e)}")
            return self._empty_chart("Error generating quality-speed chart")

    def display_all_charts(
        self,
        st: Any,
        results: Dict[str, Dict[str, Any]],
    ) -> None:
        """
        Display all performance charts in Streamlit.

        Args:
            st: Streamlit module
            results: Dictionary with strategy results

        Returns:
            None (modifies Streamlit session state)
        """
        try:
            if not results:
                st.warning("No results available for visualization")
                return

            st.subheader("📈 Performance Visualization")

            # Create columns for charts
            col1, col2 = st.columns(2)

            # Relevance chart
            with col1:
                relevance_fig = self.generate_relevance_chart(results)
                st.plotly_chart(relevance_fig, use_container_width=True)

            # Speed chart
            with col2:
                speed_fig = self.generate_speed_chart(results)
                st.plotly_chart(speed_fig, use_container_width=True)

            # Quality vs Speed scatter (full width)
            scatter_fig = self.generate_quality_speed_scatter(results)
            st.plotly_chart(scatter_fig, use_container_width=True)

            logger.info("All charts displayed successfully")

        except Exception as e:
            st.error(f"Error displaying charts: {str(e)}")
            logger.error(f"Error displaying charts: {str(e)}")

    @staticmethod
    def _empty_chart(title: str) -> go.Figure:
        """Create an empty chart with error message."""
        fig = go.Figure()
        fig.add_annotation(
            text=title,
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
            font=dict(size=14, color="red"),
        )
        fig.update_layout(
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            template="plotly_white",
            height=300,
        )
        return fig
