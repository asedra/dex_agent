from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from .config import settings
import uuid
import time
import hashlib

# Password hashing with optimized settings for better performance
# Using lower bcrypt rounds for faster verification while maintaining security
pwd_context = CryptContext(
    schemes=["bcrypt"], 
    deprecated="auto",
    bcrypt__rounds=10  # Reduced from default 12 for faster login (still secure)
)

# Simple in-memory cache for password verification to reduce bcrypt overhead
# Cache structure: {username_hash: (password_hash, timestamp, success)}
_auth_cache = {}
_cache_duration = 300  # 5 minutes cache duration

def verify_password(plain_password: str, hashed_password: str, username: str = None) -> bool:
    """Verify a password against its hash with optional caching for performance"""
    
    # If username provided, try cache first
    if username:
        cache_key = hashlib.sha256(f"{username}:{plain_password}".encode()).hexdigest()
        current_time = time.time()
        
        # Check cache
        if cache_key in _auth_cache:
            cached_hash, timestamp, success = _auth_cache[cache_key]
            # If cache is valid and hash matches
            if current_time - timestamp < _cache_duration and cached_hash == hashed_password:
                return success
        
        # Verify password
        is_valid = pwd_context.verify(plain_password, hashed_password)
        
        # Cache the result
        _auth_cache[cache_key] = (hashed_password, current_time, is_valid)
        
        # Clean old cache entries (simple cleanup)
        if len(_auth_cache) > 1000:  # Limit cache size
            old_entries = [k for k, (_, ts, _) in _auth_cache.items() 
                          if current_time - ts > _cache_duration]
            for k in old_entries[:500]:  # Remove half of old entries
                _auth_cache.pop(k, None)
        
        return is_valid
    else:
        # Fallback to direct verification if no username
        return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)

def create_access_token(data: Dict[Any, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT token"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")
    return encoded_jwt

def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """Verify and decode a JWT token"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        return payload
    except JWTError:
        return None

def generate_user_id() -> str:
    """Generate a unique user ID"""
    return str(uuid.uuid4())