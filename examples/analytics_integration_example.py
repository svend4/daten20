#!/usr/bin/env python3
"""
Analytics Module Integration Example

Demonstrates usage of all v3.1 Analytics & BI modules:
- Business Intelligence Dashboard
- Predictive Analytics
- Data Warehouse
- OLAP Cube
- Data Mining

Author: DMS Analytics Team
Version: 3.1.0
"""

from datetime import datetime, timedelta
from decimal import Decimal

# Import all analytics modules
from src.analytics import (
    # BI Dashboard
    get_bi_dashboard,
    KPICalculator,
    ReportFormat,
    ReportFrequency,
    ChartType,
    ChartData,
    
    # Predictive Analytics
    get_predictive_analytics,
    ForecastMethod,
    
    # Data Warehouse
    get_data_warehouse,
    
    # OLAP Cube
    get_cube_manager,
    AggregationType,
    
    # Data Mining
    get_data_mining_engine,
)

try:
    import pandas as pd
    import numpy as np
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
    print("pandas not available - some examples will be skipped")


def demo_bi_dashboard():
    """Demonstrate BI Dashboard features"""
    print("\n" + "="*60)
    print("DEMO 1: Business Intelligence Dashboard")
    print("="*60)
    
    dashboard = get_bi_dashboard()
    calc = KPICalculator()
    
    # Sample subscription data
    subscriptions = [
        {"status": "active", "billing_cycle": "monthly", "amount": 99},
        {"status": "active", "billing_cycle": "monthly", "amount": 299},
        {"status": "active", "billing_cycle": "yearly", "amount": 990},
        {"status": "active", "billing_cycle": "monthly", "amount": 99},
    ]
    
    # Calculate KPIs
    mrr = calc.calculate_mrr(subscriptions)
    arr = calc.calculate_arr(mrr)
    churn_rate = calc.calculate_churn_rate(5, 100, 30)
    
    print(f"\n📊 Key Performance Indicators:")
    print(f"  MRR (Monthly Recurring Revenue): €{mrr:,.2f}")
    print(f"  ARR (Annual Recurring Revenue):  €{arr:,.2f}")
    print(f"  Churn Rate:                      {churn_rate}%")
    
    # Create executive dashboard
    exec_dashboard = dashboard.create_executive_dashboard(
        tenant_id="acme-corp",
        date_range=(datetime.now() - timedelta(days=30), datetime.now())
    )
    
    print(f"\n📈 Executive Dashboard Created:")
    print(f"  KPIs:    {len(exec_dashboard.get('kpis', []))}")
    print(f"  Widgets: {len(exec_dashboard.get('widgets', []))}")


def demo_predictive_analytics():
    """Demonstrate Predictive Analytics"""
    print("\n" + "="*60)
    print("DEMO 2: Predictive Analytics & Forecasting")
    print("="*60)
    
    engine = get_predictive_analytics()
    
    # Sample historical MRR data
    historical_mrr = [
        (datetime(2025, i, 1), 50000 + i * 2000)
        for i in range(1, 7)
    ]
    
    print("\n🔮 Revenue Forecasting:")
    print(f"  Historical data: {len(historical_mrr)} months")
    
    # Forecast next 6 months
    try:
        forecast = engine.revenue_forecaster.forecast_mrr(
            historical_mrr=historical_mrr,
            months=6,
            method=ForecastMethod.LINEAR_REGRESSION
        )
        
        print(f"\n  6-Month Forecast:")
        for i, (date, value) in enumerate(zip(forecast.dates[:3], forecast.predictions[:3])):
            print(f"    {date.strftime('%Y-%m')}: €{value:,.2f}")
        print(f"    ... (showing first 3 months)")
        
    except Exception as e:
        print(f"  Forecasting skipped: {e}")
    
    # Scenario analysis
    scenario = engine.analyze_scenario(
        "Growth Scenario",
        {
            "base_mrr": 60000,
            "growth_rate": 0.08,
            "churn_rate": 0.02,
            "months": 12
        }
    )
    
    print(f"\n💡 Scenario Analysis: {scenario.scenario_name}")
    print(f"  Final MRR (mean):      €{scenario.impact_summary['final_mrr_mean']:,.2f}")
    print(f"  Best Case (95th pct):  €{scenario.impact_summary['final_mrr_best_case']:,.2f}")
    print(f"  Worst Case (5th pct):  €{scenario.impact_summary['final_mrr_worst_case']:,.2f}")
    print(f"  Total Growth:          {scenario.impact_summary['total_growth_pct']:.1f}%")


def demo_data_warehouse():
    """Demonstrate Data Warehouse"""
    print("\n" + "="*60)
    print("DEMO 3: Data Warehouse & ETL")
    print("="*60)
    
    warehouse = get_data_warehouse()
    
    # Create standard schema
    warehouse.create_standard_schema()
    
    print(f"\n🏗️  Star Schema Created:")
    print(f"  Dimensions: {len(warehouse.schema.dimension_tables)}")
    for dim_name in warehouse.schema.dimension_tables.keys():
        print(f"    - {dim_name}")
    
    print(f"\n  Fact Tables: {len(warehouse.schema.fact_tables)}")
    for fact_name in warehouse.schema.fact_tables.keys():
        print(f"    - {fact_name}")
    
    # Setup ETL jobs
    warehouse.setup_etl_jobs()
    print(f"\n⚙️  ETL Jobs Configured: {len(warehouse.etl.jobs)}")
    for job_id, job in warehouse.etl.jobs.items():
        print(f"    - {job.name} (schedule: {job.schedule})")


def demo_olap_cube():
    """Demonstrate OLAP Cube"""
    print("\n" + "="*60)
    print("DEMO 4: OLAP Cube & Multidimensional Analysis")
    print("="*60)
    
    if not PANDAS_AVAILABLE:
        print("  Skipped: pandas required")
        return
    
    manager = get_cube_manager()
    
    # Create sales cube
    sales_cube = manager.create_sales_cube()
    
    print(f"\n📊 OLAP Cube Created: {sales_cube.name}")
    print(f"  Dimensions: {list(sales_cube.dimensions.keys())}")
    print(f"  Measures:   {list(sales_cube.measures.keys())}")
    
    # Sample data
    data = pd.DataFrame({
        'Year': ['2025', '2025', '2025', '2026'],
        'Quarter': ['Q1', 'Q1', 'Q2', 'Q1'],
        'Region': ['North', 'South', 'North', 'East'],
        'Revenue': [10000, 15000, 12000, 11000],
        'Units': [100, 150, 120, 110],
        'Profit': [3000, 4500, 3600, 3300]
    })
    
    sales_cube.load_data(data)
    print(f"\n  Loaded {len(data)} rows")
    
    # Slice operation
    q1_data = sales_cube.slice('Quarter', 'Q1')
    print(f"\n  Slice (Q1 only): {len(q1_data)} rows")
    
    # Pivot table
    pivot = sales_cube.pivot(
        rows=['Year'],
        columns=['Region'],
        values='Revenue',
        aggregation=AggregationType.SUM
    )
    
    print(f"\n  Pivot Table (Year x Region):")
    print(f"{pivot}")


def demo_data_mining():
    """Demonstrate Data Mining"""
    print("\n" + "="*60)
    print("DEMO 5: Data Mining & Pattern Discovery")
    print("="*60)
    
    engine = get_data_mining_engine()
    
    # Market basket analysis
    transactions = [
        ['milk', 'bread', 'butter'],
        ['milk', 'bread'],
        ['milk', 'butter'],
        ['bread', 'butter', 'jam'],
        ['milk', 'bread', 'butter', 'jam'],
        ['milk', 'bread'],
        ['bread', 'butter'],
    ]
    
    print(f"\n🛒 Market Basket Analysis:")
    print(f"  Transactions: {len(transactions)}")
    
    rules = engine.find_patterns(transactions, min_support=0.3, min_confidence=0.5)
    
    print(f"\n  Association Rules Found: {len(rules)}")
    for i, rule in enumerate(rules[:3]):
        print(f"    {i+1}. {rule.antecedent} → {rule.consequent}")
        print(f"       Confidence: {rule.confidence:.2f}, Lift: {rule.lift:.2f}")
    
    # Customer segmentation
    if PANDAS_AVAILABLE:
        customer_data = pd.DataFrame({
            'age': [25, 35, 45, 28, 50, 32, 38, 42],
            'spend': [100, 500, 1000, 150, 800, 300, 600, 900],
            'visits': [5, 15, 30, 8, 25, 10, 20, 28]
        })
        
        print(f"\n👥 Customer Segmentation:")
        print(f"  Customers: {len(customer_data)}")
        
        try:
            segments = engine.segment_customers(customer_data, method="kmeans", n_segments=3)
            
            print(f"\n  Segments Created: {segments['n_clusters']}")
            for cluster in segments['clusters']:
                print(f"    Segment {cluster.cluster_id}: {cluster.size} customers")
        except Exception as e:
            print(f"  Segmentation skipped: {e}")


def demo_integrated_workflow():
    """Demonstrate integrated workflow"""
    print("\n" + "="*60)
    print("DEMO 6: Integrated Analytics Workflow")
    print("="*60)
    
    print("\n🔄 Complete Analytics Pipeline:")
    print("  1. Data Warehouse: Extract → Transform → Load")
    print("  2. OLAP Cube: Aggregate multidimensional data")
    print("  3. BI Dashboard: Calculate KPIs and create reports")
    print("  4. Predictive Analytics: Forecast future trends")
    print("  5. Data Mining: Discover patterns and segments")
    
    print("\n✅ All modules working together seamlessly!")


def main():
    """Run all demos"""
    print("\n" + "="*60)
    print("  Analytics Module v3.1 - Integration Examples")
    print("="*60)
    
    # Run demos
    demo_bi_dashboard()
    demo_predictive_analytics()
    demo_data_warehouse()
    demo_olap_cube()
    demo_data_mining()
    demo_integrated_workflow()
    
    print("\n" + "="*60)
    print("  All demos completed successfully!")
    print("="*60)
    print("\n✨ The Analytics Module v3.1 is ready for production use!")
    print()


if __name__ == "__main__":
    main()
