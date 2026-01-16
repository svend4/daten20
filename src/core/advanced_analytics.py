"""
Advanced Analytics Module

Provides predictive analytics, trend analysis, and forecasting capabilities.
"""

import statistics
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple


@dataclass
class TrendData:
    """Trend analysis data"""

    period: str
    value: float
    change: float
    change_percent: float
    trend: str  # 'up', 'down', 'stable'


@dataclass
class Forecast:
    """Forecast data"""

    period: str
    predicted_value: float
    confidence_interval_low: float
    confidence_interval_high: float
    confidence_level: float


@dataclass
class AnomalyDetection:
    """Anomaly detection result"""

    date: datetime
    value: float
    expected_value: float
    deviation: float
    is_anomaly: bool
    severity: str  # 'low', 'medium', 'high'


@dataclass
class AnalyticsReport:
    """Comprehensive analytics report"""

    summary: Dict[str, any]
    trends: List[TrendData]
    forecasts: List[Forecast]
    anomalies: List[AnomalyDetection]
    insights: List[str]
    recommendations: List[str]


class AdvancedAnalytics:
    """Advanced analytics and forecasting engine"""

    def __init__(self, database):
        self.db = database

    def generate_report(
        self, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None
    ) -> AnalyticsReport:
        """Generate comprehensive analytics report"""

        if not start_date:
            start_date = datetime.now() - timedelta(days=90)
        if not end_date:
            end_date = datetime.now()

        # Get data
        services = self._get_services_data(start_date, end_date)

        # Calculate summary statistics
        summary = self._calculate_summary(services)

        # Analyze trends
        trends = self._analyze_trends(services)

        # Generate forecasts
        forecasts = self._generate_forecasts(services)

        # Detect anomalies
        anomalies = self._detect_anomalies(services)

        # Generate insights
        insights = self._generate_insights(summary, trends, anomalies)

        # Generate recommendations
        recommendations = self._generate_recommendations(summary, trends, forecasts)

        return AnalyticsReport(
            summary=summary,
            trends=trends,
            forecasts=forecasts,
            anomalies=anomalies,
            insights=insights,
            recommendations=recommendations,
        )

    def _get_services_data(self, start_date: datetime, end_date: datetime) -> List[Dict]:
        """Get services data for analysis"""
        cursor = self.db.conn.cursor()

        cursor.execute(
            """
            SELECT id, service_name, region, brutto_rate, hours_per_month,
                   created_at, updated_at
            FROM services
            WHERE created_at >= ? AND created_at <= ?
            ORDER BY created_at
        """,
            (start_date.isoformat(), end_date.isoformat()),
        )

        columns = [col[0] for col in cursor.description]
        services = []

        for row in cursor.fetchall():
            services.append(dict(zip(columns, row)))

        return services

    def _calculate_summary(self, services: List[Dict]) -> Dict:
        """Calculate summary statistics"""
        if not services:
            return {
                "total_services": 0,
                "avg_rate": 0,
                "median_rate": 0,
                "avg_hours": 0,
                "total_monthly_cost": 0,
                "services_by_region": {},
                "rate_distribution": {},
            }

        rates = [s["brutto_rate"] for s in services if s.get("brutto_rate")]
        hours = [s["hours_per_month"] for s in services if s.get("hours_per_month")]

        # Regional distribution
        services_by_region = defaultdict(int)
        for service in services:
            region = service.get("region", "Unknown")
            services_by_region[region] += 1

        # Rate distribution
        rate_distribution = {"0-30": 0, "30-40": 0, "40-50": 0, "50-60": 0, "60+": 0}

        for rate in rates:
            if rate < 30:
                rate_distribution["0-30"] += 1
            elif rate < 40:
                rate_distribution["30-40"] += 1
            elif rate < 50:
                rate_distribution["40-50"] += 1
            elif rate < 60:
                rate_distribution["50-60"] += 1
            else:
                rate_distribution["60+"] += 1

        # Calculate total monthly cost
        total_monthly_cost = sum(s.get("brutto_rate", 0) * s.get("hours_per_month", 0) for s in services)

        return {
            "total_services": len(services),
            "avg_rate": statistics.mean(rates) if rates else 0,
            "median_rate": statistics.median(rates) if rates else 0,
            "std_dev_rate": statistics.stdev(rates) if len(rates) > 1 else 0,
            "avg_hours": statistics.mean(hours) if hours else 0,
            "total_monthly_cost": total_monthly_cost,
            "services_by_region": dict(services_by_region),
            "rate_distribution": rate_distribution,
        }

    def _analyze_trends(self, services: List[Dict]) -> List[TrendData]:
        """Analyze trends over time"""
        trends = []

        if not services:
            return trends

        # Group services by month
        monthly_data = defaultdict(list)

        for service in services:
            if service.get("created_at"):
                try:
                    date = datetime.fromisoformat(service["created_at"])
                    month_key = date.strftime("%Y-%m")
                    monthly_data[month_key].append(service)
                except (ValueError, TypeError):
                    continue

        # Calculate trends for each month
        sorted_months = sorted(monthly_data.keys())

        for i, month in enumerate(sorted_months):
            month_services = monthly_data[month]
            count = len(month_services)

            # Calculate change from previous month
            if i > 0:
                prev_month = sorted_months[i - 1]
                prev_count = len(monthly_data[prev_month])
                change = count - prev_count
                change_percent = (change / prev_count * 100) if prev_count > 0 else 0

                # Determine trend direction
                if change_percent > 5:
                    trend = "up"
                elif change_percent < -5:
                    trend = "down"
                else:
                    trend = "stable"
            else:
                change = 0
                change_percent = 0
                trend = "stable"

            trends.append(
                TrendData(period=month, value=count, change=change, change_percent=change_percent, trend=trend)
            )

        return trends

    def _generate_forecasts(self, services: List[Dict]) -> List[Forecast]:
        """Generate forecasts using simple linear regression"""
        forecasts = []

        if len(services) < 3:
            return forecasts

        # Group services by month and count
        monthly_counts = defaultdict(int)

        for service in services:
            if service.get("created_at"):
                try:
                    date = datetime.fromisoformat(service["created_at"])
                    month_key = date.strftime("%Y-%m")
                    monthly_counts[month_key] += 1
                except (ValueError, TypeError):
                    continue

        if len(monthly_counts) < 3:
            return forecasts

        # Prepare data for linear regression
        sorted_months = sorted(monthly_counts.keys())
        y_values = [monthly_counts[month] for month in sorted_months]
        x_values = list(range(len(y_values)))

        # Simple linear regression
        n = len(x_values)
        sum_x = sum(x_values)
        sum_y = sum(y_values)
        sum_xy = sum(x * y for x, y in zip(x_values, y_values))
        sum_x2 = sum(x * x for x in x_values)

        # Calculate slope and intercept
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
        intercept = (sum_y - slope * sum_x) / n

        # Generate forecasts for next 3 months
        last_date = datetime.strptime(sorted_months[-1], "%Y-%m")

        for i in range(1, 4):
            forecast_date = last_date + timedelta(days=30 * i)
            forecast_month = forecast_date.strftime("%Y-%m")
            x_forecast = len(x_values) + i - 1

            # Predict value
            predicted_value = slope * x_forecast + intercept
            predicted_value = max(0, predicted_value)  # Can't be negative

            # Calculate confidence interval (simplified)
            residuals = [y - (slope * x + intercept) for x, y in zip(x_values, y_values)]
            std_dev = statistics.stdev(residuals) if len(residuals) > 1 else predicted_value * 0.1

            confidence_interval_low = max(0, predicted_value - 1.96 * std_dev)
            confidence_interval_high = predicted_value + 1.96 * std_dev

            # Confidence level decreases with forecast horizon
            confidence_level = 0.95 - (i - 1) * 0.1

            forecasts.append(
                Forecast(
                    period=forecast_month,
                    predicted_value=predicted_value,
                    confidence_interval_low=confidence_interval_low,
                    confidence_interval_high=confidence_interval_high,
                    confidence_level=confidence_level,
                )
            )

        return forecasts

    def _detect_anomalies(self, services: List[Dict]) -> List[AnomalyDetection]:
        """Detect anomalies in service data"""
        anomalies = []

        if len(services) < 10:
            return anomalies

        # Extract rates
        rates = []
        for service in services:
            if service.get("brutto_rate"):
                try:
                    date = datetime.fromisoformat(service["created_at"])
                    rates.append((date, service["brutto_rate"]))
                except (ValueError, TypeError):
                    continue

        if len(rates) < 10:
            return anomalies

        # Calculate mean and standard deviation
        rate_values = [r[1] for r in rates]
        mean_rate = statistics.mean(rate_values)
        std_dev = statistics.stdev(rate_values)

        # Detect anomalies (values beyond 2 standard deviations)
        for date, rate in rates:
            expected_value = mean_rate
            deviation = abs(rate - expected_value)
            z_score = deviation / std_dev if std_dev > 0 else 0

            is_anomaly = z_score > 2

            if is_anomaly:
                # Determine severity
                if z_score > 3:
                    severity = "high"
                elif z_score > 2.5:
                    severity = "medium"
                else:
                    severity = "low"

                anomalies.append(
                    AnomalyDetection(
                        date=date,
                        value=rate,
                        expected_value=expected_value,
                        deviation=deviation,
                        is_anomaly=is_anomaly,
                        severity=severity,
                    )
                )

        return anomalies

    def _generate_insights(
        self, summary: Dict, trends: List[TrendData], anomalies: List[AnomalyDetection]
    ) -> List[str]:
        """Generate insights from analysis"""
        insights = []

        # Service count insights
        total_services = summary.get("total_services", 0)
        insights.append(f"Всего услуг в системе: {total_services}")

        # Rate insights
        avg_rate = summary.get("avg_rate", 0)
        median_rate = summary.get("median_rate", 0)
        insights.append(f"Средняя ставка: {avg_rate:.2f}€, медиана: {median_rate:.2f}€")

        # Trend insights
        if trends:
            latest_trend = trends[-1]
            if latest_trend.trend == "up":
                insights.append(
                    f"📈 Положительный тренд: количество услуг выросло на "
                    f"{latest_trend.change_percent:.1f}% за последний период"
                )
            elif latest_trend.trend == "down":
                insights.append(
                    f"📉 Негативный тренд: количество услуг снизилось на "
                    f"{abs(latest_trend.change_percent):.1f}% за последний период"
                )

        # Regional insights
        services_by_region = summary.get("services_by_region", {})
        if services_by_region:
            top_region = max(services_by_region.items(), key=lambda x: x[1])
            insights.append(f"🏆 Наиболее популярный регион: {top_region[0]} ({top_region[1]} услуг)")

        # Anomaly insights
        if anomalies:
            high_severity = [a for a in anomalies if a.severity == "high"]
            if high_severity:
                insights.append(f"⚠️ Обнаружено {len(high_severity)} аномальных значений высокой важности")

        # Cost insights
        total_cost = summary.get("total_monthly_cost", 0)
        if total_cost > 0:
            insights.append(f"💰 Общая ежемесячная стоимость: {total_cost:.2f}€")

        return insights

    def _generate_recommendations(self, summary: Dict, trends: List[TrendData], forecasts: List[Forecast]) -> List[str]:
        """Generate recommendations based on analysis"""
        recommendations = []

        # Rate optimization recommendations
        avg_rate = summary.get("avg_rate", 0)
        std_dev = summary.get("std_dev_rate", 0)

        if std_dev > avg_rate * 0.3:
            recommendations.append(
                "Рассмотрите стандартизацию ставок - высокая вариативность может указывать "
                "на несогласованность в ценообразовании"
            )

        # Growth recommendations
        if trends and len(trends) >= 3:
            recent_trends = trends[-3:]
            declining_months = sum(1 for t in recent_trends if t.trend == "down")

            if declining_months >= 2:
                recommendations.append(
                    "⚠️ Замечено снижение количества услуг. Рекомендуется проанализировать "
                    "причины и разработать стратегию привлечения новых клиентов"
                )

        # Forecast-based recommendations
        if forecasts:
            next_month_forecast = forecasts[0]
            if next_month_forecast.predicted_value < summary.get("total_services", 0) * 0.9:
                recommendations.append(
                    "📊 Прогноз указывает на возможное снижение услуг в следующем месяце. "
                    "Рекомендуется принять превентивные меры"
                )

        # Regional recommendations
        services_by_region = summary.get("services_by_region", {})
        if services_by_region and len(services_by_region) < 5:
            recommendations.append(
                "🌍 Рассмотрите расширение географического покрытия - " "вы работаете только в нескольких регионах"
            )

        # Efficiency recommendations
        avg_hours = summary.get("avg_hours", 0)
        if avg_hours > 0:
            if avg_hours < 100:
                recommendations.append(
                    "⏰ Средняя продолжительность услуги относительно низкая. "
                    "Рассмотрите возможность предложения пакетов с большим количеством часов"
                )
            elif avg_hours > 180:
                recommendations.append(
                    "⏰ Средняя продолжительность услуги очень высокая. "
                    "Убедитесь, что ресурсы используются оптимально"
                )

        return recommendations


def get_advanced_analytics(database) -> AdvancedAnalytics:
    """Get advanced analytics instance"""
    return AdvancedAnalytics(database)
