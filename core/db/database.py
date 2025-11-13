#!/usr/bin/env python
# -*- coding: utf-8 -*-
# project_assesment - by Jero98772
"""
File for database operations like migrations, create tables and more
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base


# Read database configuration from environment variables
DB_USER = os.getenv("POSTGRES_USER", "your_db_user")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "your_password")
DB_HOST = os.getenv("POSTGRES_HOST", "localhost")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")
DB_NAME = os.getenv("POSTGRES_DB", "projects_db")

# Construct the database URL dynamically
DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()