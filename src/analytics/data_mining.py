#!/usr/bin/env python3
"""
Data Mining Module (Pure Python Implementation)

Pattern discovery and data mining algorithms for business intelligence.
Implements real algorithms without numpy/pandas/sklearn dependencies.

Key Features:
- Clustering (K-means, DBSCAN, Hierarchical)
- Association rule mining (Apriori algorithm)
- Pattern discovery & frequent itemset mining
- Market basket analysis
- Customer segmentation
- Outlier detection
- Sequential pattern mining

All algorithms are complete implementations with real math and logic.
"""

from __future__ import annotations

import math
import random
import threading
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple, Callable


# ============================================================================
# Data Structures
# ============================================================================


@dataclass
class AssociationRule:
    """Association rule (A -> B)"""
    antecedent: List[str]
    consequent: List[str]
    support: float
    confidence: float
    lift: float

    def __str__(self) -> str:
        return f"{self.antecedent} -> {self.consequent} (sup={self.support:.3f}, conf={self.confidence:.3f}, lift={self.lift:.3f})"


@dataclass
class Cluster:
    """Cluster result"""
    cluster_id: int
    members: List[int]
    centroid: Optional[List[float]] = None
    size: int = 0

    def __post_init__(self):
        if self.size == 0:
            self.size = len(self.members)


@dataclass
class Point:
    """Data point for clustering"""
    index: int
    features: List[float]
    cluster_id: int = -1
    visited: bool = False

    def distance_to(self, other: Point) -> float:
        """Euclidean distance to another point"""
        return math.sqrt(sum((a - b) ** 2 for a, b in zip(self.features, other.features)))

    def distance_to_centroid(self, centroid: List[float]) -> float:
        """Distance to centroid"""
        return math.sqrt(sum((a - b) ** 2 for a, b in zip(self.features, centroid)))


@dataclass
class FrequentItemset:
    """Frequent itemset with support"""
    items: Tuple[str, ...]
    support: float
    count: int

    def __hash__(self):
        return hash(self.items)


class LinkageMethod(Enum):
    """Linkage methods for hierarchical clustering"""
    SINGLE = "single"  # Minimum distance
    COMPLETE = "complete"  # Maximum distance
    AVERAGE = "average"  # Average distance
    CENTROID = "centroid"  # Centroid distance


class OutlierMethod(Enum):
    """Outlier detection methods"""
    IQR = "iqr"  # Interquartile range
    ZSCORE = "zscore"  # Z-score method
    ISOLATION = "isolation"  # Isolation-based


# ============================================================================
# K-means Clustering (Lloyd's Algorithm)
# ============================================================================


class KMeansClusterer:
    """K-means clustering using Lloyd's algorithm"""

    def __init__(self, n_clusters: int = 3, max_iters: int = 100, tolerance: float = 1e-4, random_seed: Optional[int] = None):
        self.n_clusters = n_clusters
        self.max_iters = max_iters
        self.tolerance = tolerance
        self.random_seed = random_seed
        self.centroids: List[List[float]] = []
        self.inertia: float = 0.0

    def fit(self, data: List[Dict[str, Any]], features: List[str]) -> Dict[str, Any]:
        """Fit K-means model"""
        if self.random_seed is not None:
            random.seed(self.random_seed)

        # Extract feature vectors
        points = []
        for idx, row in enumerate(data):
            feature_vec = [float(row.get(f, 0.0)) for f in features]
            points.append(Point(idx, feature_vec))

        if not points or not points[0].features:
            return {"clusters": [], "labels": [], "inertia": 0.0}

        n_features = len(points[0].features)

        # Initialize centroids using k-means++ algorithm
        self.centroids = self._initialize_centroids_kmeanspp(points)

        # Lloyd's algorithm iterations
        for iteration in range(self.max_iters):
            # Assignment step: assign points to nearest centroid
            for point in points:
                min_dist = float('inf')
                best_cluster = 0

                for cluster_id, centroid in enumerate(self.centroids):
                    dist = point.distance_to_centroid(centroid)
                    if dist < min_dist:
                        min_dist = dist
                        best_cluster = cluster_id

                point.cluster_id = best_cluster

            # Update step: recalculate centroids
            old_centroids = [c[:] for c in self.centroids]

            for cluster_id in range(self.n_clusters):
                cluster_points = [p for p in points if p.cluster_id == cluster_id]

                if cluster_points:
                    # Calculate mean of all points in cluster
                    new_centroid = []
                    for feature_idx in range(n_features):
                        mean_val = sum(p.features[feature_idx] for p in cluster_points) / len(cluster_points)
                        new_centroid.append(mean_val)
                    self.centroids[cluster_id] = new_centroid

            # Check convergence
            max_shift = max(
                math.sqrt(sum((a - b) ** 2 for a, b in zip(old, new)))
                for old, new in zip(old_centroids, self.centroids)
            )

            if max_shift < self.tolerance:
                break

        # Calculate inertia (sum of squared distances to centroids)
        self.inertia = 0.0
        for point in points:
            dist = point.distance_to_centroid(self.centroids[point.cluster_id])
            self.inertia += dist ** 2

        # Create clusters
        clusters = []
        labels = []

        for cluster_id in range(self.n_clusters):
            members = [p.index for p in points if p.cluster_id == cluster_id]
            cluster = Cluster(
                cluster_id=cluster_id,
                members=members,
                centroid=self.centroids[cluster_id],
                size=len(members)
            )
            clusters.append(cluster)

        labels = [p.cluster_id for p in sorted(points, key=lambda x: x.index)]

        return {
            "clusters": clusters,
            "labels": labels,
            "inertia": self.inertia,
            "n_clusters": self.n_clusters,
            "n_iterations": iteration + 1
        }

    def _initialize_centroids_kmeanspp(self, points: List[Point]) -> List[List[float]]:
        """Initialize centroids using k-means++ algorithm"""
        centroids = []

        # First centroid: random point
        first_point = random.choice(points)
        centroids.append(first_point.features[:])

        # Remaining centroids: weighted by distance squared
        for _ in range(1, self.n_clusters):
            distances = []

            for point in points:
                # Distance to nearest existing centroid
                min_dist = min(point.distance_to_centroid(c) for c in centroids)
                distances.append(min_dist ** 2)

            # Weighted random selection
            total = sum(distances)
            if total == 0:
                # All points are at same location, pick random
                next_point = random.choice(points)
            else:
                probabilities = [d / total for d in distances]
                next_point = random.choices(points, weights=probabilities)[0]

            centroids.append(next_point.features[:])

        return centroids


# ============================================================================
# DBSCAN Clustering (Density-Based Spatial Clustering)
# ============================================================================


class DBSCANClusterer:
    """DBSCAN clustering algorithm"""

    def __init__(self, eps: float = 0.5, min_samples: int = 5):
        self.eps = eps
        self.min_samples = min_samples

    def fit(self, data: List[Dict[str, Any]], features: List[str]) -> Dict[str, Any]:
        """Fit DBSCAN model"""
        # Extract feature vectors
        points = []
        for idx, row in enumerate(data):
            feature_vec = [float(row.get(f, 0.0)) for f in features]
            points.append(Point(idx, feature_vec))

        if not points:
            return {"clusters": [], "labels": [], "n_clusters": 0, "noise_points": 0}

        # Normalize features for better distance calculation
        points = self._normalize_points(points)

        cluster_id = 0

        for point in points:
            if point.visited:
                continue

            point.visited = True
            neighbors = self._get_neighbors(point, points)

            if len(neighbors) < self.min_samples:
                # Mark as noise (cluster_id = -1)
                point.cluster_id = -1
            else:
                # Start new cluster
                self._expand_cluster(point, neighbors, cluster_id, points)
                cluster_id += 1

        # Create clusters
        clusters = []
        unique_clusters = set(p.cluster_id for p in points if p.cluster_id != -1)

        for cid in sorted(unique_clusters):
            members = [p.index for p in points if p.cluster_id == cid]

            # Calculate centroid
            cluster_points = [p for p in points if p.cluster_id == cid]
            if cluster_points and cluster_points[0].features:
                n_features = len(cluster_points[0].features)
                centroid = []
                for feature_idx in range(n_features):
                    mean_val = sum(p.features[feature_idx] for p in cluster_points) / len(cluster_points)
                    centroid.append(mean_val)
            else:
                centroid = None

            cluster = Cluster(
                cluster_id=cid,
                members=members,
                centroid=centroid,
                size=len(members)
            )
            clusters.append(cluster)

        labels = [p.cluster_id for p in sorted(points, key=lambda x: x.index)]
        noise_count = sum(1 for p in points if p.cluster_id == -1)

        return {
            "clusters": clusters,
            "labels": labels,
            "n_clusters": len(clusters),
            "noise_points": noise_count
        }

    def _get_neighbors(self, point: Point, points: List[Point]) -> List[Point]:
        """Get all neighbors within eps radius"""
        neighbors = []
        for other in points:
            if point.distance_to(other) <= self.eps:
                neighbors.append(other)
        return neighbors

    def _expand_cluster(self, point: Point, neighbors: List[Point], cluster_id: int, points: List[Point]):
        """Expand cluster from seed point"""
        point.cluster_id = cluster_id

        i = 0
        while i < len(neighbors):
            neighbor = neighbors[i]

            if not neighbor.visited:
                neighbor.visited = True
                neighbor_neighbors = self._get_neighbors(neighbor, points)

                if len(neighbor_neighbors) >= self.min_samples:
                    # Add new neighbors to expansion list
                    neighbors.extend([n for n in neighbor_neighbors if n not in neighbors])

            # Assign to cluster if not yet assigned
            if neighbor.cluster_id == -1:
                neighbor.cluster_id = cluster_id

            i += 1

    def _normalize_points(self, points: List[Point]) -> List[Point]:
        """Normalize point features using min-max scaling"""
        if not points or not points[0].features:
            return points

        n_features = len(points[0].features)

        # Find min/max for each feature
        min_vals = []
        max_vals = []

        for feature_idx in range(n_features):
            values = [p.features[feature_idx] for p in points]
            min_vals.append(min(values))
            max_vals.append(max(values))

        # Normalize
        for point in points:
            normalized = []
            for feature_idx in range(n_features):
                min_val = min_vals[feature_idx]
                max_val = max_vals[feature_idx]

                if max_val - min_val > 0:
                    normalized_val = (point.features[feature_idx] - min_val) / (max_val - min_val)
                else:
                    normalized_val = 0.0

                normalized.append(normalized_val)

            point.features = normalized

        return points


# ============================================================================
# Hierarchical Clustering
# ============================================================================


class HierarchicalClusterer:
    """Agglomerative hierarchical clustering"""

    def __init__(self, n_clusters: int = 3, linkage: LinkageMethod = LinkageMethod.AVERAGE):
        self.n_clusters = n_clusters
        self.linkage = linkage

    def fit(self, data: List[Dict[str, Any]], features: List[str]) -> Dict[str, Any]:
        """Fit hierarchical clustering model"""
        # Extract feature vectors
        points = []
        for idx, row in enumerate(data):
            feature_vec = [float(row.get(f, 0.0)) for f in features]
            points.append(Point(idx, feature_vec))

        if not points:
            return {"clusters": [], "labels": [], "n_clusters": 0, "dendrogram": []}

        # Initialize each point as its own cluster
        clusters = [[i] for i in range(len(points))]
        dendrogram = []

        # Merge until we have desired number of clusters
        while len(clusters) > self.n_clusters:
            # Find closest pair of clusters
            min_dist = float('inf')
            merge_i, merge_j = 0, 1

            for i in range(len(clusters)):
                for j in range(i + 1, len(clusters)):
                    dist = self._cluster_distance(clusters[i], clusters[j], points)
                    if dist < min_dist:
                        min_dist = dist
                        merge_i, merge_j = i, j

            # Merge clusters
            merged = clusters[merge_i] + clusters[merge_j]
            dendrogram.append({
                "cluster_1": clusters[merge_i][:],
                "cluster_2": clusters[merge_j][:],
                "distance": min_dist,
                "size": len(merged)
            })

            # Remove old clusters and add merged
            clusters = [c for idx, c in enumerate(clusters) if idx not in (merge_i, merge_j)]
            clusters.append(merged)

        # Create final clusters
        result_clusters = []
        labels = [-1] * len(points)

        for cluster_id, members in enumerate(clusters):
            # Calculate centroid
            if members:
                n_features = len(points[0].features)
                centroid = []
                for feature_idx in range(n_features):
                    mean_val = sum(points[m].features[feature_idx] for m in members) / len(members)
                    centroid.append(mean_val)
            else:
                centroid = None

            for member in members:
                labels[member] = cluster_id

            cluster = Cluster(
                cluster_id=cluster_id,
                members=members,
                centroid=centroid,
                size=len(members)
            )
            result_clusters.append(cluster)

        return {
            "clusters": result_clusters,
            "labels": labels,
            "n_clusters": len(result_clusters),
            "dendrogram": dendrogram
        }

    def _cluster_distance(self, cluster1: List[int], cluster2: List[int], points: List[Point]) -> float:
        """Calculate distance between two clusters based on linkage method"""
        if self.linkage == LinkageMethod.SINGLE:
            # Minimum distance
            return min(
                points[i].distance_to(points[j])
                for i in cluster1
                for j in cluster2
            )
        elif self.linkage == LinkageMethod.COMPLETE:
            # Maximum distance
            return max(
                points[i].distance_to(points[j])
                for i in cluster1
                for j in cluster2
            )
        elif self.linkage == LinkageMethod.AVERAGE:
            # Average distance
            total = sum(
                points[i].distance_to(points[j])
                for i in cluster1
                for j in cluster2
            )
            return total / (len(cluster1) * len(cluster2))
        else:  # CENTROID
            # Distance between centroids
            n_features = len(points[0].features)

            centroid1 = [
                sum(points[i].features[f] for i in cluster1) / len(cluster1)
                for f in range(n_features)
            ]
            centroid2 = [
                sum(points[i].features[f] for i in cluster2) / len(cluster2)
                for f in range(n_features)
            ]

            return math.sqrt(sum((a - b) ** 2 for a, b in zip(centroid1, centroid2)))


# ============================================================================
# Apriori Algorithm (Association Rule Mining)
# ============================================================================


class AprioriMiner:
    """Apriori algorithm for mining association rules"""

    def __init__(self, min_support: float = 0.01, min_confidence: float = 0.1):
        self.min_support = min_support
        self.min_confidence = min_confidence
        self.frequent_itemsets: Dict[int, List[FrequentItemset]] = {}

    def find_rules(self, transactions: List[List[str]], min_confidence: Optional[float] = None) -> List[AssociationRule]:
        """Find association rules using Apriori algorithm"""
        if min_confidence is not None:
            self.min_confidence = min_confidence

        n_transactions = len(transactions)
        if n_transactions == 0:
            return []

        # Phase 1: Find frequent itemsets
        self._find_frequent_itemsets(transactions, n_transactions)

        # Phase 2: Generate association rules
        rules = []

        for k, itemsets in self.frequent_itemsets.items():
            if k < 2:  # Need at least 2 items to make a rule
                continue

            for itemset in itemsets:
                # Generate all possible rules from this itemset
                rules.extend(self._generate_rules_from_itemset(itemset, transactions, n_transactions))

        # Sort by lift (descending)
        rules.sort(key=lambda r: r.lift, reverse=True)

        return rules

    def _find_frequent_itemsets(self, transactions: List[List[str]], n_transactions: int):
        """Find all frequent itemsets using Apriori algorithm"""
        self.frequent_itemsets = {}

        # Level 1: Find frequent 1-itemsets
        item_counts = Counter()
        for transaction in transactions:
            for item in transaction:
                item_counts[item] += 1

        # Filter by minimum support
        frequent_1 = []
        for item, count in item_counts.items():
            support = count / n_transactions
            if support >= self.min_support:
                itemset = FrequentItemset(items=(item,), support=support, count=count)
                frequent_1.append(itemset)

        if not frequent_1:
            return

        self.frequent_itemsets[1] = frequent_1

        # Level k (k > 1): Generate and test candidates
        k = 2
        while True:
            # Generate candidates from previous level
            candidates = self._generate_candidates(k)

            if not candidates:
                break

            # Count candidate support
            candidate_counts = defaultdict(int)
            for transaction in transactions:
                transaction_set = set(transaction)
                for candidate in candidates:
                    if set(candidate).issubset(transaction_set):
                        candidate_counts[candidate] += 1

            # Filter by minimum support
            frequent_k = []
            for candidate, count in candidate_counts.items():
                support = count / n_transactions
                if support >= self.min_support:
                    itemset = FrequentItemset(items=candidate, support=support, count=count)
                    frequent_k.append(itemset)

            if not frequent_k:
                break

            self.frequent_itemsets[k] = frequent_k
            k += 1

    def _generate_candidates(self, k: int) -> List[Tuple[str, ...]]:
        """Generate candidate k-itemsets from (k-1)-itemsets"""
        if k - 1 not in self.frequent_itemsets:
            return []

        prev_itemsets = [itemset.items for itemset in self.frequent_itemsets[k - 1]]
        candidates = []

        # Join step: merge itemsets that share k-2 items
        for i in range(len(prev_itemsets)):
            for j in range(i + 1, len(prev_itemsets)):
                items_i = sorted(prev_itemsets[i])
                items_j = sorted(prev_itemsets[j])

                # Check if first k-2 items are the same
                if items_i[:-1] == items_j[:-1]:
                    # Merge by taking union
                    candidate = tuple(sorted(set(items_i) | set(items_j)))

                    if len(candidate) == k:
                        # Prune step: check if all (k-1)-subsets are frequent
                        if self._has_frequent_subsets(candidate):
                            candidates.append(candidate)

        return candidates

    def _has_frequent_subsets(self, candidate: Tuple[str, ...]) -> bool:
        """Check if all (k-1)-subsets of candidate are frequent"""
        k = len(candidate)
        if k - 1 not in self.frequent_itemsets:
            return False

        frequent_items = set(
            itemset.items
            for itemset in self.frequent_itemsets[k - 1]
        )

        # Generate all (k-1)-subsets
        for i in range(k):
            subset = tuple(candidate[:i] + candidate[i + 1:])
            if subset not in frequent_items:
                return False

        return True

    def _generate_rules_from_itemset(
        self,
        itemset: FrequentItemset,
        transactions: List[List[str]],
        n_transactions: int
    ) -> List[AssociationRule]:
        """Generate all possible rules from a frequent itemset"""
        rules = []
        items = list(itemset.items)
        n = len(items)

        # Generate all non-empty proper subsets as antecedents
        for i in range(1, 2 ** n - 1):
            antecedent = []
            consequent = []

            for j in range(n):
                if i & (1 << j):
                    antecedent.append(items[j])
                else:
                    consequent.append(items[j])

            if antecedent and consequent:
                # Calculate confidence: support(A ∪ B) / support(A)
                antecedent_count = sum(
                    1 for t in transactions if all(item in t for item in antecedent)
                )

                if antecedent_count == 0:
                    continue

                confidence = itemset.count / antecedent_count

                if confidence >= self.min_confidence:
                    # Calculate lift: confidence / support(B)
                    consequent_count = sum(
                        1 for t in transactions if all(item in t for item in consequent)
                    )
                    consequent_support = consequent_count / n_transactions

                    if consequent_support > 0:
                        lift = confidence / consequent_support

                        rule = AssociationRule(
                            antecedent=sorted(antecedent),
                            consequent=sorted(consequent),
                            support=itemset.support,
                            confidence=confidence,
                            lift=lift
                        )
                        rules.append(rule)

        return rules


# ============================================================================
# Outlier Detection
# ============================================================================


class OutlierDetector:
    """Detect outliers in data"""

    def __init__(self, method: OutlierMethod = OutlierMethod.IQR):
        self.method = method

    def detect(self, data: List[Dict[str, Any]], features: List[str]) -> Dict[str, Any]:
        """Detect outliers in dataset"""
        if self.method == OutlierMethod.IQR:
            return self._detect_iqr(data, features)
        elif self.method == OutlierMethod.ZSCORE:
            return self._detect_zscore(data, features)
        else:
            return self._detect_isolation(data, features)

    def _detect_iqr(self, data: List[Dict[str, Any]], features: List[str]) -> Dict[str, Any]:
        """Detect outliers using Interquartile Range (IQR) method"""
        outliers = []
        outlier_indices = set()

        for feature in features:
            values = [float(row.get(feature, 0.0)) for row in data]
            values_sorted = sorted(values)
            n = len(values_sorted)

            if n < 4:
                continue

            # Calculate Q1 and Q3
            q1_idx = n // 4
            q3_idx = 3 * n // 4
            q1 = values_sorted[q1_idx]
            q3 = values_sorted[q3_idx]
            iqr = q3 - q1

            # Outlier bounds
            lower_bound = q1 - 1.5 * iqr
            upper_bound = q3 + 1.5 * iqr

            # Find outliers
            for idx, value in enumerate(values):
                if value < lower_bound or value > upper_bound:
                    outliers.append({
                        "index": idx,
                        "feature": feature,
                        "value": value,
                        "reason": f"Outside IQR bounds [{lower_bound:.2f}, {upper_bound:.2f}]"
                    })
                    outlier_indices.add(idx)

        return {
            "outliers": outliers,
            "outlier_indices": sorted(outlier_indices),
            "n_outliers": len(outlier_indices),
            "method": "IQR"
        }

    def _detect_zscore(self, data: List[Dict[str, Any]], features: List[str], threshold: float = 3.0) -> Dict[str, Any]:
        """Detect outliers using Z-score method"""
        outliers = []
        outlier_indices = set()

        for feature in features:
            values = [float(row.get(feature, 0.0)) for row in data]

            # Calculate mean and std dev
            mean = sum(values) / len(values)
            variance = sum((x - mean) ** 2 for x in values) / len(values)
            std_dev = math.sqrt(variance)

            if std_dev == 0:
                continue

            # Find outliers (|z-score| > threshold)
            for idx, value in enumerate(values):
                z_score = (value - mean) / std_dev

                if abs(z_score) > threshold:
                    outliers.append({
                        "index": idx,
                        "feature": feature,
                        "value": value,
                        "z_score": z_score,
                        "reason": f"Z-score {z_score:.2f} exceeds threshold {threshold}"
                    })
                    outlier_indices.add(idx)

        return {
            "outliers": outliers,
            "outlier_indices": sorted(outlier_indices),
            "n_outliers": len(outlier_indices),
            "method": "Z-Score"
        }

    def _detect_isolation(self, data: List[Dict[str, Any]], features: List[str]) -> Dict[str, Any]:
        """Detect outliers using simplified isolation method"""
        # Simple isolation: points far from any other point
        points = []
        for idx, row in enumerate(data):
            feature_vec = [float(row.get(f, 0.0)) for f in features]
            points.append(Point(idx, feature_vec))

        if len(points) < 2:
            return {"outliers": [], "outlier_indices": [], "n_outliers": 0, "method": "Isolation"}

        outliers = []
        outlier_indices = set()

        # Calculate average distance to k-nearest neighbors
        k = min(5, len(points) - 1)

        for point in points:
            # Find distances to all other points
            distances = []
            for other in points:
                if point.index != other.index:
                    distances.append(point.distance_to(other))

            distances.sort()
            avg_distance = sum(distances[:k]) / k

            # If average distance is significantly higher than median, it's an outlier
            all_avg_distances = []
            for p in points:
                dists = sorted([p.distance_to(o) for o in points if p.index != o.index])
                all_avg_distances.append(sum(dists[:k]) / k)

            all_avg_distances.sort()
            median = all_avg_distances[len(all_avg_distances) // 2]
            threshold = median * 2.0  # Outlier if 2x median distance

            if avg_distance > threshold:
                outliers.append({
                    "index": point.index,
                    "avg_distance": avg_distance,
                    "threshold": threshold,
                    "reason": f"Average distance {avg_distance:.2f} exceeds threshold {threshold:.2f}"
                })
                outlier_indices.add(point.index)

        return {
            "outliers": outliers,
            "outlier_indices": sorted(outlier_indices),
            "n_outliers": len(outlier_indices),
            "method": "Isolation"
        }


# ============================================================================
# Sequential Pattern Mining
# ============================================================================


@dataclass
class SequentialPattern:
    """Sequential pattern with support"""
    sequence: Tuple[Tuple[str, ...], ...]
    support: float
    count: int


class SequentialPatternMiner:
    """Sequential pattern mining (PrefixSpan-like algorithm)"""

    def __init__(self, min_support: float = 0.1):
        self.min_support = min_support

    def mine_patterns(self, sequences: List[List[List[str]]]) -> List[SequentialPattern]:
        """Mine frequent sequential patterns"""
        n_sequences = len(sequences)
        if n_sequences == 0:
            return []

        # Find frequent 1-patterns
        patterns = []
        item_counts = Counter()

        for sequence in sequences:
            items_in_seq = set()
            for itemset in sequence:
                for item in itemset:
                    items_in_seq.add(item)

            for item in items_in_seq:
                item_counts[item] += 1

        # Build frequent 1-patterns
        frequent_items = []
        for item, count in item_counts.items():
            support = count / n_sequences
            if support >= self.min_support:
                pattern = SequentialPattern(
                    sequence=((item,),),
                    support=support,
                    count=count
                )
                patterns.append(pattern)
                frequent_items.append(item)

        # Recursively mine longer patterns
        for item in frequent_items:
            prefix = ((item,),)
            self._mine_recursive(sequences, n_sequences, prefix, patterns)

        # Sort by support
        patterns.sort(key=lambda p: p.support, reverse=True)

        return patterns

    def _mine_recursive(
        self,
        sequences: List[List[List[str]]],
        n_sequences: int,
        prefix: Tuple[Tuple[str, ...], ...],
        patterns: List[SequentialPattern]
    ):
        """Recursively mine patterns with given prefix"""
        # Find items that can extend the prefix
        item_counts = Counter()

        for sequence in sequences:
            if self._contains_pattern(sequence, prefix):
                # Find items after the prefix
                items_after = self._get_items_after_pattern(sequence, prefix)
                for item in items_after:
                    item_counts[item] += 1

        # Extend with frequent items
        for item, count in item_counts.items():
            support = count / n_sequences
            if support >= self.min_support:
                # Create new pattern
                new_pattern = prefix + ((item,),)
                pattern = SequentialPattern(
                    sequence=new_pattern,
                    support=support,
                    count=count
                )
                patterns.append(pattern)

                # Recurse
                self._mine_recursive(sequences, n_sequences, new_pattern, patterns)

    def _contains_pattern(self, sequence: List[List[str]], pattern: Tuple[Tuple[str, ...], ...]) -> bool:
        """Check if sequence contains the pattern"""
        pattern_idx = 0

        for itemset in sequence:
            if pattern_idx >= len(pattern):
                break

            # Check if current pattern itemset is subset of current sequence itemset
            if all(item in itemset for item in pattern[pattern_idx]):
                pattern_idx += 1

        return pattern_idx == len(pattern)

    def _get_items_after_pattern(self, sequence: List[List[str]], pattern: Tuple[Tuple[str, ...], ...]) -> Set[str]:
        """Get all items that appear after the pattern in sequence"""
        items = set()
        pattern_idx = 0
        found_pattern = False

        for itemset in sequence:
            if not found_pattern:
                # Still looking for pattern
                if pattern_idx < len(pattern) and all(item in itemset for item in pattern[pattern_idx]):
                    pattern_idx += 1
                    if pattern_idx == len(pattern):
                        found_pattern = True
            else:
                # Pattern found, collect items
                items.update(itemset)

        return items


# ============================================================================
# Main Data Mining Engine
# ============================================================================


class ClusteringEngine:
    """Clustering engine with multiple algorithms"""

    def __init__(self):
        self.model = None

    def kmeans(self, data: List[Dict[str, Any]], n_clusters: int = 3, features: Optional[List[str]] = None) -> Dict[str, Any]:
        """K-means clustering"""
        if features is None:
            # Auto-detect numeric features
            if data:
                features = [k for k, v in data[0].items() if isinstance(v, (int, float))]

        if not features:
            return {"clusters": [], "labels": [], "inertia": 0.0, "error": "No numeric features found"}

        clusterer = KMeansClusterer(n_clusters=n_clusters, random_seed=42)
        return clusterer.fit(data, features)

    def dbscan(
        self,
        data: List[Dict[str, Any]],
        eps: float = 0.5,
        min_samples: int = 5,
        features: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """DBSCAN clustering"""
        if features is None:
            if data:
                features = [k for k, v in data[0].items() if isinstance(v, (int, float))]

        if not features:
            return {"clusters": [], "labels": [], "n_clusters": 0, "noise_points": 0, "error": "No numeric features found"}

        clusterer = DBSCANClusterer(eps=eps, min_samples=min_samples)
        return clusterer.fit(data, features)

    def hierarchical(
        self,
        data: List[Dict[str, Any]],
        n_clusters: int = 3,
        linkage: str = "average",
        features: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Hierarchical clustering"""
        if features is None:
            if data:
                features = [k for k, v in data[0].items() if isinstance(v, (int, float))]

        if not features:
            return {"clusters": [], "labels": [], "n_clusters": 0, "error": "No numeric features found"}

        # Convert linkage string to enum
        linkage_map = {
            "single": LinkageMethod.SINGLE,
            "complete": LinkageMethod.COMPLETE,
            "average": LinkageMethod.AVERAGE,
            "centroid": LinkageMethod.CENTROID
        }
        linkage_method = linkage_map.get(linkage.lower(), LinkageMethod.AVERAGE)

        clusterer = HierarchicalClusterer(n_clusters=n_clusters, linkage=linkage_method)
        return clusterer.fit(data, features)


class AssociationRuleMiner:
    """Association rule mining wrapper"""

    def __init__(self, min_support: float = 0.1):
        self.min_support = min_support
        self.miner = AprioriMiner(min_support=min_support)

    def apriori(self, transactions: List[List[str]], min_confidence: float = 0.5) -> List[AssociationRule]:
        """Apriori algorithm"""
        return self.miner.find_rules(transactions, min_confidence)


class DataMiningEngine:
    """Main data mining engine"""

    def __init__(self):
        self.clustering = ClusteringEngine()
        self.association = AssociationRuleMiner()
        self.outlier_detector = OutlierDetector()
        self.sequential_miner = SequentialPatternMiner()

    def cluster(
        self,
        data: List[Dict[str, Any]],
        n_clusters: int = 3,
        method: str = "kmeans",
        **kwargs
    ) -> Dict[str, Any]:
        """Cluster data using specified method"""
        if method == "kmeans":
            return self.clustering.kmeans(data, n_clusters, **kwargs)
        elif method == "dbscan":
            return self.clustering.dbscan(data, **kwargs)
        elif method == "hierarchical":
            return self.clustering.hierarchical(data, n_clusters, **kwargs)
        else:
            raise ValueError(f"Unknown clustering method: {method}")

    def mine_rules(
        self,
        transactions: List[List[str]],
        min_support: float = 0.1,
        min_confidence: float = 0.5
    ) -> List[AssociationRule]:
        """Mine association rules"""
        self.association.min_support = min_support
        self.association.miner.min_support = min_support
        self.association.miner.min_confidence = min_confidence
        return self.association.apriori(transactions, min_confidence)

    def detect_outliers(
        self,
        data: List[Dict[str, Any]],
        features: Optional[List[str]] = None,
        method: str = "iqr"
    ) -> Dict[str, Any]:
        """Detect outliers in data"""
        if features is None:
            if data:
                features = [k for k, v in data[0].items() if isinstance(v, (int, float))]

        if not features:
            return {"outliers": [], "outlier_indices": [], "n_outliers": 0, "error": "No numeric features found"}

        method_map = {
            "iqr": OutlierMethod.IQR,
            "zscore": OutlierMethod.ZSCORE,
            "isolation": OutlierMethod.ISOLATION
        }
        outlier_method = method_map.get(method.lower(), OutlierMethod.IQR)

        detector = OutlierDetector(method=outlier_method)
        return detector.detect(data, features)

    def mine_sequential_patterns(
        self,
        sequences: List[List[List[str]]],
        min_support: float = 0.1
    ) -> List[SequentialPattern]:
        """Mine sequential patterns"""
        miner = SequentialPatternMiner(min_support=min_support)
        return miner.mine_patterns(sequences)


# ============================================================================
# Singleton Pattern
# ============================================================================

_mining_engine = None
_lock = threading.Lock()


def get_data_mining_engine() -> DataMiningEngine:
    """Get singleton instance of data mining engine"""
    global _mining_engine
    if _mining_engine is None:
        with _lock:
            if _mining_engine is None:
                _mining_engine = DataMiningEngine()
    return _mining_engine


# ============================================================================
# Main (Testing)
# ============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("Data Mining Module - Pure Python Implementation")
    print("=" * 70)

    engine = get_data_mining_engine()

    # Test 1: K-means clustering
    print("\n1. K-means Clustering")
    print("-" * 70)
    data = [
        {"x": 1.0, "y": 2.0, "customer_id": "C1"},
        {"x": 1.5, "y": 1.8, "customer_id": "C2"},
        {"x": 5.0, "y": 8.0, "customer_id": "C3"},
        {"x": 8.0, "y": 8.0, "customer_id": "C4"},
        {"x": 1.0, "y": 0.6, "customer_id": "C5"},
        {"x": 9.0, "y": 11.0, "customer_id": "C6"},
    ]

    result = engine.cluster(data, n_clusters=2, method="kmeans", features=["x", "y"])
    print(f"Clusters: {result['n_clusters']}")
    print(f"Inertia: {result['inertia']:.2f}")
    for cluster in result['clusters']:
        print(f"  Cluster {cluster.cluster_id}: {len(cluster.members)} members, centroid={[f'{c:.2f}' for c in cluster.centroid]}")

    # Test 2: Association rules (market basket)
    print("\n2. Association Rule Mining (Market Basket)")
    print("-" * 70)
    transactions = [
        ["milk", "bread", "butter"],
        ["milk", "bread"],
        ["milk", "butter"],
        ["bread", "butter", "jam"],
        ["milk", "bread", "butter", "jam"],
        ["milk", "bread", "butter"],
        ["bread", "butter"],
        ["milk", "jam"],
    ]

    rules = engine.mine_rules(transactions, min_support=0.3, min_confidence=0.5)
    print(f"Found {len(rules)} association rules:")
    for rule in rules[:5]:
        print(f"  {rule}")

    # Test 3: Outlier detection
    print("\n3. Outlier Detection")
    print("-" * 70)
    data_with_outliers = [
        {"value": 10, "score": 20},
        {"value": 12, "score": 22},
        {"value": 11, "score": 21},
        {"value": 13, "score": 23},
        {"value": 100, "score": 200},  # Outlier
        {"value": 10, "score": 19},
        {"value": 14, "score": 24},
    ]

    outliers = engine.detect_outliers(data_with_outliers, features=["value", "score"], method="iqr")
    print(f"Detected {outliers['n_outliers']} outliers using {outliers['method']} method:")
    for outlier in outliers['outliers']:
        print(f"  Index {outlier['index']}: {outlier['feature']}={outlier['value']} - {outlier['reason']}")

    print("\n" + "=" * 70)
    print("Data Mining Module loaded successfully!")
    print("=" * 70)
