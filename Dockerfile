# ---------- Stage 1: Builder ----------
FROM python:3.11-slim AS builder

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && pip install --prefix=/install -r requirements.txt

# ---------- Stage 2: Runtime ----------
FROM python:3.11-slim

# Environment variables for Python
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# PostgreSQL connection configuration (can be overridden in docker-compose or at runtime)
ENV POSTGRES_DB=projects_db
ENV POSTGRES_USER=your_db_user
ENV POSTGRES_PASSWORD=your_password
ENV POSTGRES_HOST=db
ENV POSTGRES_PORT=5432

# Set working directory
WORKDIR /app

# Copy installed dependencies and source code
COPY --from=builder /install /usr/local
COPY . .

# Expose the app port
EXPOSE 9601

# Command to run the application
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "9601"]


