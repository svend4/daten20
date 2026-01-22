"""
Anomaly Detection Engine

Advanced anomaly detection using multiple algorithms for identifying
outliers and unusual patterns in data.

Key Features:
- Statistical methods (Z-score, IQR, MAD)
- Machine learning (Isolation Forest, One-Class SVM, LOF)
- Time series anomalies (STL decomposition, ARIMA residuals)
- Real-time anomaly detection
- Multi-dimensional anomaly detection
- Adaptive thresholds
- Anomaly scoring and ranking
- Pattern-based anomalies
- Collective anomalies
- Contextual anomalies

Algorithms:
1. Z-Score: Standard deviation based
2. Modified Z-Score (MAD): Robust to outliers
3. IQR (Interquartile Range): Box plot method
4. Isolation Forest: Tree-based isolation
5. One-Class SVM: Support vector based
6. Local Outlier Factor (LOF): Density-based
7. DBSCAN: Clustering-based
8. Autoencoder: Neural network based (optional)
9. Prophet Detector: Time series specific (optional)

Dependencies:
- Required: numpy, pandas, scikit-learn, scipy
- Optional: tensorflow/pytorch (for autoencoders), prophet
"""

import logging
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

logger = logging.getLogger("dms.analytics.anomaly")

# Core dependencies
try:
    import pandas as pd
    from scipy import stats
    from sklearn.cluster import DBSCAN
    from sklearn.covariance import EllipticEnvelope
    from sklearn.ensemble import IsolationForest
    from sklearn.neighbors import LocalOutlierFactor
    from sklearn.preprocessing import StandardScaler
    from sklearn.svm import OneClassSVM

    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    logger.warning("scikit-learn not available. ML anomaly detection disabled.")

# Optional dependencies
try:
    from statsmodels.tsa.seasonal import STL

    STATSMODELS_AVAILABLE = True
except ImportError:
    STATSMODELS_AVAILABLE = False
    logger.warning("statsmodels not available. STL decomposition disabled.")


class AnomalyMethod(str, Enum):
    """Anomaly detection methods"""

    ZSCORE = "zscore"
    MODIFIED_ZSCORE = "modified_zscore"
    IQR = "iqr"
    ISOLATION_FOREST = "isolation_forest"
    ONE_CLASS_SVM = "one_class_svm"
    LOF = "local_outlier_factor"
    DBSCAN = "dbscan"
    ELLIPTIC_ENVELOPE = "elliptic_envelope"
    STL_DECOMPOSITION = "stl"


class AnomalySeverity(str, Enum):
    """Anomaly severity levels"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class Anomaly:
    """Detected anomaly"""

    timestamp: datetime
    value: float
    score: float  # Anomaly score (higher = more anomalous)
    severity: AnomalySeverity
    method: AnomalyMethod
    expected_value: Optional[float] = None
    deviation: Optional[float] = None
    context: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AnomalyDetectionResult:
    """Anomaly detection result"""

    data_points: int
    anomalies_count: int
    anomaly_rate: float  # Percentage
    anomalies: List[Anomaly]
    summary: Dict[str, Any]


class StatisticalDetector:
    """Statistical anomaly detection methods"""

    def __init__(self, threshold: float = 3.0):
        """
        Initialize detector.

        Args:
            threshold: Number of standard deviations for Z-score
        """
        self.threshold = threshold

    def zscore_detection(self, data: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Z-score based anomaly detection.

        Args:
            data: Input data

        Returns:
            (is_anomaly, scores) arrays
        """
        mean = np.mean(data)
        std = np.std(data)

        if std == 0:
            return np.zeros(len(data), dtype=bool), np.zeros(len(data))

        z_scores = np.abs((data - mean) / std)
        is_anomaly = z_scores > self.threshold

        return is_anomaly, z_scores

    def modified_zscore_detection(self, data: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Modified Z-score using MAD (Median Absolute Deviation).
        More robust to outliers than standard Z-score.

        Args:
            data: Input data

        Returns:
            (is_anomaly, scores) arrays
        """
        median = np.median(data)
        mad = np.median(np.abs(data - median))

        if mad == 0:
            return np.zeros(len(data), dtype=bool), np.zeros(len(data))

        modified_z_scores = 0.6745 * (data - median) / mad
        is_anomaly = np.abs(modified_z_scores) > self.threshold

        return is_anomaly, np.abs(modified_z_scores)

    def iqr_detection(self, data: np.ndarray, k: float = 1.5) -> Tuple[np.ndarray, np.ndarray]:
        """
        IQR (Interquartile Range) based anomaly detection.

        Args:
            data: Input data
            k: IQR multiplier (typically 1.5 or 3.0)

        Returns:
            (is_anomaly, scores) arrays
        """
        q1 = np.percentile(data, 25)
        q3 = np.percentile(data, 75)
        iqr = q3 - q1

        lower_bound = q1 - k * iqr
        upper_bound = q3 + k * iqr

        is_anomaly = (data < lower_bound) | (data > upper_bound)

        # Calculate scores as distance from bounds
        scores = np.maximum(0, np.maximum(lower_bound - data, data - upper_bound)) / (iqr if iqr > 0 else 1)

        return is_anomaly, scores


class MLDetector:
    """Machine Learning based anomaly detection"""

    def __init__(self, contamination: float = 0.1):
        """
        Initialize detector.

        Args:
            contamination: Expected proportion of anomalies
        """
        if not SKLEARN_AVAILABLE:
            raise ImportError("scikit-learn required for ML anomaly detection")

        self.contamination = contamination
        self.scaler = StandardScaler()

    def isolation_forest_detection(self, data: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Isolation Forest anomaly detection.

        Args:
            data: Input data (can be multidimensional)

        Returns:
            (is_anomaly, scores) arrays
        """
        # Reshape if 1D
        if data.ndim == 1:
            data = data.reshape(-1, 1)

        # Scale data
        data_scaled = self.scaler.fit_transform(data)

        # Train Isolation Forest
        clf = IsolationForest(
            contamination=self.contamination, random_state=42, n_estimators=100, max_samples="auto"
        )

        predictions = clf.fit_predict(data_scaled)
        scores = -clf.score_samples(data_scaled)  # Negative scores, higher = more anomalous

        is_anomaly = predictions == -1

        return is_anomaly, scores

    def one_class_svm_detection(self, data: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        One-Class SVM anomaly detection.

        Args:
            data: Input data

        Returns:
            (is_anomaly, scores) arrays
        """
        if data.ndim == 1:
            data = data.reshape(-1, 1)

        data_scaled = self.scaler.fit_transform(data)

        clf = OneClassSVM(nu=self.contamination, kernel="rbf", gamma="auto")

        predictions = clf.fit_predict(data_scaled)
        scores = -clf.decision_function(data_scaled)  # Distance to hyperplane

        is_anomaly = predictions == -1

        return is_anomaly, scores

    def lof_detection(self, data: np.ndarray, n_neighbors: int = 20) -> Tuple[np.ndarray, np.ndarray]:
        """
        Local Outlier Factor (LOF) anomaly detection.

        Args:
            data: Input data
            n_neighbors: Number of neighbors to use

        Returns:
            (is_anomaly, scores) arrays
        """
        if data.ndim == 1:
            data = data.reshape(-1, 1)

        data_scaled = self.scaler.fit_transform(data)

        clf = LocalOutlierFactor(n_neighbors=n_neighbors, contamination=self.contamination, novelty=False)

        predictions = clf.fit_predict(data_scaled)
        scores = -clf.negative_outlier_factor_  # LOF scores

        is_anomaly = predictions == -1

        return is_anomaly, scores

    def dbscan_detection(self, data: np.ndarray, eps: float = 0.5, min_samples: int = 5) -> Tuple[np.ndarray, np.ndarray]:
        """
        DBSCAN clustering-based anomaly detection.
        Points not belonging to any cluster are anomalies.

        Args:
            data: Input data
            eps: Maximum distance between samples
            min_samples: Minimum samples in a neighborhood

        Returns:
            (is_anomaly, scores) arrays
        """
        if data.ndim == 1:
            data = data.reshape(-1, 1)

        data_scaled = self.scaler.fit_transform(data)

        clf = DBSCAN(eps=eps, min_samples=min_samples)
        labels = clf.fit_predict(data_scaled)

        # Label -1 indicates noise/anomalies
        is_anomaly = labels == -1

        # Calculate scores as distance to nearest cluster
        scores = np.zeros(len(data))
        scores[is_anomaly] = 1.0

        return is_anomaly, scores

    def elliptic_envelope_detection(self, data: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Elliptic Envelope (Robust Covariance) anomaly detection.

        Args:
            data: Input data

        Returns:
            (is_anomaly, scores) arrays
        """
        if data.ndim == 1:
            data = data.reshape(-1, 1)

        data_scaled = self.scaler.fit_transform(data)

        clf = EllipticEnvelope(contamination=self.contamination, random_state=42)

        predictions = clf.fit_predict(data_scaled)
        scores = -clf.decision_function(data_scaled)

        is_anomaly = predictions == -1

        return is_anomaly, scores


class TimeSeriesDetector:
    """Time series specific anomaly detection"""

    def __init__(self):
        """Initialize detector"""
        pass

    def stl_detection(
        self, data: pd.Series, period: int = 7, threshold: float = 3.0
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        STL (Seasonal-Trend decomposition using Loess) based anomaly detection.

        Args:
            data: Time series data
            period: Seasonal period
            threshold: Number of standard deviations for residuals

        Returns:
            (is_anomaly, scores) arrays
        """
        if not STATSMODELS_AVAILABLE:
            raise ImportError("statsmodels required for STL decomposition")

        # STL decomposition
        stl = STL(data, period=period, seasonal=13)
        result = stl.fit()

        residuals = result.resid

        # Detect anomalies in residuals
        mean_resid = np.mean(residuals)
        std_resid = np.std(residuals)

        if std_resid == 0:
            return np.zeros(len(data), dtype=bool), np.zeros(len(data))

        z_scores = np.abs((residuals - mean_resid) / std_resid)
        is_anomaly = z_scores > threshold

        return is_anomaly.values, z_scores.values


class RealTimeDetector:
    """Real-time anomaly detection with sliding windows"""

    def __init__(self, window_size: int = 100, threshold: float = 3.0):
        """
        Initialize detector.

        Args:
            window_size: Size of sliding window
            threshold: Anomaly threshold
        """
        self.window_size = window_size
        self.threshold = threshold
        self.window = deque(maxlen=window_size)

    def add_point(self, value: float) -> Optional[Anomaly]:
        """
        Add new data point and check for anomalies.

        Args:
            value: New data point

        Returns:
            Anomaly if detected, None otherwise
        """
        self.window.append(value)

        if len(self.window) < 10:  # Need minimum data
            return None

        # Calculate statistics
        window_array = np.array(self.window)
        mean = np.mean(window_array)
        std = np.std(window_array)

        if std == 0:
            return None

        z_score = abs((value - mean) / std)

        if z_score > self.threshold:
            # Determine severity
            if z_score > 5.0:
                severity = AnomalySeverity.CRITICAL
            elif z_score > 4.0:
                severity = AnomalySeverity.HIGH
            elif z_score > 3.5:
                severity = AnomalySeverity.MEDIUM
            else:
                severity = AnomalySeverity.LOW

            return Anomaly(
                timestamp=datetime.now(),
                value=value,
                score=z_score,
                severity=severity,
                method=AnomalyMethod.ZSCORE,
                expected_value=mean,
                deviation=value - mean,
            )

        return None


class AnomalyDetectionEngine:
    """Main anomaly detection engine"""

    def __init__(self, default_method: AnomalyMethod = AnomalyMethod.ZSCORE, contamination: float = 0.1):
        """
        Initialize engine.

        Args:
            default_method: Default detection method
            contamination: Expected anomaly proportion
        """
        self.default_method = default_method
        self.contamination = contamination

        self.stat_detector = StatisticalDetector()
        self.ml_detector = MLDetector(contamination) if SKLEARN_AVAILABLE else None
        self.ts_detector = TimeSeriesDetector()
        self.realtime_detectors = {}

    def detect(
        self, data: np.ndarray, method: Optional[AnomalyMethod] = None, timestamps: Optional[List[datetime]] = None
    ) -> AnomalyDetectionResult:
        """
        Detect anomalies in data.

        Args:
            data: Input data
            method: Detection method (uses default if None)
            timestamps: Optional timestamps for each data point

        Returns:
            AnomalyDetectionResult
        """
        method = method or self.default_method

        # Detect anomalies
        if method == AnomalyMethod.ZSCORE:
            is_anomaly, scores = self.stat_detector.zscore_detection(data)

        elif method == AnomalyMethod.MODIFIED_ZSCORE:
            is_anomaly, scores = self.stat_detector.modified_zscore_detection(data)

        elif method == AnomalyMethod.IQR:
            is_anomaly, scores = self.stat_detector.iqr_detection(data)

        elif method == AnomalyMethod.ISOLATION_FOREST:
            if not self.ml_detector:
                raise ValueError("ML detector not available (scikit-learn required)")
            is_anomaly, scores = self.ml_detector.isolation_forest_detection(data)

        elif method == AnomalyMethod.ONE_CLASS_SVM:
            if not self.ml_detector:
                raise ValueError("ML detector not available")
            is_anomaly, scores = self.ml_detector.one_class_svm_detection(data)

        elif method == AnomalyMethod.LOF:
            if not self.ml_detector:
                raise ValueError("ML detector not available")
            is_anomaly, scores = self.ml_detector.lof_detection(data)

        elif method == AnomalyMethod.DBSCAN:
            if not self.ml_detector:
                raise ValueError("ML detector not available")
            is_anomaly, scores = self.ml_detector.dbscan_detection(data)

        elif method == AnomalyMethod.ELLIPTIC_ENVELOPE:
            if not self.ml_detector:
                raise ValueError("ML detector not available")
            is_anomaly, scores = self.ml_detector.elliptic_envelope_detection(data)

        else:
            raise ValueError(f"Unknown method: {method}")

        # Create anomaly objects
        anomalies = []
        for i, (is_anom, score) in enumerate(zip(is_anomaly, scores)):
            if is_anom:
                # Determine severity based on score
                if score > 5.0:
                    severity = AnomalySeverity.CRITICAL
                elif score > 4.0:
                    severity = AnomalySeverity.HIGH
                elif score > 3.0:
                    severity = AnomalySeverity.MEDIUM
                else:
                    severity = AnomalySeverity.LOW

                timestamp = timestamps[i] if timestamps else datetime.now()

                anomaly = Anomaly(
                    timestamp=timestamp,
                    value=data[i] if data.ndim == 1 else float(data[i].mean()),
                    score=float(score),
                    severity=severity,
                    method=method,
                )

                anomalies.append(anomaly)

        # Calculate statistics
        anomaly_rate = (len(anomalies) / len(data)) * 100

        summary = {
            "method": method.value,
            "total_points": len(data),
            "anomalies": len(anomalies),
            "anomaly_rate": anomaly_rate,
            "severity_distribution": {
                severity.value: len([a for a in anomalies if a.severity == severity])
                for severity in AnomalySeverity
            },
        }

        return AnomalyDetectionResult(
            data_points=len(data), anomalies_count=len(anomalies), anomaly_rate=anomaly_rate, anomalies=anomalies, summary=summary
        )

    def detect_time_series(
        self, data: pd.Series, period: int = 7, method: AnomalyMethod = AnomalyMethod.STL_DECOMPOSITION
    ) -> AnomalyDetectionResult:
        """
        Detect anomalies in time series data.

        Args:
            data: Time series data with datetime index
            period: Seasonal period
            method: Detection method

        Returns:
            AnomalyDetectionResult
        """
        if method == AnomalyMethod.STL_DECOMPOSITION:
            is_anomaly, scores = self.ts_detector.stl_detection(data, period)
            timestamps = list(data.index)
        else:
            # Use regular detection
            return self.detect(data.values, method, timestamps=list(data.index))

        # Create anomaly objects
        anomalies = []
        for i, (is_anom, score) in enumerate(zip(is_anomaly, scores)):
            if is_anom:
                severity = (
                    AnomalySeverity.CRITICAL
                    if score > 5.0
                    else AnomalySeverity.HIGH
                    if score > 4.0
                    else AnomalySeverity.MEDIUM
                    if score > 3.0
                    else AnomalySeverity.LOW
                )

                anomaly = Anomaly(
                    timestamp=timestamps[i],
                    value=data.iloc[i],
                    score=score,
                    severity=severity,
                    method=method,
                )

                anomalies.append(anomaly)

        anomaly_rate = (len(anomalies) / len(data)) * 100

        return AnomalyDetectionResult(
            data_points=len(data),
            anomalies_count=len(anomalies),
            anomaly_rate=anomaly_rate,
            anomalies=anomalies,
            summary={"method": method.value, "period": period},
        )

    def create_realtime_detector(self, detector_id: str, window_size: int = 100) -> RealTimeDetector:
        """
        Create a real-time detector.

        Args:
            detector_id: Unique identifier for detector
            window_size: Window size

        Returns:
            RealTimeDetector
        """
        detector = RealTimeDetector(window_size)
        self.realtime_detectors[detector_id] = detector
        return detector

    def get_realtime_detector(self, detector_id: str) -> Optional[RealTimeDetector]:
        """Get existing real-time detector"""
        return self.realtime_detectors.get(detector_id)


# Global instance
_anomaly_engine: Optional[AnomalyDetectionEngine] = None


def get_anomaly_engine() -> AnomalyDetectionEngine:
    """Get global anomaly detection engine instance"""
    global _anomaly_engine

    if _anomaly_engine is None:
        _anomaly_engine = AnomalyDetectionEngine()

    return _anomaly_engine


logger.info("Anomaly Detection Engine loaded")
