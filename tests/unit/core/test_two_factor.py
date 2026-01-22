"""
Unit tests for two_factor (2FA/TOTP authentication) module
"""

import hashlib
import os
import sqlite3
import tempfile
from unittest.mock import MagicMock, Mock, patch

import pytest

# Check if dependencies are available
try:
    import pyotp
    import qrcode
    from src.core.two_factor import TwoFactorAuth, get_two_factor_auth, require_2fa

    DEPENDENCIES_AVAILABLE = True
except ImportError:
    DEPENDENCIES_AVAILABLE = False
    TwoFactorAuth = None
    get_two_factor_auth = None
    require_2fa = None

pytestmark = pytest.mark.skipif(not DEPENDENCIES_AVAILABLE, reason="pyotp/qrcode not available")


# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def temp_db():
    """Create temporary database"""
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    yield path
    if os.path.exists(path):
        os.unlink(path)


@pytest.fixture
def two_factor(temp_db):
    """Create TwoFactorAuth instance"""
    return TwoFactorAuth(db_path=temp_db)


# ============================================================================
# TwoFactorAuth Initialization Tests
# ============================================================================


class TestTwoFactorAuthInit:
    """Test TwoFactorAuth initialization"""

    def test_init_creates_database(self, temp_db):
        """Test initialization creates database tables"""
        two_factor = TwoFactorAuth(db_path=temp_db)

        # Verify tables exist
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()

        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]

        assert "two_factor_secrets" in tables
        assert "backup_codes" in tables

        conn.close()

    def test_init_with_existing_database(self, temp_db):
        """Test initialization with existing database"""
        # Create first instance
        two_factor1 = TwoFactorAuth(db_path=temp_db)

        # Create second instance (should not fail)
        two_factor2 = TwoFactorAuth(db_path=temp_db)

        assert two_factor2 is not None


# ============================================================================
# Secret Generation Tests
# ============================================================================


class TestSecretGeneration:
    """Test 2FA secret generation"""

    def test_generate_secret(self, two_factor):
        """Test generating new secret"""
        secret = two_factor.generate_secret(user_id=1, username="testuser")

        assert secret is not None
        assert isinstance(secret, str)
        assert len(secret) > 0

    def test_generate_secret_is_base32(self, two_factor):
        """Test secret is valid base32"""
        secret = two_factor.generate_secret(user_id=1, username="testuser")

        # Base32 should only contain A-Z and 2-7
        assert all(c in "ABCDEFGHIJKLMNOPQRSTUVWXYZ234567" for c in secret)

    def test_generate_secret_stores_in_database(self, two_factor):
        """Test secret is stored in database"""
        secret = two_factor.generate_secret(user_id=1, username="testuser")

        # Retrieve from database
        retrieved_secret = two_factor.get_secret(user_id=1)

        assert retrieved_secret == secret

    def test_generate_secret_not_enabled_initially(self, two_factor):
        """Test secret is not enabled initially"""
        two_factor.generate_secret(user_id=1, username="testuser")

        # Should not be enabled
        assert two_factor.is_enabled(user_id=1) is False

    def test_generate_secret_replaces_existing(self, two_factor):
        """Test generating new secret replaces existing"""
        secret1 = two_factor.generate_secret(user_id=1, username="testuser")
        secret2 = two_factor.generate_secret(user_id=1, username="testuser")

        assert secret1 != secret2
        assert two_factor.get_secret(user_id=1) == secret2


# ============================================================================
# Provisioning URI Tests
# ============================================================================


class TestProvisioningURI:
    """Test provisioning URI generation"""

    def test_get_provisioning_uri(self, two_factor):
        """Test getting provisioning URI"""
        secret = two_factor.generate_secret(user_id=1, username="testuser")

        uri = two_factor.get_provisioning_uri(user_id=1, username="testuser")

        assert uri is not None
        assert "otpauth://totp/" in uri
        assert "testuser" in uri

    def test_provisioning_uri_includes_issuer(self, two_factor):
        """Test provisioning URI includes issuer"""
        two_factor.generate_secret(user_id=1, username="testuser")

        uri = two_factor.get_provisioning_uri(user_id=1, username="testuser", issuer="DMS")

        assert "DMS" in uri

    def test_provisioning_uri_generates_secret_if_missing(self, two_factor):
        """Test provisioning URI generates secret if not exists"""
        uri = two_factor.get_provisioning_uri(user_id=1, username="testuser")

        assert uri is not None
        assert two_factor.get_secret(user_id=1) is not None


# ============================================================================
# QR Code Generation Tests
# ============================================================================


class TestQRCodeGeneration:
    """Test QR code generation"""

    def test_generate_qr_code(self, two_factor):
        """Test generating QR code"""
        qr_code = two_factor.generate_qr_code(user_id=1, username="testuser")

        assert qr_code is not None
        assert isinstance(qr_code, str)
        assert "data:image/png;base64," in qr_code

    def test_qr_code_is_base64(self, two_factor):
        """Test QR code is base64 encoded"""
        qr_code = two_factor.generate_qr_code(user_id=1, username="testuser")

        # Remove data URL prefix
        base64_part = qr_code.split(",")[1]

        # Should be valid base64
        import base64

        try:
            base64.b64decode(base64_part)
            valid = True
        except Exception:
            valid = False

        assert valid is True


# ============================================================================
# Token Verification Tests
# ============================================================================


class TestTokenVerification:
    """Test TOTP token verification"""

    def test_verify_valid_token(self, two_factor):
        """Test verifying valid token"""
        secret = two_factor.generate_secret(user_id=1, username="testuser")

        # Generate current token
        totp = pyotp.TOTP(secret)
        token = totp.now()

        # Verify
        assert two_factor.verify_token(user_id=1, token=token) is True

    def test_verify_invalid_token(self, two_factor):
        """Test verifying invalid token"""
        two_factor.generate_secret(user_id=1, username="testuser")

        # Use obviously wrong token
        assert two_factor.verify_token(user_id=1, token="000000") is False

    def test_verify_token_no_secret(self, two_factor):
        """Test verifying token with no secret"""
        # No secret generated
        assert two_factor.verify_token(user_id=999, token="123456") is False

    def test_verify_token_with_window(self, two_factor):
        """Test token verification with time window"""
        secret = two_factor.generate_secret(user_id=1, username="testuser")

        totp = pyotp.TOTP(secret)

        # Current token should work
        current_token = totp.now()
        assert two_factor.verify_token(user_id=1, token=current_token) is True


# ============================================================================
# Enable/Disable 2FA Tests
# ============================================================================


class TestEnableDisable2FA:
    """Test enabling and disabling 2FA"""

    def test_enable_2fa_with_valid_token(self, two_factor):
        """Test enabling 2FA with valid token"""
        secret = two_factor.generate_secret(user_id=1, username="testuser")

        # Generate valid token
        totp = pyotp.TOTP(secret)
        token = totp.now()

        # Enable
        result = two_factor.enable_2fa(user_id=1, verification_token=token)

        assert result is True
        assert two_factor.is_enabled(user_id=1) is True

    def test_enable_2fa_with_invalid_token(self, two_factor):
        """Test enabling 2FA with invalid token"""
        two_factor.generate_secret(user_id=1, username="testuser")

        # Try to enable with wrong token
        result = two_factor.enable_2fa(user_id=1, verification_token="000000")

        assert result is False
        assert two_factor.is_enabled(user_id=1) is False

    def test_disable_2fa(self, two_factor):
        """Test disabling 2FA"""
        # Enable 2FA
        secret = two_factor.generate_secret(user_id=1, username="testuser")
        totp = pyotp.TOTP(secret)
        two_factor.enable_2fa(user_id=1, verification_token=totp.now())

        # Disable
        two_factor.disable_2fa(user_id=1)

        assert two_factor.is_enabled(user_id=1) is False
        assert two_factor.get_secret(user_id=1) is None

    def test_is_enabled_for_new_user(self, two_factor):
        """Test is_enabled returns False for new user"""
        assert two_factor.is_enabled(user_id=999) is False


# ============================================================================
# Backup Codes Tests
# ============================================================================


class TestBackupCodes:
    """Test backup code generation and verification"""

    def test_generate_backup_codes(self, two_factor):
        """Test generating backup codes"""
        codes = two_factor.generate_backup_codes(user_id=1, count=10)

        assert len(codes) == 10
        assert all(isinstance(code, str) for code in codes)

    def test_backup_codes_are_unique(self, two_factor):
        """Test backup codes are unique"""
        codes = two_factor.generate_backup_codes(user_id=1, count=10)

        # All codes should be unique
        assert len(set(codes)) == 10

    def test_backup_codes_format(self, two_factor):
        """Test backup code format"""
        codes = two_factor.generate_backup_codes(user_id=1, count=5)

        for code in codes:
            # Should be 8 characters (4 bytes hex = 8 chars)
            assert len(code) == 8
            # Should be hex (uppercase)
            assert all(c in "0123456789ABCDEF" for c in code)

    def test_verify_valid_backup_code(self, two_factor):
        """Test verifying valid backup code"""
        codes = two_factor.generate_backup_codes(user_id=1, count=5)

        # Use first code
        result = two_factor.verify_backup_code(user_id=1, code=codes[0])

        assert result is True

    def test_verify_invalid_backup_code(self, two_factor):
        """Test verifying invalid backup code"""
        two_factor.generate_backup_codes(user_id=1, count=5)

        # Try invalid code
        result = two_factor.verify_backup_code(user_id=1, code="INVALID1")

        assert result is False

    def test_backup_code_single_use(self, two_factor):
        """Test backup code can only be used once"""
        codes = two_factor.generate_backup_codes(user_id=1, count=5)

        # Use code first time
        assert two_factor.verify_backup_code(user_id=1, code=codes[0]) is True

        # Try to use same code again
        assert two_factor.verify_backup_code(user_id=1, code=codes[0]) is False

    def test_get_remaining_backup_codes(self, two_factor):
        """Test getting remaining backup code count"""
        codes = two_factor.generate_backup_codes(user_id=1, count=10)

        # Initially all codes available
        assert two_factor.get_remaining_backup_codes(user_id=1) == 10

        # Use one code
        two_factor.verify_backup_code(user_id=1, code=codes[0])

        # Should have 9 remaining
        assert two_factor.get_remaining_backup_codes(user_id=1) == 9

    def test_generate_backup_codes_replaces_existing(self, two_factor):
        """Test generating new codes replaces existing"""
        codes1 = two_factor.generate_backup_codes(user_id=1, count=5)

        # Use one code
        two_factor.verify_backup_code(user_id=1, code=codes1[0])

        # Generate new codes
        codes2 = two_factor.generate_backup_codes(user_id=1, count=5)

        # Old codes should not work
        assert two_factor.verify_backup_code(user_id=1, code=codes1[1]) is False

        # New codes should work
        assert two_factor.verify_backup_code(user_id=1, code=codes2[0]) is True

    def test_disable_2fa_removes_backup_codes(self, two_factor):
        """Test disabling 2FA removes backup codes"""
        # Generate secret and backup codes
        two_factor.generate_secret(user_id=1, username="testuser")
        two_factor.generate_backup_codes(user_id=1, count=5)

        # Disable 2FA
        two_factor.disable_2fa(user_id=1)

        # Backup codes should be removed
        assert two_factor.get_remaining_backup_codes(user_id=1) == 0


# ============================================================================
# Helper Function Tests
# ============================================================================


class TestHelperFunctions:
    """Test helper functions"""

    @pytest.fixture(autouse=True)
    def reset_global(self):
        """Reset global instance"""
        from src.core import two_factor

        two_factor._two_factor_auth = None
        yield
        two_factor._two_factor_auth = None

    def test_get_two_factor_auth_creates_instance(self):
        """Test get_two_factor_auth creates instance"""
        instance = get_two_factor_auth()

        assert instance is not None
        assert isinstance(instance, TwoFactorAuth)

    def test_get_two_factor_auth_returns_singleton(self):
        """Test get_two_factor_auth returns same instance"""
        instance1 = get_two_factor_auth()
        instance2 = get_two_factor_auth()

        assert instance1 is instance2


# ============================================================================
# Integration Tests
# ============================================================================


class TestTwoFactorIntegration:
    """Test two-factor authentication integration scenarios"""

    def test_full_2fa_setup_workflow(self, two_factor):
        """Test complete 2FA setup workflow"""
        # Step 1: Generate secret
        secret = two_factor.generate_secret(user_id=1, username="testuser")
        assert secret is not None

        # Step 2: Get QR code for user
        qr_code = two_factor.generate_qr_code(user_id=1, username="testuser")
        assert "data:image/png;base64," in qr_code

        # Step 3: User verifies with authenticator app
        totp = pyotp.TOTP(secret)
        token = totp.now()

        # Step 4: Enable 2FA
        enabled = two_factor.enable_2fa(user_id=1, verification_token=token)
        assert enabled is True

        # Step 5: Generate backup codes
        backup_codes = two_factor.generate_backup_codes(user_id=1, count=10)
        assert len(backup_codes) == 10

        # Step 6: Verify 2FA is enabled
        assert two_factor.is_enabled(user_id=1) is True

    def test_full_2fa_login_workflow(self, two_factor):
        """Test complete 2FA login workflow"""
        # Setup 2FA
        secret = two_factor.generate_secret(user_id=1, username="testuser")
        totp = pyotp.TOTP(secret)
        two_factor.enable_2fa(user_id=1, verification_token=totp.now())

        # User logs in and needs to verify 2FA
        current_token = totp.now()
        assert two_factor.verify_token(user_id=1, token=current_token) is True

    def test_backup_code_recovery_workflow(self, two_factor):
        """Test account recovery using backup code"""
        # Setup 2FA
        secret = two_factor.generate_secret(user_id=1, username="testuser")
        totp = pyotp.TOTP(secret)
        two_factor.enable_2fa(user_id=1, verification_token=totp.now())

        # Generate backup codes
        backup_codes = two_factor.generate_backup_codes(user_id=1, count=10)

        # User lost authenticator, uses backup code
        assert two_factor.verify_backup_code(user_id=1, code=backup_codes[0]) is True

        # Backup code consumed
        assert two_factor.get_remaining_backup_codes(user_id=1) == 9

    def test_multiple_users_isolation(self, two_factor):
        """Test multiple users have isolated 2FA"""
        # Setup 2FA for user 1
        secret1 = two_factor.generate_secret(user_id=1, username="user1")
        totp1 = pyotp.TOTP(secret1)
        two_factor.enable_2fa(user_id=1, verification_token=totp1.now())

        # Setup 2FA for user 2
        secret2 = two_factor.generate_secret(user_id=2, username="user2")
        totp2 = pyotp.TOTP(secret2)
        two_factor.enable_2fa(user_id=2, verification_token=totp2.now())

        # Secrets should be different
        assert secret1 != secret2

        # Tokens should be independent
        token1 = totp1.now()
        assert two_factor.verify_token(user_id=1, token=token1) is True
        assert two_factor.verify_token(user_id=2, token=token1) is False

    def test_disable_and_re_enable_workflow(self, two_factor):
        """Test disabling and re-enabling 2FA"""
        # Setup and enable 2FA
        secret1 = two_factor.generate_secret(user_id=1, username="testuser")
        totp = pyotp.TOTP(secret1)
        two_factor.enable_2fa(user_id=1, verification_token=totp.now())

        # Disable
        two_factor.disable_2fa(user_id=1)
        assert two_factor.is_enabled(user_id=1) is False

        # Re-enable with new secret
        secret2 = two_factor.generate_secret(user_id=1, username="testuser")
        assert secret1 != secret2  # New secret generated

        totp2 = pyotp.TOTP(secret2)
        two_factor.enable_2fa(user_id=1, verification_token=totp2.now())

        assert two_factor.is_enabled(user_id=1) is True
