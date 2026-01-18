"""
REST API for API Key Management.

This module provides REST API endpoints for managing API keys,
including creation, validation, rotation, revocation, and usage tracking.

Endpoints:
- POST /api/keys - Create new API key
- GET /api/keys - List API keys
- GET /api/keys/<key_id> - Get specific key details
- PUT /api/keys/<key_id> - Update API key
- DELETE /api/keys/<key_id> - Delete/revoke API key
- POST /api/keys/<key_id>/rotate - Rotate API key
- POST /api/keys/<key_id>/revoke - Revoke API key
- POST /api/keys/validate - Validate API key
- GET /api/keys/<key_id>/usage - Get key usage statistics
- GET /api/keys/statistics - Get overall statistics
- POST /api/keys/cleanup - Cleanup expired keys
- GET /api/keys/health - Health check

Author: DMS Team
Date: 2026-01-18
"""

from flask import Blueprint, request, jsonify
from typing import Dict, Any, List
import logging
from datetime import datetime

from src.gateway.api_keys import (
    APIKeyManager,
    APIKey,
    APIKeyStatus,
    APIKeyScope,
    APIKeyMetadata,
    get_api_key_manager,
    create_api_key,
    validate_api_key
)

logger = logging.getLogger(__name__)

# Create Blueprint
api_keys_bp = Blueprint('api_keys', __name__, url_prefix='/api/keys')

# Global manager
manager: APIKeyManager = None


def get_manager() -> APIKeyManager:
    """Get or create API key manager instance."""
    global manager
    if manager is None:
        manager = get_api_key_manager()
    return manager


# ==================== HELPER FUNCTIONS ====================

def api_key_to_dict(api_key: APIKey, include_sensitive: bool = False) -> Dict[str, Any]:
    """
    Convert APIKey object to dictionary.

    Args:
        api_key: APIKey object
        include_sensitive: Include sensitive data (key_hash)

    Returns:
        Dictionary representation
    """
    result = {
        'key_id': api_key.key_id,
        'prefix': api_key.prefix,
        'status': api_key.status.value,
        'scopes': [s.value for s in api_key.scopes],
        'metadata': {
            'name': api_key.metadata.name,
            'description': api_key.metadata.description,
            'owner_id': api_key.metadata.owner_id,
            'owner_email': api_key.metadata.owner_email,
            'ip_whitelist': api_key.metadata.ip_whitelist,
            'allowed_origins': api_key.metadata.allowed_origins,
            'tags': api_key.metadata.tags,
            'custom_data': api_key.metadata.custom_data
        },
        'usage': {
            'total_requests': api_key.usage.total_requests,
            'successful_requests': api_key.usage.successful_requests,
            'failed_requests': api_key.usage.failed_requests,
            'last_used_at': api_key.usage.last_used_at.isoformat() if api_key.usage.last_used_at else None,
            'last_ip': api_key.usage.last_ip,
            'last_endpoint': api_key.usage.last_endpoint
        },
        'created_at': api_key.created_at.isoformat(),
        'expires_at': api_key.expires_at.isoformat() if api_key.expires_at else None,
        'last_rotated_at': api_key.last_rotated_at.isoformat() if api_key.last_rotated_at else None,
        'revoked_at': api_key.revoked_at.isoformat() if api_key.revoked_at else None,
        'revoked_by': api_key.revoked_by,
        'revoked_reason': api_key.revoked_reason,
        'is_expired': api_key.is_expired(),
        'is_valid': api_key.is_valid()
    }

    if include_sensitive:
        result['key_hash'] = api_key.key_hash

    return result


def parse_scopes(scope_list: List[str]) -> set:
    """Parse scope strings to APIKeyScope enums."""
    try:
        return {APIKeyScope(s) for s in scope_list}
    except ValueError as e:
        raise ValueError(f"Invalid scope: {str(e)}")


# ==================== API KEY CRUD ENDPOINTS ====================

@api_keys_bp.route('', methods=['POST'])
def create_key():
    """
    Create new API key.

    Request JSON:
    {
        "name": "Production API Key",
        "owner_id": "user_123",
        "owner_email": "user@example.com",
        "scopes": ["read", "write"],
        "description": "Key for production use",
        "expires_in_days": 90,
        "ip_whitelist": ["192.168.1.1"],
        "allowed_origins": ["https://app.example.com"],
        "tags": ["production", "api"],
        "custom_data": {"department": "engineering"}
    }

    Returns:
        201: Key created successfully with plain key (only time it's shown!)
        400: Invalid request data
        500: Server error
    """
    try:
        data = request.get_json()

        # Validate required fields
        required_fields = ['name', 'owner_id', 'scopes']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400

        # Parse scopes
        try:
            scopes = parse_scopes(data['scopes'])
        except ValueError as e:
            return jsonify({'error': str(e)}), 400

        # Generate key
        manager = get_manager()
        plain_key, api_key = manager.generate_key(
            name=data['name'],
            owner_id=data['owner_id'],
            scopes=scopes,
            description=data.get('description'),
            expires_in_days=data.get('expires_in_days'),
            ip_whitelist=data.get('ip_whitelist'),
            metadata=data.get('custom_data')
        )

        # Update additional metadata
        if 'owner_email' in data:
            api_key.metadata.owner_email = data['owner_email']
        if 'allowed_origins' in data:
            api_key.metadata.allowed_origins = data['allowed_origins']
        if 'tags' in data:
            api_key.metadata.tags = data['tags']

        logger.info(f"API key created: {api_key.key_id} for owner {data['owner_id']}")

        return jsonify({
            'message': 'API key created successfully',
            'api_key': plain_key,  # Only shown once!
            'key_info': api_key_to_dict(api_key),
            'warning': 'Save this API key securely. It cannot be retrieved again.'
        }), 201

    except Exception as e:
        logger.error(f"Error creating API key: {str(e)}")
        return jsonify({'error': 'Internal server error', 'details': str(e)}), 500


@api_keys_bp.route('', methods=['GET'])
def list_keys():
    """
    List API keys.

    Query Parameters:
        owner_id: Filter by owner
        status: Filter by status (active/inactive/revoked/expired)
        include_expired: Include expired keys (default: false)
        limit: Maximum number of results (default: 100)
        offset: Offset for pagination (default: 0)

    Returns:
        200: List of API keys
    """
    try:
        manager = get_manager()

        # Get filters
        owner_id = request.args.get('owner_id')
        status_str = request.args.get('status')
        include_expired = request.args.get('include_expired', 'false').lower() == 'true'
        limit = int(request.args.get('limit', 100))
        offset = int(request.args.get('offset', 0))

        # Parse status
        status = None
        if status_str:
            try:
                status = APIKeyStatus(status_str.lower())
            except ValueError:
                return jsonify({'error': f'Invalid status: {status_str}'}), 400

        # Get keys
        keys = manager.list_keys(owner_id=owner_id, status=status)

        # Filter expired if needed
        if not include_expired:
            keys = [k for k in keys if not k.is_expired()]

        # Apply pagination
        total = len(keys)
        keys = keys[offset:offset + limit]

        return jsonify({
            'count': len(keys),
            'total': total,
            'offset': offset,
            'limit': limit,
            'keys': [api_key_to_dict(k) for k in keys]
        }), 200

    except Exception as e:
        logger.error(f"Error listing keys: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@api_keys_bp.route('/<key_id>', methods=['GET'])
def get_key(key_id: str):
    """
    Get specific API key details.

    Returns:
        200: Key details
        404: Key not found
    """
    try:
        manager = get_manager()
        api_key = manager.get_key(key_id)

        if not api_key:
            return jsonify({'error': 'API key not found'}), 404

        return jsonify(api_key_to_dict(api_key)), 200

    except Exception as e:
        logger.error(f"Error getting key: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@api_keys_bp.route('/<key_id>', methods=['PUT'])
def update_key(key_id: str):
    """
    Update API key.

    Request JSON:
    {
        "scopes": ["read", "write", "admin"],
        "description": "Updated description",
        "ip_whitelist": ["192.168.1.1", "192.168.1.2"],
        "tags": ["updated"]
    }

    Returns:
        200: Key updated successfully
        404: Key not found
        400: Invalid request
    """
    try:
        manager = get_manager()
        api_key = manager.get_key(key_id)

        if not api_key:
            return jsonify({'error': 'API key not found'}), 404

        data = request.get_json()

        # Update scopes
        if 'scopes' in data:
            try:
                scopes = parse_scopes(data['scopes'])
                manager.update_key_scopes(key_id, scopes)
            except ValueError as e:
                return jsonify({'error': str(e)}), 400

        # Update metadata
        if 'description' in data:
            api_key.metadata.description = data['description']
        if 'ip_whitelist' in data:
            api_key.metadata.ip_whitelist = data['ip_whitelist']
        if 'allowed_origins' in data:
            api_key.metadata.allowed_origins = data['allowed_origins']
        if 'tags' in data:
            api_key.metadata.tags = data['tags']
        if 'custom_data' in data:
            api_key.metadata.custom_data.update(data['custom_data'])

        logger.info(f"API key updated: {key_id}")

        return jsonify({
            'message': 'API key updated successfully',
            'key': api_key_to_dict(api_key)
        }), 200

    except Exception as e:
        logger.error(f"Error updating key: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@api_keys_bp.route('/<key_id>', methods=['DELETE'])
def delete_key(key_id: str):
    """
    Delete/revoke API key.

    Query Parameters:
        reason: Reason for deletion

    Returns:
        200: Key deleted successfully
        404: Key not found
    """
    try:
        manager = get_manager()
        reason = request.args.get('reason', 'Deleted via API')

        # Get authenticated user (would come from auth middleware)
        revoked_by = request.headers.get('X-User-ID', 'api_user')

        success = manager.revoke_key(key_id, revoked_by, reason)

        if not success:
            return jsonify({'error': 'API key not found'}), 404

        logger.info(f"API key deleted: {key_id} by {revoked_by}")

        return jsonify({
            'message': 'API key deleted successfully',
            'key_id': key_id
        }), 200

    except Exception as e:
        logger.error(f"Error deleting key: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


# ==================== KEY OPERATIONS ====================

@api_keys_bp.route('/<key_id>/rotate', methods=['POST'])
def rotate_key(key_id: str):
    """
    Rotate API key (generate new key with same permissions).

    Returns:
        200: New key generated
        404: Key not found
    """
    try:
        manager = get_manager()
        new_plain_key, new_api_key = manager.rotate_key(key_id)

        if not new_api_key:
            return jsonify({'error': 'API key not found'}), 404

        logger.info(f"API key rotated: {key_id} -> {new_api_key.key_id}")

        return jsonify({
            'message': 'API key rotated successfully',
            'new_api_key': new_plain_key,  # Only shown once!
            'new_key_info': api_key_to_dict(new_api_key),
            'old_key_id': key_id,
            'warning': 'Save the new API key securely. The old key has been revoked.'
        }), 200

    except Exception as e:
        logger.error(f"Error rotating key: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@api_keys_bp.route('/<key_id>/revoke', methods=['POST'])
def revoke_key_endpoint(key_id: str):
    """
    Revoke API key.

    Request JSON:
    {
        "reason": "Security incident"
    }

    Returns:
        200: Key revoked successfully
        404: Key not found
    """
    try:
        data = request.get_json() or {}
        reason = data.get('reason', 'Revoked via API')

        # Get authenticated user
        revoked_by = request.headers.get('X-User-ID', 'api_user')

        manager = get_manager()
        success = manager.revoke_key(key_id, revoked_by, reason)

        if not success:
            return jsonify({'error': 'API key not found'}), 404

        logger.info(f"API key revoked: {key_id} by {revoked_by}, reason: {reason}")

        return jsonify({
            'message': 'API key revoked successfully',
            'key_id': key_id,
            'revoked_at': datetime.utcnow().isoformat()
        }), 200

    except Exception as e:
        logger.error(f"Error revoking key: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@api_keys_bp.route('/validate', methods=['POST'])
def validate_key_endpoint():
    """
    Validate API key.

    Request JSON:
    {
        "api_key": "dms_xxxxx",
        "required_scope": "read",
        "ip": "192.168.1.1",
        "origin": "https://app.example.com"
    }

    Returns:
        200: Valid key
        401: Invalid key
    """
    try:
        data = request.get_json()

        if 'api_key' not in data:
            return jsonify({'error': 'Missing api_key'}), 400

        api_key = data['api_key']
        required_scope = data.get('required_scope')
        ip = data.get('ip') or request.remote_addr
        origin = data.get('origin')

        # Validate
        valid, key_obj, error = validate_api_key(
            api_key,
            required_scope=required_scope,
            ip=ip,
            origin=origin
        )

        if not valid:
            return jsonify({
                'valid': False,
                'error': error
            }), 401

        # Record usage
        if key_obj:
            manager = get_manager()
            manager.record_usage(key_obj.key_id, success=True)

        return jsonify({
            'valid': True,
            'key_id': key_obj.key_id if key_obj else None,
            'scopes': [s.value for s in key_obj.scopes] if key_obj else [],
            'owner_id': key_obj.metadata.owner_id if key_obj else None
        }), 200

    except Exception as e:
        logger.error(f"Error validating key: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


# ==================== USAGE & STATISTICS ====================

@api_keys_bp.route('/<key_id>/usage', methods=['GET'])
def get_key_usage(key_id: str):
    """
    Get API key usage statistics.

    Returns:
        200: Usage statistics
        404: Key not found
    """
    try:
        manager = get_manager()
        api_key = manager.get_key(key_id)

        if not api_key:
            return jsonify({'error': 'API key not found'}), 404

        return jsonify({
            'key_id': key_id,
            'usage': {
                'total_requests': api_key.usage.total_requests,
                'successful_requests': api_key.usage.successful_requests,
                'failed_requests': api_key.usage.failed_requests,
                'success_rate': (api_key.usage.successful_requests / api_key.usage.total_requests * 100)
                if api_key.usage.total_requests > 0 else 0,
                'last_used_at': api_key.usage.last_used_at.isoformat() if api_key.usage.last_used_at else None,
                'last_ip': api_key.usage.last_ip,
                'last_endpoint': api_key.usage.last_endpoint
            },
            'created_at': api_key.created_at.isoformat(),
            'days_active': (datetime.utcnow() - api_key.created_at).days
        }), 200

    except Exception as e:
        logger.error(f"Error getting usage: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@api_keys_bp.route('/statistics', methods=['GET'])
def get_statistics():
    """
    Get overall API key statistics.

    Returns:
        200: Statistics
    """
    try:
        manager = get_manager()
        all_keys = list(manager.keys.values())

        # Calculate statistics
        total = len(all_keys)
        active = len([k for k in all_keys if k.status == APIKeyStatus.ACTIVE])
        revoked = len([k for k in all_keys if k.status == APIKeyStatus.REVOKED])
        expired = len([k for k in all_keys if k.is_expired()])

        total_requests = sum(k.usage.total_requests for k in all_keys)
        successful_requests = sum(k.usage.successful_requests for k in all_keys)

        # Group by owner
        by_owner = {}
        for key in all_keys:
            owner = key.metadata.owner_id
            if owner not in by_owner:
                by_owner[owner] = 0
            by_owner[owner] += 1

        return jsonify({
            'total_keys': total,
            'active_keys': active,
            'revoked_keys': revoked,
            'expired_keys': expired,
            'total_requests': total_requests,
            'successful_requests': successful_requests,
            'success_rate': (successful_requests / total_requests * 100) if total_requests > 0 else 0,
            'keys_by_owner': by_owner,
            'keys_by_status': {
                'active': active,
                'revoked': revoked,
                'expired': expired,
                'inactive': total - active - revoked - expired
            }
        }), 200

    except Exception as e:
        logger.error(f"Error getting statistics: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


# ==================== UTILITY ENDPOINTS ====================

@api_keys_bp.route('/cleanup', methods=['POST'])
def cleanup_expired():
    """
    Cleanup expired API keys.

    Returns:
        200: Cleanup completed
    """
    try:
        manager = get_manager()

        # Count before
        before = len([k for k in manager.keys.values() if k.status == APIKeyStatus.EXPIRED])

        # Cleanup
        manager.cleanup_expired_keys()

        # Count after
        after = len([k for k in manager.keys.values() if k.status == APIKeyStatus.EXPIRED])

        marked = after - before

        logger.info(f"Expired keys cleanup: {marked} keys marked as expired")

        return jsonify({
            'message': 'Cleanup completed',
            'keys_marked_expired': marked,
            'total_expired': after
        }), 200

    except Exception as e:
        logger.error(f"Error during cleanup: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@api_keys_bp.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint.

    Returns:
        200: Service is healthy
    """
    try:
        manager = get_manager()
        total_keys = len(manager.keys)
        active_keys = len([k for k in manager.keys.values() if k.is_valid()])

        return jsonify({
            'status': 'healthy',
            'total_keys': total_keys,
            'active_keys': active_keys,
            'timestamp': datetime.utcnow().isoformat()
        }), 200

    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500


# ==================== ERROR HANDLERS ====================

@api_keys_bp.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({'error': 'Endpoint not found'}), 404


@api_keys_bp.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    logger.error(f"Internal server error: {str(error)}")
    return jsonify({'error': 'Internal server error'}), 500


# ==================== EXAMPLE USAGE ====================

if __name__ == "__main__":
    from flask import Flask

    app = Flask(__name__)
    app.register_blueprint(api_keys_bp)

    print("API Keys Management API server starting...")
    print("Available endpoints:")
    print("  POST   /api/keys - Create API key")
    print("  GET    /api/keys - List keys")
    print("  GET    /api/keys/<key_id> - Get key")
    print("  PUT    /api/keys/<key_id> - Update key")
    print("  DELETE /api/keys/<key_id> - Delete key")
    print("  POST   /api/keys/<key_id>/rotate - Rotate key")
    print("  POST   /api/keys/<key_id>/revoke - Revoke key")
    print("  POST   /api/keys/validate - Validate key")
    print("  GET    /api/keys/<key_id>/usage - Get usage")
    print("  GET    /api/keys/statistics - Get statistics")
    print("  POST   /api/keys/cleanup - Cleanup expired")
    print("  GET    /api/keys/health - Health check")

    app.run(host='0.0.0.0', port=5003, debug=True)
