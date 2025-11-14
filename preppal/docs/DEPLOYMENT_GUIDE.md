# PrepPal Deployment Guide

Comprehensive guide for deploying PrepPal to production environments.

## Table of Contents

1. [Local Development](#local-development)
2. [Docker Deployment](#docker-deployment)
3. [Cloud Platforms](#cloud-platforms)
4. [Production Checklist](#production-checklist)
5. [Monitoring & Maintenance](#monitoring--maintenance)

---

## Local Development

Covered in `QUICKSTART.md`. Summary:

```bash
# Setup
./scripts/setup.sh  # or setup.bat on Windows

# Run
cd backend && uvicorn main:app --reload  # Terminal 1
cd frontend && streamlit run app.py      # Terminal 2
```

---

## Docker Deployment

### Prerequisites
- Docker Desktop or Docker Engine
- Docker Compose

### Step 1: Create Dockerfiles

**`Dockerfile.backend`**
```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY backend/ ./backend/
COPY data/ ./data/

# Create upload directory
RUN mkdir -p /app/data/uploads

EXPOSE 8000

# Run application
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**`Dockerfile.frontend`**
```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY frontend/ ./frontend/

EXPOSE 8501

# Health check
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

# Run Streamlit
CMD ["streamlit", "run", "frontend/app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### Step 2: Create docker-compose.yml

```yaml
version: '3.8'

services:
  backend:
    build:
      context: .
      dockerfile: Dockerfile.backend
    container_name: preppal-backend
    ports:
      - "8000:8000"
    environment:
      - GOOGLE_API_KEY=${GOOGLE_API_KEY}
      - AGORA_APP_ID=${AGORA_APP_ID}
      - AGORA_APP_CERT=${AGORA_APP_CERT}
    volumes:
      - ./data:/app/data
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000"]
      interval: 30s
      timeout: 10s
      retries: 3
  
  frontend:
    build:
      context: .
      dockerfile: Dockerfile.frontend
    container_name: preppal-frontend
    ports:
      - "8501:8501"
    environment:
      - API_BASE_URL=http://backend:8000
    depends_on:
      - backend
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8501/_stcore/health"]
      interval: 30s
      timeout: 10s
      retries: 3

volumes:
  data:
```

### Step 3: Build and Run

```bash
# Build images
docker-compose build

# Run containers
docker-compose up -d

# View logs
docker-compose logs -f

# Stop containers
docker-compose down
```

### Step 4: Access Application

- Backend: http://localhost:8000
- Frontend: http://localhost:8501

---

## Cloud Platforms

### 1. Railway (Recommended for Quick Deploy)

**Backend Deployment:**

1. Push code to GitHub
2. Visit [railway.app](https://railway.app)
3. Click "New Project" → "Deploy from GitHub"
4. Select your repository
5. Add environment variables:
   ```
   GOOGLE_API_KEY=your_key
   ```
6. Railway auto-detects Python and deploys

**Frontend Deployment:**

1. Create new service in same project
2. Select repository again
3. Set start command:
   ```
   streamlit run frontend/app.py --server.port $PORT
   ```
4. Deploy

### 2. Render

**Backend:**

1. Create new Web Service
2. Connect GitHub repository
3. Settings:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT`
4. Add environment variables

**Frontend:**

1. Deploy to Streamlit Cloud (see below)
2. Or create another Render service with:
   - **Start Command**: `cd frontend && streamlit run app.py --server.port $PORT`

### 3. Streamlit Cloud (Frontend Only)

1. Push code to GitHub
2. Visit [share.streamlit.io](https://share.streamlit.io)
3. Click "New app"
4. Select repository and branch
5. Set main file path: `frontend/app.py`
6. Add secrets in dashboard (API keys)
7. Deploy

**Secrets format** (`.streamlit/secrets.toml`):
```toml
GOOGLE_API_KEY = "your_key_here"
API_BASE_URL = "https://your-backend.railway.app"
```

### 4. AWS EC2

**Launch Instance:**

```bash
# SSH into instance
ssh -i your-key.pem ubuntu@your-ip

# Update system
sudo apt update && sudo apt upgrade -y

# Install Python
sudo apt install python3.10 python3.10-venv python3-pip -y

# Clone repository
git clone https://github.com/your-repo/preppal.git
cd preppal

# Setup
chmod +x scripts/setup.sh
./scripts/setup.sh

# Install nginx
sudo apt install nginx -y

# Configure nginx (see nginx config below)
sudo nano /etc/nginx/sites-available/preppal

# Enable site
sudo ln -s /etc/nginx/sites-available/preppal /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# Setup systemd services (see systemd configs below)
```

**Nginx Configuration** (`/etc/nginx/sites-available/preppal`):
```nginx
server {
    listen 80;
    server_name your-domain.com;

    # Backend API
    location /api/ {
        proxy_pass http://localhost:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # Frontend
    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }
}
```

**Systemd Service for Backend** (`/etc/systemd/system/preppal-backend.service`):
```ini
[Unit]
Description=PrepPal Backend
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/preppal
Environment="PATH=/home/ubuntu/preppal/venv/bin"
ExecStart=/home/ubuntu/preppal/venv/bin/uvicorn backend.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

**Systemd Service for Frontend** (`/etc/systemd/system/preppal-frontend.service`):
```ini
[Unit]
Description=PrepPal Frontend
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/preppal
Environment="PATH=/home/ubuntu/preppal/venv/bin"
ExecStart=/home/ubuntu/preppal/venv/bin/streamlit run frontend/app.py --server.port 8501
Restart=always

[Install]
WantedBy=multi-user.target
```

**Start Services:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable preppal-backend preppal-frontend
sudo systemctl start preppal-backend preppal-frontend
sudo systemctl status preppal-backend preppal-frontend
```

### 5. Heroku

**Backend:**

Create `Procfile`:
```
web: cd backend && uvicorn main:app --host=0.0.0.0 --port=${PORT:-8000}
```

Deploy:
```bash
heroku create preppal-backend
heroku config:set GOOGLE_API_KEY=your_key
git push heroku main
```

**Frontend:**

Create separate Heroku app or use Streamlit Cloud.

---

## Production Checklist

### Security

- [ ] Enable HTTPS (use Let's Encrypt or cloud provider SSL)
- [ ] Implement JWT authentication
- [ ] Add rate limiting (e.g., 100 requests/hour per IP)
- [ ] Sanitize all user inputs
- [ ] Enable CORS only for trusted domains
- [ ] Use environment variables for all secrets
- [ ] Implement API key rotation
- [ ] Add request validation middleware

### Database

- [ ] Replace in-memory storage with PostgreSQL/MongoDB
- [ ] Implement database migrations (Alembic)
- [ ] Set up regular backups
- [ ] Add database connection pooling
- [ ] Index frequently queried fields

### Storage

- [ ] Move PDF uploads to cloud storage (S3/GCS)
- [ ] Implement file size limits
- [ ] Add virus scanning for uploads
- [ ] Set up CDN for static assets

### Performance

- [ ] Add Redis for caching
- [ ] Implement query result caching
- [ ] Use Gunicorn with multiple workers
- [ ] Enable gzip compression
- [ ] Optimize database queries
- [ ] Add pagination for large lists

### Monitoring

- [ ] Set up error tracking (Sentry)
- [ ] Implement structured logging
- [ ] Add performance monitoring (DataDog/New Relic)
- [ ] Create health check endpoints
- [ ] Set up uptime monitoring
- [ ] Configure alerting for errors

### Testing

- [ ] Write unit tests (pytest)
- [ ] Add integration tests
- [ ] Implement CI/CD pipeline (GitHub Actions)
- [ ] Set up staging environment
- [ ] Perform load testing

---

## Monitoring & Maintenance

### Logging

**Structured Logging** (add to backend):
```python
import logging
import json
from datetime import datetime

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
        }
        return json.dumps(log_data)

# Configure
logging.basicConfig(level=logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(JSONFormatter())
logger = logging.getLogger('preppal')
logger.addHandler(handler)
```

### Health Checks

Add to `backend/main.py`:
```python
@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "database": "connected",  # Add actual DB check
        "documents": len(documents_store)
    }
```

### Metrics

Install Prometheus client:
```python
from prometheus_client import Counter, Histogram, generate_latest

request_count = Counter('http_requests_total', 'Total HTTP requests')
request_duration = Histogram('http_request_duration_seconds', 'Request duration')

@app.middleware("http")
async def metrics_middleware(request, call_next):
    request_count.inc()
    with request_duration.time():
        response = await call_next(request)
    return response

@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type="text/plain")
```

### Backup Strategy

**Database Backups:**
```bash
# Daily backup script
#!/bin/bash
BACKUP_DIR="/backups"
DATE=$(date +%Y%m%d_%H%M%S)

# PostgreSQL
pg_dump preppal_db > "$BACKUP_DIR/db_$DATE.sql"

# Keep only last 7 days
find $BACKUP_DIR -name "db_*.sql" -mtime +7 -delete
```

**Automated Backups with Cron:**
```bash
# Edit crontab
crontab -e

# Add daily backup at 2 AM
0 2 * * * /path/to/backup-script.sh
```

---

## Scaling Strategies

### Horizontal Scaling

1. **Load Balancer**: Use nginx or cloud load balancer
2. **Multiple Instances**: Run multiple backend containers
3. **Database Replication**: Master-slave setup
4. **Distributed Cache**: Redis Cluster

### Vertical Scaling

1. Increase server resources (CPU, RAM)
2. Optimize database queries
3. Use faster storage (SSD)

---

## Rollback Procedure

```bash
# Docker
docker-compose down
docker-compose up -d --build  # Rebuild from previous version

# Git
git revert HEAD
git push

# Systemd
sudo systemctl restart preppal-backend
sudo systemctl restart preppal-frontend
```

---

## Support

For deployment issues:
- Check logs: `docker-compose logs` or `sudo journalctl -u preppal-*`
- GitHub Issues
- Email: devops@preppal.dev