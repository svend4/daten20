"""
Business Intelligence Engine

Provides OLAP cube creation, multidimensional analysis, and dashboard building.
"""

from typing import List, Dict, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
from collections import defaultdict


class AggregationType(str, Enum):
    """Aggregation types"""
    SUM = "sum"
    AVG = "avg"
    COUNT = "count"
    MIN = "min"
    MAX = "max"
    DISTINCT_COUNT = "distinct_count"


class ChartType(str, Enum):
    """Chart types"""
    LINE = "line"
    BAR = "bar"
    PIE = "pie"
    SCATTER = "scatter"
    HEATMAP = "heatmap"
    TABLE = "table"
    KPI = "kpi"
    GAUGE = "gauge"


@dataclass
class Dimension:
    """OLAP dimension"""
    name: str
    display_name: str
    field: str
    data_type: str = "string"
    hierarchies: List[str] = field(default_factory=list)


@dataclass
class Measure:
    """OLAP measure"""
    name: str
    display_name: str
    field: str
    aggregation: AggregationType
    format: str = "{:.2f}"


@dataclass
class Filter:
    """Data filter"""
    dimension: str
    operator: str  # eq, ne, gt, lt, in, contains
    value: Any


@dataclass
class Widget:
    """Dashboard widget"""
    id: str
    type: ChartType
    title: str
    dimensions: List[str]
    measures: List[str]
    filters: List[Filter] = field(default_factory=list)
    settings: Dict[str, Any] = field(default_factory=dict)
    position: Dict[str, int] = field(default_factory=dict)


@dataclass
class Dashboard:
    """BI Dashboard"""
    id: str
    name: str
    description: str
    widgets: List[Widget] = field(default_factory=list)
    filters: List[Filter] = field(default_factory=list)
    created_by: Optional[int] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


class OLAPCube:
    """OLAP cube for multidimensional analysis"""

    def __init__(
        self,
        name: str,
        dimensions: List[Dimension],
        measures: List[Measure]
    ):
        self.name = name
        self.dimensions = {d.name: d for d in dimensions}
        self.measures = {m.name: m for m in measures}
        self.data: List[Dict[str, Any]] = []

    def load_data(self, data: List[Dict[str, Any]]):
        """Load data into cube"""
        self.data = data

    def slice(self, dimension: str, value: Any) -> 'OLAPCube':
        """Slice operation - fix one dimension"""
        filtered_data = [
            row for row in self.data
            if row.get(dimension) == value
        ]

        new_cube = OLAPCube(
            name=f"{self.name}_slice",
            dimensions=list(self.dimensions.values()),
            measures=list(self.measures.values())
        )
        new_cube.data = filtered_data
        return new_cube

    def dice(self, filters: List[Filter]) -> 'OLAPCube':
        """Dice operation - multiple dimension filters"""
        filtered_data = self.data.copy()

        for f in filters:
            if f.operator == "eq":
                filtered_data = [r for r in filtered_data if r.get(f.dimension) == f.value]
            elif f.operator == "in":
                filtered_data = [r for r in filtered_data if r.get(f.dimension) in f.value]
            elif f.operator == "gt":
                filtered_data = [r for r in filtered_data if r.get(f.dimension) > f.value]
            elif f.operator == "lt":
                filtered_data = [r for r in filtered_data if r.get(f.dimension) < f.value]

        new_cube = OLAPCube(
            name=f"{self.name}_dice",
            dimensions=list(self.dimensions.values()),
            measures=list(self.measures.values())
        )
        new_cube.data = filtered_data
        return new_cube

    def drill_down(self, dimension: str) -> Dict[Any, List[Dict[str, Any]]]:
        """Drill down - break down by dimension"""
        groups = defaultdict(list)

        for row in self.data:
            key = row.get(dimension)
            groups[key].append(row)

        return dict(groups)

    def aggregate(
        self,
        group_by: List[str],
        measures: List[str]
    ) -> List[Dict[str, Any]]:
        """Aggregate data by dimensions"""
        groups = defaultdict(list)

        # Group data
        for row in self.data:
            key = tuple(row.get(dim) for dim in group_by)
            groups[key].append(row)

        # Calculate aggregations
        results = []
        for key, rows in groups.items():
            result = dict(zip(group_by, key))

            for measure_name in measures:
                if measure_name not in self.measures:
                    continue

                measure = self.measures[measure_name]
                values = [row.get(measure.field) for row in rows if row.get(measure.field) is not None]

                if not values:
                    result[measure_name] = 0
                    continue

                if measure.aggregation == AggregationType.SUM:
                    result[measure_name] = sum(values)
                elif measure.aggregation == AggregationType.AVG:
                    result[measure_name] = sum(values) / len(values)
                elif measure.aggregation == AggregationType.COUNT:
                    result[measure_name] = len(values)
                elif measure.aggregation == AggregationType.MIN:
                    result[measure_name] = min(values)
                elif measure.aggregation == AggregationType.MAX:
                    result[measure_name] = max(values)
                elif measure.aggregation == AggregationType.DISTINCT_COUNT:
                    result[measure_name] = len(set(values))

            results.append(result)

        return results


class BIEngine:
    """Business Intelligence Engine"""

    def __init__(self, database):
        self.database = database
        self.cubes: Dict[str, OLAPCube] = {}
        self.dashboards: Dict[str, Dashboard] = {}

        # Create default cube
        self._create_services_cube()

    def _create_services_cube(self):
        """Create services OLAP cube"""
        dimensions = [
            Dimension(
                name="region",
                display_name="Region",
                field="region",
                data_type="string"
            ),
            Dimension(
                name="service_name",
                display_name="Service Name",
                field="service_name",
                data_type="string"
            ),
            Dimension(
                name="date",
                display_name="Date",
                field="created_at",
                data_type="date",
                hierarchies=["year", "month", "day"]
            )
        ]

        measures = [
            Measure(
                name="total_services",
                display_name="Total Services",
                field="id",
                aggregation=AggregationType.COUNT
            ),
            Measure(
                name="avg_rate",
                display_name="Average Rate",
                field="brutto_rate",
                aggregation=AggregationType.AVG,
                format="{:.2f}€"
            ),
            Measure(
                name="total_hours",
                display_name="Total Hours",
                field="hours_per_month",
                aggregation=AggregationType.SUM
            ),
            Measure(
                name="min_rate",
                display_name="Min Rate",
                field="brutto_rate",
                aggregation=AggregationType.MIN,
                format="{:.2f}€"
            ),
            Measure(
                name="max_rate",
                display_name="Max Rate",
                field="brutto_rate",
                aggregation=AggregationType.MAX,
                format="{:.2f}€"
            )
        ]

        cube = OLAPCube(name="services", dimensions=dimensions, measures=measures)

        # Load data from database
        cursor = self.database.conn.cursor()
        cursor.execute("""
            SELECT id, service_name, region, brutto_rate, hours_per_month, created_at
            FROM services
        """)

        data = []
        for row in cursor.fetchall():
            data.append({
                'id': row[0],
                'service_name': row[1],
                'region': row[2],
                'brutto_rate': row[3],
                'hours_per_month': row[4],
                'created_at': row[5]
            })

        cube.load_data(data)
        self.cubes['services'] = cube

    def create_dashboard(self, dashboard: Dashboard):
        """Create new dashboard"""
        self.dashboards[dashboard.id] = dashboard

    def get_dashboard(self, dashboard_id: str) -> Optional[Dashboard]:
        """Get dashboard by ID"""
        return self.dashboards.get(dashboard_id)

    def execute_widget(self, widget: Widget) -> Dict[str, Any]:
        """Execute widget query and return data"""
        # Get cube
        # For now, assume services cube
        cube = self.cubes.get('services')
        if not cube:
            return {'error': 'Cube not found'}

        # Apply filters
        if widget.filters:
            cube = cube.dice(widget.filters)

        # Aggregate data
        data = cube.aggregate(
            group_by=widget.dimensions,
            measures=widget.measures
        )

        return {
            'type': widget.type.value,
            'data': data,
            'dimensions': widget.dimensions,
            'measures': widget.measures
        }

    def get_kpi_metrics(self) -> Dict[str, Any]:
        """Get key performance indicators"""
        cube = self.cubes.get('services')
        if not cube:
            return {}

        # Total services
        total_services = len(cube.data)

        # Average rate
        rates = [row['brutto_rate'] for row in cube.data if row.get('brutto_rate')]
        avg_rate = sum(rates) / len(rates) if rates else 0

        # Services by region
        by_region = cube.drill_down('region')

        # Growth rate (last 30 days)
        thirty_days_ago = (datetime.now() - timedelta(days=30)).isoformat()
        recent_services = [
            row for row in cube.data
            if row.get('created_at', '') >= thirty_days_ago
        ]
        growth_rate = len(recent_services) / total_services * 100 if total_services > 0 else 0

        return {
            'total_services': total_services,
            'avg_rate': f"{avg_rate:.2f}€",
            'regions_count': len(by_region),
            'growth_rate': f"{growth_rate:.1f}%",
            'recent_services_30d': len(recent_services)
        }

    def generate_report(
        self,
        cube_name: str,
        dimensions: List[str],
        measures: List[str],
        filters: Optional[List[Filter]] = None
    ) -> Dict[str, Any]:
        """Generate custom report"""
        cube = self.cubes.get(cube_name)
        if not cube:
            return {'error': f'Cube {cube_name} not found'}

        # Apply filters
        if filters:
            cube = cube.dice(filters)

        # Aggregate
        data = cube.aggregate(group_by=dimensions, measures=measures)

        return {
            'cube': cube_name,
            'dimensions': dimensions,
            'measures': measures,
            'data': data,
            'total_rows': len(data)
        }


class DashboardBuilder:
    """Visual dashboard builder"""

    def __init__(self, bi_engine: BIEngine):
        self.engine = bi_engine

    def create_default_dashboard(self) -> Dashboard:
        """Create default overview dashboard"""
        dashboard = Dashboard(
            id="overview",
            name="Services Overview",
            description="Main overview dashboard with key metrics"
        )

        # KPI Widget - Total Services
        dashboard.widgets.append(Widget(
            id="kpi_total",
            type=ChartType.KPI,
            title="Total Services",
            dimensions=[],
            measures=["total_services"],
            position={'x': 0, 'y': 0, 'w': 3, 'h': 2}
        ))

        # KPI Widget - Average Rate
        dashboard.widgets.append(Widget(
            id="kpi_avg_rate",
            type=ChartType.KPI,
            title="Average Rate",
            dimensions=[],
            measures=["avg_rate"],
            position={'x': 3, 'y': 0, 'w': 3, 'h': 2}
        ))

        # Bar Chart - Services by Region
        dashboard.widgets.append(Widget(
            id="bar_region",
            type=ChartType.BAR,
            title="Services by Region",
            dimensions=["region"],
            measures=["total_services"],
            position={'x': 0, 'y': 2, 'w': 6, 'h': 4}
        ))

        # Line Chart - Services Over Time
        dashboard.widgets.append(Widget(
            id="line_time",
            type=ChartType.LINE,
            title="Services Created Over Time",
            dimensions=["date"],
            measures=["total_services"],
            position={'x': 6, 'y': 0, 'w': 6, 'h': 6}
        ))

        # Table - Top Services
        dashboard.widgets.append(Widget(
            id="table_top",
            type=ChartType.TABLE,
            title="Top Services",
            dimensions=["service_name", "region"],
            measures=["avg_rate", "total_hours"],
            position={'x': 0, 'y': 6, 'w': 12, 'h': 4}
        ))

        return dashboard


# Global instance
_bi_engine: Optional[BIEngine] = None


def get_bi_engine(database=None) -> BIEngine:
    """Get global BI engine instance"""
    global _bi_engine

    if _bi_engine is None and database:
        _bi_engine = BIEngine(database)

    return _bi_engine


def configure_bi_engine(database):
    """Configure BI engine"""
    global _bi_engine
    _bi_engine = BIEngine(database)
