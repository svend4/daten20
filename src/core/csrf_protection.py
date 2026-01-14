"""
CSRF Protection Module

Implements Cross-Site Request Forgery (CSRF) protection for Flask applications.
Uses token-based validation to prevent CSRF attacks.
"""

import secrets
import hmac
import hashlib
import logging
from typing import Optional, Callable
from functools import wraps
from flask import session, request, abort, current_app
from datetime import datetime, timedelta

logger = logging.getLogger('dms.csrf')


class CSRFProtection:
    """
    CSRF protection manager.

    Generates and validates CSRF tokens for form submissions.
    """

    def __init__(self, app=None, secret_key: Optional[str] = None):
        """
        Initialize CSRF protection.

        Args:
            app: Flask application (optional)
            secret_key: Secret key for token generation
        """
        self.secret_key = secret_key
        self.token_key = '_csrf_token'
        self.header_name = 'X-CSRF-Token'
        self.exempt_methods = {'GET', 'HEAD', 'OPTIONS', 'TRACE'}
        self.exempt_views = set()

        if app:
            self.init_app(app)

    def init_app(self, app):
        """
        Initialize CSRF protection for Flask app.

        Args:
            app: Flask application
        """
        # Set secret key
        if not self.secret_key:
            self.secret_key = app.config.get('SECRET_KEY')

        if not self.secret_key:
            raise ValueError("SECRET_KEY required for CSRF protection")

        # Configure
        app.config.setdefault('CSRF_ENABLED', True)
        app.config.setdefault('CSRF_TIME_LIMIT', 3600)  # 1 hour

        # Add to app extensions
        if not hasattr(app, 'extensions'):
            app.extensions = {}
        app.extensions['csrf'] = self

        # Register protection
        @app.before_request
        def csrf_protect():
            """Protect against CSRF attacks."""
            if not app.config.get('CSRF_ENABLED'):
                return

            # Skip exempt methods
            if request.method in self.exempt_methods:
                return

            # Skip exempt views
            if request.endpoint in self.exempt_views:
                return

            # Validate token
            if not self.validate_token():
                logger.warning(
                    f"CSRF validation failed for {request.method} {request.path} "
                    f"from {request.remote_addr}"
                )
                abort(403, description="CSRF validation failed")

        # Add token to Jinja2 context
        @app.context_processor
        def csrf_token():
            """Make CSRF token available in templates."""
            return {
                'csrf_token': self.generate_token,
                'csrf_input': self.generate_input
            }

        logger.info("CSRF protection initialized")

    def generate_token(self) -> str:
        """
        Generate CSRF token for current session.

        Returns:
            CSRF token string
        """
        # Get or create session token
        if self.token_key not in session:
            session[self.token_key] = secrets.token_hex(32)

        session_token = session[self.token_key]

        # Create HMAC signature
        timestamp = str(int(datetime.now().timestamp()))
        message = f"{session_token}:{timestamp}"
        signature = hmac.new(
            self.secret_key.encode(),
            message.encode(),
            hashlib.sha256
        ).hexdigest()

        # Combine into token
        token = f"{timestamp}.{signature}"
        return token

    def generate_input(self) -> str:
        """
        Generate HTML input field with CSRF token.

        Returns:
            HTML input tag
        """
        token = self.generate_token()
        return f'<input type="hidden" name="{self.token_key}" value="{token}">'

    def validate_token(self, token: Optional[str] = None) -> bool:
        """
        Validate CSRF token.

        Args:
            token: Token to validate (from form or header)

        Returns:
            True if valid, False otherwise
        """
        # Get session token
        session_token = session.get(self.token_key)
        if not session_token:
            logger.debug("No session token found")
            return False

        # Get request token
        if token is None:
            # Try form data
            token = request.form.get(self.token_key)

            # Try headers
            if not token:
                token = request.headers.get(self.header_name)

            # Try JSON
            if not token and request.is_json:
                token = request.json.get(self.token_key)

        if not token:
            logger.debug("No CSRF token in request")
            return False

        # Parse token
        try:
            timestamp_str, signature = token.split('.', 1)
            timestamp = int(timestamp_str)
        except (ValueError, AttributeError):
            logger.debug("Invalid token format")
            return False

        # Check expiration
        token_age = datetime.now().timestamp() - timestamp
        max_age = current_app.config.get('CSRF_TIME_LIMIT', 3600)

        if token_age > max_age:
            logger.debug(f"Token expired (age: {token_age}s)")
            return False

        # Verify signature
        message = f"{session_token}:{timestamp_str}"
        expected_signature = hmac.new(
            self.secret_key.encode(),
            message.encode(),
            hashlib.sha256
        ).hexdigest()

        if not hmac.compare_digest(signature, expected_signature):
            logger.debug("Invalid token signature")
            return False

        return True

    def exempt(self, view: Callable) -> Callable:
        """
        Decorator to exempt view from CSRF protection.

        Args:
            view: View function to exempt

        Returns:
            Decorated view function
        """
        @wraps(view)
        def wrapped(*args, **kwargs):
            return view(*args, **kwargs)

        # Mark as exempt
        self.exempt_views.add(view.__name__)
        return wrapped


# Global instance
csrf = CSRFProtection()


def csrf_exempt(view: Callable) -> Callable:
    """
    Decorator to exempt view from CSRF protection.

    Usage:
        @app.route('/api/webhook', methods=['POST'])
        @csrf_exempt
        def webhook():
            return jsonify({'status': 'ok'})

    Args:
        view: View function

    Returns:
        Decorated view
    """
    return csrf.exempt(view)


def csrf_protect(view: Callable) -> Callable:
    """
    Decorator to explicitly protect view with CSRF validation.

    Useful for API endpoints that need CSRF protection.

    Usage:
        @app.route('/api/sensitive', methods=['POST'])
        @csrf_protect
        def sensitive_api():
            return jsonify({'status': 'ok'})

    Args:
        view: View function

    Returns:
        Decorated view
    """
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not csrf.validate_token():
            logger.warning(
                f"CSRF validation failed for {request.method} {request.path} "
                f"from {request.remote_addr}"
            )
            abort(403, description="CSRF validation failed")
        return view(*args, **kwargs)

    return wrapped


# Flask-WTF compatibility
class FlaskWTFCompat:
    """
    Compatibility layer for Flask-WTF forms.

    Provides csrf_token() method for WTForms integration.
    """

    @staticmethod
    def csrf_token():
        """Generate CSRF token for forms."""
        return csrf.generate_token()


# Example usage
if __name__ == '__main__':
    from flask import Flask, render_template_string

    # Create app
    app = Flask(__name__)
    app.secret_key = 'test-secret-key-change-in-production'

    # Initialize CSRF protection
    csrf.init_app(app)

    # Template with CSRF token
    FORM_TEMPLATE = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>CSRF Protection Demo</title>
    </head>
    <body>
        <h1>CSRF Protection Demo</h1>

        <h2>Method 1: Using csrf_input() helper</h2>
        <form method="POST" action="/submit">
            {{ csrf_input() | safe }}
            <input type="text" name="data" placeholder="Enter data">
            <button type="submit">Submit</button>
        </form>

        <h2>Method 2: Manual token in hidden field</h2>
        <form method="POST" action="/submit">
            <input type="hidden" name="_csrf_token" value="{{ csrf_token() }}">
            <input type="text" name="data" placeholder="Enter data">
            <button type="submit">Submit</button>
        </form>

        <h2>Method 3: AJAX with header</h2>
        <button onclick="sendAjax()">Send AJAX Request</button>

        <script>
        function sendAjax() {
            fetch('/submit', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRF-Token': '{{ csrf_token() }}'
                },
                body: JSON.stringify({data: 'test'})
            })
            .then(r => r.json())
            .then(data => alert('Success: ' + JSON.stringify(data)))
            .catch(err => alert('Error: ' + err));
        }
        </script>

        <h2>Test: Form without CSRF token (will fail)</h2>
        <form method="POST" action="/submit">
            <input type="text" name="data" placeholder="Enter data">
            <button type="submit">Submit (No Token)</button>
        </form>
    </body>
    </html>
    '''

    @app.route('/')
    def index():
        """Show demo form."""
        return render_template_string(FORM_TEMPLATE)

    @app.route('/submit', methods=['POST'])
    def submit():
        """Handle form submission."""
        from flask import jsonify
        data = request.form.get('data') or request.json.get('data')
        return jsonify({'status': 'success', 'data': data})

    @app.route('/api/public', methods=['POST'])
    @csrf_exempt
    def public_api():
        """Public API endpoint (CSRF exempt)."""
        from flask import jsonify
        return jsonify({'status': 'ok', 'message': 'No CSRF required'})

    # Run app
    print("\n" + "="*60)
    print("CSRF Protection Demo")
    print("="*60)
    print("\nVisit: http://localhost:5000")
    print("\nTry submitting forms with and without CSRF tokens")
    print("="*60 + "\n")

    app.run(debug=True, port=5000)
