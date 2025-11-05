#!/usr/bin/env python
# -*- coding: utf-8 -*-"
#project_assesment - by Jero98772

from fastapi import APIRouter, HTTPException, Depends, File, UploadFile, Request
from fastapi.responses import FileResponse

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
from datetime import datetime

router = APIRouter()

UPLOAD_DIR = "uploads"
Path(UPLOAD_DIR).mkdir(exist_ok=True)

ALLOWED_EXTENSIONS = {'pdf', 'docx','txt'}

def get_document_dto(doc):
    """
    Convert a Document model instance to a Data Transfer Object (DTO).
    """
    return {
        "id": doc.id,
        "original_filename": doc.original_filename,
        "file_type": doc.file_type,
        "uploaded_by": doc.uploader.login if doc.uploader else "unknown",
        "created_at": doc.created_at.isoformat(),
        "updated_at": doc.updated_at.isoformat()
    }


@router.get("/document/{document_id}", tags=["Documents"])
async def download_document(
    document_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Download a specific document file.
    Authentication via cookies.
    """
    token = extract_token(request)
    user_id = get_current_user(token)
    
    document = get_document_by_id(db, document_id)
    print("\n\n\n")
    print("document")
    print(document)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    if not check_project_access(db, user_id, document.project_id):
        raise HTTPException(status_code=403, detail="Access denied")
    
    if not os.path.exists(document.file_path):
        raise HTTPException(status_code=404, detail="File not found on server")
    
    return FileResponse(document.file_path, filename=document.original_filename)

@router.put("/document/{document_id}", tags=["Documents"])
async def update_doc(
    document_id: int,
    original_filename: str,
    request: Request,
    db: Session = Depends(get_db)
):

    token = extract_token(request)
    user_id = get_current_user(token)
    
    document = get_document_by_id(db, document_id)
    print("\n\n\n")
    print("document")
    print(document)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    if not check_project_access(db, user_id, document.project_id):
        raise HTTPException(status_code=403, detail="Access denied")
    
    role = get_user_role(db, user_id, document.project_id)
    if role not in ['owner', 'participant']:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Get the old file path
    old_file_path = document.file_path
    
    # Check if the old file exists
    print(document.file_path)
    if not os.path.exists(old_file_path):
        raise HTTPException(status_code=404, detail="File not found on server")
    
    # Extract the file extension from the new filename
    new_file_ext = original_filename.split('.')[-1].lower() if '.' in original_filename else document.file_type
    
    # Validate file extension
    if new_file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"File type {new_file_ext} not allowed")
    
    # Generate new unique filename keeping the UUID prefix
    # Extract the UUID part from the current filename
    old_filename_parts = document.filename.split('_', 1)
    if len(old_filename_parts) == 2:
        uuid_part = old_filename_parts[0]
        new_unique_filename = f"{uuid_part}_{original_filename}"
    else:
        # If no UUID prefix exists, generate a new one
        new_unique_filename = f"{uuid.uuid4()}_{original_filename}"
    
    # Create new file path
    new_file_path = os.path.join(UPLOAD_DIR, new_unique_filename)
    
    # Rename the physical file
    try:
        os.rename(old_file_path, new_file_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to rename file: {str(e)}")
    
    # Update document in database with new information
    doc = update_document(
        db, 
        document_id, 
        original_filename,
        new_unique_filename,
        new_file_path,
        new_file_ext
    )
    
    return get_document_dto(doc)

@router.delete("/document/{document_id}", tags=["Documents"])
async def delete_doc(
    document_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Permanently delete a document and its associated file.
    Authentication via cookies.
    """
    token = extract_token(request)
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