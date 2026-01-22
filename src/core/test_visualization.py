#!/usr/bin/env python3
"""Test visualization module Pure Python version"""

import sys
sys.path.insert(0, '/home/user/daten20/src')

def test_visualization():
    from core.visualization import ChartGenerator, get_chart_generator
    
    print("Testing visualization...")
    
    cg = get_chart_generator()
    
    # Line chart
    line_result = cg.line_chart(
        data={"series1": [1, 2, 3, 4]},
        title="Test Line Chart"
    )
    print(f"  Line chart: {line_result}")
    
    # Bar chart
    bar_result = cg.bar_chart(
        data={"A": 10, "B": 20, "C": 15},
        title="Test Bar Chart"
    )
    print(f"  Bar chart: {bar_result}")
    
    # Pie chart
    pie_result = cg.pie_chart(
        data={"Category1": 30, "Category2": 70},
        title="Test Pie Chart"
    )
    print(f"  Pie chart: {pie_result}")
    
    # Scatter plot
    scatter_result = cg.scatter_plot(
        x_data=[1, 2, 3, 4],
        y_data=[2, 4, 6, 8],
        title="Test Scatter"
    )
    print(f"  Scatter plot: {scatter_result}")
    
    # Histogram
    hist_result = cg.histogram(
        data=[1, 2, 2, 3, 3, 3, 4, 4, 5],
        bins=5,
        title="Test Histogram"
    )
    print(f"  Histogram: {hist_result}")
    
    # Heatmap
    heatmap_result = cg.heatmap(
        data=[[1, 2], [3, 4]],
        title="Test Heatmap"
    )
    print(f"  Heatmap: {heatmap_result}")
    
    # Time series
    ts_result = cg.time_series(
        dates=["2024-01", "2024-02", "2024-03"],
        values=[100, 150, 120],
        title="Test Time Series"
    )
    print(f"  Time series: {ts_result}")
    
    # Interactive chart
    interactive_result = cg.interactive_chart(
        chart_type="line",
        data={"x": [1, 2, 3], "y": [1, 4, 9]},
        title="Test Interactive"
    )
    print(f"  Interactive chart: {interactive_result}")
    
    print("  ✅ visualization works!")

if __name__ == "__main__":
    print("=" * 60)
    print("Visualization Module Test Suite (Pure Python)")
    print("=" * 60)
    print()
    
    test_visualization()
    
    print()
    print("=" * 60)
    print("✅ ALL VISUALIZATION TESTS PASSED!")
    print("=" * 60)
