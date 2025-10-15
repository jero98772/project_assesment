#!/usr/bin/env python
# -*- coding: utf-8 -*-"
#project_assesment - by Jero98772
"""
File for database operations like migrations, create tables and more
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from core.tools.tools import get_env

DATABASE_URL = SQLALCHEMY_DATABASE_URL = "postgresql+psycopg2://your_db_user:your_password@localhost:5432/projects_db"


engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()