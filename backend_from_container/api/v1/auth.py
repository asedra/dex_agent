from datetime import timedelta
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials
from ...schemas.auth import UserLogin, TokenResponse, UserResponse
from ...core.database import db_manager
from ...core.jwt_utils import verify_password, create_access_token, verify_token
from ...core.config import settings
from ...core.auth import security, get_current_user
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/login", response_model=TokenResponse)
async def login_for_access_token(user_credentials: UserLogin):
    """Optimized login user and return JWT token - targeting sub-100ms response"""
    try:
        # Get user from database and update login in single transaction for better performance
        user = getattr(db_manager, 'get_user_by_username_and_update_login', None)
        if user is None:
            # Fallback for SQLite or older implementations
            user = db_manager.get_user_by_username(user_credentials.username)
            if user:
                db_manager.update_user_last_login(user["id"])
        else:
            # Use optimized combined query
            user = user(user_credentials.username)
        
        if not user:
            logger.warning(f"Login attempt with invalid username: {user_credentials.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Check if user is active before password verification for early exit
        if not user.get("is_active", True):
            logger.warning(f"Login attempt for inactive user: {user_credentials.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Inactive user",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Verify password with caching for better performance
        if not verify_password(user_credentials.password, user["password_hash"], user_credentials.username):
            logger.warning(f"Login attempt with invalid password for user: {user_credentials.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Create access token
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user["username"], "user_id": user["id"]},
            expires_delta=access_token_expires
        )
        
        # Prepare user response (last_login already updated if using optimized method)
        user_response = UserResponse(
            id=str(user["id"]),
            username=user["username"],
            email=user["email"],
            full_name=user.get("full_name"),
            is_active=user.get("is_active", True),
            created_at=user["created_at"],
            last_login=user.get("last_login")
        )
        
        logger.info(f"User {user_credentials.username} logged in successfully")
        
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=user_response
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: Annotated[dict, Depends(get_current_user)]):
    """Get current user information"""
    try:
        return UserResponse(
            id=str(current_user["id"]),
            username=current_user["username"],
            email=current_user["email"],
            full_name=current_user.get("full_name"),
            is_active=current_user.get("is_active", True),
            created_at=current_user["created_at"],
            last_login=current_user.get("last_login")
        )
        
    except Exception as e:
        logger.error(f"Get user error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.post("/logout")
async def logout(current_user: Annotated[dict, Depends(get_current_user)]):
    """Logout user (client should discard token)"""
    try:
        username = current_user.get("username")
        logger.info(f"User {username} logged out")
        
        return {"message": "Successfully logged out"}
        
    except Exception as e:
        logger.error(f"Logout error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )