"""
Interactive Visualizations with Plotly

Advanced interactive charts and dashboards using Plotly.
Provides rich, interactive visualizations for analytics data.

Key Features:
- Line charts, bar charts, scatter plots
- Heat maps, box plots, violin plots
- 3D visualizations
- Time series charts with range slider
- Real-time updating charts
- Multi-axis plots
- Subplots and dashboard layouts
- Export to HTML, JSON, PNG
- Responsive and mobile-friendly
- Customizable themes

Dependencies:
- plotly>=5.0.0
"""

import json
import logging
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np
import pandas as pd

logger = logging.getLogger("dms.analytics.viz")

# Check if Plotly is available
try:
    import plotly.graph_objects as go
    import plotly.express as px
    from plotly.subplots import make_subplots

    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False
    logger.warning("Plotly not available. Install with: pip install plotly")


class ChartType(str, Enum):
    """Chart types"""

    LINE = "line"
    BAR = "bar"
    SCATTER = "scatter"
    AREA = "area"
    PIE = "pie"
    DONUT = "donut"
    HEATMAP = "heatmap"
    BOX = "box"
    VIOLIN = "violin"
    HISTOGRAM = "histogram"
    CANDLESTICK = "candlestick"
    WATERFALL = "waterfall"
    FUNNEL = "funnel"
    TREEMAP = "treemap"
    SUNBURST = "sunburst"
    SANKEY = "sankey"
    GAUGE = "gauge"
    TABLE = "table"


class Theme(str, Enum):
    """Chart themes"""

    PLOTLY = "plotly"
    PLOTLY_WHITE = "plotly_white"
    PLOTLY_DARK = "plotly_dark"
    GGPLOT2 = "ggplot2"
    SEABORN = "seaborn"
    SIMPLE_WHITE = "simple_white"
    NONE = "none"


@dataclass
class ChartConfig:
    """Chart configuration"""

    title: str
    theme: Theme = Theme.PLOTLY_WHITE
    width: Optional[int] = None
    height: Optional[int] = 600
    show_legend: bool = True
    responsive: bool = True
    font_size: int = 12


class PlotlyChart:
    """Plotly chart builder"""

    def __init__(self, config: Optional[ChartConfig] = None):
        """
        Initialize chart.

        Args:
            config: Chart configuration
        """
        if not PLOTLY_AVAILABLE:
            raise ImportError("Plotly required. Install with: pip install plotly")

        self.config = config or ChartConfig(title="Chart")
        self.fig = None

    def create_line_chart(
        self,
        data: Union[pd.DataFrame, Dict[str, List]],
        x: str,
        y: Union[str, List[str]],
        markers: bool = False,
        smooth: bool = False,
    ) -> "PlotlyChart":
        """
        Create line chart.

        Args:
            data: Data (DataFrame or dict)
            x: X-axis column name
            y: Y-axis column name(s)
            markers: Show markers
            smooth: Smooth lines

        Returns:
            self
        """
        if isinstance(data, dict):
            data = pd.DataFrame(data)

        y_columns = [y] if isinstance(y, str) else y

        self.fig = go.Figure()

        for col in y_columns:
            mode = "lines+markers" if markers else "lines"
            if smooth:
                mode = "lines"

            self.fig.add_trace(go.Scatter(x=data[x], y=data[col], mode=mode, name=col, line=dict(shape="spline" if smooth else "linear")))

        self._apply_layout()
        return self

    def create_bar_chart(
        self,
        data: Union[pd.DataFrame, Dict[str, List]],
        x: str,
        y: Union[str, List[str]],
        orientation: str = "v",
        stacked: bool = False,
    ) -> "PlotlyChart":
        """
        Create bar chart.

        Args:
            data: Data
            x: X-axis column
            y: Y-axis column(s)
            orientation: 'v' for vertical, 'h' for horizontal
            stacked: Stack bars

        Returns:
            self
        """
        if isinstance(data, dict):
            data = pd.DataFrame(data)

        y_columns = [y] if isinstance(y, str) else y

        self.fig = go.Figure()

        for col in y_columns:
            if orientation == "v":
                self.fig.add_trace(go.Bar(x=data[x], y=data[col], name=col))
            else:
                self.fig.add_trace(go.Bar(y=data[x], x=data[col], name=col, orientation="h"))

        if stacked:
            self.fig.update_layout(barmode="stack")
        else:
            self.fig.update_layout(barmode="group")

        self._apply_layout()
        return self

    def create_scatter_chart(
        self,
        data: Union[pd.DataFrame, Dict[str, List]],
        x: str,
        y: str,
        size: Optional[str] = None,
        color: Optional[str] = None,
        text: Optional[str] = None,
    ) -> "PlotlyChart":
        """
        Create scatter plot.

        Args:
            data: Data
            x: X-axis column
            y: Y-axis column
            size: Column for marker size
            color: Column for marker color
            text: Column for hover text

        Returns:
            self
        """
        if isinstance(data, dict):
            data = pd.DataFrame(data)

        self.fig = px.scatter(data, x=x, y=y, size=size, color=color, text=text, template=self.config.theme.value)

        self._apply_layout()
        return self

    def create_heatmap(self, data: Union[pd.DataFrame, np.ndarray], x_labels: Optional[List] = None, y_labels: Optional[List] = None, colorscale: str = "Viridis") -> "PlotlyChart":
        """
        Create heatmap.

        Args:
            data: 2D data
            x_labels: X-axis labels
            y_labels: Y-axis labels
            colorscale: Color scale

        Returns:
            self
        """
        if isinstance(data, pd.DataFrame):
            z = data.values
            x_labels = x_labels or list(data.columns)
            y_labels = y_labels or list(data.index)
        else:
            z = data

        self.fig = go.Figure(data=go.Heatmap(z=z, x=x_labels, y=y_labels, colorscale=colorscale))

        self._apply_layout()
        return self

    def create_pie_chart(self, data: Dict[str, float], hole: float = 0.0) -> "PlotlyChart":
        """
        Create pie chart.

        Args:
            data: Label -> value mapping
            hole: Hole size for donut chart (0.0 - 0.9)

        Returns:
            self
        """
        labels = list(data.keys())
        values = list(data.values())

        self.fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=hole)])

        self._apply_layout()
        return self

    def create_box_plot(
        self,
        data: Union[pd.DataFrame, Dict[str, List]],
        y: Union[str, List[str]],
        x: Optional[str] = None,
        points: bool = False,
    ) -> "PlotlyChart":
        """
        Create box plot.

        Args:
            data: Data
            y: Y-axis column(s)
            x: Grouping column
            points: Show all points

        Returns:
            self
        """
        if isinstance(data, dict):
            data = pd.DataFrame(data)

        y_columns = [y] if isinstance(y, str) else y

        self.fig = go.Figure()

        for col in y_columns:
            self.fig.add_trace(go.Box(y=data[col], x=data[x] if x else None, name=col, boxpoints="all" if points else "outliers"))

        self._apply_layout()
        return self

    def create_time_series(
        self,
        data: pd.DataFrame,
        x: str,
        y: Union[str, List[str]],
        range_slider: bool = True,
        markers: bool = False,
    ) -> "PlotlyChart":
        """
        Create time series chart with range slider.

        Args:
            data: Data with datetime index or column
            x: Time column
            y: Y-axis column(s)
            range_slider: Show range slider
            markers: Show markers

        Returns:
            self
        """
        y_columns = [y] if isinstance(y, str) else y

        self.fig = go.Figure()

        for col in y_columns:
            mode = "lines+markers" if markers else "lines"
            self.fig.add_trace(go.Scatter(x=data[x], y=data[col], mode=mode, name=col))

        if range_slider:
            self.fig.update_xaxes(rangeslider_visible=True)

        self._apply_layout()
        return self

    def create_gauge(
        self,
        value: float,
        max_value: float = 100,
        title: str = "Metric",
        threshold_ranges: Optional[List[Tuple[float, float, str]]] = None,
    ) -> "PlotlyChart":
        """
        Create gauge chart.

        Args:
            value: Current value
            max_value: Maximum value
            title: Gauge title
            threshold_ranges: List of (min, max, color) tuples

        Returns:
            self
        """
        # Default ranges: green, yellow, red
        if not threshold_ranges:
            third = max_value / 3
            threshold_ranges = [(0, third, "green"), (third, 2 * third, "yellow"), (2 * third, max_value, "red")]

        steps = [{"range": [r[0], r[1]], "color": r[2]} for r in threshold_ranges]

        self.fig = go.Figure(
            go.Indicator(
                mode="gauge+number+delta",
                value=value,
                title={"text": title},
                delta={"reference": max_value * 0.8},
                gauge={"axis": {"range": [None, max_value]}, "steps": steps, "threshold": {"line": {"color": "red", "width": 4}, "thickness": 0.75, "value": max_value * 0.9}},
            )
        )

        self._apply_layout()
        return self

    def create_funnel(self, data: Dict[str, float]) -> "PlotlyChart":
        """
        Create funnel chart.

        Args:
            data: Stage -> value mapping

        Returns:
            self
        """
        stages = list(data.keys())
        values = list(data.values())

        self.fig = go.Figure(go.Funnel(y=stages, x=values))

        self._apply_layout()
        return self

    def create_treemap(self, data: pd.DataFrame, labels: str, parents: str, values: str) -> "PlotlyChart":
        """
        Create treemap.

        Args:
            data: Data
            labels: Labels column
            parents: Parents column
            values: Values column

        Returns:
            self
        """
        self.fig = go.Figure(go.Treemap(labels=data[labels], parents=data[parents], values=data[values]))

        self._apply_layout()
        return self

    def add_annotation(self, text: str, x: float, y: float, arrow: bool = True) -> "PlotlyChart":
        """
        Add text annotation to chart.

        Args:
            text: Annotation text
            x: X coordinate
            y: Y coordinate
            arrow: Show arrow

        Returns:
            self
        """
        if self.fig:
            self.fig.add_annotation(
                x=x,
                y=y,
                text=text,
                showarrow=arrow,
                arrowhead=2,
                arrowsize=1,
                arrowwidth=2,
            )

        return self

    def _apply_layout(self):
        """Apply layout configuration"""
        if not self.fig:
            return

        layout_config = {
            "title": self.config.title,
            "template": self.config.theme.value,
            "showlegend": self.config.show_legend,
            "font": {"size": self.config.font_size},
        }

        if self.config.width:
            layout_config["width"] = self.config.width

        if self.config.height:
            layout_config["height"] = self.config.height

        self.fig.update_layout(**layout_config)

        # Make responsive
        if self.config.responsive:
            self.fig.update_layout(autosize=True)

    def to_html(self, filename: Optional[str] = None, include_plotlyjs: str = "cdn") -> str:
        """
        Export to HTML.

        Args:
            filename: Output filename (optional)
            include_plotlyjs: Include Plotly.js ('cdn', True, False)

        Returns:
            HTML string
        """
        if not self.fig:
            raise ValueError("No figure created")

        html = self.fig.to_html(include_plotlyjs=include_plotlyjs)

        if filename:
            with open(filename, "w") as f:
                f.write(html)

        return html

    def to_json(self) -> str:
        """Export to JSON"""
        if not self.fig:
            raise ValueError("No figure created")

        return self.fig.to_json()

    def show(self):
        """Display chart in browser"""
        if self.fig:
            self.fig.show()


class DashboardBuilder:
    """Build multi-chart dashboards"""

    def __init__(self, title: str = "Dashboard", rows: int = 2, cols: int = 2):
        """
        Initialize dashboard.

        Args:
            title: Dashboard title
            rows: Number of rows
            cols: Number of columns
        """
        if not PLOTLY_AVAILABLE:
            raise ImportError("Plotly required")

        self.title = title
        self.fig = make_subplots(rows=rows, cols=cols, subplot_titles=[f"Chart {i+1}" for i in range(rows * cols)])

        self.current_row = 1
        self.current_col = 1
        self.max_cols = cols

    def add_chart(self, chart: PlotlyChart, row: Optional[int] = None, col: Optional[int] = None):
        """
        Add chart to dashboard.

        Args:
            chart: PlotlyChart instance
            row: Row position (auto if None)
            col: Column position (auto if None)
        """
        if not chart.fig:
            raise ValueError("Chart has no figure")

        row = row or self.current_row
        col = col or self.current_col

        # Add all traces from chart
        for trace in chart.fig.data:
            self.fig.add_trace(trace, row=row, col=col)

        # Move to next position
        self.current_col += 1
        if self.current_col > self.max_cols:
            self.current_col = 1
            self.current_row += 1

    def to_html(self, filename: Optional[str] = None) -> str:
        """Export dashboard to HTML"""
        self.fig.update_layout(title_text=self.title, height=800)

        html = self.fig.to_html(include_plotlyjs="cdn")

        if filename:
            with open(filename, "w") as f:
                f.write(html)

        return html

    def show(self):
        """Display dashboard"""
        self.fig.show()


logger.info("Interactive Visualization module loaded")
