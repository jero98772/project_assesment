# 📋 Project Execution Plan — User Stories (Tickets)

## Epic 1: Authentication & User Management

### 🧾 Ticket 1 — User Registration

**Endpoint:** `POST /auth`
**As a** new user
**I want** to register by providing a login, password, and password confirmation
**So that** I can create an account and access the system

**Acceptance Criteria:**

* Input validated with Pydantic (`login`, `password`, `repeat_password`)
* Password and repeat password must match
* Login must be unique
* Store hashed password in the database
* Return success message and user ID

---

### 🧾 Ticket 2 — User Login

**Endpoint:** `POST /login`
**As a** registered user
**I want** to log in using my credentials
**So that** I can receive a JWT to access authorized routes

**Acceptance Criteria:**

* Validate input with Pydantic (`login`, `password`)
* Verify login and password hash
* Issue a JWT token valid for 1 hour
* Include user ID and role (admin, participant) in JWT claims

---

## Epic 2: Project Management

### 🧾 Ticket 3 — Create Project

**Endpoint:** `POST /projects`
**As a** logged-in user
**I want** to create a project with a name and description
**So that** I can manage documents and collaborators within it

**Acceptance Criteria:**

* Validate JWT token and extract user ID
* Validate input (`name`, `description`) with Pydantic
* Save project in DB and assign current user as project owner
* Return full project details (ID, name, description, owner_id, created_at)

---

### 🧾 Ticket 4 — Get All Accessible Projects

**Endpoint:** `GET /projects`
**As a** logged-in user
**I want** to view all projects I have access to
**So that** I can see details and documents of each project

**Acceptance Criteria:**

* Validate JWT token
* Retrieve all projects where user is owner or participant
* Return list of projects including details + documents

---

### 🧾 Ticket 5 — Get Project Details

**Endpoint:** `GET /project/<project_id>/info`
**As a** user with project access
**I want** to retrieve detailed info about a specific project
**So that** I can review its details

**Acceptance Criteria:**

* Validate JWT token and check access rights
* Return project’s details (ID, name, description, owner_id, documents)

---

### 🧾 Ticket 6 — Update Project Details

**Endpoint:** `PUT /project/<project_id>/info`
**As a** project owner
**I want** to update my project’s name or description
**So that** I can modify its information

**Acceptance Criteria:**

* Validate JWT and verify ownership
* Validate input (`name`, `description`) with Pydantic
* Update DB and return updated project details

---

### 🧾 Ticket 7 — Delete Project

**Endpoint:** `DELETE /project/<project_id>`
**As a** project owner
**I want** to delete my project
**So that** I can remove it and its documents permanently

**Acceptance Criteria:**

* Validate JWT and verify ownership
* Delete project and all related documents
* Return success message

---

## Epic 3: Document Management

### 🧾 Ticket 8 — Get All Documents of Project

**Endpoint:** `GET /project/<project_id>/documents`
**As a** project member
**I want** to list all documents in a project
**So that** I can view and manage them

**Acceptance Criteria:**

* Validate JWT and project access
* Return list of documents (IDs, names, upload_date, metadata)

---

### 🧾 Ticket 9 — Upload Documents

**Endpoint:** `POST /project/<project_id>/documents`
**As a** project member
**I want** to upload one or more documents
**So that** I can store files in the project

**Acceptance Criteria:**

* Validate JWT and project access
* Accept multiple files (multipart/form-data)
* Save files to storage and record in DB
* Return metadata for uploaded documents

---

### 🧾 Ticket 10 — Download Document

**Endpoint:** `GET /document/<document_id>`
**As a** project member
**I want** to download a document
**So that** I can view or use it locally

**Acceptance Criteria:**

* Validate JWT and project access
* Stream file to client

---

### 🧾 Ticket 11 — Update Document

**Endpoint:** `PUT /document/<document_id>`
**As a** project member
**I want** to replace or update a document
**So that** I can keep the latest version

**Acceptance Criteria:**

* Validate JWT and project access
* Replace file or update metadata in DB
* Return updated document info

---

### 🧾 Ticket 12 — Delete Document

**Endpoint:** `DELETE /document/<document_id>`
**As a** project member
**I want** to delete a document
**So that** I can remove outdated files

**Acceptance Criteria:**

* Validate JWT and project access
* Delete document from storage and DB
* Return success message

---

## Epic 4: Access & Sharing

### 🧾 Ticket 13 — Invite User to Project

**Endpoint:** `POST /project/<project_id>/invite?user=<login>`
**As a** project owner
**I want** to grant access to another user
**So that** they can collaborate on the project

**Acceptance Criteria:**

* Validate JWT and ownership
* Find target user by login
* Add as participant in project access table
* Return confirmation message

---

### 🧾 Ticket 14 (Optional) — Share Project via Email

**Endpoint:** `GET /project/<project_id>/share?with=<email>`
**As a** project owner
**I want** to share a project with an external user via email
**So that** they can join using a secure link

**Acceptance Criteria:**

* Validate JWT and ownership
* Generate a time-limited join link with a hashed token
* Send email via configured SMTP
* Return confirmation message

---

## Epic 5: Testing & Deployment

### 🧾 Ticket 15 — Unit & Integration Tests

**As a** developer
**I want** to test each endpoint’s functionality and security
**So that** I can ensure reliability and correctness

**Acceptance Criteria:**

* Use `pytest` + `httpx` for async FastAPI testing
* Cover all CRUD operations and auth cases
* Include token expiration and invalid token tests

---
## Epic 5: Dockerizate & upload to dockerHub

### 🧾 Ticket 16 — add Docker fie  & add docker.yalm

**As a** DevOps engineer
**I want** to containerize the service with Docker and configure `.env`  i need to dockerizate the database too
**So that** it can be deployed easily in production

**Acceptance Criteria:**

* Create `Dockerfile` and `docker-compose.yml`
* Environment variables for JWT secret, DB URL, email settings

---

### 🧾 Ticket 17 — Upload to dockerhub

**As a** DevOps engineer
**I want** Prepare my project for do docker pull from aws
**So that** it can be deployed easily in production

**Acceptance Criteria:**

* run `docker pull registry.example.com/myimage:latest`  without problem 
* Ready for deployment to services like Render, Fly.io, or AWS

---

## 🌐 Epic 6: AWS Network & Public Accessibility

### 🧾 Ticket 20 — Enable Public IP Access for the Service

**As a** DevOps engineer
**I want** to configure my AWS deployment so that the FastAPI service can be accessed via a public IP or DNS endpoint
**So that** users and developers can interact with the API externally

**Acceptance Criteria:**

* Configure AWS EC2 instance or ECS service to have a **public IP address**

  * Port **80 (HTTP)**
  * Port **443 (HTTPS)** (optional, if SSL/TLS enabled)
* Update **VPC and subnet configuration** to allow public routing:

  * Subnet must be public (associated with an Internet Gateway)
  * Instance must have “Auto-assign public IPv4” enabled
* Verify connectivity by accessing `http://<public-ip>:<port>`

**Deliverables:**

* Updated AWS network configuration (VPC, subnets)
* Publicly accessible API URL

