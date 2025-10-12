#!/usr/bin/env python
# -*- coding: utf-8 -*-"
#Epam_assesment - by Jero98772
"""
File for CRUD operations 
"""

from sqlalchemy.orm import Session
from core.db.models import User, Project, Document, project_access
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["sha256_crypt"], deprecated="auto")

# User CRUD
def create_user(db: Session, login: str, email: str, password: str):
    hashed_password = pwd_context.hash(password)
    db_user = User(login=login, email=email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user_by_login(db: Session, login: str):
    return db.query(User).filter(User.login == login).first()

def get_user_by_id(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)

# Project CRUD
def create_project(db: Session, name: str, description: str, owner_id: int):
    db_project = Project(name=name, description=description, owner_id=owner_id)
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    
    db.execute(project_access.insert().values(user_id=owner_id, project_id=db_project.id, role='owner'))
    db.commit()
    return db_project

def get_project_by_id(db: Session, project_id: int):
    return db.query(Project).filter(Project.id == project_id).first()

def get_user_projects(db: Session, user_id: int):
    return db.query(Project).join(project_access).filter(project_access.c.user_id == user_id).all()

def update_project(db: Session, project_id: int, name: str = None, description: str = None):
    db_project = get_project_by_id(db, project_id)
    if db_project:
        if name:
            db_project.name = name
        if description:
            db_project.description = description
        db.commit()
        db.refresh(db_project)
    return db_project

def delete_project(db: Session, project_id: int):
    db_project = get_project_by_id(db, project_id)
    if db_project:
        db.delete(db_project)
        db.commit()
        return True
    return False

def check_project_access(db: Session, user_id: int, project_id: int):
    result = db.query(project_access).filter(
        project_access.c.user_id == user_id,
        project_access.c.project_id == project_id
    ).first()
    return result

def get_user_role(db: Session, user_id: int, project_id: int):
    result = db.query(project_access.c.role).filter(
        project_access.c.user_id == user_id,
        project_access.c.project_id == project_id
    ).first()
    return result[0] if result else None

def grant_project_access(db: Session, user_id: int, project_id: int, role: str = 'participant'):
    db.execute(project_access.insert().values(user_id=user_id, project_id=project_id, role=role))
    db.commit()

# Document CRUD
def create_document(db: Session, project_id: int, filename: str, original_filename: str, file_path: str, file_type: str, uploaded_by: int):
    db_document = Document(
        project_id=project_id,
        filename=filename,
        original_filename=original_filename,
        file_path=file_path,
        file_type=file_type,
        uploaded_by=uploaded_by
    )
    db.add(db_document)
    db.commit()
    db.refresh(db_document)
    return db_document

def get_document_by_id(db: Session, document_id: int):
    return db.query(Document).filter(Document.id == document_id).first()

def get_project_documents(db: Session, project_id: int):
    return db.query(Document).filter(Document.project_id == project_id).all()

def delete_document(db: Session, document_id: int):
    db_document = get_document_by_id(db, document_id)
    if db_document:
        db.delete(db_document)
        db.commit()
        return True
    return False

def update_document(db: Session, document_id: int, original_filename: str = None):
    db_document = get_document_by_id(db, document_id)
    if db_document and original_filename:
        db_document.original_filename = original_filename
        db.commit()
        db.refresh(db_document)
    return db_document
