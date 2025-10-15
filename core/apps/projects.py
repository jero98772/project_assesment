#!/usr/bin/env python
# -*- coding: utf-8 -*-"
#project_assesment - by Jero98772

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from core.db.database import get_db
from core.db.crud import (
    create_project, get_project_by_id, get_user_projects, update_project,
    delete_project, check_project_access, grant_project_access, get_user_role, get_user_by_login
)
from core.tools.tools import (
	verify_token,
	extract_token,
	get_current_user
	)
from core.apps.documents import get_document_dto

router = APIRouter()

class ProjectCreate(BaseModel):
    name: str
    description: str

class ProjectUpdate(BaseModel):
    name: str = None
    description: str = None

class ProjectDetail(BaseModel):
    id: int
    name: str
    description: str
    created_at: str
    updated_at: str
    documents: list


@router.post("/projects", tags=["Projects"])
async def create_new_project(
    project: ProjectCreate,
    authorization: str = None,
    db: Session = Depends(get_db)
):
    token = extract_token(authorization)
    user_id = get_current_user(token)
    
    new_project = create_project(db, project.name, project.description, user_id)
    return {
        "id": new_project.id,
        "name": new_project.name,
        "description": new_project.description,
        "created_at": new_project.created_at.isoformat(),
        "updated_at": new_project.updated_at.isoformat(),
        "documents": []
    }

@router.get("/projects", tags=["Projects"])
async def get_all_projects(
    authorization: str = None,
    db: Session = Depends(get_db)
):
    token = extract_token(authorization)
    user_id = get_current_user(token)
    
    projects = get_user_projects(db, user_id)
    result = []
    for proj in projects:
        docs = [get_document_dto(doc) for doc in proj.documents]
        result.append({
            "id": proj.id,
            "name": proj.name,
            "description": proj.description,
            "created_at": proj.created_at.isoformat(),
            "updated_at": proj.updated_at.isoformat(),
            "documents": docs
        })
    return result

@router.get("/project/{project_id}/info", tags=["Projects"])
async def get_project_info(
    project_id: int,
    authorization: str = None,
    db: Session = Depends(get_db)
):
    token = extract_token(authorization)
    user_id = get_current_user(token)
    
    if not check_project_access(db, user_id, project_id):
        raise HTTPException(status_code=403, detail="Access denied")
    
    project = get_project_by_id(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    docs = [get_document_dto(doc) for doc in project.documents]
    return {
        "id": project.id,
        "name": project.name,
        "description": project.description,
        "created_at": project.created_at.isoformat(),
        "updated_at": project.updated_at.isoformat(),
        "documents": docs
    }

@router.put("/project/{project_id}/info", tags=["Projects"])
async def update_project_info(
    project_id: int,
    project_update: ProjectUpdate,
    authorization: str = None,
    db: Session = Depends(get_db)
):
    token = extract_token(authorization)
    user_id = get_current_user(token)
    
    if not check_project_access(db, user_id, project_id):
        raise HTTPException(status_code=403, detail="Access denied")
    
    role = get_user_role(db, user_id, project_id)
    if role != 'owner':
        raise HTTPException(status_code=403, detail="Only owner can update project info")
    
    project = update_project(db, project_id, project_update.name, project_update.description)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    docs = [get_document_dto(doc) for doc in project.documents]
    return {
        "id": project.id,
        "name": project.name,
        "description": project.description,
        "created_at": project.created_at.isoformat(),
        "updated_at": project.updated_at.isoformat(),
        "documents": docs
    }

@router.delete("/project/{project_id}", tags=["Projects"])
async def delete_project_endpoint(
    project_id: int,
    authorization: str = None,
    db: Session = Depends(get_db)
):
    token = extract_token(authorization)
    user_id = get_current_user(token)
    
    role = get_user_role(db, user_id, project_id)
    if role != 'owner':
        raise HTTPException(status_code=403, detail="Only owner can delete project")
    
    success = delete_project(db, project_id)
    if not success:
        raise HTTPException(status_code=404, detail="Project not found")
    
    return {"message": "Project deleted successfully"}

@router.post("/project/{project_id}/invite", tags=["Projects"])
async def invite_user(
    project_id: int,
    user: str,
    authorization: str = None,
    db: Session = Depends(get_db)
):
    token = extract_token(authorization)
    user_id = get_current_user(token)
    
    role = get_user_role(db, user_id, project_id)
    if role != 'owner':
        raise HTTPException(status_code=403, detail="Only owner can invite users")
    
    invited_user = get_user_by_login(db, user)
    if not invited_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if check_project_access(db, invited_user.id, project_id):
        raise HTTPException(status_code=400, detail="User already has access")
    
    grant_project_access(db, invited_user.id, project_id, 'participant')
    return {"message": f"User {user} invited successfully"}