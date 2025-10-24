# Project_assesment


A FastAPI-based project management service for creating, updating, sharing, and deleting projects with document management.

## Features

- User authentication with JWT tokens (1-hour expiration)
- Project CRUD operations
- Document management (upload, download, update, delete)
- Project sharing with role-based access (owner, participant)
- PostgreSQL database with SQLAlchemy ORM

## Setup

### Prerequisites
- Python 3.10+
- PostgreSQL
- Docker


### Installation

#### Option 1

run with docker:

    sudo docker-compose up --build

#### Options 2

1. Create a virtual environment:
```bash
python -m venv env
source env/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment variables in `.env`:
```
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=localhost
DB_PORT=5432
DB_NAME=projects_db
SECRET_KEY=your-secret-key
```

4. Create database:
```bash
sudo -u postgres createdb projects_db

sudo -u postgres psql

-- Create a user (you can name it however you want)

CREATE USER your_db_user WITH PASSWORD 'your_password';

-- Create a database
CREATE DATABASE projects_db OWNER your_db_user;

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE projects_db TO your_db_user;
```

5. Run the application:
```bash
uvicorn app:app --host 0.0.0.0 --port 9601
```

## API Endpoints

### Authentication
- `POST /auth` - Register new user
- `POST /login` - Login and get JWT token

### Projects
- `POST /projects` - Create project
- `GET /projects` - Get all accessible projects
- `GET /project/{project_id}/info` - Get project details
- `PUT /project/{project_id}/info` - Update project
- `DELETE /project/{project_id}` - Delete project (owner only)
- `POST /project/{project_id}/invite?user=<login>` - Invite user to project

### Documents
- `GET /project/{project_id}/documents` - List project documents
- `POST /project/{project_id}/documents` - Upload documents
- `GET /document/{document_id}` - Download document
- `PUT /document/{document_id}?original_filename=<name>` - Update document
- `DELETE /document/{document_id}` - Delete document

## Testing with cURL

### Register
```bash
curl -X POST "http://127.0.0.1:9601/auth" \
  -H "Content-Type: application/json" \
  -d '{"login":"user1","email":"user1@test.com","password":"pass123","password_repeat":"pass123"}'
```

### Login
```bash
curl -X POST "http://127.0.0.1:9601/login" \
  -H "Content-Type: application/json" \
  -d '{"login":"user1","password":"pass123"}'
```

### Create Project
```bash
curl -X POST "http://127.0.0.1:9601/projects" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"My Project","description":"Test project"}'
```

### Get All Projects
```bash
curl -X GET "http://127.0.0.1:9601/projects" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Upload Documents
```bash
curl -X POST "http://127.0.0.1:9601/project/1/documents" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "files=@/path/to/file.pdf" \
  -F "files=@/path/to/file.docx"
```
