#!/usr/bin/env python
# -*- coding: utf-8 -*-
# project_assessment - by Jero98772
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
from jose import JWTError, jwt
from fastapi import HTTPException, Request
import time

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
        data (dict): The payload data to encode in the token (must contain 'sub')
        
    Returns:
        str: The encoded JWT access token
    """
    to_encode = data.copy()
    
    # Ensure 'sub' is a string (jose library requirement)
    if "sub" in to_encode and not isinstance(to_encode["sub"], str):
        to_encode["sub"] = str(to_encode["sub"])
    
    now = int(time.time())
    
    # Set token type and expiration
    to_encode.update({
        "iat": now,
        "exp": now + (ACCESS_TOKEN_EXPIRE_MINUTES * 60),  # Convert minutes to seconds
        "type": "access",  # Add type field for verification
        "role": "user"
    })
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    print(f"[DEBUG] Generated access token: {encoded_jwt}")
    return encoded_jwt


def create_refresh_token(data: dict):
    """
    Create a JWT refresh token with longer expiration.
    
    Args:
        data (dict): The payload data to encode in the token (must contain 'sub')
        
    Returns:
        str: The encoded JWT refresh token
    """
    to_encode = data.copy()
    
    # Ensure 'sub' is a string (jose library requirement)
    if "sub" in to_encode and not isinstance(to_encode["sub"], str):
        to_encode["sub"] = str(to_encode["sub"])
    
    now = int(time.time())
    expire_seconds = REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60  # Convert days to seconds
    
    to_encode.update({
        "iat": now,
        "exp": now + expire_seconds,
        "type": "refresh"
    })
    
    encoded_jwt = jwt.encode(to_encode, REFRESH_SECRET_KEY, algorithm=ALGORITHM)
    print(f"[DEBUG] Generated refresh token: {encoded_jwt}")
    return encoded_jwt


def verify_token(token: str):
    """
    Verify and decode a JWT access token.
    
    Args:
        token (str): The JWT access token to verify
        
    Returns:
        str or None: The user ID (sub) from the token if valid, None otherwise
    """
    print(f"[DEBUG] Verifying token: {token}")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        print(f"[DEBUG] Decoded payload: {payload}")
        
        user_id = payload.get("sub")
        token_type = payload.get("type")
        
        # Validate token type
        if token_type != "access":
            print(f"[DEBUG] Invalid token type: {token_type}")
            return None
            
        if user_id is None:
            print("[DEBUG] No user_id (sub) in token")
            return None
        
        # Convert back to int if needed for your application
        # If you need it as int, uncomment the next line
        # user_id = int(user_id) if isinstance(user_id, str) and user_id.isdigit() else user_id
            
        return user_id
        
    except JWTError as e:
        print(f"[DEBUG] JWT Error: {e}")
        return None


def verify_refresh_token(token: str):
    """
    Verify and decode a JWT refresh token.
    
    Args:
        token (str): The JWT refresh token to verify
        
    Returns:
        str or None: The user ID (sub) from the token if valid, None otherwise
    """
    print(f"[DEBUG] Verifying refresh token: {token}")
    try:
        payload = jwt.decode(token, REFRESH_SECRET_KEY, algorithms=[ALGORITHM])
        print(f"[DEBUG] Decoded refresh payload: {payload}")
        
        user_id = payload.get("sub")
        token_type = payload.get("type")
        
        # Validate token type
        if token_type != "refresh":
            print(f"[DEBUG] Invalid refresh token type: {token_type}")
            return None
            
        if user_id is None:
            print("[DEBUG] No user_id (sub) in refresh token")
            return None
        
        # Convert back to int if needed for your application
        # If you need it as int, uncomment the next line
        # user_id = int(user_id) if isinstance(user_id, str) and user_id.isdigit() else user_id
            
        return user_id
        
    except JWTError as e:
        print(f"[DEBUG] JWT Error on refresh token: {e}")
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
    print(f"[DEBUG] All cookies received: {request.cookies}")
    token = request.cookies.get("access_token")
    print(f"[DEBUG] Access token from cookie: {token}")
    
    if not token:
        raise HTTPException(
            status_code=401, 
            detail="Not authenticated - no access token in cookies"
        )
    return token


def get_current_user(token: str):
    """
    Get the current user from a verified access token.
    
    Args:
        token (str): The JWT access token to verify
        
    Returns:
        str: The user ID (sub) from the token
        
    Raises:
        HTTPException: 401 error if the token is invalid
    """
    user_id = verify_token(token)
    if not user_id:
        raise HTTPException(
            status_code=401, 
            detail="Invalid or expired token"
        )
    return user_id
