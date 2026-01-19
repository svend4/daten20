#!/usr/bin/env python3
"""
Data Mining Module - Usage Examples

Demonstrates:
1. Customer segmentation with K-means clustering
2. Market basket analysis with Apriori algorithm
3. Density-based clustering with DBSCAN
4. Advanced pattern mining
5. Complete data mining workflow

Requirements:
- pandas, numpy, scikit-learn
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.analytics.data_mining import (
    get_data_mining_engine,
    SKLEARN_AVAILABLE,
)

# Check dependencies
try:
    import pandas as pd
    import numpy as np
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
    print("Warning: pandas/numpy not available. Some examples will be skipped.")


def print_section(title: str):
    """Print section header"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


# ============================================================================
# EXAMPLE 1: CUSTOMER SEGMENTATION (K-MEANS)
# ============================================================================

def example_customer_segmentation():
    """Example 1: Segment customers using K-means clustering"""
    print_section("EXAMPLE 1: Customer Segmentation with K-means")

    if not SKLEARN_AVAILABLE or not PANDAS_AVAILABLE:
        print("⚠️  Skipped: Requires scikit-learn and pandas")
        return

    # Create sample customer data
    np.random.seed(42)

    # Group 1: Young, low income (students)
    young = pd.DataFrame({
        'age': np.random.randint(18, 25, 30),
        'income': np.random.randint(15000, 25000, 30),
        'spending': np.random.randint(200, 500, 30),
    })

    # Group 2: Middle-aged, high income (professionals)
    professionals = pd.DataFrame({
        'age': np.random.randint(35, 50, 30),
        'income': np.random.randint(60000, 100000, 30),
        'spending': np.random.randint(1500, 3000, 30),
    })

    # Group 3: Retired, medium income
    retired = pd.DataFrame({
        'age': np.random.randint(60, 75, 30),
        'income': np.random.randint(30000, 50000, 30),
        'spending': np.random.randint(500, 1000, 30),
    })

    customers = pd.concat([young, professionals, retired], ignore_index=True)
    print(f"Total customers: {len(customers)}")
    print(f"\nData sample:")
    print(customers.head(10))

    # Segment customers
    engine = get_data_mining_engine()
    result = engine.segment_customers(customers, method='kmeans', n_segments=3)

    print(f"\n✓ Clustering completed!")
    print(f"  Number of clusters: {result['n_clusters']}")
    print(f"  Inertia (lower is better): {result['inertia']:.2f}")

    print(f"\n📊 Cluster Details:")
    for cluster in result['clusters']:
        members = customers.iloc[cluster.members]
        print(f"\n  Cluster {cluster.cluster_id}:")
        print(f"    Size: {cluster.size} customers")
        print(f"    Avg Age: {members['age'].mean():.1f} years")
        print(f"    Avg Income: ${members['income'].mean():.2f}")
        print(f"    Avg Spending: ${members['spending'].mean():.2f}")

        # Identify segment type
        avg_age = members['age'].mean()
        avg_income = members['income'].mean()
        if avg_age < 30:
            segment_type = "Young/Students"
        elif avg_income > 60000:
            segment_type = "Professionals"
        else:
            segment_type = "Retired/Seniors"
        print(f"    Segment Type: {segment_type}")

    print("\n✅ Example 1 completed successfully!")


# ============================================================================
# EXAMPLE 2: MARKET BASKET ANALYSIS (APRIORI)
# ============================================================================

def example_market_basket_analysis():
    """Example 2: Find product associations using Apriori"""
    print_section("EXAMPLE 2: Market Basket Analysis with Apriori")

    # Create sample transaction data
    transactions = [
        # Breakfast items
        ["milk", "bread", "butter", "eggs"],
        ["milk", "bread", "butter"],
        ["milk", "bread", "eggs"],
        ["bread", "butter", "eggs"],
        ["milk", "eggs"],

        # Lunch/dinner items
        ["pasta", "tomato_sauce", "cheese"],
        ["pasta", "tomato_sauce", "olive_oil"],
        ["pasta", "cheese", "olive_oil"],
        ["tomato_sauce", "cheese"],

        # Baking items
        ["flour", "sugar", "butter", "eggs"],
        ["flour", "sugar", "eggs"],
        ["butter", "eggs", "milk"],

        # Snacks
        ["chips", "soda", "candy"],
        ["chips", "soda"],
        ["candy", "chocolate"],

        # Mixed
        ["milk", "bread", "cheese"],
        ["pasta", "milk"],
        ["eggs", "bread", "cheese"],
        ["butter", "bread", "milk"],
        ["tomato_sauce", "pasta", "cheese"],
        ["milk", "bread", "butter", "eggs", "cheese"],
    ]

    print(f"Total transactions: {len(transactions)}")
    print(f"\nSample transactions:")
    for i, txn in enumerate(transactions[:5], 1):
        print(f"  {i}. {', '.join(txn)}")

    # Find association rules
    engine = get_data_mining_engine()
    rules = engine.find_patterns(
        transactions,
        min_support=0.15,  # Item must appear in 15% of transactions
        min_confidence=0.4  # Rule must be correct 40% of the time
    )

    print(f"\n✓ Pattern mining completed!")
    print(f"  Found {len(rules)} association rules")

    if len(rules) > 0:
        print(f"\n📊 Top 10 Association Rules (by lift):")
        print(f"  {'#':<3} {'Rule':<40} {'Support':<10} {'Conf':<8} {'Lift':<6}")
        print(f"  {'-'*3} {'-'*40} {'-'*10} {'-'*8} {'-'*6}")

        for i, rule in enumerate(rules[:10], 1):
            antecedent = ", ".join(rule.antecedent)
            consequent = ", ".join(rule.consequent)
            rule_str = f"{antecedent} → {consequent}"
            print(f"  {i:<3} {rule_str:<40} {rule.support:<10.3f} "
                  f"{rule.confidence:<8.3f} {rule.lift:<6.2f}")

        # Interpret top rule
        if rules:
            top_rule = rules[0]
            print(f"\n💡 Interpretation of Top Rule:")
            print(f"  If customer buys: {', '.join(top_rule.antecedent)}")
            print(f"  They will also buy: {', '.join(top_rule.consequent)}")
            print(f"  Probability: {top_rule.confidence*100:.1f}%")
            print(f"  Lift: {top_rule.lift:.2f}x more likely than random")

            if top_rule.lift > 1.5:
                print(f"  ✓ Strong positive correlation!")
            elif top_rule.lift > 1.0:
                print(f"  ✓ Positive correlation")
            else:
                print(f"  ⚠️  Weak or negative correlation")

    else:
        print("  ℹ️  No rules found with current thresholds")

    print("\n✅ Example 2 completed successfully!")


# ============================================================================
# EXAMPLE 3: DENSITY-BASED CLUSTERING (DBSCAN)
# ============================================================================

def example_dbscan_clustering():
    """Example 3: Density-based clustering with noise detection"""
    print_section("EXAMPLE 3: Density-based Clustering (DBSCAN)")

    if not SKLEARN_AVAILABLE or not PANDAS_AVAILABLE:
        print("⚠️  Skipped: Requires scikit-learn and pandas")
        return

    # Create customer data with clear clusters and outliers
    np.random.seed(42)

    # Cluster 1: High value customers (tight cluster)
    cluster1 = pd.DataFrame({
        'recency': np.random.randint(1, 10, 20),  # Recent purchases
        'frequency': np.random.randint(15, 25, 20),  # High frequency
        'monetary': np.random.randint(8000, 12000, 20),  # High value
    })

    # Cluster 2: Regular customers (tight cluster)
    cluster2 = pd.DataFrame({
        'recency': np.random.randint(20, 40, 25),
        'frequency': np.random.randint(5, 10, 25),
        'monetary': np.random.randint(2000, 4000, 25),
    })

    # Cluster 3: Low engagement (loose cluster)
    cluster3 = pd.DataFrame({
        'recency': np.random.randint(80, 120, 20),
        'frequency': np.random.randint(1, 3, 20),
        'monetary': np.random.randint(100, 500, 20),
    })

    # Outliers: Unusual customers
    outliers = pd.DataFrame({
        'recency': [5, 150, 2, 200],
        'frequency': [1, 30, 50, 1],
        'monetary': [50000, 100, 15000, 50],
    })

    customers = pd.concat([cluster1, cluster2, cluster3, outliers], ignore_index=True)
    print(f"Total customers: {len(customers)}")
    print(f"  - Normal customers: {len(customers) - len(outliers)}")
    print(f"  - Potential outliers: {len(outliers)}")

    print(f"\nData sample:")
    print(customers.head(10))

    # Apply DBSCAN
    engine = get_data_mining_engine()
    result = engine.segment_customers(customers, method='dbscan')

    print(f"\n✓ DBSCAN clustering completed!")
    print(f"  Clusters found: {result['n_clusters']}")
    print(f"  Noise points: {result['noise_points']}")

    if result['n_clusters'] > 0:
        print(f"\n📊 Cluster Details:")
        for cluster in result['clusters']:
            members = customers.iloc[cluster.members]
            print(f"\n  Cluster {cluster.cluster_id}:")
            print(f"    Size: {cluster.size} customers")
            print(f"    Avg Recency: {members['recency'].mean():.1f} days")
            print(f"    Avg Frequency: {members['frequency'].mean():.1f} purchases")
            print(f"    Avg Monetary: ${members['monetary'].mean():.2f}")

    if result['noise_points'] > 0:
        print(f"\n🔍 Outlier Analysis:")
        outlier_mask = pd.Series(result['labels']) == -1
        outlier_indices = customers[outlier_mask].index
        outlier_data = customers.iloc[outlier_indices]

        print(f"  Detected {result['noise_points']} outliers:")
        for idx in outlier_indices[:5]:  # Show first 5
            row = customers.iloc[idx]
            print(f"    Customer {idx}: Recency={row['recency']}, "
                  f"Frequency={row['frequency']}, Monetary=${row['monetary']}")

    print("\n✅ Example 3 completed successfully!")


# ============================================================================
# EXAMPLE 4: ADVANCED PATTERN MINING
# ============================================================================

def example_advanced_pattern_mining():
    """Example 4: Advanced pattern mining with different thresholds"""
    print_section("EXAMPLE 4: Advanced Pattern Mining")

    # E-commerce transaction data
    transactions = [
        ["laptop", "mouse", "keyboard", "monitor"],
        ["laptop", "mouse", "laptop_bag"],
        ["desktop", "keyboard", "monitor", "speakers"],
        ["mouse", "mousepad"],
        ["laptop", "mouse", "keyboard"],
        ["tablet", "stylus", "tablet_case"],
        ["laptop", "mouse", "laptop_bag", "external_drive"],
        ["desktop", "monitor", "speakers"],
        ["laptop", "keyboard", "mouse"],
        ["headphones", "headphone_case"],
        ["laptop", "mouse", "monitor", "keyboard", "laptop_bag"],
        ["desktop", "keyboard", "mouse", "monitor"],
        ["laptop", "external_drive"],
        ["mouse", "keyboard"],
        ["laptop", "mouse", "keyboard", "external_drive"],
    ]

    print(f"Analyzing {len(transactions)} e-commerce transactions")

    engine = get_data_mining_engine()

    # Try different threshold combinations
    thresholds = [
        (0.2, 0.5, "Conservative"),
        (0.15, 0.4, "Moderate"),
        (0.1, 0.3, "Aggressive"),
    ]

    for min_sup, min_conf, strategy in thresholds:
        print(f"\n{'─' * 80}")
        print(f"Strategy: {strategy}")
        print(f"  Min Support: {min_sup*100:.0f}%")
        print(f"  Min Confidence: {min_conf*100:.0f}%")

        rules = engine.find_patterns(transactions, min_support=min_sup, min_confidence=min_conf)

        print(f"  Rules found: {len(rules)}")

        if rules:
            # Show top 3 rules
            print(f"\n  Top 3 Rules:")
            for i, rule in enumerate(rules[:3], 1):
                ant = ", ".join(rule.antecedent)
                cons = ", ".join(rule.consequent)
                print(f"    {i}. {ant} → {cons}")
                print(f"       (conf: {rule.confidence:.2f}, lift: {rule.lift:.2f})")

    print(f"\n{'─' * 80}")
    print("\n💡 Insights:")
    print("  - Conservative: Few but highly confident rules")
    print("  - Moderate: Balanced approach (recommended)")
    print("  - Aggressive: Many rules but may include noise")

    print("\n✅ Example 4 completed successfully!")


# ============================================================================
# EXAMPLE 5: COMPLETE DATA MINING WORKFLOW
# ============================================================================

def example_complete_workflow():
    """Example 5: Complete data mining workflow"""
    print_section("EXAMPLE 5: Complete Data Mining Workflow")

    if not SKLEARN_AVAILABLE or not PANDAS_AVAILABLE:
        print("⚠️  Skipped: Requires scikit-learn and pandas")
        return

    print("Scenario: Analyze customer behavior and shopping patterns\n")

    # Step 1: Customer Segmentation
    print("Step 1: Customer Segmentation")
    print("-" * 40)

    np.random.seed(42)
    customers = pd.DataFrame({
        'customer_id': range(1, 51),
        'age': np.random.randint(18, 70, 50),
        'income': np.random.randint(20000, 120000, 50),
        'purchase_count': np.random.randint(1, 30, 50),
    })

    engine = get_data_mining_engine()
    segments = engine.segment_customers(
        customers[['age', 'income', 'purchase_count']],
        method='kmeans',
        n_segments=3
    )

    print(f"  ✓ Identified {segments['n_clusters']} customer segments")

    # Assign segment labels
    customers['segment'] = segments['labels']

    # Step 2: Analyze each segment's shopping patterns
    print(f"\nStep 2: Shopping Pattern Analysis")
    print("-" * 40)

    # Generate transactions for each segment with different buying patterns
    all_transactions = []

    # Segment 0: Tech enthusiasts
    tech_items = ["laptop", "mouse", "keyboard", "monitor", "headphones"]
    # Segment 1: Office workers
    office_items = ["notebook", "pen", "stapler", "folder", "desk_lamp"]
    # Segment 2: Students
    student_items = ["backpack", "textbook", "notebook", "pen", "calculator"]

    for idx, row in customers.iterrows():
        segment = row['segment']
        if segment == 0:
            items = np.random.choice(tech_items, size=np.random.randint(2, 4), replace=False)
        elif segment == 1:
            items = np.random.choice(office_items, size=np.random.randint(2, 4), replace=False)
        else:
            items = np.random.choice(student_items, size=np.random.randint(2, 3), replace=False)

        all_transactions.append(list(items))

    # Find patterns
    rules = engine.find_patterns(all_transactions, min_support=0.15, min_confidence=0.4)

    print(f"  ✓ Found {len(rules)} association rules")

    if rules:
        print(f"\n  Top 3 Product Associations:")
        for i, rule in enumerate(rules[:3], 1):
            print(f"    {i}. {', '.join(rule.antecedent)} → {', '.join(rule.consequent)}")
            print(f"       Lift: {rule.lift:.2f}")

    # Step 3: Generate insights
    print(f"\nStep 3: Business Insights")
    print("-" * 40)

    for segment_id in range(segments['n_clusters']):
        segment_customers = customers[customers['segment'] == segment_id]
        print(f"\n  Segment {segment_id}:")
        print(f"    Size: {len(segment_customers)} customers")
        print(f"    Avg Age: {segment_customers['age'].mean():.1f}")
        print(f"    Avg Income: ${segment_customers['income'].mean():.2f}")
        print(f"    Avg Purchases: {segment_customers['purchase_count'].mean():.1f}")

        # Recommend strategy based on segment
        avg_income = segment_customers['income'].mean()
        avg_purchases = segment_customers['purchase_count'].mean()

        if avg_income > 70000 and avg_purchases > 15:
            strategy = "Premium products, loyalty program"
        elif avg_income < 40000:
            strategy = "Budget-friendly options, student discounts"
        else:
            strategy = "Mid-range products, bulk discounts"

        print(f"    Strategy: {strategy}")

    print("\n✅ Example 5 completed successfully!")
    print("\n💡 Complete workflow: Segmentation → Pattern Mining → Insights → Strategy")


# ============================================================================
# MAIN
# ============================================================================

def main():
    """Run all examples"""
    print("\n" + "=" * 80)
    print("  DATA MINING MODULE - USAGE EXAMPLES")
    print("=" * 80)

    print("\nDependency Status:")
    print(f"  - scikit-learn: {'✓ Available' if SKLEARN_AVAILABLE else '✗ Not available'}")
    print(f"  - pandas: {'✓ Available' if PANDAS_AVAILABLE else '✗ Not available'}")

    try:
        # Run examples
        example_customer_segmentation()
        example_market_basket_analysis()
        example_dbscan_clustering()
        example_advanced_pattern_mining()
        example_complete_workflow()

        # Summary
        print_section("SUMMARY")
        print("All examples completed successfully!")
        print("\nKey Takeaways:")
        print("  1. K-means: Best for well-separated clusters")
        print("  2. DBSCAN: Handles noise and arbitrary shapes")
        print("  3. Apriori: Discovers product associations")
        print("  4. Patterns: Adjust thresholds based on needs")
        print("  5. Workflow: Combine techniques for insights")

        print("\n📚 Next Steps:")
        print("  - Try with your own data")
        print("  - Experiment with different parameters")
        print("  - Combine with other analytics modules")
        print("  - Use insights for business decisions")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

    print("\n" + "=" * 80)
    return 0


if __name__ == "__main__":
    exit(main())
