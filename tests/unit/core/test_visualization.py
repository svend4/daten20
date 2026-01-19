"""
Comprehensive tests for core/visualization.py module.

Tests chart generation with matplotlib and plotly, including
static charts, interactive dashboards, and comprehensive reports.
"""

import pytest
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch, call
import matplotlib.pyplot as plt


# ============================================================================
# ChartGenerator Tests
# ============================================================================


class TestChartGenerator:
    """Test ChartGenerator functionality."""

    @pytest.fixture
    def temp_output_dir(self, tmp_path):
        """Create temporary output directory."""
        return tmp_path / "charts"

    @pytest.fixture
    def chart_generator(self, temp_output_dir):
        """Create ChartGenerator instance."""
        from src.core.visualization import ChartGenerator

        return ChartGenerator(output_dir=temp_output_dir)

    @pytest.fixture
    def sample_services(self):
        """Create sample services for testing."""
        from src.models.service import Service, BasicInfo, SystemSettings
        from src.models.financial import FinancialParameters

        services = []

        regions = ["Berlin", "Munich", "Hamburg", "Berlin", "Munich"]
        rates = [35.0, 45.0, 40.0, 30.0, 50.0]

        for i, (region, rate) in enumerate(zip(regions, rates)):
            services.append(
                Service(
                    id=i + 1,
                    basic_info=BasicInfo(
                        service_name=f"Service {i+1}",
                        target_group="Test",
                        region=region
                    ),
                    financial=FinancialParameters(brutto_rate=rate),
                    system_settings=SystemSettings(service_type="standard"),
                    created_at=datetime(2024, 1, 1) + timedelta(days=i)
                )
            )

        return services

    def test_chart_generator_initialization(self, chart_generator, temp_output_dir):
        """Test ChartGenerator initialization"""
        assert chart_generator.output_dir == temp_output_dir
        assert temp_output_dir.exists()
        assert len(chart_generator.colors) == 5

    def test_chart_generator_default_output_dir(self):
        """Test ChartGenerator with default output directory"""
        from src.core.visualization import ChartGenerator

        generator = ChartGenerator()

        assert generator.output_dir == Path("data/exports/charts")

    @patch('matplotlib.pyplot.savefig')
    @patch('matplotlib.pyplot.close')
    def test_generate_service_distribution_by_region(self, mock_close, mock_savefig, chart_generator, sample_services):
        """Test generating region distribution chart"""
        output_file = "test_region.png"

        result = chart_generator.generate_service_distribution_by_region(
            sample_services,
            output_file=output_file
        )

        # Should save the chart
        mock_savefig.assert_called_once()
        mock_close.assert_called_once()

        # Should return path to file
        assert output_file in result
        assert str(chart_generator.output_dir) in result

    @patch('matplotlib.pyplot.savefig')
    @patch('matplotlib.pyplot.close')
    def test_generate_service_distribution_auto_filename(self, mock_close, mock_savefig, chart_generator, sample_services):
        """Test generating region distribution with auto filename"""
        result = chart_generator.generate_service_distribution_by_region(sample_services)

        # Should save with auto-generated filename
        mock_savefig.assert_called_once()
        assert "service_distribution_by_region" in result

    @patch('matplotlib.pyplot.savefig')
    @patch('matplotlib.pyplot.close')
    def test_generate_service_distribution_empty_services(self, mock_close, mock_savefig, chart_generator):
        """Test region distribution with no services"""
        result = chart_generator.generate_service_distribution_by_region([])

        # Should still generate chart
        mock_savefig.assert_called_once()

    @patch('matplotlib.pyplot.savefig')
    @patch('matplotlib.pyplot.close')
    def test_generate_rate_distribution(self, mock_close, mock_savefig, chart_generator, sample_services):
        """Test generating rate distribution chart"""
        output_file = "test_rates.png"

        result = chart_generator.generate_rate_distribution(
            sample_services,
            output_file=output_file
        )

        # Should save the chart
        mock_savefig.assert_called_once()
        mock_close.assert_called_once()

        assert output_file in result

    @patch('matplotlib.pyplot.savefig')
    @patch('matplotlib.pyplot.close')
    def test_generate_rate_distribution_no_rates(self, mock_close, mock_savefig, chart_generator):
        """Test rate distribution with services having no rates"""
        from src.models.service import Service, BasicInfo, SystemSettings
        from src.models.financial import FinancialParameters

        services = [
            Service(
                id=1,
                basic_info=BasicInfo(service_name="Test", target_group="T", region="Berlin"),
                financial=FinancialParameters(brutto_rate=0.0),  # Zero rate
                system_settings=SystemSettings(service_type="standard")
            )
        ]

        result = chart_generator.generate_rate_distribution(services)

        # Should return empty string when no data
        assert result == ""
        mock_savefig.assert_not_called()

    @patch('matplotlib.pyplot.savefig')
    @patch('matplotlib.pyplot.close')
    def test_generate_cost_breakdown_pie(self, mock_close, mock_savefig, chart_generator):
        """Test generating cost breakdown pie chart"""
        cost_breakdown = {
            "Base Rate": 30.0,
            "Insurance": 5.0,
            "Overhead": 3.0,
            "Profit": 2.0
        }

        output_file = "test_breakdown.png"

        result = chart_generator.generate_cost_breakdown_pie(
            cost_breakdown,
            output_file=output_file
        )

        # Should save the chart
        mock_savefig.assert_called_once()
        mock_close.assert_called_once()

        assert output_file in result

    @patch('matplotlib.pyplot.savefig')
    @patch('matplotlib.pyplot.close')
    def test_generate_trend_chart(self, mock_close, mock_savefig, chart_generator):
        """Test generating trend chart"""
        dates = [datetime(2024, 1, 1) + timedelta(days=i) for i in range(5)]
        values = [10.0, 15.0, 12.0, 18.0, 20.0]

        output_file = "test_trend.png"

        result = chart_generator.generate_trend_chart(
            dates=dates,
            values=values,
            title="Test Trend",
            ylabel="Value",
            output_file=output_file
        )

        # Should save the chart
        mock_savefig.assert_called_once()
        mock_close.assert_called_once()

        assert output_file in result

    @patch('matplotlib.pyplot.savefig')
    @patch('matplotlib.pyplot.close')
    def test_generate_trend_chart_custom_labels(self, mock_close, mock_savefig, chart_generator):
        """Test trend chart with custom labels"""
        dates = [datetime(2024, 1, 1)]
        values = [100.0]

        result = chart_generator.generate_trend_chart(
            dates=dates,
            values=values,
            title="Custom Title",
            ylabel="Custom Y-Label"
        )

        mock_savefig.assert_called_once()

    @patch('plotly.graph_objects.Figure.write_html')
    def test_generate_interactive_dashboard(self, mock_write_html, chart_generator, sample_services):
        """Test generating interactive dashboard"""
        output_file = "test_dashboard.html"

        result = chart_generator.generate_interactive_dashboard(
            sample_services,
            output_file=output_file
        )

        # Should save HTML file
        mock_write_html.assert_called_once()

        assert output_file in result
        assert ".html" in result

    @patch('plotly.graph_objects.Figure.write_html')
    def test_generate_interactive_dashboard_auto_filename(self, mock_write_html, chart_generator, sample_services):
        """Test dashboard with auto-generated filename"""
        result = chart_generator.generate_interactive_dashboard(sample_services)

        mock_write_html.assert_called_once()
        assert "interactive_dashboard" in result

    @patch('plotly.graph_objects.Figure.write_html')
    def test_generate_interactive_dashboard_empty_services(self, mock_write_html, chart_generator):
        """Test dashboard with no services"""
        result = chart_generator.generate_interactive_dashboard([])

        # Should still generate dashboard
        mock_write_html.assert_called_once()

    @patch('plotly.graph_objects.Figure.write_html')
    def test_generate_3d_scatter(self, mock_write_html, chart_generator, sample_services):
        """Test generating 3D scatter plot"""
        output_file = "test_3d.html"

        result = chart_generator.generate_3d_scatter(
            sample_services,
            output_file=output_file
        )

        # Should save HTML file
        mock_write_html.assert_called_once()

        assert output_file in result

    @patch('plotly.graph_objects.Figure.write_html')
    def test_generate_3d_scatter_auto_filename(self, mock_write_html, chart_generator, sample_services):
        """Test 3D scatter with auto-generated filename"""
        result = chart_generator.generate_3d_scatter(sample_services)

        mock_write_html.assert_called_once()
        assert "3d_scatter" in result


# ============================================================================
# Comprehensive Report Tests
# ============================================================================


class TestComprehensiveReport:
    """Test comprehensive report generation."""

    @pytest.fixture
    def sample_services(self):
        """Create sample services."""
        from src.models.service import Service, BasicInfo, SystemSettings
        from src.models.financial import FinancialParameters

        return [
            Service(
                id=1,
                basic_info=BasicInfo(service_name="Service 1", target_group="T", region="Berlin"),
                financial=FinancialParameters(brutto_rate=35.0),
                system_settings=SystemSettings(service_type="standard")
            ),
            Service(
                id=2,
                basic_info=BasicInfo(service_name="Service 2", target_group="T", region="Munich"),
                financial=FinancialParameters(brutto_rate=45.0),
                system_settings=SystemSettings(service_type="premium")
            )
        ]

    @patch('src.core.visualization.ChartGenerator.generate_service_distribution_by_region')
    @patch('src.core.visualization.ChartGenerator.generate_rate_distribution')
    @patch('src.core.visualization.ChartGenerator.generate_interactive_dashboard')
    @patch('src.core.visualization.ChartGenerator.generate_3d_scatter')
    def test_generate_comprehensive_report(
        self,
        mock_3d,
        mock_dashboard,
        mock_rate_dist,
        mock_region_dist,
        sample_services,
        tmp_path
    ):
        """Test generating comprehensive report"""
        from src.core.visualization import generate_comprehensive_report

        # Mock return values
        mock_region_dist.return_value = str(tmp_path / "region.png")
        mock_rate_dist.return_value = str(tmp_path / "rate.png")
        mock_dashboard.return_value = str(tmp_path / "dashboard.html")
        mock_3d.return_value = str(tmp_path / "3d.html")

        result = generate_comprehensive_report(sample_services, output_dir=tmp_path)

        # Should generate all 4 charts
        assert len(result) == 4
        assert "region_distribution" in result
        assert "rate_distribution" in result
        assert "dashboard" in result
        assert "3d_scatter" in result

        # All generator methods should be called
        mock_region_dist.assert_called_once()
        mock_rate_dist.assert_called_once()
        mock_dashboard.assert_called_once()
        mock_3d.assert_called_once()

    @patch('src.core.visualization.ChartGenerator.generate_service_distribution_by_region')
    @patch('src.core.visualization.ChartGenerator.generate_rate_distribution')
    @patch('src.core.visualization.ChartGenerator.generate_interactive_dashboard')
    @patch('src.core.visualization.ChartGenerator.generate_3d_scatter')
    def test_generate_comprehensive_report_error_handling(
        self,
        mock_3d,
        mock_dashboard,
        mock_rate_dist,
        mock_region_dist,
        sample_services,
        tmp_path
    ):
        """Test comprehensive report handles errors gracefully"""
        from src.core.visualization import generate_comprehensive_report

        # Simulate error in one chart
        mock_region_dist.side_effect = Exception("Chart error")
        mock_rate_dist.return_value = str(tmp_path / "rate.png")
        mock_dashboard.return_value = str(tmp_path / "dashboard.html")
        mock_3d.return_value = str(tmp_path / "3d.html")

        # Should not raise, but handle error
        result = generate_comprehensive_report(sample_services, output_dir=tmp_path)

        # Should return whatever charts succeeded
        assert isinstance(result, dict)


# ============================================================================
# Integration Tests
# ============================================================================


class TestVisualizationIntegration:
    """Integration tests for visualization system."""

    @pytest.fixture
    def sample_services(self):
        """Create diverse sample services."""
        from src.models.service import Service, BasicInfo, SystemSettings
        from src.models.financial import FinancialParameters

        services = []
        regions = ["Berlin", "Munich", "Hamburg"] * 3
        rates = [25.0, 30.0, 35.0, 40.0, 45.0, 50.0, 55.0, 60.0, 65.0]

        for i in range(9):
            services.append(
                Service(
                    id=i + 1,
                    basic_info=BasicInfo(
                        service_name=f"Service {i+1}",
                        target_group="Elderly" if i % 2 == 0 else "Disabled",
                        region=regions[i]
                    ),
                    financial=FinancialParameters(brutto_rate=rates[i]),
                    system_settings=SystemSettings(service_type="standard" if i % 2 == 0 else "premium"),
                    created_at=datetime(2024, 1, 1) + timedelta(days=i * 10)
                )
            )

        return services

    @patch('matplotlib.pyplot.savefig')
    @patch('matplotlib.pyplot.close')
    def test_multiple_chart_generation_workflow(self, mock_close, mock_savefig, sample_services, tmp_path):
        """Test generating multiple charts in sequence"""
        from src.core.visualization import ChartGenerator

        generator = ChartGenerator(output_dir=tmp_path)

        # Generate multiple charts
        chart1 = generator.generate_service_distribution_by_region(sample_services, "chart1.png")
        chart2 = generator.generate_rate_distribution(sample_services, "chart2.png")

        # Should generate both charts
        assert mock_savefig.call_count == 2
        assert mock_close.call_count == 2

        assert "chart1.png" in chart1
        assert "chart2.png" in chart2

    @patch('matplotlib.pyplot.savefig')
    @patch('matplotlib.pyplot.close')
    @patch('plotly.graph_objects.Figure.write_html')
    def test_mixed_static_and_interactive_charts(
        self,
        mock_write_html,
        mock_close,
        mock_savefig,
        sample_services,
        tmp_path
    ):
        """Test generating mix of static and interactive charts"""
        from src.core.visualization import ChartGenerator

        generator = ChartGenerator(output_dir=tmp_path)

        # Generate static chart
        static = generator.generate_service_distribution_by_region(sample_services, "static.png")

        # Generate interactive chart
        interactive = generator.generate_interactive_dashboard(sample_services, "interactive.html")

        # Static chart should use matplotlib
        mock_savefig.assert_called_once()

        # Interactive should use plotly
        mock_write_html.assert_called_once()

        assert ".png" in static
        assert ".html" in interactive

    @patch('matplotlib.pyplot.savefig')
    @patch('matplotlib.pyplot.close')
    def test_trend_chart_with_real_data(self, mock_close, mock_savefig, tmp_path):
        """Test trend chart with realistic time series data"""
        from src.core.visualization import ChartGenerator

        generator = ChartGenerator(output_dir=tmp_path)

        # Create realistic time series
        start_date = datetime(2024, 1, 1)
        dates = [start_date + timedelta(days=i*7) for i in range(12)]  # Weekly data for 12 weeks
        values = [100, 105, 110, 108, 115, 120, 118, 125, 130, 128, 135, 140]

        result = generator.generate_trend_chart(
            dates=dates,
            values=values,
            title="Service Growth Trend",
            ylabel="Number of Services"
        )

        mock_savefig.assert_called_once()
        assert "trend_chart" in result

    @patch('matplotlib.pyplot.savefig')
    @patch('matplotlib.pyplot.close')
    def test_cost_breakdown_realistic_data(self, mock_close, mock_savefig, tmp_path):
        """Test cost breakdown with realistic breakdown"""
        from src.core.visualization import ChartGenerator

        generator = ChartGenerator(output_dir=tmp_path)

        # Realistic cost components
        cost_breakdown = {
            "Base Hourly Rate": 25.50,
            "Health Insurance": 4.75,
            "Pension Insurance": 3.25,
            "Unemployment Insurance": 1.50,
            "Administrative Overhead": 2.00,
            "Profit Margin": 3.00
        }

        result = generator.generate_cost_breakdown_pie(cost_breakdown, "breakdown.png")

        mock_savefig.assert_called_once()
        assert "breakdown.png" in result

    @patch('matplotlib.pyplot.savefig')
    @patch('matplotlib.pyplot.close')
    def test_chart_generation_with_unicode_data(self, mock_close, mock_savefig, tmp_path):
        """Test chart generation with Unicode characters (German umlauts)"""
        from src.core.visualization import ChartGenerator
        from src.models.service import Service, BasicInfo, SystemSettings
        from src.models.financial import FinancialParameters

        generator = ChartGenerator(output_dir=tmp_path)

        # Services with German characters
        services = [
            Service(
                id=1,
                basic_info=BasicInfo(service_name="Pflege München", target_group="Ältere", region="München"),
                financial=FinancialParameters(brutto_rate=35.0),
                system_settings=SystemSettings(service_type="standard")
            ),
            Service(
                id=2,
                basic_info=BasicInfo(service_name="Betreuung Köln", target_group="Behinderte", region="Köln"),
                financial=FinancialParameters(brutto_rate=40.0),
                system_settings=SystemSettings(service_type="standard")
            )
        ]

        result = generator.generate_service_distribution_by_region(services, "unicode.png")

        # Should handle Unicode without errors
        mock_savefig.assert_called_once()
        assert "unicode.png" in result
