#!/usr/bin/env python
# -*- coding: utf-8 -*-"
#project_assesment - by Jero98772

from fastapi import APIRouter, HTTPException, Depends, Response, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel
from core.db.database import get_db
from core.db.crud import create_user, get_user_by_login, verify_password, get_user_by_id
from core.tools.tools import create_access_token, create_refresh_token, verify_refresh_token

router = APIRouter()

class UserRegister(BaseModel):
    login: str
    email: str
    password: str
    password_repeat: str

class UserLogin(BaseModel):
    login: str
    password: str

@router.post("/auth", tags=["Authentication"])
async def register(user: UserRegister, db: Session = Depends(get_db)):
    """
    Register a new user in the system.
    
    Args:
        user (UserRegister): User registration data containing login, email, password, and password confirmation
        db (Session): Database session dependency
        
    Returns:
        dict: User creation success response with user details
        
    Raises:
        HTTPException: 400 error if passwords don't match or user already exists
    """
    if user.password != user.password_repeat:
        raise HTTPException(status_code=400, detail="Passwords do not match")
    
    existing_user = get_user_by_login(db, user.login)
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")
    
    new_user = create_user(db, user.login, user.email, user.password)
    return {"id": new_user.id, "login": new_user.login, "email": new_user.email, "message": "User created successfully"}

@router.post("/login", tags=["Authentication"])
async def login(user: UserLogin, response: Response, db: Session = Depends(get_db)):
    """
    Authenticate user and issue JWT tokens.
    
    Args:
        user (UserLogin): User login credentials (login and password)
        response (Response): FastAPI response object to set cookies
        db (Session): Database session dependency
        
    Returns:
        dict: Login success response with user details
        
    Raises:
        HTTPException: 401 error if credentials are invalid
        
    Notes:
        Sets HTTP-only cookies for access_token (1 hour) and refresh_token (7 days)
    """
    db_user = get_user_by_login(db, user.login)
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    access_token = create_access_token(data={"sub": db_user.id})
    refresh_token = create_refresh_token(data={"sub": db_user.id})
    
    # Set access token as HTTP-only cookie
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        max_age=3600,  # 1 hour
        samesite="lax"
    )
    
    # Set refresh token as HTTP-only cookie
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        max_age=604800,  # 7 days
        samesite="lax"
    )
    
    return {
        "message": "Login successful",
        "user": {
            "id": db_user.id,
            "login": db_user.login,
            "email": db_user.email
        }
    }

@router.post("/refresh", tags=["Authentication"])
async def refresh_token(request: Request, response: Response, db: Session = Depends(get_db)):
    """
    Refresh access token using valid refresh token.
    
    Args:
        request (Request): FastAPI request object to extract refresh token from cookies
        response (Response): FastAPI response object to set new access token cookie
        db (Session): Database session dependency
        
    Returns:
        dict: Token refresh success message
        
    Raises:
        HTTPException: 401 error if refresh token is missing, invalid, or user not found
        
    Notes:
        Issues a new access token while maintaining the same refresh token
    """
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Refresh token not found")
    
    user_id = verify_refresh_token(refresh_token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    
    db_user = get_user_by_id(db, user_id)
    if not db_user:
        raise HTTPException(status_code=401, detail="User not found")
    
    # Create new access token
    new_access_token = create_access_token(data={"sub": db_user.id})
    
    # Set new access token as cookie
    response.set_cookie(
        key="access_token",
        value=new_access_token,
        httponly=True,
        max_age=3600,  # 1 hour
        samesite="lax"
    )
    
    return {"message": "Token refreshed successfully"}

@router.post("/logout", tags=["Authentication"])
async def logout(response: Response):
    """
    Logout user by clearing authentication cookies.
    
    Args:
        response (Response): FastAPI response object to clear cookies
        
    Returns:
        dict: Logout success message
        
    Notes:
        Removes both access_token and refresh_token cookies from client
    """
    response.delete_cookie(key="access_token")
    response.delete_cookie(key="refresh_token")
    return {"message": "Logged out successfully"}