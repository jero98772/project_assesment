#!/usr/bin/env python
# -*- coding: utf-8 -*-"
#project_assesment - by Jero98772

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from core.db.database import get_db
from core.db.crud import create_user, get_user_by_login, verify_password
from core.tools.tools import create_access_token

router = APIRouter()

class UserRegister(BaseModel):
    login: str
    email: str
    password: str
    password_repeat: str

class UserLogin(BaseModel):
    login: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str

@router.post("/auth", tags=["Authentication"])
async def register(user: UserRegister, db: Session = Depends(get_db)):
    if user.password != user.password_repeat:
        raise HTTPException(status_code=400, detail="Passwords do not match")
    
    existing_user = get_user_by_login(db, user.login)
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")
    
    new_user = create_user(db, user.login, user.email, user.password)
    return {"id": new_user.id, "login": new_user.login, "email": new_user.email, "message": "User created successfully"}

@router.post("/login", response_model=TokenResponse, tags=["Authentication"])
async def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = get_user_by_login(db, user.login)
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    access_token = create_access_token(data={"sub": db_user.id})
    return {"access_token": access_token, "token_type": "bearer"}