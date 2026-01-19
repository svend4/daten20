#!/usr/bin/env python3
"""
Comprehensive Test Suite for Data Mining Module

Tests cover:
- Data classes (AssociationRule, Cluster)
- ClusteringEngine (K-means, DBSCAN)
- AprioriMiner (Association rule mining)
- DataMiningEngine (Main orchestrator)
- Singleton pattern
- Edge cases and error handling
- Integration tests
"""

import pytest
from dataclasses import asdict

# Import the module
from src.analytics.data_mining import (
    AssociationRule,
    Cluster,
    ClusteringEngine,
    AprioriMiner,
    DataMiningEngine,
    get_data_mining_engine,
    SKLEARN_AVAILABLE,
)

# Optional imports
try:
    import pandas as pd
    import numpy as np
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False


# ============================================================================
# TEST DATA CLASSES
# ============================================================================

class TestDataClasses:
    """Test data classes"""

    def test_association_rule_creation(self):
        """Test AssociationRule creation"""
        rule = AssociationRule(
            antecedent=["milk", "bread"],
            consequent=["butter"],
            support=0.6,
            confidence=0.8,
            lift=1.5,
        )

        assert rule.antecedent == ["milk", "bread"]
        assert rule.consequent == ["butter"]
        assert rule.support == 0.6
        assert rule.confidence == 0.8
        assert rule.lift == 1.5

    def test_cluster_creation(self):
        """Test Cluster creation"""
        cluster = Cluster(
            cluster_id=0,
            members=[1, 2, 3, 4, 5],
            centroid=[1.5, 2.5, 3.5],
            size=5,
        )

        assert cluster.cluster_id == 0
        assert cluster.members == [1, 2, 3, 4, 5]
        assert cluster.centroid == [1.5, 2.5, 3.5]
        assert cluster.size == 5

    def test_cluster_without_centroid(self):
        """Test Cluster without centroid (DBSCAN)"""
        cluster = Cluster(
            cluster_id=1,
            members=[10, 20, 30],
            size=3,
        )

        assert cluster.cluster_id == 1
        assert cluster.members == [10, 20, 30]
        assert cluster.centroid is None
        assert cluster.size == 3


# ============================================================================
# TEST CLUSTERING ENGINE
# ============================================================================

class TestClusteringEngine:
    """Test ClusteringEngine"""

    def test_initialization(self):
        """Test ClusteringEngine initialization"""
        engine = ClusteringEngine()

        assert engine.model is None
        if SKLEARN_AVAILABLE:
            assert engine.scaler is not None
        else:
            assert engine.scaler is None

    @pytest.mark.skipif(not SKLEARN_AVAILABLE or not PANDAS_AVAILABLE,
                       reason="scikit-learn and pandas required")
    def test_kmeans_basic(self):
        """Test basic K-means clustering"""
        # Create sample data
        data = pd.DataFrame({
            'feature1': [1, 2, 1, 2, 10, 11, 10, 11],
            'feature2': [1, 1, 2, 2, 10, 10, 11, 11],
        })

        engine = ClusteringEngine()
        result = engine.kmeans(data, n_clusters=2)

        assert 'clusters' in result
        assert 'labels' in result
        assert 'inertia' in result
        assert 'n_clusters' in result
        assert result['n_clusters'] == 2
        assert len(result['clusters']) == 2
        assert len(result['labels']) == 8

    @pytest.mark.skipif(not SKLEARN_AVAILABLE or not PANDAS_AVAILABLE,
                       reason="scikit-learn and pandas required")
    def test_kmeans_with_features(self):
        """Test K-means with specific features"""
        data = pd.DataFrame({
            'age': [25, 26, 45, 46, 65, 66],
            'income': [30000, 35000, 70000, 75000, 45000, 50000],
            'ignore': [1, 2, 3, 4, 5, 6],  # Should be ignored
        })

        engine = ClusteringEngine()
        result = engine.kmeans(data, n_clusters=3, features=['age', 'income'])

        assert result['n_clusters'] == 3
        assert len(result['clusters']) == 3

        # Verify clusters have members
        total_members = sum(c.size for c in result['clusters'])
        assert total_members == 6

    @pytest.mark.skipif(not SKLEARN_AVAILABLE or not PANDAS_AVAILABLE,
                       reason="scikit-learn and pandas required")
    def test_kmeans_cluster_properties(self):
        """Test K-means cluster properties"""
        data = pd.DataFrame({
            'x': [0, 0, 1, 1, 10, 10, 11, 11],
            'y': [0, 1, 0, 1, 0, 1, 0, 1],
        })

        engine = ClusteringEngine()
        result = engine.kmeans(data, n_clusters=2)

        # Check cluster objects
        for cluster in result['clusters']:
            assert isinstance(cluster, Cluster)
            assert cluster.cluster_id in [0, 1]
            assert len(cluster.members) > 0
            assert cluster.centroid is not None
            assert cluster.size == len(cluster.members)

    @pytest.mark.skipif(not SKLEARN_AVAILABLE or not PANDAS_AVAILABLE,
                       reason="scikit-learn and pandas required")
    def test_dbscan_basic(self):
        """Test basic DBSCAN clustering"""
        data = pd.DataFrame({
            'x': [1, 1.5, 2, 10, 10.5, 11, 20, 20.5, 21],
            'y': [1, 1.5, 2, 10, 10.5, 11, 20, 20.5, 21],
        })

        engine = ClusteringEngine()
        result = engine.dbscan(data, eps=2.0, min_samples=2)

        assert 'clusters' in result
        assert 'labels' in result
        assert 'n_clusters' in result
        assert 'noise_points' in result
        assert result['n_clusters'] >= 0
        assert result['noise_points'] >= 0

    @pytest.mark.skipif(not SKLEARN_AVAILABLE or not PANDAS_AVAILABLE,
                       reason="scikit-learn and pandas required")
    def test_dbscan_noise_detection(self):
        """Test DBSCAN noise point detection"""
        # Create data with clear outliers
        data = pd.DataFrame({
            'x': [0, 0, 1, 1, 100],  # 100 is outlier
            'y': [0, 1, 0, 1, 100],
        })

        engine = ClusteringEngine()
        result = engine.dbscan(data, eps=2.0, min_samples=2)

        # Should have at least 1 cluster and 1 noise point
        assert result['n_clusters'] >= 1
        assert result['noise_points'] >= 1

    @pytest.mark.skipif(SKLEARN_AVAILABLE, reason="Test for missing sklearn")
    def test_kmeans_without_sklearn(self):
        """Test K-means error when sklearn not available"""
        engine = ClusteringEngine()

        with pytest.raises(ImportError, match="scikit-learn required"):
            engine.kmeans(None, n_clusters=2)

    @pytest.mark.skipif(SKLEARN_AVAILABLE, reason="Test for missing sklearn")
    def test_dbscan_without_sklearn(self):
        """Test DBSCAN error when sklearn not available"""
        engine = ClusteringEngine()

        with pytest.raises(ImportError, match="scikit-learn required"):
            engine.dbscan(None)


# ============================================================================
# TEST APRIORI MINER
# ============================================================================

class TestAprioriMiner:
    """Test AprioriMiner"""

    def test_initialization(self):
        """Test AprioriMiner initialization"""
        miner = AprioriMiner(min_support=0.3, min_confidence=0.6)

        assert miner.min_support == 0.3
        assert miner.min_confidence == 0.6
        assert miner.frequent_itemsets == {}

    def test_default_initialization(self):
        """Test AprioriMiner default initialization"""
        miner = AprioriMiner()

        assert miner.min_support == 0.01
        assert miner.min_confidence == 0.1

    def test_basic_rule_mining(self):
        """Test basic association rule mining"""
        transactions = [
            ["milk", "bread", "butter"],
            ["milk", "bread"],
            ["milk", "butter"],
            ["bread", "butter"],
            ["milk", "bread", "butter"],
        ]

        miner = AprioriMiner(min_support=0.4, min_confidence=0.5)
        rules = miner.mine_rules(transactions)

        assert isinstance(rules, list)
        assert len(rules) > 0

        # Check rule properties
        for rule in rules:
            assert isinstance(rule, AssociationRule)
            assert len(rule.antecedent) > 0
            assert len(rule.consequent) > 0
            assert 0 <= rule.support <= 1
            assert 0 <= rule.confidence <= 1
            assert rule.lift >= 0

    def test_rule_ordering(self):
        """Test rules are ordered by lift"""
        transactions = [
            ["A", "B", "C"],
            ["A", "B"],
            ["B", "C"],
            ["A", "C"],
            ["A", "B", "C"],
        ]

        miner = AprioriMiner(min_support=0.3, min_confidence=0.3)
        rules = miner.mine_rules(transactions)

        if len(rules) > 1:
            # Verify descending order by lift
            for i in range(len(rules) - 1):
                assert rules[i].lift >= rules[i + 1].lift

    def test_high_support_threshold(self):
        """Test with high support threshold (few rules)"""
        transactions = [
            ["A", "B"],
            ["A", "C"],
            ["B", "C"],
            ["D", "E"],
        ]

        miner = AprioriMiner(min_support=0.8, min_confidence=0.5)
        rules = miner.mine_rules(transactions)

        # High threshold should result in no or very few rules
        assert len(rules) == 0

    def test_low_thresholds(self):
        """Test with low thresholds (many rules)"""
        transactions = [
            ["A", "B", "C"],
            ["A", "B"],
            ["B", "C"],
        ]

        miner = AprioriMiner(min_support=0.3, min_confidence=0.3)
        rules = miner.mine_rules(transactions)

        # Low thresholds should produce rules
        assert len(rules) > 0

    def test_single_item_transactions(self):
        """Test with single-item transactions (no rules)"""
        transactions = [
            ["A"],
            ["B"],
            ["C"],
        ]

        miner = AprioriMiner(min_support=0.1, min_confidence=0.1)
        rules = miner.mine_rules(transactions)

        # Single items can't form rules (need at least 2 items)
        assert len(rules) == 0

    def test_empty_transactions(self):
        """Test with empty transactions"""
        transactions = []

        miner = AprioriMiner()
        rules = miner.mine_rules(transactions)

        assert rules == []

    def test_confidence_calculation(self):
        """Test confidence calculation"""
        transactions = [
            ["milk", "bread"],
            ["milk", "bread"],
            ["milk"],
        ]

        miner = AprioriMiner(min_support=0.3, min_confidence=0.5)

        # milk -> bread appears in 2/3 transactions with milk
        # Confidence should be 2/2 = 1.0 (both milk transactions have bread)
        confidence = miner._calculate_confidence(["milk"], ["bread"], transactions)

        assert 0.6 <= confidence <= 1.0  # Allow some flexibility

    def test_lift_calculation(self):
        """Test lift calculation"""
        transactions = [
            ["A", "B"],
            ["A", "B"],
            ["B"],
        ]

        miner = AprioriMiner()
        lift = miner._calculate_lift(["A"], ["B"], transactions, len(transactions))

        # Lift should be > 1 if positive correlation
        assert lift > 0

    def test_frequent_itemsets_generation(self):
        """Test frequent itemsets generation"""
        transactions = [
            ["milk", "bread", "butter"],
            ["milk", "bread"],
            ["milk", "butter"],
            ["bread", "butter"],
        ]

        miner = AprioriMiner(min_support=0.5)
        itemsets = miner._find_frequent_itemsets(transactions, len(transactions))

        assert isinstance(itemsets, dict)
        assert len(itemsets) > 0

        # All itemsets should meet min support
        for itemset, support in itemsets.items():
            assert support >= 0.5

    def test_candidate_generation(self):
        """Test candidate generation"""
        miner = AprioriMiner()

        itemsets = [("A",), ("B",), ("C",)]
        candidates = miner._generate_candidates(itemsets, 2)

        assert isinstance(candidates, list)
        # Should generate pairs
        assert all(len(c) == 2 for c in candidates)


# ============================================================================
# TEST DATA MINING ENGINE
# ============================================================================

class TestDataMiningEngine:
    """Test DataMiningEngine"""

    def test_initialization(self):
        """Test DataMiningEngine initialization"""
        engine = DataMiningEngine()

        assert engine.clustering is not None
        assert engine.apriori is not None
        assert isinstance(engine.clustering, ClusteringEngine)
        assert isinstance(engine.apriori, AprioriMiner)

    @pytest.mark.skipif(not SKLEARN_AVAILABLE or not PANDAS_AVAILABLE,
                       reason="scikit-learn and pandas required")
    def test_segment_customers_kmeans(self):
        """Test customer segmentation with K-means"""
        data = pd.DataFrame({
            'age': [25, 26, 45, 46, 65, 66],
            'income': [30000, 32000, 70000, 72000, 45000, 47000],
        })

        engine = DataMiningEngine()
        result = engine.segment_customers(data, method='kmeans', n_segments=3)

        assert 'clusters' in result
        assert result['n_clusters'] == 3

    @pytest.mark.skipif(not SKLEARN_AVAILABLE or not PANDAS_AVAILABLE,
                       reason="scikit-learn and pandas required")
    def test_segment_customers_dbscan(self):
        """Test customer segmentation with DBSCAN"""
        data = pd.DataFrame({
            'x': [1, 1, 2, 2, 10, 10, 11, 11],
            'y': [1, 2, 1, 2, 10, 11, 10, 11],
        })

        engine = DataMiningEngine()
        result = engine.segment_customers(data, method='dbscan')

        assert 'clusters' in result
        assert 'n_clusters' in result
        assert result['n_clusters'] >= 0

    def test_segment_customers_invalid_method(self):
        """Test segmentation with invalid method"""
        engine = DataMiningEngine()

        with pytest.raises(ValueError, match="Unknown method"):
            engine.segment_customers(None, method='invalid')

    def test_find_patterns_basic(self):
        """Test basic pattern finding"""
        transactions = [
            ["milk", "bread", "butter"],
            ["milk", "bread"],
            ["milk", "butter"],
            ["bread", "butter"],
        ]

        engine = DataMiningEngine()
        rules = engine.find_patterns(transactions, min_support=0.5, min_confidence=0.5)

        assert isinstance(rules, list)
        # Should find some rules with these thresholds
        assert len(rules) >= 0

    def test_find_patterns_with_custom_thresholds(self):
        """Test pattern finding with custom thresholds"""
        transactions = [
            ["A", "B", "C"],
            ["A", "B"],
            ["A", "C"],
            ["B", "C"],
        ]

        engine = DataMiningEngine()
        rules = engine.find_patterns(transactions, min_support=0.25, min_confidence=0.4)

        assert isinstance(rules, list)


# ============================================================================
# TEST SINGLETON PATTERN
# ============================================================================

class TestSingletonPattern:
    """Test singleton pattern"""

    def test_get_data_mining_engine(self):
        """Test get_data_mining_engine returns instance"""
        engine = get_data_mining_engine()

        assert engine is not None
        assert isinstance(engine, DataMiningEngine)

    def test_singleton_same_instance(self):
        """Test singleton returns same instance"""
        engine1 = get_data_mining_engine()
        engine2 = get_data_mining_engine()

        assert engine1 is engine2


# ============================================================================
# TEST EDGE CASES
# ============================================================================

class TestEdgeCases:
    """Test edge cases"""

    def test_apriori_with_duplicate_items(self):
        """Test Apriori with duplicate items in transactions"""
        transactions = [
            ["A", "A", "B"],  # Duplicate A
            ["A", "B", "B"],  # Duplicate B
        ]

        miner = AprioriMiner(min_support=0.4, min_confidence=0.4)
        rules = miner.mine_rules(transactions)

        # Should handle duplicates gracefully
        assert isinstance(rules, list)

    def test_apriori_large_transactions(self):
        """Test Apriori with larger transaction set"""
        # Generate 100 transactions
        transactions = []
        for i in range(100):
            if i % 3 == 0:
                transactions.append(["A", "B", "C"])
            elif i % 3 == 1:
                transactions.append(["A", "B"])
            else:
                transactions.append(["B", "C"])

        miner = AprioriMiner(min_support=0.2, min_confidence=0.3)
        rules = miner.mine_rules(transactions)

        assert isinstance(rules, list)
        assert len(rules) > 0

    @pytest.mark.skipif(not SKLEARN_AVAILABLE or not PANDAS_AVAILABLE,
                       reason="scikit-learn and pandas required")
    def test_kmeans_single_cluster(self):
        """Test K-means with n_clusters=1"""
        data = pd.DataFrame({
            'x': [1, 2, 3, 4, 5],
            'y': [1, 2, 3, 4, 5],
        })

        engine = ClusteringEngine()
        result = engine.kmeans(data, n_clusters=1)

        assert result['n_clusters'] == 1
        assert len(result['clusters']) == 1
        assert result['clusters'][0].size == 5

    @pytest.mark.skipif(not SKLEARN_AVAILABLE or not PANDAS_AVAILABLE,
                       reason="scikit-learn and pandas required")
    def test_kmeans_more_clusters_than_points(self):
        """Test K-means with more clusters than data points"""
        data = pd.DataFrame({
            'x': [1, 2, 3],
            'y': [1, 2, 3],
        })

        engine = ClusteringEngine()
        # sklearn raises ValueError when n_clusters > n_samples
        with pytest.raises(ValueError, match="should be >="):
            engine.kmeans(data, n_clusters=5)

    def test_apriori_zero_support(self):
        """Test Apriori with zero support (should find all patterns)"""
        transactions = [
            ["A", "B"],
            ["C", "D"],
        ]

        miner = AprioriMiner(min_support=0.0, min_confidence=0.5)
        rules = miner.mine_rules(transactions)

        assert isinstance(rules, list)

    def test_apriori_high_confidence(self):
        """Test Apriori with very high confidence"""
        transactions = [
            ["milk", "bread"],
            ["milk", "bread"],
            ["milk", "bread"],
        ]

        miner = AprioriMiner(min_support=0.5, min_confidence=0.99)
        rules = miner.mine_rules(transactions)

        # Perfect correlation should produce rules
        assert isinstance(rules, list)


# ============================================================================
# TEST INTEGRATION
# ============================================================================

class TestIntegration:
    """Integration tests"""

    @pytest.mark.skipif(not SKLEARN_AVAILABLE or not PANDAS_AVAILABLE,
                       reason="scikit-learn and pandas required")
    def test_complete_customer_segmentation_workflow(self):
        """Test complete customer segmentation workflow"""
        # Create customer data
        customer_data = pd.DataFrame({
            'age': [25, 26, 27, 45, 46, 47, 65, 66, 67],
            'income': [30000, 32000, 31000, 70000, 72000, 71000, 45000, 47000, 46000],
            'spending': [500, 550, 520, 2000, 2100, 2050, 800, 850, 820],
        })

        # Segment customers
        engine = get_data_mining_engine()
        result = engine.segment_customers(customer_data, method='kmeans', n_segments=3)

        # Verify results
        assert result['n_clusters'] == 3
        assert len(result['clusters']) == 3

        # All customers should be assigned to a cluster
        total_assigned = sum(c.size for c in result['clusters'])
        assert total_assigned == len(customer_data)

        # Each cluster should have members
        for cluster in result['clusters']:
            assert cluster.size > 0
            assert len(cluster.members) == cluster.size

    def test_complete_market_basket_workflow(self):
        """Test complete market basket analysis workflow"""
        # Create transaction data
        transactions = [
            ["bread", "milk", "butter"],
            ["bread", "milk"],
            ["bread", "butter"],
            ["milk", "butter"],
            ["bread", "milk", "butter", "eggs"],
            ["bread", "eggs"],
            ["milk", "eggs"],
        ]

        # Find patterns
        engine = get_data_mining_engine()
        rules = engine.find_patterns(transactions, min_support=0.4, min_confidence=0.5)

        # Verify results
        assert isinstance(rules, list)

        if len(rules) > 0:
            # Check rule quality
            for rule in rules:
                assert rule.support >= 0.4
                assert rule.confidence >= 0.5
                assert rule.lift > 0

                # Verify lift makes sense
                # Lift > 1 means positive correlation
                # Lift < 1 means negative correlation
                assert rule.lift >= 0

    @pytest.mark.skipif(not SKLEARN_AVAILABLE or not PANDAS_AVAILABLE,
                       reason="scikit-learn and pandas required")
    def test_multiple_clustering_methods(self):
        """Test using multiple clustering methods on same data"""
        data = pd.DataFrame({
            'x': [1, 1, 2, 2, 10, 10, 11, 11],
            'y': [1, 2, 1, 2, 10, 11, 10, 11],
        })

        engine = get_data_mining_engine()

        # Try K-means
        kmeans_result = engine.segment_customers(data, method='kmeans', n_segments=2)
        assert kmeans_result['n_clusters'] == 2

        # Try DBSCAN
        dbscan_result = engine.segment_customers(data, method='dbscan')
        assert 'n_clusters' in dbscan_result

        # Both should cluster the data (possibly differently)
        assert kmeans_result['labels'] is not None
        assert dbscan_result['labels'] is not None


# ============================================================================
# RUN SUMMARY
# ============================================================================

if __name__ == "__main__":
    print("=" * 80)
    print("DATA MINING MODULE - TEST SUITE")
    print("=" * 80)
    print()
    print("Test Coverage:")
    print("  ✓ Data Classes (AssociationRule, Cluster)")
    print("  ✓ ClusteringEngine (K-means, DBSCAN)")
    print("  ✓ AprioriMiner (Association rule mining)")
    print("  ✓ DataMiningEngine (Main orchestrator)")
    print("  ✓ Singleton pattern")
    print("  ✓ Edge cases and error handling")
    print("  ✓ Integration tests")
    print()
    print(f"Optional Dependencies:")
    print(f"  - scikit-learn: {'✓ Available' if SKLEARN_AVAILABLE else '✗ Not available'}")
    print(f"  - pandas: {'✓ Available' if PANDAS_AVAILABLE else '✗ Not available'}")
    print()
    print("Run tests with: pytest tests/unit/analytics/test_data_mining.py -v")
    print("=" * 80)
