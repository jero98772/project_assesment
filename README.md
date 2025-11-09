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


\c projects_db

-- Grant privileges on the public schema
GRANT ALL ON SCHEMA public TO your_db_user;

-- Also allow creation of objects in it
ALTER SCHEMA public OWNER TO your_db_user;

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE projects_db TO your_db_user;

-- Exit
\q

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
curl -c cookies.txt -X POST "http://127.0.0.1:9601/login" \
  -H "Content-Type: application/json" \
  -d '{"login":"user1","password":"pass123"}'
```

### Create Project
```bash
curl -b cookies.txt -X POST "http://127.0.0.1:9601/projects" \
  -H "Content-Type: application/json" \
  -d '{"name":"My Project","description":"Test project"}'
```

### Get All Projects
```bash
curl -b cookies.txt -X GET "http://127.0.0.1:9601/projects"
```
### Get info for project with ID 1
```bash
curl -b cookies.txt -X GET "http://127.0.0.1:9601/project/1/info"
```

### Update info for project with ID 1
```bash

curl -b cookies.txt -X PUT "http://127.0.0.1:9601/project/1/info" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Updated Project Name",
    "description": "Updated project description with more details"
  }'
```


### Delete project with ID 1
```bash
curl -b cookies.txt -X DELETE "http://127.0.0.1:9601/project/1"
```

### Upload Documents (yes Documents in plural)
```bash
curl -b cookies.txt -X POST "http://127.0.0.1:9601/project/2/documents" \
  -F "files=@document3.txt"
```

### Get Documents
```bash
curl -b cookies.txt -X GET "http://127.0.0.1:9601/project/2/documents"
```

### Delete Document

```bash
curl -b cookies.txt -X DELETE "http://127.0.0.1:9601/document/2"
```

### Download File

```bash
curl -b cookies.txt -X GET "http://127.0.0.1:9601/document/2"   -o downloaded_file.txt
```

### Update just the filename
```
curl -b cookies.txt -X PUT "http://127.0.0.1:9601/document/123" \
  -F "original_filename=renamed_document.txt"
```
### Update both filename and content
```
curl -b cookies.txt -X PUT "http://127.0.0.1:9601/document/123" \
  -F "file=@new_document.txt" \
  -F "original_filename=renamed_document.txt"
```
