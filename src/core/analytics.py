"""Analytics and reporting module"""

from collections import defaultdict
from datetime import datetime, timedelta
from typing import Any, Dict, List

from ..financial_calculator import FinancialCalculator
from ..models.service import Service


class AnalyticsEngine:
    """Analytics and reporting engine"""

    def __init__(self):
        """Initialize analytics engine"""
        self.calculator = FinancialCalculator()

    def analyze_services(self, services: List[Service]) -> Dict[str, Any]:
        """
        Comprehensive analysis of services

        Args:
            services: List of services

        Returns:
            Analysis report
        """
        if not services:
            return {"error": "No services to analyze"}

        report = {
            "total_services": len(services),
            "by_region": self._analyze_by_region(services),
            "by_type": self._analyze_by_type(services),
            "financial_stats": self._analyze_financial(services),
            "cost_distribution": self._analyze_cost_distribution(services),
            "recommendations": self._generate_recommendations(services),
        }

        return report

    def _analyze_by_region(self, services: List[Service]) -> Dict[str, int]:
        """Analyze services by region"""
        by_region = defaultdict(int)

        for service in services:
            region = service.basic_info.region or "Не указан"
            by_region[region] += 1

        return dict(by_region)

    def _analyze_by_type(self, services: List[Service]) -> Dict[str, int]:
        """Analyze services by type"""
        by_type = defaultdict(int)

        for service in services:
            stype = service.system_settings.service_type or "Не указан"
            by_type[stype] += 1

        return dict(by_type)

    def _analyze_financial(self, services: List[Service]) -> Dict[str, Any]:
        """Analyze financial data"""
        rates = [float(s.financial.brutto_rate) for s in services if s.financial.brutto_rate]

        if not rates:
            return {}

        # Calculate final rates
        final_rates = []
        for service in services:
            try:
                breakdown = self.calculator.calculate_hourly_rate(service.financial)
                final_rates.append(float(breakdown.final_hourly_rate))
            except:
                continue

        stats = {
            "brutto_rates": {
                "min": min(rates),
                "max": max(rates),
                "avg": sum(rates) / len(rates),
                "median": self._median(rates),
            }
        }

        if final_rates:
            stats["final_rates"] = {
                "min": min(final_rates),
                "max": max(final_rates),
                "avg": sum(final_rates) / len(final_rates),
                "median": self._median(final_rates),
            }

        return stats

    def _analyze_cost_distribution(self, services: List[Service]) -> Dict[str, List[int]]:
        """Analyze cost distribution"""
        distribution = {"0-20": 0, "20-30": 0, "30-40": 0, "40-50": 0, "50+": 0}

        for service in services:
            try:
                breakdown = self.calculator.calculate_hourly_rate(service.financial)
                rate = float(breakdown.final_hourly_rate)

                if rate < 20:
                    distribution["0-20"] += 1
                elif rate < 30:
                    distribution["20-30"] += 1
                elif rate < 40:
                    distribution["30-40"] += 1
                elif rate < 50:
                    distribution["40-50"] += 1
                else:
                    distribution["50+"] += 1
            except:
                continue

        return distribution

    def _generate_recommendations(self, services: List[Service]) -> List[str]:
        """Generate recommendations based on analysis"""
        recommendations = []

        # Check rate variation
        rates = [float(s.financial.brutto_rate) for s in services if s.financial.brutto_rate]
        if rates:
            rate_range = max(rates) - min(rates)
            if rate_range > 20:
                recommendations.append(f"Большой разброс ставок ({rate_range:.2f} €). Рассмотрите стандартизацию.")

        # Check regional distribution
        by_region = self._analyze_by_region(services)
        if len(by_region) < 3:
            recommendations.append("Услуги представлены в малом количестве регионов. Рассмотрите расширение.")

        # Check calculation modes
        umlages_count = sum(1 for s in services if s.system_settings.use_umlages)
        reserve_count = len(services) - umlages_count

        if umlages_count > 0 and reserve_count > 0:
            recommendations.append("Используются разные режимы расчета. Рассмотрите унификацию для упрощения.")

        return recommendations

    def compare_services(self, service_ids: List[int], services: List[Service]) -> Dict[str, Any]:
        """
        Compare multiple services

        Args:
            service_ids: List of service IDs to compare
            services: All services

        Returns:
            Comparison report
        """
        selected_services = [s for s in services if s.id in service_ids]

        if not selected_services:
            return {"error": "No services found for comparison"}

        comparison = {"services": [], "differences": [], "summary": {}}

        # Calculate costs for each service
        for service in selected_services:
            try:
                breakdown = self.calculator.calculate_hourly_rate(service.financial)

                comparison["services"].append(
                    {
                        "id": service.id,
                        "name": service.basic_info.service_name,
                        "region": service.basic_info.region,
                        "brutto_rate": float(service.financial.brutto_rate),
                        "final_rate": float(breakdown.final_hourly_rate),
                        "total_insurance": float(breakdown.total_insurance),
                        "calculation_mode": breakdown.calculation_mode,
                    }
                )
            except Exception as e:
                print(f"Error calculating service {service.id}: {e}")

        # Identify differences
        if len(comparison["services"]) >= 2:
            rates = [s["final_rate"] for s in comparison["services"]]
            comparison["summary"] = {
                "min_rate": min(rates),
                "max_rate": max(rates),
                "avg_rate": sum(rates) / len(rates),
                "difference": max(rates) - min(rates),
            }

        return comparison

    def forecast_costs(self, service: Service, scenarios: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Forecast costs under different scenarios

        Args:
            service: Base service
            scenarios: List of scenario parameters

        Returns:
            Forecast report
        """
        forecasts = []

        for scenario in scenarios:
            try:
                # Create modified service
                from copy import deepcopy

                modified_service = deepcopy(service)

                # Apply scenario changes
                if "brutto_rate_change" in scenario:
                    change = scenario["brutto_rate_change"]  # percentage
                    modified_service.financial.brutto_rate *= 1 + change / 100

                if "region_coefficient" in scenario:
                    modified_service.financial.region_coefficient = scenario["region_coefficient"]

                # Calculate
                breakdown = self.calculator.calculate_hourly_rate(modified_service.financial)

                forecasts.append(
                    {
                        "scenario_name": scenario.get("name", "Unnamed"),
                        "parameters": scenario,
                        "final_rate": float(breakdown.final_hourly_rate),
                        "change_percent": self._calculate_change_percent(
                            float(service.financial.brutto_rate), float(breakdown.final_hourly_rate)
                        ),
                    }
                )
            except Exception as e:
                print(f"Error forecasting scenario: {e}")

        return {
            "base_service": service.basic_info.service_name,
            "base_rate": float(service.financial.brutto_rate),
            "forecasts": forecasts,
        }

    def generate_time_series(self, services: List[Service], group_by: str = "month") -> Dict[str, Any]:
        """
        Generate time series data

        Args:
            services: List of services
            group_by: Grouping period (day, week, month)

        Returns:
            Time series data
        """
        time_series = defaultdict(lambda: {"count": 0, "avg_rate": []})

        for service in services:
            if service.created_at:
                if group_by == "month":
                    key = service.created_at.strftime("%Y-%m")
                elif group_by == "week":
                    key = service.created_at.strftime("%Y-W%W")
                else:  # day
                    key = service.created_at.strftime("%Y-%m-%d")

                time_series[key]["count"] += 1
                time_series[key]["avg_rate"].append(float(service.financial.brutto_rate))

        # Calculate averages
        result = {}
        for period, data in time_series.items():
            result[period] = {
                "count": data["count"],
                "avg_rate": sum(data["avg_rate"]) / len(data["avg_rate"]) if data["avg_rate"] else 0,
            }

        return dict(sorted(result.items()))

    def _median(self, values: List[float]) -> float:
        """Calculate median"""
        sorted_values = sorted(values)
        n = len(sorted_values)

        if n % 2 == 0:
            return (sorted_values[n // 2 - 1] + sorted_values[n // 2]) / 2
        else:
            return sorted_values[n // 2]

    def _calculate_change_percent(self, old_value: float, new_value: float) -> float:
        """Calculate percentage change"""
        if old_value == 0:
            return 0
        return ((new_value - old_value) / old_value) * 100
