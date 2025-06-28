"""
Authentication routes and utilities
"""

import os
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

try:
    from fastapi import APIRouter, Depends, HTTPException, Request, Form
    from fastapi.responses import RedirectResponse, JSONResponse
    from passlib.context import CryptContext
    import jwt
    
    # Password hashing
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    # JWT settings
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 30
    
except ImportError:
    logger.warning("FastAPI dependencies not installed - web features disabled")
    pwd_context = None
    SECRET_KEY = None
    ALGORITHM = None
    ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Router
auth_router = None

def create_auth_router():
    """Create authentication router"""
    global auth_router
    
    if auth_router is not None:
        return auth_router
    
    try:
        auth_router = APIRouter()
        
        @auth_router.post("/login")
        async def login(request: Request, username: str = Form(), password: str = Form()):
            """Login endpoint"""
            # TODO: Implement proper user authentication with database
            # For now, use demo credentials
            
            if username == "admin" and password == "admin":
                # Create access token
                access_token = create_access_token(data={"sub": username})
                
                # Set session
                request.session["access_token"] = access_token
                request.session["user"] = {"username": username, "role": "admin"}
                
                return JSONResponse({
                    "access_token": access_token,
                    "token_type": "bearer",
                    "user": {"username": username, "role": "admin"}
                })
            else:
                raise HTTPException(status_code=401, detail="Invalid credentials")
        
        @auth_router.post("/logout")
        async def logout(request: Request):
            """Logout endpoint"""
            request.session.clear()
            return {"message": "Logged out successfully"}
        
        @auth_router.get("/me")
        async def get_current_user(request: Request):
            """Get current user info"""
            user = request.session.get("user")
            if not user:
                raise HTTPException(status_code=401, detail="Not authenticated")
            return user
        
        return auth_router
        
    except Exception as e:
        logger.error(f"Failed to create auth router: {e}")
        return None

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password"""
    if pwd_context is None:
        return plain_password == hashed_password  # Fallback for demo
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash password"""
    if pwd_context is None:
        return password  # Fallback for demo
    return pwd_context.hash(password)

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None):
    """Create JWT access token"""
    if SECRET_KEY is None:
        return "demo-token"  # Fallback for demo
    
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """Verify JWT token"""
    if SECRET_KEY is None:
        return {"sub": "demo-user"}  # Fallback for demo
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.PyJWTError:
        return None

def get_current_user_from_token(token: str) -> Optional[Dict[str, Any]]:
    """Get user from token"""
    payload = verify_token(token)
    if payload is None:
        return None
    
    username = payload.get("sub")
    if username is None:
        return None
    
    # TODO: Get user from database
    return {"username": username, "role": "user"}

def require_auth(request: Request) -> Dict[str, Any]:
    """Dependency to require authentication"""
    user = request.session.get("user")
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    return user

# Initialize router
auth_router = create_auth_router()
