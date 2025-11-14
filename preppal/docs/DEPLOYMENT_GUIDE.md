# PrepPal Deployment Guide

## Local Development
Covered in QUICKSTART.md

## Docker Deployment

### Create Dockerfile for Backend
```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ ./backend/
COPY .env .

EXPOSE 8000

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Create Dockerfile for Frontend
```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY frontend/ ./frontend/

EXPOSE 8501

CMD ["streamlit", "run", "frontend/app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### Docker Compose
```yaml
version: '3.8'

services:
  backend:
    build:
      context: .
      dockerfile: Dockerfile.backend
    ports:
      - "8000:8000"
    environment:
      - GOOGLE_API_KEY=${GOOGLE_API_KEY}
    volumes:
      - ./data:/app/data
  
  frontend:
    build:
      context: .
      dockerfile: Dockerfile.frontend
    ports:
      - "8501:8501"
    depends_on:
      - backend
    environment:
      - API_BASE_URL=http://backend:8000
```

Run with:
```bash
docker-compose up --build
```

## Cloud Deployment

### Railway (Recommended for Backend)
1. Connect GitHub repo
2. Add environment variables
3. Deploy automatically

### Streamlit Cloud (Recommended for Frontend)
1. Push to GitHub
2. Connect at share.streamlit.io
3. Add secrets in dashboard

### AWS EC2
1. Launch Ubuntu instance
2. Install Python 3.10+
3. Clone repo and setup
4. Use systemd for process management
5. Setup nginx reverse proxy

### Heroku
1. Create `Procfile`: