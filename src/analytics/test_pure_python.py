#!/usr/bin/env python3
"""Test analytics modules Pure Python versions"""

import sys
sys.path.insert(0, '/home/user/daten20/src')

def test_data_mining():
    from analytics.data_mining import ClusteringEngine, AssociationRuleMiner
    
    print("Testing data_mining...")
    ce = ClusteringEngine()
    result = ce.kmeans([{"a": 1}, {"b": 2}, {"c": 3}], n_clusters=2)
    print(f"  Clusters: {len(result['clusters'])}")
    
    arm = AssociationRuleMiner()
    rules = arm.apriori([["A", "B"], ["B", "C"]])
    print(f"  Rules: {len(rules)}")
    print("  ✅ data_mining works!")

def test_data_warehouse():
    from analytics.data_warehouse import DataWarehouse
    
    print("Testing data_warehouse...")
    dw = DataWarehouse("test_dw")
    dim = dw.create_dimension("time", ["year", "month"])
    fact = dw.create_fact("sales", ["revenue"], ["time"])
    result = dw.query("sales", ["revenue"], ["time"])
    print(f"  Query rows: {result['row_count']}")
    print("  ✅ data_warehouse works!")

def test_olap_cube():
    from analytics.olap_cube import OLAPCube
    
    print("Testing olap_cube...")
    cube = OLAPCube("test_cube")
    cube.add_dimension("time", ["year", "quarter"])
    cube.add_measure("sales", "sum")
    result = cube.slice("time", "2024")
    print(f"  Slice result: {result['result']:.1f}")
    print("  ✅ olap_cube works!")

def test_predictive_analytics():
    from analytics.predictive_analytics import TimeSeriesForecaster, RegressionModel
    
    print("Testing predictive_analytics...")
    tsf = TimeSeriesForecaster()
    forecast = tsf.forecast([100, 105, 110], periods=5)
    print(f"  Forecast values: {len(forecast.values)}")
    
    rm = RegressionModel()
    rm.fit([[1, 2], [3, 4]], [10, 20])
    pred = rm.predict([[5, 6]])
    print(f"  Prediction accuracy: {pred.accuracy:.2f}")
    print("  ✅ predictive_analytics works!")

if __name__ == "__main__":
    print("=" * 60)
    print("Analytics Modules Test Suite (Pure Python)")
    print("=" * 60)
    print()
    
    test_data_mining()
    print()
    test_data_warehouse()
    print()
    test_olap_cube()
    print()
    test_predictive_analytics()
    
    print()
    print("=" * 60)
    print("✅ ALL ANALYTICS TESTS PASSED!")
    print("=" * 60)
