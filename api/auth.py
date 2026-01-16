"""
BALE Authentication & Authorization
JWT-based auth with API key support and RBAC.
"""
import os
import secrets
import hashlib
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from enum import Enum

from fastapi import HTTPException, Security, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, APIKeyHeader
from jose import jwt, JWTError
from passlib.context import CryptContext
from pydantic import BaseModel

from src.logger import setup_logger

logger = setup_logger("bale_auth")


# ==================== CONFIGURATION ====================

SECRET_KEY = os.getenv("BALE_SECRET_KEY", secrets.token_urlsafe(32))
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
REFRESH_TOKEN_EXPIRE_DAYS = 7

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
bearer_scheme = HTTPBearer(auto_error=False)
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


# ==================== MODELS ====================

class Role(str, Enum):
    """User roles for RBAC."""
    ADMIN = "admin"
    ANALYST = "analyst"
    VIEWER = "viewer"
    API_USER = "api_user"


class Permission(str, Enum):
    """Granular permissions."""
    READ_CONTRACTS = "read:contracts"
    WRITE_CONTRACTS = "write:contracts"
    DELETE_CONTRACTS = "delete:contracts"
    RUN_ANALYSIS = "run:analysis"
    RUN_SIMULATION = "run:simulation"
    MANAGE_USERS = "manage:users"
    MANAGE_API_KEYS = "manage:api_keys"
    VIEW_AUDIT_LOG = "view:audit_log"
    EXPORT_DATA = "export:data"


# Role to permissions mapping
ROLE_PERMISSIONS: Dict[Role, List[Permission]] = {
    Role.ADMIN: list(Permission),  # All permissions
    Role.ANALYST: [
        Permission.READ_CONTRACTS,
        Permission.WRITE_CONTRACTS,
        Permission.RUN_ANALYSIS,
        Permission.RUN_SIMULATION,
        Permission.EXPORT_DATA,
    ],
    Role.VIEWER: [
        Permission.READ_CONTRACTS,
    ],
    Role.API_USER: [
        Permission.READ_CONTRACTS,
        Permission.RUN_ANALYSIS,
        Permission.RUN_SIMULATION,
    ],
}


@dataclass
class TokenPayload:
    """JWT token payload."""
    sub: str  # User ID
    email: str
    role: str
    permissions: List[str]
    exp: datetime
    iat: datetime
    type: str  # access or refresh


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class UserCreate(BaseModel):
    email: str
    password: str
    full_name: Optional[str] = None
    role: Role = Role.VIEWER


class UserLogin(BaseModel):
    email: str
    password: str


# ==================== PASSWORD UTILITIES ====================

def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


# ==================== API KEY UTILITIES ====================

def generate_api_key() -> tuple[str, str]:
    """
    Generate a new API key.
    Returns (key, key_hash) - only show key once, store hash.
    """
    key = f"bale_{'pk' if secrets.randbelow(2) else 'sk'}_{secrets.token_urlsafe(32)}"
    key_hash = hashlib.sha256(key.encode()).hexdigest()
    return key, key_hash


def verify_api_key(key: str, key_hash: str) -> bool:
    """Verify an API key against its hash."""
    return hashlib.sha256(key.encode()).hexdigest() == key_hash


# ==================== JWT UTILITIES ====================

def create_access_token(
    user_id: str,
    email: str,
    role: Role,
    expires_delta: timedelta = None
) -> str:
    """Create a new JWT access token."""
    if expires_delta is None:
        expires_delta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    now = datetime.utcnow()
    expire = now + expires_delta
    
    permissions = [p.value for p in ROLE_PERMISSIONS.get(role, [])]
    
    payload = {
        "sub": user_id,
        "email": email,
        "role": role.value,
        "permissions": permissions,
        "exp": expire,
        "iat": now,
        "type": "access"
    }
    
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(user_id: str) -> str:
    """Create a new JWT refresh token."""
    now = datetime.utcnow()
    expire = now + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    
    payload = {
        "sub": user_id,
        "exp": expire,
        "iat": now,
        "type": "refresh"
    }
    
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> Optional[Dict[str, Any]]:
    """Decode and validate a JWT token."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError as e:
        logger.warning(f"JWT decode failed: {e}")
        return None


def create_tokens(user_id: str, email: str, role: Role) -> TokenResponse:
    """Create both access and refresh tokens."""
    access_token = create_access_token(user_id, email, role)
    refresh_token = create_refresh_token(user_id)
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )


# ==================== FASTAPI DEPENDENCIES ====================

class AuthenticatedUser:
    """Represents an authenticated user."""
    def __init__(
        self,
        user_id: str,
        email: str,
        role: Role,
        permissions: List[Permission],
        auth_method: str  # "jwt" or "api_key"
    ):
        self.user_id = user_id
        self.email = email
        self.role = role
        self.permissions = permissions
        self.auth_method = auth_method
    
    def has_permission(self, permission: Permission) -> bool:
        return permission in self.permissions


async def get_current_user(
    request: Request,
    bearer_token: HTTPAuthorizationCredentials = Security(bearer_scheme),
    api_key: str = Security(api_key_header)
) -> AuthenticatedUser:
    """
    Extract and validate user from JWT token or API key.
    This is the main authentication dependency.
    """
    
    # Try JWT first
    if bearer_token:
        payload = decode_token(bearer_token.credentials)
        if payload and payload.get("type") == "access":
            try:
                role = Role(payload.get("role", "viewer"))
                permissions = [Permission(p) for p in payload.get("permissions", [])]
                
                return AuthenticatedUser(
                    user_id=payload["sub"],
                    email=payload.get("email", ""),
                    role=role,
                    permissions=permissions,
                    auth_method="jwt"
                )
            except (ValueError, KeyError) as e:
                logger.warning(f"Invalid token payload: {e}")
    
    # Try API key
    if api_key:
        # In production, validate against database
        # For now, accept any properly formatted key
        if api_key.startswith("bale_"):
            return AuthenticatedUser(
                user_id="api_user",
                email="api@bale.dev",
                role=Role.API_USER,
                permissions=ROLE_PERMISSIONS[Role.API_USER],
                auth_method="api_key"
            )
    
    raise HTTPException(
        status_code=401,
        detail="Not authenticated",
        headers={"WWW-Authenticate": "Bearer"}
    )


async def get_optional_user(
    request: Request,
    bearer_token: HTTPAuthorizationCredentials = Security(bearer_scheme),
    api_key: str = Security(api_key_header)
) -> Optional[AuthenticatedUser]:
    """
    Get current user if authenticated, None otherwise.
    Use for optional auth endpoints.
    """
    try:
        return await get_current_user(request, bearer_token, api_key)
    except HTTPException:
        return None


def require_permission(permission: Permission):
    """
    Dependency factory for permission checking.
    
    Usage:
        @app.get("/admin", dependencies=[Depends(require_permission(Permission.MANAGE_USERS))])
    """
    async def check_permission(user: AuthenticatedUser = Depends(get_current_user)):
        if not user.has_permission(permission):
            raise HTTPException(
                status_code=403,
                detail=f"Permission denied: {permission.value} required"
            )
        return user
    return check_permission


def require_role(role: Role):
    """
    Dependency factory for role checking.
    
    Usage:
        @app.get("/admin", dependencies=[Depends(require_role(Role.ADMIN))])
    """
    async def check_role(user: AuthenticatedUser = Depends(get_current_user)):
        if user.role != role and user.role != Role.ADMIN:
            raise HTTPException(
                status_code=403,
                detail=f"Role required: {role.value}"
            )
        return user
    return check_role


# ==================== RATE LIMITING ====================

class RateLimiter:
    """
    Simple in-memory rate limiter.
    In production, use Redis for distributed limiting.
    """
    
    def __init__(self, requests_per_minute: int = 60):
        self.rpm = requests_per_minute
        self.requests: Dict[str, List[datetime]] = {}
    
    def is_allowed(self, key: str) -> bool:
        """Check if request is allowed for the given key."""
        now = datetime.utcnow()
        minute_ago = now - timedelta(minutes=1)
        
        if key not in self.requests:
            self.requests[key] = []
        
        # Clean old requests
        self.requests[key] = [
            ts for ts in self.requests[key] 
            if ts > minute_ago
        ]
        
        if len(self.requests[key]) >= self.rpm:
            return False
        
        self.requests[key].append(now)
        return True
    
    def get_remaining(self, key: str) -> int:
        """Get remaining requests for the key."""
        if key not in self.requests:
            return self.rpm
        
        now = datetime.utcnow()
        minute_ago = now - timedelta(minutes=1)
        
        recent = sum(1 for ts in self.requests[key] if ts > minute_ago)
        return max(0, self.rpm - recent)


# Global rate limiter
rate_limiter = RateLimiter(requests_per_minute=60)


async def check_rate_limit(
    request: Request,
    user: AuthenticatedUser = Depends(get_current_user)
) -> AuthenticatedUser:
    """Rate limiting dependency."""
    key = f"{user.user_id}:{user.auth_method}"
    
    if not rate_limiter.is_allowed(key):
        remaining = rate_limiter.get_remaining(key)
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded",
            headers={
                "X-RateLimit-Remaining": str(remaining),
                "Retry-After": "60"
            }
        )
    
    return user
