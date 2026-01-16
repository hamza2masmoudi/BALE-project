"""
BALE Authentication Tests
Tests for JWT, API keys, and RBAC.
"""
import pytest
from datetime import datetime, timedelta


class TestPasswordUtils:
    """Test password hashing utilities."""
    
    def test_hash_password(self):
        """Test password hashing."""
        from api.auth import hash_password, verify_password
        
        password = "test_password_123"
        hashed = hash_password(password)
        
        assert hashed != password
        assert len(hashed) > 50  # bcrypt hashes are long
    
    def test_verify_correct_password(self):
        """Test correct password verification."""
        from api.auth import hash_password, verify_password
        
        password = "correct_password"
        hashed = hash_password(password)
        
        assert verify_password(password, hashed) is True
    
    def test_verify_incorrect_password(self):
        """Test incorrect password rejection."""
        from api.auth import hash_password, verify_password
        
        password = "correct_password"
        hashed = hash_password(password)
        
        assert verify_password("wrong_password", hashed) is False


class TestAPIKeys:
    """Test API key generation and verification."""
    
    def test_generate_api_key(self):
        """Test API key generation."""
        from api.auth import generate_api_key
        
        key, key_hash = generate_api_key()
        
        assert key.startswith("bale_")
        assert len(key) > 40
        assert len(key_hash) == 64  # SHA256 hex
    
    def test_verify_valid_key(self):
        """Test valid API key verification."""
        from api.auth import generate_api_key, verify_api_key
        
        key, key_hash = generate_api_key()
        
        assert verify_api_key(key, key_hash) is True
    
    def test_verify_invalid_key(self):
        """Test invalid API key rejection."""
        from api.auth import generate_api_key, verify_api_key
        
        _, key_hash = generate_api_key()
        
        assert verify_api_key("fake_key", key_hash) is False


class TestJWT:
    """Test JWT token operations."""
    
    def test_create_access_token(self):
        """Test access token creation."""
        from api.auth import create_access_token, Role
        
        token = create_access_token(
            user_id="user_123",
            email="test@example.com",
            role=Role.ANALYST
        )
        
        assert isinstance(token, str)
        assert len(token) > 100
    
    def test_decode_valid_token(self):
        """Test valid token decoding."""
        from api.auth import create_access_token, decode_token, Role
        
        token = create_access_token(
            user_id="user_123",
            email="test@example.com",
            role=Role.ANALYST
        )
        
        payload = decode_token(token)
        
        assert payload is not None
        assert payload["sub"] == "user_123"
        assert payload["email"] == "test@example.com"
        assert payload["role"] == "analyst"
        assert payload["type"] == "access"
    
    def test_decode_invalid_token(self):
        """Test invalid token rejection."""
        from api.auth import decode_token
        
        payload = decode_token("invalid.token.here")
        
        assert payload is None
    
    def test_create_refresh_token(self):
        """Test refresh token creation."""
        from api.auth import create_refresh_token, decode_token
        
        token = create_refresh_token("user_123")
        payload = decode_token(token)
        
        assert payload["type"] == "refresh"
        assert payload["sub"] == "user_123"
    
    def test_token_expiry(self):
        """Test token contains expiry."""
        from api.auth import create_access_token, decode_token, Role
        
        token = create_access_token(
            user_id="user_123",
            email="test@example.com",
            role=Role.VIEWER
        )
        
        payload = decode_token(token)
        
        assert "exp" in payload
        assert payload["exp"] > datetime.utcnow().timestamp()


class TestRBAC:
    """Test role-based access control."""
    
    def test_role_permissions(self):
        """Test roles have correct permissions."""
        from api.auth import Role, Permission, ROLE_PERMISSIONS
        
        # Admin has all permissions
        admin_perms = ROLE_PERMISSIONS[Role.ADMIN]
        assert Permission.MANAGE_USERS in admin_perms
        assert Permission.RUN_ANALYSIS in admin_perms
        
        # Analyst can analyze but not manage users
        analyst_perms = ROLE_PERMISSIONS[Role.ANALYST]
        assert Permission.RUN_ANALYSIS in analyst_perms
        assert Permission.MANAGE_USERS not in analyst_perms
        
        # Viewer can only read
        viewer_perms = ROLE_PERMISSIONS[Role.VIEWER]
        assert Permission.READ_CONTRACTS in viewer_perms
        assert Permission.WRITE_CONTRACTS not in viewer_perms


class TestRateLimiter:
    """Test rate limiting."""
    
    def test_allows_under_limit(self):
        """Test requests under limit are allowed."""
        from api.auth import RateLimiter
        
        limiter = RateLimiter(requests_per_minute=10)
        
        for _ in range(5):
            assert limiter.is_allowed("test_user") is True
    
    def test_blocks_over_limit(self):
        """Test requests over limit are blocked."""
        from api.auth import RateLimiter
        
        limiter = RateLimiter(requests_per_minute=5)
        
        # Use up the limit
        for _ in range(5):
            limiter.is_allowed("test_user")
        
        # Next request should be blocked
        assert limiter.is_allowed("test_user") is False
    
    def test_different_keys_separate(self):
        """Test different keys have separate limits."""
        from api.auth import RateLimiter
        
        limiter = RateLimiter(requests_per_minute=5)
        
        for _ in range(5):
            limiter.is_allowed("user_1")
        
        # user_2 should still have quota
        assert limiter.is_allowed("user_2") is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
