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
from core.tools.tools import verify_token
from core.apps.projects import extract_token, get_current_user
import os
import uuid
from pathlib import Path

router = APIRouter()

UPLOAD_DIR = "uploads"
Path(UPLOAD_DIR).mkdir(exist_ok=True)

ALLOWED_EXTENSIONS = {'pdf', 'docx'}

def get_document_dto(doc):
    """
    Convert a Document model instance to a Data Transfer Object (DTO).
    
    This helper function transforms a SQLAlchemy Document object into a
    serializable dictionary for API responses, including user-friendly
    field names and formatted timestamps.
    
    Args:
        doc (Document): The Document model instance to convert
        
    Returns:
        dict: Document DTO containing:
            - id: Document ID
            - original_filename: Original filename as uploaded by user
            - file_type: File extension/type
            - uploaded_by: Username of the uploader
            - created_at: ISO format creation timestamp
            - updated_at: ISO format last update timestamp
    """
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
    """
    Retrieve all documents associated with a specific project.
    
    This endpoint returns a list of all documents in a project that the
    authenticated user has access to. Users must have at least participant
    access to the project to view its documents.
    
    Args:
        project_id (int): The ID of the project to retrieve documents from
        authorization (str, optional): Bearer token for authentication
        db (Session): Database session dependency
        
    Returns:
        list: List of document DTOs containing document metadata
        
    Raises:
        HTTPException: 
            - 401 error if user is not authenticated
            - 403 error if user doesn't have access to the project
    """
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
    """
    Upload one or multiple documents to a project.
    
    This endpoint allows authenticated users with project access to upload
    documents. Files are validated for allowed extensions, stored with unique
    filenames, and associated with the project in the database.
    
    Args:
        project_id (int): The ID of the project to upload documents to
        files (list[UploadFile]): List of files to upload (multipart form data)
        authorization (str, optional): Bearer token for authentication
        db (Session): Database session dependency
        
    Returns:
        dict: Upload success response containing:
            - documents: List of uploaded document DTOs
            
    Raises:
        HTTPException: 
            - 401 error if user is not authenticated
            - 403 error if user doesn't have access to the project
            - 404 error if project doesn't exist
            - 400 error if file type is not allowed (only PDF and DOCX permitted)
            
    Notes:
        - Files are stored in the 'uploads' directory with UUID-prefixed names
        - Original filenames are preserved in the database
        - Maximum file size limits should be configured at the web server level
    """
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
    """
    Download a specific document file.
    
    This endpoint allows authenticated users with project access to download
    the actual document file. The file is served with its original filename.
    
    Args:
        document_id (int): The ID of the document to download
        authorization (str, optional): Bearer token for authentication
        db (Session): Database session dependency
        
    Returns:
        FileResponse: The document file with original filename
        
    Raises:
        HTTPException: 
            - 401 error if user is not authenticated
            - 403 error if user doesn't have access to the project
            - 404 error if document or file doesn't exist
            
    Notes:
        - Uses FastAPI's FileResponse for efficient file streaming
        - Browser will typically download the file with its original name
    """
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
    """
    Update document metadata (rename document).
    
    This endpoint allows project participants and owners to update the
    display name (original filename) of a document without affecting
    the actual stored file.
    
    Args:
        document_id (int): The ID of the document to update
        original_filename (str): New display name for the document
        authorization (str, optional): Bearer token for authentication
        db (Session): Database session dependency
        
    Returns:
        dict: Updated document DTO
        
    Raises:
        HTTPException: 
            - 401 error if user is not authenticated
            - 403 error if user doesn't have appropriate access rights
            - 404 error if document doesn't exist
            
    Notes:
        - Only updates the display name, not the physical file name
        - Requires at least participant role in the project
    """
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
    """
    Permanently delete a document and its associated file.
    
    This endpoint allows project participants and owners to delete a document.
    Both the database record and the physical file are removed from the system.
    
    Args:
        document_id (int): The ID of the document to delete
        authorization (str, optional): Bearer token for authentication
        db (Session): Database session dependency
        
    Returns:
        dict: Success message confirming document deletion
        
    Raises:
        HTTPException: 
            - 401 error if user is not authenticated
            - 403 error if user doesn't have appropriate access rights
            - 404 error if document doesn't exist
            
    Notes:
        - This action is irreversible
        - Both database record and physical file are deleted
        - Requires at least participant role in the project
    """
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