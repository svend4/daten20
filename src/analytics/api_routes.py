"""
Analytics API Routes

REST API endpoints for advanced analytics features.
"""

import logging
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
from flask import Blueprint, jsonify, request

from src.analytics.anomaly_detection import AnomalyMethod, get_anomaly_engine

logger = logging.getLogger("dms.analytics.api")

# Create Blueprint
analytics_api = Blueprint("analytics_api", __name__, url_prefix="/api/v1/analytics")


@analytics_api.route("/anomaly/detect", methods=["POST"])
def detect_anomalies():
    """
    Detect anomalies in data.

    Request body:
    {
        "data": [1, 2, 3, 100, 5, 6],
        "method": "zscore",  # Optional
        "threshold": 3.0     # Optional
    }
    """
    try:
        data_json = request.get_json()

        if not data_json or "data" not in data_json:
            return jsonify({"error": "Missing 'data' field"}), 400

        data = np.array(data_json["data"])
        method_str = data_json.get("method", "zscore")

        try:
            method = AnomalyMethod(method_str)
        except ValueError:
            return jsonify({"error": f"Invalid method: {method_str}"}), 400

        engine = get_anomaly_engine()
        result = engine.detect(data, method=method)

        return jsonify(
            {
                "data_points": result.data_points,
                "anomalies_count": result.anomalies_count,
                "anomaly_rate": result.anomaly_rate,
                "anomalies": [
                    {
                        "index": i,
                        "value": a.value,
                        "score": a.score,
                        "severity": a.severity.value,
                    }
                    for i, a in enumerate(result.anomalies)
                ],
                "summary": result.summary,
            }
        )

    except Exception as e:
        logger.error(f"Error detecting anomalies: {e}")
        return jsonify({"error": str(e)}), 500


@analytics_api.route("/anomaly/realtime", methods=["POST"])
def check_realtime_anomaly():
    """
    Check if a single value is anomaly in real-time context.

    Request body:
    {
        "detector_id": "sensor_1",
        "value": 42.5,
        "window_size": 100  # Optional
    }
    """
    try:
        data = request.get_json()

        if not data or "detector_id" not in data or "value" not in data:
            return jsonify({"error": "Missing required fields"}), 400

        detector_id = data["detector_id"]
        value = float(data["value"])
        window_size = data.get("window_size", 100)

        engine = get_anomaly_engine()

        # Get or create detector
        detector = engine.get_realtime_detector(detector_id)
        if not detector:
            detector = engine.create_realtime_detector(detector_id, window_size)

        # Check anomaly
        anomaly = detector.add_point(value)

        if anomaly:
            return jsonify(
                {
                    "is_anomaly": True,
                    "value": anomaly.value,
                    "score": anomaly.score,
                    "severity": anomaly.severity.value,
                    "expected_value": anomaly.expected_value,
                    "deviation": anomaly.deviation,
                }
            )
        else:
            return jsonify({"is_anomaly": False, "value": value})

    except Exception as e:
        logger.error(f"Error in realtime anomaly detection: {e}")
        return jsonify({"error": str(e)}), 500


@analytics_api.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "ok", "module": "analytics", "version": "3.2.0"})


logger.info("Analytics API routes loaded")
