#!/usr/bin/env python
# -*- coding: utf-8 -*-"
#project_assesment - by Jero98772

from fastapi import FastAPI, Header
from fastapi.middleware.cors import CORSMiddleware
from core.db.database import Base, engine
from core.apps import auth, projects, documents

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Project Management API",
    description="API for managing projects and documents",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(projects.router)
app.include_router(documents.router)

@app.get("/", tags=["Root"])
async def root():
    return {"message": "Project Management API is running"}
