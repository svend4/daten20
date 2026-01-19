"""
Advanced BI Dashboard UI Module

Provides REST API endpoints and React component specifications for
enterprise-grade Business Intelligence dashboards.

Features:
- REST API for dashboard data
- WebSocket support for real-time updates
- React component specifications
- Chart configurations (Chart.js, D3.js compatible)
- Dashboard layouts and themes
- Interactive filters and drill-downs
- Export functionality
- Responsive design specifications

API Endpoints:
    GET  /api/bi/dashboards - List all dashboards
    GET  /api/bi/dashboards/{id} - Get dashboard
    POST /api/bi/dashboards - Create dashboard
    PUT  /api/bi/dashboards/{id} - Update dashboard
    DELETE /api/bi/dashboards/{id} - Delete dashboard
    GET  /api/bi/kpis - Get KPI data
    GET  /api/bi/charts/{id} - Get chart data
    POST /api/bi/export - Export dashboard
    WS   /ws/bi/realtime - Real-time updates

Frontend Stack:
- React 18+ with TypeScript
- Chart.js / Recharts for visualizations
- TailwindCSS for styling
- WebSocket for real-time updates
- React Query for data fetching
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime, timedelta
from enum import Enum
import json
import logging
from decimal import Decimal

logger = logging.getLogger(__name__)


# ============================================================
# Data Models
# ============================================================

class DashboardTheme(str, Enum):
    """Dashboard color themes"""
    LIGHT = "light"
    DARK = "dark"
    CORPORATE = "corporate"
    COLORFUL = "colorful"


class LayoutType(str, Enum):
    """Dashboard layout types"""
    GRID = "grid"
    FREEFORM = "freeform"
    TABBED = "tabbed"


class WidgetType(str, Enum):
    """Dashboard widget types"""
    KPI_CARD = "kpi_card"
    LINE_CHART = "line_chart"
    BAR_CHART = "bar_chart"
    PIE_CHART = "pie_chart"
    AREA_CHART = "area_chart"
    GAUGE = "gauge"
    TABLE = "table"
    HEATMAP = "heatmap"
    FUNNEL = "funnel"
    SCATTER = "scatter"
    MAP = "map"


@dataclass
class WidgetPosition:
    """Widget position in grid layout"""
    x: int  # Grid column
    y: int  # Grid row
    width: int  # Number of columns
    height: int  # Number of rows


@dataclass
class ChartConfig:
    """Chart.js/Recharts compatible configuration"""
    type: str
    data: Dict[str, Any]
    options: Dict[str, Any] = field(default_factory=dict)
    responsive: bool = True
    maintain_aspect_ratio: bool = True


@dataclass
class Widget:
    """Dashboard widget/component"""
    id: str
    type: WidgetType
    title: str
    position: WidgetPosition
    config: ChartConfig
    data_source: str  # API endpoint or query
    refresh_interval: Optional[int] = None  # Seconds, None = manual only
    filters: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DashboardLayout:
    """Dashboard layout configuration"""
    type: LayoutType
    grid_columns: int = 12
    grid_row_height: int = 60  # pixels
    gap: int = 16  # pixels
    widgets: List[Widget] = field(default_factory=list)


@dataclass
class Dashboard:
    """Complete dashboard definition"""
    id: str
    name: str
    description: str
    theme: DashboardTheme
    layout: DashboardLayout
    permissions: Dict[str, List[str]]  # role -> [permissions]
    created_at: datetime
    updated_at: datetime
    created_by: str
    is_public: bool = False
    tags: List[str] = field(default_factory=list)


@dataclass
class KPIData:
    """KPI data for frontend"""
    id: str
    label: str
    value: str  # Formatted value (e.g., "$123.4K")
    raw_value: float
    change: float  # Percentage change
    trend: str  # "up", "down", "stable"
    sparkline: Optional[List[float]] = None  # Mini trend line data
    target: Optional[float] = None
    unit: str = ""
    icon: str = ""
    color: str = "#3b82f6"  # Tailwind blue-500


# ============================================================
# React Component Specifications
# ============================================================

class ReactComponent:
    """Base class for React component specifications"""

    @staticmethod
    def kpi_card(kpi: KPIData) -> Dict[str, Any]:
        """
        Generate KPI card component specification

        Returns React component props for a KPI card showing:
        - Main value
        - Trend indicator
        - Sparkline
        - Comparison to target
        """
        return {
            "component": "KPICard",
            "props": {
                "id": kpi.id,
                "label": kpi.label,
                "value": kpi.value,
                "change": kpi.change,
                "trend": kpi.trend,
                "sparkline": kpi.sparkline or [],
                "target": kpi.target,
                "icon": kpi.icon,
                "color": kpi.color,
                "unit": kpi.unit
            },
            "className": "rounded-lg shadow-md p-6 bg-white dark:bg-gray-800 transition-all hover:shadow-lg"
        }

    @staticmethod
    def line_chart(
        title: str,
        labels: List[str],
        datasets: List[Dict[str, Any]],
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate line chart component specification

        Compatible with Chart.js and Recharts
        """
        return {
            "component": "LineChart",
            "props": {
                "title": title,
                "data": {
                    "labels": labels,
                    "datasets": datasets
                },
                "options": options or {
                    "responsive": True,
                    "maintainAspectRatio": False,
                    "plugins": {
                        "legend": {"position": "top"},
                        "title": {"display": True, "text": title}
                    },
                    "scales": {
                        "y": {"beginAtZero": True}
                    }
                }
            },
            "className": "h-96 p-4"
        }

    @staticmethod
    def bar_chart(
        title: str,
        labels: List[str],
        datasets: List[Dict[str, Any]],
        horizontal: bool = False
    ) -> Dict[str, Any]:
        """Generate bar chart component"""
        return {
            "component": "BarChart",
            "props": {
                "title": title,
                "data": {"labels": labels, "datasets": datasets},
                "options": {
                    "indexAxis": "y" if horizontal else "x",
                    "responsive": True,
                    "plugins": {
                        "legend": {"position": "top"},
                        "title": {"display": True, "text": title}
                    }
                }
            },
            "className": "h-96 p-4"
        }

    @staticmethod
    def pie_chart(
        title: str,
        labels: List[str],
        data: List[float],
        colors: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Generate pie chart component"""
        return {
            "component": "PieChart",
            "props": {
                "title": title,
                "data": {
                    "labels": labels,
                    "datasets": [{
                        "data": data,
                        "backgroundColor": colors or [
                            "#3b82f6", "#10b981", "#f59e0b",
                            "#ef4444", "#8b5cf6", "#ec4899"
                        ]
                    }]
                },
                "options": {
                    "responsive": True,
                    "plugins": {
                        "legend": {"position": "right"},
                        "title": {"display": True, "text": title}
                    }
                }
            },
            "className": "h-96 p-4"
        }

    @staticmethod
    def gauge_chart(
        title: str,
        value: float,
        max_value: float,
        target: Optional[float] = None,
        color: str = "#3b82f6"
    ) -> Dict[str, Any]:
        """Generate gauge/radial chart component"""
        percentage = (value / max_value) * 100 if max_value > 0 else 0

        return {
            "component": "GaugeChart",
            "props": {
                "title": title,
                "value": value,
                "max": max_value,
                "percentage": round(percentage, 1),
                "target": target,
                "color": color,
                "showTarget": target is not None
            },
            "className": "h-64 p-4"
        }

    @staticmethod
    def data_table(
        title: str,
        columns: List[Dict[str, str]],
        data: List[Dict[str, Any]],
        sortable: bool = True,
        filterable: bool = True,
        exportable: bool = True
    ) -> Dict[str, Any]:
        """Generate data table component"""
        return {
            "component": "DataTable",
            "props": {
                "title": title,
                "columns": columns,
                "data": data,
                "sortable": sortable,
                "filterable": filterable,
                "exportable": exportable,
                "pageSize": 10,
                "showPagination": True
            },
            "className": "rounded-lg shadow-md bg-white dark:bg-gray-800"
        }


# ============================================================
# Dashboard Builder
# ============================================================

class DashboardBuilder:
    """
    Builder for creating dashboards programmatically

    Provides fluent API for building complex dashboards.
    """

    def __init__(self, dashboard_id: str, name: str):
        self.dashboard = Dashboard(
            id=dashboard_id,
            name=name,
            description="",
            theme=DashboardTheme.LIGHT,
            layout=DashboardLayout(type=LayoutType.GRID),
            permissions={},
            created_at=datetime.now(),
            updated_at=datetime.now(),
            created_by="system"
        )
        self._next_widget_id = 1

    def set_description(self, description: str) -> 'DashboardBuilder':
        """Set dashboard description"""
        self.dashboard.description = description
        return self

    def set_theme(self, theme: DashboardTheme) -> 'DashboardBuilder':
        """Set dashboard theme"""
        self.dashboard.theme = theme
        return self

    def set_layout(self, layout_type: LayoutType, columns: int = 12) -> 'DashboardBuilder':
        """Set layout type and grid columns"""
        self.dashboard.layout.type = layout_type
        self.dashboard.layout.grid_columns = columns
        return self

    def add_kpi(
        self,
        title: str,
        kpi_data: KPIData,
        position: Optional[WidgetPosition] = None
    ) -> 'DashboardBuilder':
        """Add KPI card widget"""
        if position is None:
            position = self._next_position(width=3, height=2)

        widget = Widget(
            id=f"widget_{self._next_widget_id}",
            type=WidgetType.KPI_CARD,
            title=title,
            position=position,
            config=ChartConfig(
                type="kpi",
                data={"kpi": kpi_data.__dict__}
            ),
            data_source=f"/api/bi/kpis/{kpi_data.id}"
        )

        self.dashboard.layout.widgets.append(widget)
        self._next_widget_id += 1
        return self

    def add_line_chart(
        self,
        title: str,
        data_source: str,
        position: Optional[WidgetPosition] = None,
        refresh_interval: Optional[int] = None
    ) -> 'DashboardBuilder':
        """Add line chart widget"""
        if position is None:
            position = self._next_position(width=6, height=4)

        widget = Widget(
            id=f"widget_{self._next_widget_id}",
            type=WidgetType.LINE_CHART,
            title=title,
            position=position,
            config=ChartConfig(type="line", data={}),
            data_source=data_source,
            refresh_interval=refresh_interval
        )

        self.dashboard.layout.widgets.append(widget)
        self._next_widget_id += 1
        return self

    def add_bar_chart(
        self,
        title: str,
        data_source: str,
        position: Optional[WidgetPosition] = None,
        horizontal: bool = False
    ) -> 'DashboardBuilder':
        """Add bar chart widget"""
        if position is None:
            position = self._next_position(width=6, height=4)

        widget = Widget(
            id=f"widget_{self._next_widget_id}",
            type=WidgetType.BAR_CHART,
            title=title,
            position=position,
            config=ChartConfig(
                type="bar",
                data={},
                options={"indexAxis": "y" if horizontal else "x"}
            ),
            data_source=data_source
        )

        self.dashboard.layout.widgets.append(widget)
        self._next_widget_id += 1
        return self

    def add_pie_chart(
        self,
        title: str,
        data_source: str,
        position: Optional[WidgetPosition] = None
    ) -> 'DashboardBuilder':
        """Add pie chart widget"""
        if position is None:
            position = self._next_position(width=4, height=4)

        widget = Widget(
            id=f"widget_{self._next_widget_id}",
            type=WidgetType.PIE_CHART,
            title=title,
            position=position,
            config=ChartConfig(type="pie", data={}),
            data_source=data_source
        )

        self.dashboard.layout.widgets.append(widget)
        self._next_widget_id += 1
        return self

    def add_gauge(
        self,
        title: str,
        data_source: str,
        position: Optional[WidgetPosition] = None
    ) -> 'DashboardBuilder':
        """Add gauge widget"""
        if position is None:
            position = self._next_position(width=3, height=3)

        widget = Widget(
            id=f"widget_{self._next_widget_id}",
            type=WidgetType.GAUGE,
            title=title,
            position=position,
            config=ChartConfig(type="gauge", data={}),
            data_source=data_source
        )

        self.dashboard.layout.widgets.append(widget)
        self._next_widget_id += 1
        return self

    def add_table(
        self,
        title: str,
        data_source: str,
        position: Optional[WidgetPosition] = None
    ) -> 'DashboardBuilder':
        """Add data table widget"""
        if position is None:
            position = self._next_position(width=12, height=6)

        widget = Widget(
            id=f"widget_{self._next_widget_id}",
            type=WidgetType.TABLE,
            title=title,
            position=position,
            config=ChartConfig(type="table", data={}),
            data_source=data_source
        )

        self.dashboard.layout.widgets.append(widget)
        self._next_widget_id += 1
        return self

    def set_permissions(self, permissions: Dict[str, List[str]]) -> 'DashboardBuilder':
        """Set role-based permissions"""
        self.dashboard.permissions = permissions
        return self

    def build(self) -> Dashboard:
        """Build and return the dashboard"""
        return self.dashboard

    def _next_position(self, width: int, height: int) -> WidgetPosition:
        """Calculate next available position in grid"""
        # Simple row-based placement
        row = len(self.dashboard.layout.widgets) // 2
        col = (len(self.dashboard.layout.widgets) % 2) * 6

        return WidgetPosition(x=col, y=row * 4, width=width, height=height)


# ============================================================
# REST API Handlers
# ============================================================

class BIDashboardAPI:
    """
    REST API handlers for BI dashboards

    Provides CRUD operations and data endpoints for dashboards.
    """

    def __init__(self):
        self.dashboards: Dict[str, Dashboard] = {}
        self.widgets_data_cache: Dict[str, Any] = {}

    def list_dashboards(
        self,
        user_id: str,
        tags: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        GET /api/bi/dashboards

        List all dashboards accessible to user
        """
        accessible = []

        for dashboard in self.dashboards.values():
            # Check permissions
            if dashboard.is_public or self._has_access(user_id, dashboard):
                # Return summary without full widget data
                accessible.append({
                    "id": dashboard.id,
                    "name": dashboard.name,
                    "description": dashboard.description,
                    "theme": dashboard.theme.value,
                    "widgets_count": len(dashboard.layout.widgets),
                    "created_at": dashboard.created_at.isoformat(),
                    "updated_at": dashboard.updated_at.isoformat(),
                    "is_public": dashboard.is_public,
                    "tags": dashboard.tags
                })

        # Filter by tags if provided
        if tags:
            accessible = [
                d for d in accessible
                if any(tag in d["tags"] for tag in tags)
            ]

        return accessible

    def get_dashboard(
        self,
        dashboard_id: str,
        user_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        GET /api/bi/dashboards/{id}

        Get complete dashboard configuration
        """
        dashboard = self.dashboards.get(dashboard_id)

        if not dashboard:
            return None

        if not (dashboard.is_public or self._has_access(user_id, dashboard)):
            return None

        # Serialize dashboard
        return {
            "id": dashboard.id,
            "name": dashboard.name,
            "description": dashboard.description,
            "theme": dashboard.theme.value,
            "layout": {
                "type": dashboard.layout.type.value,
                "columns": dashboard.layout.grid_columns,
                "rowHeight": dashboard.layout.grid_row_height,
                "gap": dashboard.layout.gap,
                "widgets": [
                    {
                        "id": w.id,
                        "type": w.type.value,
                        "title": w.title,
                        "position": {
                            "x": w.position.x,
                            "y": w.position.y,
                            "width": w.position.width,
                            "height": w.position.height
                        },
                        "dataSource": w.data_source,
                        "refreshInterval": w.refresh_interval,
                        "config": {
                            "type": w.config.type,
                            "responsive": w.config.responsive,
                            "options": w.config.options
                        }
                    }
                    for w in dashboard.layout.widgets
                ]
            },
            "permissions": dashboard.permissions,
            "created_at": dashboard.created_at.isoformat(),
            "updated_at": dashboard.updated_at.isoformat(),
            "is_public": dashboard.is_public,
            "tags": dashboard.tags
        }

    def create_dashboard(
        self,
        dashboard: Dashboard,
        user_id: str
    ) -> Dict[str, Any]:
        """
        POST /api/bi/dashboards

        Create new dashboard
        """
        dashboard.created_by = user_id
        dashboard.created_at = datetime.now()
        dashboard.updated_at = datetime.now()

        self.dashboards[dashboard.id] = dashboard

        logger.info(f"Created dashboard {dashboard.id} by user {user_id}")

        return {"id": dashboard.id, "message": "Dashboard created successfully"}

    def update_dashboard(
        self,
        dashboard_id: str,
        updates: Dict[str, Any],
        user_id: str
    ) -> Dict[str, Any]:
        """
        PUT /api/bi/dashboards/{id}

        Update dashboard
        """
        dashboard = self.dashboards.get(dashboard_id)

        if not dashboard:
            return {"error": "Dashboard not found"}

        if not self._has_access(user_id, dashboard):
            return {"error": "Permission denied"}

        # Apply updates
        if "name" in updates:
            dashboard.name = updates["name"]
        if "description" in updates:
            dashboard.description = updates["description"]
        if "theme" in updates:
            dashboard.theme = DashboardTheme(updates["theme"])
        if "layout" in updates:
            # Update layout (simplified)
            pass

        dashboard.updated_at = datetime.now()

        logger.info(f"Updated dashboard {dashboard_id} by user {user_id}")

        return {"message": "Dashboard updated successfully"}

    def delete_dashboard(
        self,
        dashboard_id: str,
        user_id: str
    ) -> Dict[str, Any]:
        """
        DELETE /api/bi/dashboards/{id}

        Delete dashboard
        """
        dashboard = self.dashboards.get(dashboard_id)

        if not dashboard:
            return {"error": "Dashboard not found"}

        if dashboard.created_by != user_id:
            return {"error": "Only creator can delete dashboard"}

        del self.dashboards[dashboard_id]

        logger.info(f"Deleted dashboard {dashboard_id} by user {user_id}")

        return {"message": "Dashboard deleted successfully"}

    def get_widget_data(
        self,
        widget_id: str,
        filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        GET /api/bi/widgets/{id}/data

        Get data for specific widget
        """
        # In production, this would fetch from database/cache
        # For now, return mock data structure

        cache_key = f"{widget_id}:{json.dumps(filters or {}, sort_keys=True)}"

        if cache_key in self.widgets_data_cache:
            return self.widgets_data_cache[cache_key]

        # Mock data (in production, fetch from data source)
        data = {
            "widget_id": widget_id,
            "timestamp": datetime.now().isoformat(),
            "data": {}
        }

        self.widgets_data_cache[cache_key] = data
        return data

    def export_dashboard(
        self,
        dashboard_id: str,
        format: str,
        user_id: str
    ) -> Dict[str, Any]:
        """
        POST /api/bi/dashboards/{id}/export

        Export dashboard to PDF/Excel/PowerPoint
        """
        dashboard = self.dashboards.get(dashboard_id)

        if not dashboard:
            return {"error": "Dashboard not found"}

        if not (dashboard.is_public or self._has_access(user_id, dashboard)):
            return {"error": "Permission denied"}

        # In production, generate actual file
        export_url = f"/exports/{dashboard_id}_{datetime.now().timestamp()}.{format}"

        logger.info(f"Exported dashboard {dashboard_id} to {format} by user {user_id}")

        return {
            "download_url": export_url,
            "format": format,
            "expires_at": (datetime.now() + timedelta(hours=24)).isoformat()
        }

    def _has_access(self, user_id: str, dashboard: Dashboard) -> bool:
        """Check if user has access to dashboard"""
        # Simplified permission check
        # In production, check against user roles and dashboard permissions
        return True


# ============================================================
# Pre-built Dashboard Templates
# ============================================================

class DashboardTemplates:
    """Pre-built dashboard templates"""

    @staticmethod
    def executive_overview() -> Dashboard:
        """Executive KPI overview dashboard"""
        builder = DashboardBuilder("exec_overview", "Executive Overview")

        builder.set_description("High-level KPIs and trends for executive team")
        builder.set_theme(DashboardTheme.CORPORATE)

        # KPI cards
        mrr_kpi = KPIData(
            id="mrr",
            label="Monthly Recurring Revenue",
            value="$124.5K",
            raw_value=124500,
            change=12.5,
            trend="up",
            icon="dollar",
            color="#10b981"
        )
        builder.add_kpi("MRR", mrr_kpi, WidgetPosition(0, 0, 3, 2))

        arr_kpi = KPIData(
            id="arr",
            label="Annual Recurring Revenue",
            value="$1.49M",
            raw_value=1494000,
            change=15.2,
            trend="up",
            icon="chart",
            color="#3b82f6"
        )
        builder.add_kpi("ARR", arr_kpi, WidgetPosition(3, 0, 3, 2))

        churn_kpi = KPIData(
            id="churn",
            label="Churn Rate",
            value="2.3%",
            raw_value=2.3,
            change=-0.5,
            trend="down",
            target=2.0,
            icon="users",
            color="#ef4444"
        )
        builder.add_kpi("Churn", churn_kpi, WidgetPosition(6, 0, 3, 2))

        clv_kpi = KPIData(
            id="clv",
            label="Customer Lifetime Value",
            value="$4.2K",
            raw_value=4200,
            change=8.1,
            trend="up",
            icon="trophy",
            color="#f59e0b"
        )
        builder.add_kpi("CLV", clv_kpi, WidgetPosition(9, 0, 3, 2))

        # Charts
        builder.add_line_chart(
            "Revenue Trend",
            "/api/bi/data/revenue_trend",
            WidgetPosition(0, 2, 8, 4),
            refresh_interval=300
        )

        builder.add_pie_chart(
            "Revenue by Plan",
            "/api/bi/data/revenue_by_plan",
            WidgetPosition(8, 2, 4, 4)
        )

        builder.set_permissions({
            "executive": ["view", "export"],
            "admin": ["view", "edit", "export"]
        })

        return builder.build()

    @staticmethod
    def sales_dashboard() -> Dashboard:
        """Sales performance dashboard"""
        builder = DashboardBuilder("sales_dashboard", "Sales Performance")

        builder.set_description("Track sales metrics and pipeline")
        builder.set_theme(DashboardTheme.COLORFUL)

        # Add sales-specific widgets
        builder.add_bar_chart(
            "Sales by Region",
            "/api/bi/data/sales_by_region",
            WidgetPosition(0, 0, 6, 4)
        )

        builder.add_line_chart(
            "Pipeline Growth",
            "/api/bi/data/pipeline_growth",
            WidgetPosition(6, 0, 6, 4)
        )

        builder.add_table(
            "Top Deals",
            "/api/bi/data/top_deals",
            WidgetPosition(0, 4, 12, 6)
        )

        return builder.build()


# ============================================================
# WebSocket Real-time Updates
# ============================================================

class RealtimeDashboardUpdates:
    """
    WebSocket handler for real-time dashboard updates

    Broadcasts widget data updates to connected clients.
    """

    def __init__(self):
        self.subscribers: Dict[str, List[Any]] = {}  # dashboard_id -> [connections]

    async def subscribe(self, dashboard_id: str, connection: Any):
        """Subscribe to dashboard updates"""
        if dashboard_id not in self.subscribers:
            self.subscribers[dashboard_id] = []

        self.subscribers[dashboard_id].append(connection)
        logger.info(f"Client subscribed to dashboard {dashboard_id}")

    async def unsubscribe(self, dashboard_id: str, connection: Any):
        """Unsubscribe from dashboard updates"""
        if dashboard_id in self.subscribers:
            self.subscribers[dashboard_id].remove(connection)

    async def broadcast_update(
        self,
        dashboard_id: str,
        widget_id: str,
        data: Dict[str, Any]
    ):
        """Broadcast widget data update to all subscribers"""
        if dashboard_id not in self.subscribers:
            return

        message = {
            "type": "widget_update",
            "dashboard_id": dashboard_id,
            "widget_id": widget_id,
            "data": data,
            "timestamp": datetime.now().isoformat()
        }

        for connection in self.subscribers[dashboard_id]:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Failed to send update to client: {e}")


# ============================================================
# Example Usage
# ============================================================

if __name__ == "__main__":
    # Create executive dashboard
    dashboard = DashboardTemplates.executive_overview()
    print(f"Created dashboard: {dashboard.name}")
    print(f"Widgets: {len(dashboard.layout.widgets)}")

    # Initialize API
    api = BIDashboardAPI()
    api.create_dashboard(dashboard, user_id="admin")

    # Get dashboard
    dashboard_data = api.get_dashboard(dashboard.id, user_id="admin")
    print(f"\nDashboard JSON:")
    print(json.dumps(dashboard_data, indent=2, default=str))

    # Build custom dashboard
    custom = (
        DashboardBuilder("custom_1", "Custom Dashboard")
        .set_description("My custom dashboard")
        .set_theme(DashboardTheme.DARK)
        .add_line_chart("Revenue", "/api/data/revenue")
        .add_bar_chart("Users", "/api/data/users")
        .add_pie_chart("Distribution", "/api/data/distribution")
        .build()
    )

    print(f"\n✅ Created custom dashboard with {len(custom.layout.widgets)} widgets")
