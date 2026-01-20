#!/usr/bin/env python3
"""
Data Mining Module

Pattern discovery and data mining algorithms for business intelligence.

Key Features:
- Clustering (K-means, DBSCAN, Hierarchical)
- Association rule mining (Apriori)
- Pattern discovery
- Market basket analysis
- Customer segmentation

Dependencies:
- pandas, numpy, scikit-learn
"""

from __future__ import annotations

import threading
from collections import Counter, defaultdict
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple

if TYPE_CHECKING:
    import pandas as pd
    import numpy as np

try:
    import numpy as np
    import pandas as pd
    from sklearn.cluster import DBSCAN, KMeans
    from sklearn.preprocessing import StandardScaler

    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    np = None  # type: ignore
    pd = None  # type: ignore
    print("Warning: scikit-learn not available. Data mining features limited.")


@dataclass
class AssociationRule:
    """Association rule (A -> B)"""

    antecedent: List[str]
    consequent: List[str]
    support: float
    confidence: float
    lift: float


@dataclass
class Cluster:
    """Cluster result"""

    cluster_id: int
    members: List[int]
    centroid: Optional[List[float]] = None
    size: int = 0


class ClusteringEngine:
    """Clustering algorithms for customer segmentation"""

    def __init__(self):
        self.model = None
        self.scaler = StandardScaler() if SKLEARN_AVAILABLE else None

    def kmeans(self, data: pd.DataFrame, n_clusters: int = 3, features: Optional[List[str]] = None) -> Dict[str, Any]:
        """K-means clustering"""
        if not SKLEARN_AVAILABLE:
            raise ImportError("scikit-learn required")

        # Select features
        if features:
            X = data[features].values
        else:
            X = data.select_dtypes(include=[np.number]).values

        # Standardize
        X_scaled = self.scaler.fit_transform(X)

        # Fit model
        self.model = KMeans(n_clusters=n_clusters, random_state=42)
        labels = self.model.fit_predict(X_scaled)

        # Create clusters
        clusters = []
        for i in range(n_clusters):
            members = np.where(labels == i)[0].tolist()
            cluster = Cluster(
                cluster_id=i, members=members, centroid=self.model.cluster_centers_[i].tolist(), size=len(members)
            )
            clusters.append(cluster)

        return {
            "clusters": clusters,
            "labels": labels.tolist(),
            "inertia": float(self.model.inertia_),
            "n_clusters": n_clusters,
        }

    def dbscan(
        self, data: pd.DataFrame, eps: float = 0.5, min_samples: int = 5, features: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """DBSCAN clustering (density-based)"""
        if not SKLEARN_AVAILABLE:
            raise ImportError("scikit-learn required")

        if features:
            X = data[features].values
        else:
            X = data.select_dtypes(include=[np.number]).values

        X_scaled = self.scaler.fit_transform(X)

        model = DBSCAN(eps=eps, min_samples=min_samples)
        labels = model.fit_predict(X_scaled)

        unique_labels = set(labels)
        clusters = []
        for label in unique_labels:
            if label == -1:  # Noise points
                continue
            members = np.where(labels == label)[0].tolist()
            cluster = Cluster(cluster_id=int(label), members=members, size=len(members))
            clusters.append(cluster)

        return {
            "clusters": clusters,
            "labels": labels.tolist(),
            "n_clusters": len(clusters),
            "noise_points": int((labels == -1).sum()),
        }


class AprioriMiner:
    """Apriori algorithm for association rule mining"""

    def __init__(self, min_support: float = 0.01, min_confidence: float = 0.1):
        self.min_support = min_support
        self.min_confidence = min_confidence
        self.frequent_itemsets = {}

    def mine_rules(self, transactions: List[List[str]]) -> List[AssociationRule]:
        """Mine association rules from transactions"""
        n_transactions = len(transactions)

        # Find frequent itemsets
        itemsets = self._find_frequent_itemsets(transactions, n_transactions)

        # Generate rules
        rules = []
        for itemset, support in itemsets.items():
            if len(itemset) < 2:
                continue

            # Generate all possible rules
            for i in range(1, len(itemset)):
                antecedents = list(itemset[:i])
                consequents = list(itemset[i:])

                confidence = self._calculate_confidence(antecedents, consequents, transactions)
                if confidence >= self.min_confidence:
                    lift = self._calculate_lift(antecedents, consequents, transactions, n_transactions)

                    rule = AssociationRule(
                        antecedent=antecedents,
                        consequent=consequents,
                        support=support,
                        confidence=confidence,
                        lift=lift,
                    )
                    rules.append(rule)

        return sorted(rules, key=lambda r: r.lift, reverse=True)

    def _find_frequent_itemsets(
        self, transactions: List[List[str]], n_transactions: int
    ) -> Dict[Tuple[str, ...], float]:
        """Find frequent itemsets using Apriori"""
        itemsets = {}

        # Count 1-itemsets
        item_counts = Counter()
        for transaction in transactions:
            for item in transaction:
                item_counts[item] += 1

        # Filter by min support
        for item, count in item_counts.items():
            support = count / n_transactions
            if support >= self.min_support:
                itemsets[(item,)] = support

        # Generate larger itemsets
        k = 2
        while True:
            candidates = self._generate_candidates(list(itemsets.keys()), k)
            if not candidates:
                break

            # Count candidates
            candidate_counts = defaultdict(int)
            for transaction in transactions:
                for candidate in candidates:
                    if all(item in transaction for item in candidate):
                        candidate_counts[candidate] += 1

            # Filter by min support
            new_itemsets = {}
            for candidate, count in candidate_counts.items():
                support = count / n_transactions
                if support >= self.min_support:
                    new_itemsets[candidate] = support

            if not new_itemsets:
                break

            itemsets.update(new_itemsets)
            k += 1

        return itemsets

    def _generate_candidates(self, itemsets: List[Tuple[str, ...]], k: int) -> List[Tuple[str, ...]]:
        """Generate candidate itemsets of size k"""
        candidates = []
        n = len(itemsets)

        for i in range(n):
            for j in range(i + 1, n):
                # Merge if they share k-2 items
                union = tuple(sorted(set(itemsets[i]) | set(itemsets[j])))
                if len(union) == k and union not in candidates:
                    candidates.append(union)

        return candidates

    def _calculate_confidence(
        self, antecedent: List[str], consequent: List[str], transactions: List[List[str]]
    ) -> float:
        """Calculate rule confidence"""
        antecedent_count = sum(1 for t in transactions if all(item in t for item in antecedent))
        if antecedent_count == 0:
            return 0.0

        both_count = sum(1 for t in transactions if all(item in t for item in antecedent + consequent))
        return both_count / antecedent_count

    def _calculate_lift(
        self, antecedent: List[str], consequent: List[str], transactions: List[List[str]], n_transactions: int
    ) -> float:
        """Calculate rule lift"""
        consequent_support = sum(1 for t in transactions if all(item in t for item in consequent)) / n_transactions
        if consequent_support == 0:
            return 0.0

        confidence = self._calculate_confidence(antecedent, consequent, transactions)
        return confidence / consequent_support


class DataMiningEngine:
    """Main data mining engine"""

    def __init__(self):
        self.clustering = ClusteringEngine()
        self.apriori = AprioriMiner()

    def segment_customers(
        self, customer_data: pd.DataFrame, method: str = "kmeans", n_segments: int = 3
    ) -> Dict[str, Any]:
        """Segment customers using clustering"""
        if method == "kmeans":
            return self.clustering.kmeans(customer_data, n_clusters=n_segments)
        elif method == "dbscan":
            return self.clustering.dbscan(customer_data)
        else:
            raise ValueError(f"Unknown method: {method}")

    def find_patterns(
        self, transactions: List[List[str]], min_support: float = 0.01, min_confidence: float = 0.1
    ) -> List[AssociationRule]:
        """Find association patterns"""
        self.apriori.min_support = min_support
        self.apriori.min_confidence = min_confidence
        return self.apriori.mine_rules(transactions)


# Singleton
_mining_engine = None
_lock = threading.Lock()


def get_data_mining_engine() -> DataMiningEngine:
    """Get singleton instance"""
    global _mining_engine
    if _mining_engine is None:
        with _lock:
            if _mining_engine is None:
                _mining_engine = DataMiningEngine()
    return _mining_engine


if __name__ == "__main__":
    engine = get_data_mining_engine()
    print("Data Mining Engine initialized!")

    # Example: Market basket analysis
    transactions = [
        ["milk", "bread", "butter"],
        ["milk", "bread"],
        ["milk", "butter"],
        ["bread", "butter", "jam"],
        ["milk", "bread", "butter", "jam"],
    ]

    rules = engine.find_patterns(transactions, min_support=0.4, min_confidence=0.5)
    print(f"\nFound {len(rules)} association rules:")
    for rule in rules[:3]:
        print(f"  {rule.antecedent} -> {rule.consequent} (confidence: {rule.confidence:.2f}, lift: {rule.lift:.2f})")

    print("\nData Mining module loaded successfully!")
