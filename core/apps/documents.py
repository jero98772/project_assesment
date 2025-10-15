#!/usr/bin/env python
# -*- coding: utf-8 -*-"
#project_assesment - by Jero98772

from fastapi import APIRouter, HTTPException, Depends, File, UploadFile
from sqlalchemy.orm import Session
from core.db.database import get_db
from core.db.crud import (
    get_document_by_id, create_document, delete_document,
    get_project_documents, check_project_access, get_user_role, update_document, get_project_by_id
)
from core.tools.tools import (
	verify_token,
	extract_token,
	get_current_user
	)

import os
import uuid
from pathlib import Path

router = APIRouter()

UPLOAD_DIR = "uploads"
Path(UPLOAD_DIR).mkdir(exist_ok=True)

ALLOWED_EXTENSIONS = {'pdf', 'docx'}

def get_document_dto(doc):
    return {
        "id": doc.id,
        "original_filename": doc.original_filename,
        "file_type": doc.file_type,
        "uploaded_by": doc.uploader.login if doc.uploader else "unknown",
        "created_at": doc.created_at.isoformat(),
        "updated_at": doc.updated_at.isoformat()
    }

@router.get("/project/{project_id}/documents", tags=["Documents"])
async def get_documents(
    project_id: int,
    authorization: str = None,
    db: Session = Depends(get_db)
):
    token = extract_token(authorization)
    user_id = get_current_user(token)
    
    if not check_project_access(db, user_id, project_id):
        raise HTTPException(status_code=403, detail="Access denied")
    
    documents = get_project_documents(db, project_id)
    return [get_document_dto(doc) for doc in documents]

@router.post("/project/{project_id}/documents", tags=["Documents"])
async def upload_documents(
    project_id: int,
    files: list[UploadFile] = File(...),
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
    
    uploaded_docs = []
    for file in files:
        file_ext = file.filename.split('.')[-1].lower()
        if file_ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(status_code=400, detail=f"File type {file_ext} not allowed")
        
        unique_filename = f"{uuid.uuid4()}_{file.filename}"
        file_path = os.path.join(UPLOAD_DIR, unique_filename)
        
        with open(file_path, "wb") as f:
            f.write(await file.read())
        
        doc = create_document(
            db, project_id, unique_filename, file.filename,
            file_path, file_ext, user_id
        )
        uploaded_docs.append(get_document_dto(doc))
    
    return {"documents": uploaded_docs}

@router.get("/document/{document_id}", tags=["Documents"])
async def download_document(
    document_id: int,
    authorization: str = None,
    db: Session = Depends(get_db)
):
    token = extract_token(authorization)
    user_id = get_current_user(token)
    
    document = get_document_by_id(db, document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    if not check_project_access(db, user_id, document.project_id):
        raise HTTPException(status_code=403, detail="Access denied")
    
    if not os.path.exists(document.file_path):
        raise HTTPException(status_code=404, detail="File not found on server")
    
    from fastapi.responses import FileResponse
    return FileResponse(document.file_path, filename=document.original_filename)

@router.put("/document/{document_id}", tags=["Documents"])
async def update_doc(
    document_id: int,
    original_filename: str,
    authorization: str = None,
    db: Session = Depends(get_db)
):
    token = extract_token(authorization)
    user_id = get_current_user(token)
    
    document = get_document_by_id(db, document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    if not check_project_access(db, user_id, document.project_id):
        raise HTTPException(status_code=403, detail="Access denied")
    
    role = get_user_role(db, user_id, document.project_id)
    if role not in ['owner', 'participant']:
        raise HTTPException(status_code=403, detail="Access denied")
    
    doc = update_document(db, document_id, original_filename)
    return get_document_dto(doc)

@router.delete("/document/{document_id}", tags=["Documents"])
async def delete_doc(
    document_id: int,
    authorization: str = None,
    db: Session = Depends(get_db)
):
    token = extract_token(authorization)
    user_id = get_current_user(token)
    
    document = get_document_by_id(db, document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    if not check_project_access(db, user_id, document.project_id):
        raise HTTPException(status_code=403, detail="Access denied")
    
    role = get_user_role(db, user_id, document.project_id)
    if role not in ['owner', 'participant']:
        raise HTTPException(status_code=403, detail="Access denied")
    
    if os.path.exists(document.file_path):
        os.remove(document.file_path)
    
    delete_document(db, document_id)
    return {"message": "Document deleted successfully"}