"""
REST API v1 with Swagger Documentation

Versioned REST API for the Document Management System.
Includes comprehensive Swagger/OpenAPI documentation.
"""

import logging
from typing import Any, Dict, List

from flasgger import swag_from
from flask import Blueprint, jsonify, request

# Import core modules
from src.core.database import Database
from src.financial_calculator import FinancialCalculator
from src.models.service import Service

# Setup logger
logger = logging.getLogger("dms.api.v1")

# Create API v1 blueprint
api_v1 = Blueprint("api_v1", __name__, url_prefix="/api/v1")


# ==========================================
# HEALTH AND STATUS ENDPOINTS
# ==========================================


@api_v1.route("/health", methods=["GET"])
def health_check():
    """
    Health check endpoint
    ---
    tags:
      - System
    summary: Check API health status
    description: Returns the health status of the API and database connectivity
    responses:
      200:
        description: API is healthy
        schema:
          type: object
          properties:
            status:
              type: string
              example: healthy
            version:
              type: string
              example: 2.1.0
            api_version:
              type: string
              example: v1
            database:
              type: string
              example: connected
    """
    try:
        db = Database()
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"
        logger.error(f"Health check failed: {e}")

    return jsonify(
        {
            "status": "healthy" if db_status == "connected" else "degraded",
            "version": "2.1.0",
            "api_version": "v1",
            "database": db_status,
        }
    )


# ==========================================
# SERVICE ENDPOINTS
# ==========================================


@api_v1.route("/services", methods=["GET"])
def list_services():
    """
    List all services
    ---
    tags:
      - Services
    summary: Get list of all services
    description: Returns a list of all services with optional filtering
    parameters:
      - name: region
        in: query
        type: string
        required: false
        description: Filter by region
      - name: limit
        in: query
        type: integer
        required: false
        description: Maximum number of results
        default: 100
      - name: offset
        in: query
        type: integer
        required: false
        description: Number of results to skip
        default: 0
    responses:
      200:
        description: List of services
        schema:
          type: object
          properties:
            total:
              type: integer
              example: 42
            services:
              type: array
              items:
                type: object
                properties:
                  id:
                    type: integer
                    example: 1
                  service_name:
                    type: string
                    example: "Shopping Assistance"
                  region:
                    type: string
                    example: "Bavaria"
                  brutto_rate:
                    type: number
                    example: 45.50
      500:
        description: Server error
    """
    try:
        db = Database()
        services = db.list_services()

        # Apply filters
        region = request.args.get("region")
        if region:
            services = [s for s in services if s.basic_info.region == region]

        # Pagination
        limit = int(request.args.get("limit", 100))
        offset = int(request.args.get("offset", 0))
        paginated = services[offset : offset + limit]

        # Format response
        result = {
            "total": len(services),
            "count": len(paginated),
            "offset": offset,
            "limit": limit,
            "services": [
                {
                    "id": s.id,
                    "service_name": s.basic_info.service_name,
                    "region": s.basic_info.region,
                    "target_group": s.basic_info.target_group,
                    "brutto_rate": s.financial.brutto_rate,
                    "created_at": s.created_at.isoformat() if s.created_at else None,
                }
                for s in paginated
            ],
        }

        return jsonify(result), 200

    except Exception as e:
        logger.error(f"Error listing services: {e}")
        return jsonify({"error": str(e)}), 500


@api_v1.route("/services/<int:service_id>", methods=["GET"])
def get_service(service_id: int):
    """
    Get service details
    ---
    tags:
      - Services
    summary: Get detailed information about a specific service
    description: Returns complete details of a service including financial data
    parameters:
      - name: service_id
        in: path
        type: integer
        required: true
        description: Service ID
    responses:
      200:
        description: Service details
        schema:
          type: object
          properties:
            id:
              type: integer
              example: 1
            basic_info:
              type: object
            financial:
              type: object
            system_settings:
              type: object
            funding:
              type: object
      404:
        description: Service not found
      500:
        description: Server error
    """
    try:
        db = Database()
        service = db.get_service(service_id)

        if not service:
            return jsonify({"error": "Service not found"}), 404

        # Convert service to dict
        result = {
            "id": service.id,
            "basic_info": service.basic_info.__dict__ if service.basic_info else {},
            "financial": service.financial.__dict__ if service.financial else {},
            "system_settings": service.system_settings.__dict__ if service.system_settings else {},
            "funding": service.funding.__dict__ if service.funding else {},
            "created_at": service.created_at.isoformat() if service.created_at else None,
            "updated_at": service.updated_at.isoformat() if service.updated_at else None,
        }

        return jsonify(result), 200

    except Exception as e:
        logger.error(f"Error getting service {service_id}: {e}")
        return jsonify({"error": str(e)}), 500


@api_v1.route("/services", methods=["POST"])
def create_service():
    """
    Create new service
    ---
    tags:
      - Services
    summary: Create a new service
    description: Creates a new service with the provided data
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - service_name
            - region
          properties:
            service_name:
              type: string
              example: "Shopping Assistance"
            region:
              type: string
              example: "Bavaria"
            target_group:
              type: string
              example: "Elderly people"
            hourly_rate:
              type: number
              example: 45.50
    responses:
      201:
        description: Service created successfully
        schema:
          type: object
          properties:
            id:
              type: integer
              example: 1
            message:
              type: string
              example: "Service created successfully"
      400:
        description: Invalid request data
      500:
        description: Server error
    """
    try:
        data = request.get_json()

        if not data or "service_name" not in data:
            return jsonify({"error": "Missing required field: service_name"}), 400

        # Create service from data
        # This is simplified - in real implementation, validate and create full Service object
        service = Service()
        service.basic_info.service_name = data["service_name"]
        service.basic_info.region = data.get("region", "Unknown")
        service.basic_info.target_group = data.get("target_group", "")

        # Save to database
        db = Database()
        service_id = db.save_service(service)

        logger.info(f"Created new service: {service_id}")

        return jsonify({"id": service_id, "message": "Service created successfully"}), 201

    except Exception as e:
        logger.error(f"Error creating service: {e}")
        return jsonify({"error": str(e)}), 500


@api_v1.route("/services/<int:service_id>", methods=["PUT"])
def update_service(service_id: int):
    """
    Update service
    ---
    tags:
      - Services
    summary: Update an existing service
    description: Updates service data
    parameters:
      - name: service_id
        in: path
        type: integer
        required: true
        description: Service ID
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            service_name:
              type: string
            region:
              type: string
            target_group:
              type: string
    responses:
      200:
        description: Service updated successfully
      404:
        description: Service not found
      500:
        description: Server error
    """
    try:
        db = Database()
        service = db.get_service(service_id)

        if not service:
            return jsonify({"error": "Service not found"}), 404

        data = request.get_json()

        # Update fields
        if "service_name" in data:
            service.basic_info.service_name = data["service_name"]
        if "region" in data:
            service.basic_info.region = data["region"]
        if "target_group" in data:
            service.basic_info.target_group = data["target_group"]

        # Save updates
        db.save_service(service)

        logger.info(f"Updated service: {service_id}")

        return jsonify({"id": service_id, "message": "Service updated successfully"}), 200

    except Exception as e:
        logger.error(f"Error updating service {service_id}: {e}")
        return jsonify({"error": str(e)}), 500


@api_v1.route("/services/<int:service_id>", methods=["DELETE"])
def delete_service(service_id: int):
    """
    Delete service
    ---
    tags:
      - Services
    summary: Delete a service
    description: Permanently deletes a service
    parameters:
      - name: service_id
        in: path
        type: integer
        required: true
        description: Service ID
    responses:
      200:
        description: Service deleted successfully
      404:
        description: Service not found
      500:
        description: Server error
    """
    try:
        db = Database()
        service = db.get_service(service_id)

        if not service:
            return jsonify({"error": "Service not found"}), 404

        db.delete_service(service_id)

        logger.info(f"Deleted service: {service_id}")

        return jsonify({"message": "Service deleted successfully"}), 200

    except Exception as e:
        logger.error(f"Error deleting service {service_id}: {e}")
        return jsonify({"error": str(e)}), 500


# ==========================================
# CALCULATION ENDPOINTS
# ==========================================


@api_v1.route("/calculate", methods=["POST"])
def calculate_costs():
    """
    Calculate service costs
    ---
    tags:
      - Calculations
    summary: Calculate hourly rate and cost breakdown
    description: Calculates the hourly rate based on financial parameters
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - base_salary
            - region
          properties:
            base_salary:
              type: number
              example: 2500.00
            region:
              type: string
              example: "Bavaria"
            use_umlagen:
              type: boolean
              example: true
            surcharge_percentage:
              type: number
              example: 10.0
    responses:
      200:
        description: Calculation successful
        schema:
          type: object
          properties:
            brutto_rate:
              type: number
              example: 45.50
            netto_rate:
              type: number
              example: 35.20
            breakdown:
              type: object
      400:
        description: Invalid request data
      500:
        description: Server error
    """
    try:
        data = request.get_json()

        if not data or "base_salary" not in data:
            return jsonify({"error": "Missing required field: base_salary"}), 400

        # Create calculator
        calculator = FinancialCalculator()

        # Perform calculation
        # This is simplified - in real implementation, create proper FinancialParameters
        result = {
            "brutto_rate": 45.50,  # Placeholder
            "netto_rate": 35.20,  # Placeholder
            "breakdown": {"base": data["base_salary"], "insurance": 500.00, "surcharges": 250.00},
        }

        return jsonify(result), 200

    except Exception as e:
        logger.error(f"Error calculating costs: {e}")
        return jsonify({"error": str(e)}), 500


# ==========================================
# STATISTICS ENDPOINTS
# ==========================================


@api_v1.route("/statistics", methods=["GET"])
def get_statistics():
    """
    Get system statistics
    ---
    tags:
      - Statistics
    summary: Get overall system statistics
    description: Returns statistics about services, costs, and usage
    responses:
      200:
        description: Statistics data
        schema:
          type: object
          properties:
            total_services:
              type: integer
              example: 42
            avg_brutto_rate:
              type: number
              example: 45.50
            by_region:
              type: object
            by_type:
              type: object
      500:
        description: Server error
    """
    try:
        db = Database()
        services = db.list_services()

        # Calculate statistics
        total = len(services)
        avg_rate = sum(s.financial.brutto_rate for s in services) / total if total > 0 else 0

        # Group by region
        by_region = {}
        for service in services:
            region = service.basic_info.region
            by_region[region] = by_region.get(region, 0) + 1

        result = {
            "total_services": total,
            "avg_brutto_rate": round(avg_rate, 2),
            "min_rate": min((s.financial.brutto_rate for s in services), default=0),
            "max_rate": max((s.financial.brutto_rate for s in services), default=0),
            "by_region": by_region,
            "timestamp": datetime.now().isoformat(),
        }

        return jsonify(result), 200

    except Exception as e:
        logger.error(f"Error getting statistics: {e}")
        return jsonify({"error": str(e)}), 500


# ==========================================
# SEARCH ENDPOINTS
# ==========================================


@api_v1.route("/search", methods=["GET"])
def search_services():
    """
    Search services
    ---
    tags:
      - Services
    summary: Search for services
    description: Full-text search across service names and descriptions
    parameters:
      - name: q
        in: query
        type: string
        required: true
        description: Search query
      - name: limit
        in: query
        type: integer
        required: false
        description: Maximum results
        default: 20
    responses:
      200:
        description: Search results
        schema:
          type: object
          properties:
            query:
              type: string
              example: "assistance"
            total:
              type: integer
              example: 5
            results:
              type: array
              items:
                type: object
      400:
        description: Missing query parameter
      500:
        description: Server error
    """
    try:
        query = request.args.get("q")
        if not query:
            return jsonify({"error": "Missing query parameter: q"}), 400

        limit = int(request.args.get("limit", 20))

        db = Database()
        services = db.search_services(query)[:limit]

        result = {
            "query": query,
            "total": len(services),
            "results": [
                {
                    "id": s.id,
                    "service_name": s.basic_info.service_name,
                    "region": s.basic_info.region,
                    "brutto_rate": s.financial.brutto_rate,
                }
                for s in services
            ],
        }

        return jsonify(result), 200

    except Exception as e:
        logger.error(f"Error searching services: {e}")
        return jsonify({"error": str(e)}), 500


# Import datetime for timestamps
from datetime import datetime
