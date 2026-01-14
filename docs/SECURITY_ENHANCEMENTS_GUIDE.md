# Security Enhancements Guide

Comprehensive guide to security features implemented in Phase 2.

## 🔐 Overview

This guide covers the security enhancements added in Phase 2 of the gap fixing plan:

1. **HTTPS/TLS Configuration** - Secure communications
2. **CSRF Protection** - Cross-Site Request Forgery prevention
3. **API Key Authentication** - REST API security
4. **Backup Encryption** - Secure backup storage

---

## 1. HTTPS/TLS Configuration

### Overview

The HTTPS configuration module (`src/core/https_config.py`) provides secure HTTPS/TLS support for production deployments.

### Features

- **TLS 1.2/1.3** - Modern TLS versions only
- **Strong Cipher Suites** - ECDHE, AES-GCM, ChaCha20
- **Security Headers** - HSTS, CSP, X-Frame-Options, etc.
- **Self-Signed Certificates** - For development
- **Certificate Management** - Expiry checking

### Usage

#### Development (Self-Signed Certificate)

```python
from src.core.https_config import HTTPSConfig, run_https_server
from src.web_app import app

# Generate self-signed certificate for development
https_config = HTTPSConfig()
cert, key = https_config.generate_self_signed_cert()

# Run HTTPS server
run_https_server(app, host='0.0.0.0', port=5443)
```

#### Production (Real Certificate)

```bash
# Set environment variables
export SSL_CERT_PATH=/path/to/cert.pem
export SSL_KEY_PATH=/path/to/key.pem
export FLASK_ENV=production

# Run application
python -m src.web_app
```

#### Security Headers

All HTTPS responses include:

- `Strict-Transport-Security`: Force HTTPS for 1 year
- `Content-Security-Policy`: Restrict resource loading
- `X-Content-Type-Options`: Prevent MIME sniffing
- `X-Frame-Options`: Prevent clickjacking
- `X-XSS-Protection`: Enable XSS filtering
- `Referrer-Policy`: Control referrer information
- `Permissions-Policy`: Restrict browser features

### Certificate Generation

```python
from src.core.https_config import HTTPSConfig

config = HTTPSConfig()

# Generate for localhost
cert, key = config.generate_self_signed_cert(
    days_valid=365,
    common_name='localhost'
)

# Check certificate expiry
days_left = config.check_certificate_expiry()
print(f"Certificate expires in {days_left} days")
```

---

## 2. CSRF Protection

### Overview

CSRF protection module (`src/core/csrf_protection.py`) prevents Cross-Site Request Forgery attacks using token-based validation.

### Features

- **Token Generation** - Cryptographically secure tokens
- **HMAC Signatures** - Token integrity verification
- **Time-Limited** - Tokens expire after 1 hour
- **Auto-Integration** - Automatic Flask integration
- **Template Helpers** - Easy token insertion

### Usage

#### Initialize CSRF Protection

```python
from flask import Flask
from src.core.csrf_protection import csrf

app = Flask(__name__)
app.secret_key = 'your-secret-key'

# Initialize CSRF protection
csrf.init_app(app)
```

#### In HTML Templates

Method 1: Using helper function
```html
<form method="POST" action="/submit">
    {{ csrf_input() | safe }}
    <input type="text" name="data">
    <button type="submit">Submit</button>
</form>
```

Method 2: Manual token
```html
<form method="POST" action="/submit">
    <input type="hidden" name="_csrf_token" value="{{ csrf_token() }}">
    <input type="text" name="data">
    <button type="submit">Submit</button>
</form>
```

Method 3: AJAX with header
```javascript
fetch('/api/endpoint', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'X-CSRF-Token': '{{ csrf_token() }}'
    },
    body: JSON.stringify({data: 'value'})
});
```

#### Exempt API Endpoints

```python
from src.core.csrf_protection import csrf_exempt

@app.route('/api/webhook', methods=['POST'])
@csrf_exempt
def webhook():
    """Public webhook (CSRF exempt)"""
    return jsonify({'status': 'ok'})
```

#### Configuration

```python
app.config['CSRF_ENABLED'] = True          # Enable/disable CSRF
app.config['CSRF_TIME_LIMIT'] = 3600       # Token lifetime (seconds)
```

---

## 3. API Key Authentication

### Overview

API authentication module (`src/core/api_auth.py`) provides API key-based authentication for REST API endpoints.

### Features

- **Secure Key Generation** - 256-bit random keys
- **SHA-256 Hashing** - Keys stored as hashes
- **Expiration Support** - Optional key expiration
- **Permissions** - Fine-grained access control
- **Rate Limiting** - Per-key rate limits
- **Usage Tracking** - Last used timestamps

### API Key Format

```
dms_<32_random_bytes_base64>
Example: dms_xK9mP2qR7sT4vW8yZ1aC3dF5gH6jL9nQ2rU4wX7zB0
```

### Usage

#### Generate API Key

```python
from src.core.api_auth import api_key_manager

# Generate key for user
api_key = api_key_manager.generate_api_key(
    name="Production API Key",
    user_id=1,
    expires_in_days=365,
    permissions=['read', 'write'],
    rate_limit=10000  # requests per hour
)

print(f"API Key: {api_key}")
print("Keep this secret! It won't be shown again.")
```

#### Protect Endpoints

```python
from src.core.api_auth import require_api_key

# Require any valid API key
@app.route('/api/data')
@require_api_key()
def get_data():
    return jsonify({'data': 'secret'})

# Require specific permissions
@app.route('/api/admin/users')
@require_api_key(permissions=['admin'])
def admin_users():
    return jsonify({'users': []})
```

#### Optional Authentication

```python
from src.core.api_auth import optional_api_key
from flask import g

@app.route('/api/public')
@optional_api_key
def public_endpoint():
    if hasattr(g, 'api_key_info'):
        # Authenticated request
        user_id = g.api_key_info['user_id']
        return jsonify({'message': f'Hello user {user_id}'})
    else:
        # Anonymous request
        return jsonify({'message': 'Hello anonymous'})
```

#### Using API Keys

```bash
# In request header
curl -H "X-API-Key: dms_your_key_here" https://api.example.com/data

# Or with Bearer token format
curl -H "Authorization: Bearer dms_your_key_here" https://api.example.com/data
```

#### Manage Keys

```python
from src.core.api_auth import api_key_manager

# List keys for user
keys = api_key_manager.list_api_keys(user_id=1)
for key in keys:
    print(f"{key['key_prefix']}... - {key['name']}")

# Revoke key
api_key_manager.revoke_api_key(api_key)

# Cleanup expired keys
api_key_manager.cleanup_expired_keys()
```

---

## 4. Backup Encryption

### Overview

Backup encryption module (`src/core/backup_encryption.py`) provides secure encryption for backup files using Fernet (symmetric encryption).

### Features

- **Fernet Encryption** - Secure symmetric encryption
- **Compression** - Automatic gzip compression
- **Metadata** - Backup metadata storage
- **Key Management** - Secure key generation and storage
- **Full Backup** - Directory archiving with tar

### Installation

```bash
pip install cryptography
```

### Usage

#### Generate Encryption Key

```python
from src.core.backup_encryption import BackupEncryption

# Generate new key
key = BackupEncryption.generate_key()
print(f"Encryption key: {key.decode()}")

# Save key securely
encryptor = BackupEncryption(key=key)
encryptor.save_key('backup.key')  # Saved with 0600 permissions
```

#### Encrypt Files

```python
from src.core.backup_encryption import BackupEncryption

# Initialize with key
encryptor = BackupEncryption(key_file='backup.key')

# Encrypt file
encrypted_path = encryptor.encrypt_file(
    'data/database.db',
    'backups/database.db.encrypted',
    compress=True
)
```

#### Decrypt Files

```python
# Decrypt file
decrypted_path = encryptor.decrypt_file(
    'backups/database.db.encrypted',
    'restored/database.db',
    compressed=True
)
```

#### Full Backup with Encryption

```python
# Create encrypted backup of directory
backup_path = encryptor.encrypt_backup(
    backup_dir='data',
    output_file='backups/full_backup_20240114.enc',
    metadata={
        'description': 'Full system backup',
        'version': '1.0'
    }
)
```

#### Restore Encrypted Backup

```python
# Restore encrypted backup
metadata = encryptor.restore_backup(
    backup_file='backups/full_backup_20240114.enc',
    output_dir='restored',
    verify_metadata=True
)

print(f"Backup timestamp: {metadata['timestamp']}")
print(f"Original size: {metadata['size_bytes']} bytes")
```

#### Integrated with BackupManager

```python
from src.core.backup import BackupManager

# Create backup manager with encryption
backup_mgr = BackupManager(
    backup_dir='backups',
    encrypt=True,
    encryption_key=key  # or None to auto-generate
)

# Create encrypted backup
backup_path = backup_mgr.create_backup(include_files=True)

# Restore encrypted backup
backup_mgr.restore_backup(backup_path)
```

### Environment Variables

```bash
# Set encryption key via environment
export BACKUP_ENCRYPTION_KEY=<base64_key>

# BackupEncryption will use it automatically
```

### Security Best Practices

1. **Key Storage**
   - Store encryption keys separately from backups
   - Use secure key management system (e.g., HashiCorp Vault)
   - Set file permissions to 0600 (owner read/write only)

2. **Key Rotation**
   - Rotate encryption keys periodically
   - Re-encrypt old backups with new keys

3. **Access Control**
   - Limit access to encryption keys
   - Use separate keys for different environments

4. **Backup Verification**
   - Test restore process regularly
   - Verify backup integrity after encryption

---

## 🔒 Security Checklist

### Production Deployment

- [ ] **HTTPS Enabled**
  - [ ] Valid SSL certificate installed
  - [ ] Certificate not expired
  - [ ] HSTS header enabled
  - [ ] HTTP redirects to HTTPS

- [ ] **CSRF Protection**
  - [ ] CSRF tokens in all forms
  - [ ] API endpoints exempt where appropriate
  - [ ] Token validation working

- [ ] **API Authentication**
  - [ ] API keys generated for users
  - [ ] Keys stored securely (hashed)
  - [ ] Rate limiting configured
  - [ ] Permissions assigned correctly

- [ ] **Backup Encryption**
  - [ ] Encryption keys generated
  - [ ] Keys backed up separately
  - [ ] Restore process tested
  - [ ] Automated backups encrypted

- [ ] **Environment**
  - [ ] `FLASK_ENV=production`
  - [ ] `SECRET_KEY` set to random value
  - [ ] `SSL_CERT_PATH` configured
  - [ ] `SSL_KEY_PATH` configured
  - [ ] `BACKUP_ENCRYPTION_KEY` set

### Security Headers Check

```bash
# Test security headers
curl -I https://your-domain.com

# Should include:
# Strict-Transport-Security: max-age=31536000
# Content-Security-Policy: ...
# X-Content-Type-Options: nosniff
# X-Frame-Options: DENY
```

### API Authentication Test

```bash
# Test without key (should fail)
curl https://api.example.com/data

# Test with valid key (should succeed)
curl -H "X-API-Key: dms_your_key" https://api.example.com/data
```

---

## 📚 References

- [OWASP HTTPS Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Transport_Layer_Protection_Cheat_Sheet.html)
- [OWASP CSRF Prevention](https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html)
- [API Security Best Practices](https://owasp.org/www-project-api-security/)
- [Backup Security](https://www.nist.gov/publications/guide-selecting-security-configuration-checklist)

---

**Last Updated:** 2026-01-14
**Security Level:** 🟢 Enhanced
**Status:** Production Ready
