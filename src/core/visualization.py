"""
Advanced Data Visualization Module

Provides advanced charting and visualization capabilities using matplotlib and plotly.
Supports static images, interactive charts, and export to various formats.
"""

import matplotlib

matplotlib.use("Agg")  # Non-interactive backend for server use

import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from matplotlib.patches import Patch
from plotly.subplots import make_subplots

logger = logging.getLogger("dms.visualization")


class ChartGenerator:
    """Generate various types of charts for data visualization."""

    def __init__(self, output_dir: Optional[Path] = None):
        """
        Initialize chart generator.

        Args:
            output_dir: Directory to save generated charts
        """
        self.output_dir = output_dir or Path("data/exports/charts")
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Set matplotlib style
        plt.style.use("seaborn-v0_8-darkgrid")

        # Default colors
        self.colors = ["#0d6efd", "#198754", "#ffc107", "#dc3545", "#0dcaf0"]

    # ==========================================
    # MATPLOTLIB CHARTS (Static)
    # ==========================================

    def generate_service_distribution_by_region(self, services: List[Any], output_file: Optional[str] = None) -> str:
        """
        Generate bar chart showing service distribution by region.

        Args:
            services: List of Service objects
            output_file: Output file name (auto-generated if None)

        Returns:
            Path to generated chart
        """
        # Count services by region
        region_counts = {}
        for service in services:
            region = service.basic_info.region
            region_counts[region] = region_counts.get(region, 0) + 1

        # Sort by count
        sorted_regions = sorted(region_counts.items(), key=lambda x: x[1], reverse=True)
        regions, counts = zip(*sorted_regions) if sorted_regions else ([], [])

        # Create chart
        fig, ax = plt.subplots(figsize=(12, 6))

        bars = ax.bar(range(len(regions)), counts, color=self.colors[0], alpha=0.8)

        # Customize
        ax.set_xlabel("Region", fontsize=12, fontweight="bold")
        ax.set_ylabel("Number of Services", fontsize=12, fontweight="bold")
        ax.set_title("Service Distribution by Region", fontsize=14, fontweight="bold")
        ax.set_xticks(range(len(regions)))
        ax.set_xticklabels(regions, rotation=45, ha="right")

        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            ax.text(
                bar.get_x() + bar.get_width() / 2.0,
                height,
                f"{int(height)}",
                ha="center",
                va="bottom",
                fontweight="bold",
            )

        plt.tight_layout()

        # Save
        if output_file is None:
            output_file = f'service_distribution_by_region_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png'

        output_path = self.output_dir / output_file
        plt.savefig(output_path, dpi=300, bbox_inches="tight")
        plt.close()

        logger.info(f"Generated region distribution chart: {output_path}")
        return str(output_path)

    def generate_rate_distribution(self, services: List[Any], output_file: Optional[str] = None) -> str:
        """
        Generate histogram showing distribution of hourly rates.

        Args:
            services: List of Service objects
            output_file: Output file name

        Returns:
            Path to generated chart
        """
        # Extract rates
        rates = [s.financial.brutto_rate for s in services if s.financial.brutto_rate > 0]

        if not rates:
            logger.warning("No rate data available for distribution chart")
            return ""

        # Create chart
        fig, ax = plt.subplots(figsize=(10, 6))

        # Histogram
        n, bins, patches = ax.hist(rates, bins=20, color=self.colors[1], alpha=0.7, edgecolor="black")

        # Add statistics
        mean_rate = np.mean(rates)
        median_rate = np.median(rates)

        ax.axvline(mean_rate, color=self.colors[3], linestyle="--", linewidth=2, label=f"Mean: €{mean_rate:.2f}")
        ax.axvline(median_rate, color=self.colors[4], linestyle="--", linewidth=2, label=f"Median: €{median_rate:.2f}")

        # Customize
        ax.set_xlabel("Hourly Rate (€)", fontsize=12, fontweight="bold")
        ax.set_ylabel("Frequency", fontsize=12, fontweight="bold")
        ax.set_title("Distribution of Hourly Rates", fontsize=14, fontweight="bold")
        ax.legend()
        ax.grid(True, alpha=0.3)

        plt.tight_layout()

        # Save
        if output_file is None:
            output_file = f'rate_distribution_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png'

        output_path = self.output_dir / output_file
        plt.savefig(output_path, dpi=300, bbox_inches="tight")
        plt.close()

        logger.info(f"Generated rate distribution chart: {output_path}")
        return str(output_path)

    def generate_cost_breakdown_pie(self, cost_breakdown: Dict[str, float], output_file: Optional[str] = None) -> str:
        """
        Generate pie chart showing cost breakdown.

        Args:
            cost_breakdown: Dictionary of cost components
            output_file: Output file name

        Returns:
            Path to generated chart
        """
        # Prepare data
        labels = list(cost_breakdown.keys())
        values = list(cost_breakdown.values())

        # Create chart
        fig, ax = plt.subplots(figsize=(10, 8))

        wedges, texts, autotexts = ax.pie(
            values, labels=labels, autopct="%1.1f%%", colors=self.colors, startangle=90, explode=[0.05] * len(labels)
        )

        # Enhance text
        for text in texts:
            text.set_fontsize(11)
            text.set_fontweight("bold")

        for autotext in autotexts:
            autotext.set_color("white")
            autotext.set_fontsize(10)
            autotext.set_fontweight("bold")

        ax.set_title("Cost Breakdown", fontsize=14, fontweight="bold")

        plt.tight_layout()

        # Save
        if output_file is None:
            output_file = f'cost_breakdown_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png'

        output_path = self.output_dir / output_file
        plt.savefig(output_path, dpi=300, bbox_inches="tight")
        plt.close()

        logger.info(f"Generated cost breakdown chart: {output_path}")
        return str(output_path)

    def generate_trend_chart(
        self,
        dates: List[datetime],
        values: List[float],
        title: str = "Trend Over Time",
        ylabel: str = "Value",
        output_file: Optional[str] = None,
    ) -> str:
        """
        Generate line chart showing trends over time.

        Args:
            dates: List of dates
            values: List of corresponding values
            title: Chart title
            ylabel: Y-axis label
            output_file: Output file name

        Returns:
            Path to generated chart
        """
        fig, ax = plt.subplots(figsize=(12, 6))

        # Plot line
        ax.plot(dates, values, marker="o", linewidth=2, markersize=6, color=self.colors[0])

        # Fill area under curve
        ax.fill_between(dates, values, alpha=0.3, color=self.colors[0])

        # Customize
        ax.set_xlabel("Date", fontsize=12, fontweight="bold")
        ax.set_ylabel(ylabel, fontsize=12, fontweight="bold")
        ax.set_title(title, fontsize=14, fontweight="bold")

        # Format dates
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
        ax.xaxis.set_major_locator(mdates.AutoDateLocator())
        plt.xticks(rotation=45, ha="right")

        ax.grid(True, alpha=0.3)
        plt.tight_layout()

        # Save
        if output_file is None:
            output_file = f'trend_chart_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png'

        output_path = self.output_dir / output_file
        plt.savefig(output_path, dpi=300, bbox_inches="tight")
        plt.close()

        logger.info(f"Generated trend chart: {output_path}")
        return str(output_path)

    # ==========================================
    # PLOTLY CHARTS (Interactive)
    # ==========================================

    def generate_interactive_dashboard(self, services: List[Any], output_file: Optional[str] = None) -> str:
        """
        Generate interactive dashboard with multiple charts.

        Args:
            services: List of Service objects
            output_file: Output HTML file name

        Returns:
            Path to generated HTML file
        """
        # Create subplots
        fig = make_subplots(
            rows=2,
            cols=2,
            subplot_titles=(
                "Services by Region",
                "Rate Distribution",
                "Top 10 Services by Rate",
                "Average Rate by Region",
            ),
            specs=[[{"type": "bar"}, {"type": "histogram"}], [{"type": "bar"}, {"type": "scatter"}]],
        )

        # 1. Services by region (bar chart)
        region_counts = {}
        for service in services:
            region = service.basic_info.region
            region_counts[region] = region_counts.get(region, 0) + 1

        sorted_regions = sorted(region_counts.items(), key=lambda x: x[1], reverse=True)
        regions, counts = zip(*sorted_regions) if sorted_regions else ([], [])

        fig.add_trace(go.Bar(x=list(regions), y=list(counts), name="Services", marker_color="#0d6efd"), row=1, col=1)

        # 2. Rate distribution (histogram)
        rates = [s.financial.brutto_rate for s in services if s.financial.brutto_rate > 0]

        fig.add_trace(go.Histogram(x=rates, name="Rates", marker_color="#198754", nbinsx=20), row=1, col=2)

        # 3. Top 10 services (horizontal bar)
        sorted_services = sorted(services, key=lambda s: s.financial.brutto_rate, reverse=True)[:10]
        service_names = [s.basic_info.service_name[:30] for s in sorted_services]
        service_rates = [s.financial.brutto_rate for s in sorted_services]

        fig.add_trace(
            go.Bar(y=service_names, x=service_rates, orientation="h", name="Rate", marker_color="#ffc107"), row=2, col=1
        )

        # 4. Average rate by region (scatter)
        region_avg_rates = {}
        region_service_counts = {}

        for service in services:
            region = service.basic_info.region
            rate = service.financial.brutto_rate

            if region not in region_avg_rates:
                region_avg_rates[region] = []
                region_service_counts[region] = 0

            region_avg_rates[region].append(rate)
            region_service_counts[region] += 1

        avg_rates = {k: np.mean(v) for k, v in region_avg_rates.items()}
        sorted_avg = sorted(avg_rates.items(), key=lambda x: x[1], reverse=True)
        avg_regions, avg_values = zip(*sorted_avg) if sorted_avg else ([], [])

        fig.add_trace(
            go.Scatter(
                x=list(avg_regions),
                y=list(avg_values),
                mode="markers+lines",
                name="Avg Rate",
                marker=dict(size=10, color="#dc3545"),
                line=dict(width=2),
            ),
            row=2,
            col=2,
        )

        # Update layout
        fig.update_layout(title_text="Document Management System - Analytics Dashboard", showlegend=False, height=800)

        # Save
        if output_file is None:
            output_file = f'interactive_dashboard_{datetime.now().strftime("%Y%m%d_%H%M%S")}.html'

        output_path = self.output_dir / output_file
        fig.write_html(str(output_path))

        logger.info(f"Generated interactive dashboard: {output_path}")
        return str(output_path)

    def generate_3d_scatter(self, services: List[Any], output_file: Optional[str] = None) -> str:
        """
        Generate 3D scatter plot of services.

        Args:
            services: List of Service objects
            output_file: Output HTML file name

        Returns:
            Path to generated HTML file
        """
        # Extract data
        rates = [s.financial.brutto_rate for s in services]
        regions = [s.basic_info.region for s in services]
        names = [s.basic_info.service_name for s in services]

        # Create numeric values for regions
        unique_regions = list(set(regions))
        region_values = [unique_regions.index(r) for r in regions]

        # Create 3D scatter
        fig = go.Figure(
            data=[
                go.Scatter3d(
                    x=region_values,
                    y=rates,
                    z=list(range(len(services))),
                    mode="markers",
                    marker=dict(
                        size=8,
                        color=rates,
                        colorscale="Viridis",
                        showscale=True,
                        colorbar=dict(title="Hourly Rate (€)"),
                    ),
                    text=[
                        f"{name}<br>Region: {region}<br>Rate: €{rate:.2f}"
                        for name, region, rate in zip(names, regions, rates)
                    ],
                    hoverinfo="text",
                )
            ]
        )

        fig.update_layout(
            title="3D Service Visualization",
            scene=dict(xaxis_title="Region", yaxis_title="Hourly Rate (€)", zaxis_title="Service Index"),
            height=700,
        )

        # Save
        if output_file is None:
            output_file = f'3d_scatter_{datetime.now().strftime("%Y%m%d_%H%M%S")}.html'

        output_path = self.output_dir / output_file
        fig.write_html(str(output_path))

        logger.info(f"Generated 3D scatter plot: {output_path}")
        return str(output_path)


def generate_comprehensive_report(services: List[Any], output_dir: Optional[Path] = None) -> Dict[str, str]:
    """
    Generate comprehensive visualization report with all charts.

    Args:
        services: List of Service objects
        output_dir: Output directory for charts

    Returns:
        Dictionary mapping chart types to file paths
    """
    generator = ChartGenerator(output_dir)

    charts = {}

    try:
        # Generate static charts
        charts["region_distribution"] = generator.generate_service_distribution_by_region(services)
        charts["rate_distribution"] = generator.generate_rate_distribution(services)

        # Generate interactive charts
        charts["dashboard"] = generator.generate_interactive_dashboard(services)
        charts["3d_scatter"] = generator.generate_3d_scatter(services)

        logger.info(f"Generated comprehensive report with {len(charts)} charts")

    except Exception as e:
        logger.error(f"Error generating comprehensive report: {e}")

    return charts
