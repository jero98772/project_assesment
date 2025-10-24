#!/usr/bin/env python
# -*- coding: utf-8 -*-"
#project_assesment - by Jero98772

import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
from jose import JWTError, jwt
from fastapi import HTTPException, Request

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY") or "your-secret-key-change-in-production"
REFRESH_SECRET_KEY = os.getenv("REFRESH_SECRET_KEY") or "your-refresh-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
REFRESH_TOKEN_EXPIRE_DAYS = 7

def create_access_token(data: dict):
    """
    Create a JWT access token with expiration.
    
    Args:
        data (dict): The payload data to encode in the token (typically contains 'sub' subject)
        
    Returns:
        str: The encoded JWT access token
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    print(f"[DEBUG] Generated access token: {encoded_jwt}")
    return encoded_jwt

def create_refresh_token(data: dict):
    """
    Create a JWT refresh token with longer expiration.
    
    Args:
        data (dict): The payload data to encode in the token (typically contains 'sub' subject)
        
    Returns:
        str: The encoded JWT refresh token
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, REFRESH_SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str):
    """
    Verify and decode a JWT access token.
    
    Args:
        token (str): The JWT access token to verify
        
    Returns:
        int or None: The user ID (sub) from the token if valid, None otherwise
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("sub")
        token_type: str = payload.get("type")
        if user_id is None or token_type != "access":
            return None
        return user_id
    except JWTError:
        return None

def verify_refresh_token(token: str):
    """
    Verify and decode a JWT refresh token.
    
    Args:
        token (str): The JWT refresh token to verify
        
    Returns:
        int or None: The user ID (sub) from the token if valid, None otherwise
    """
    try:
        payload = jwt.decode(token, REFRESH_SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("sub")
        token_type: str = payload.get("type")
        if user_id is None or token_type != "refresh":
            return None
        return user_id
    except JWTError:
        return None

def extract_token(request: Request):
    """
    Extract the access token from request cookies.
    
    Args:
        request (Request): The FastAPI request object
        
    Returns:
        str: The access token from cookies
        
    Raises:
        HTTPException: 401 error if no access token is found in cookies
    """
    token = request.cookies.get("access_token")
    print(f"[DEBUG] Cookies received: {request.cookies}")
    print(f"[DEBUG] Access token from cookie: {token}")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return token

def get_current_user(token: str):
    """
    Get the current user from a verified access token.
    
    Args:
        token (str): The JWT access token to verify
        
    Returns:
        int: The user ID (sub) from the token
        
    Raises:
        HTTPException: 401 error if the token is invalid
    """
    user_id = verify_token(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")
    return user_id