# PrepPal Project Structure

```
preppal/
│
├── backend/
│   ├── __init__.py
│   ├── main.py                 # Main FastAPI application
│   ├── models.py               # Pydantic models (optional separation)
│   ├── rag_engine.py          # RAG logic (optional separation)
│   └── utils.py               # Helper functions
│
├── frontend/
│   ├── app.py                 # Main Streamlit application
│   ├── components/            # Reusable UI components (optional)
│   │   ├── __init__.py
│   │   ├── chat.py
│   │   ├── documents.py
│   │   └── quiz.py
│   └── styles/                # CSS and styling
│       └── custom.css
│
├── data/
│   ├── uploads/               # Uploaded PDFs (auto-created)
│   └── demo.pdf              # Sample PDF for testing
│
├── tests/
│   ├── __init__.py
│   ├── test_backend.py       # Backend API tests
│   └── test_rag.py           # RAG functionality tests
│
├── docs/
│   ├── API.md                # API documentation
│   ├── DEPLOYMENT.md         # Deployment guide
│   └── ARCHITECTURE.md       # System architecture
│
├── scripts/
│   ├── setup.sh              # Setup script for Unix
│   ├── setup.bat             # Setup script for Windows
│   └── create_demo_data.py   # Generate demo PDFs
│
├── .env.template             # Environment variables template
├── .env                      # Actual environment variables (gitignored)
├── .gitignore               # Git ignore rules
├── requirements.txt         # Python dependencies
├── README.md               # Main documentation
├── LICENSE                 # MIT License
└── PROJECT_STRUCTURE.md    # This file
```

## File Purposes

### Backend Files

**backend/main.py**
- FastAPI application setup
- API endpoints for upload, chat, quiz, and planning
- CORS middleware configuration
- In-memory storage management

**backend/models.py** (Optional)
- Pydantic models for request/response validation
- Data schemas for documents, chats, quizzes, plans

**backend/rag_engine.py** (Optional)
- Text chunking logic
- Embedding generation
- Vector similarity search
- Context retrieval

**backend/utils.py** (Optional)
- PDF parsing utilities
- Text preprocessing
- Helper functions

### Frontend Files

**frontend/app.py**
- Streamlit UI configuration
- Multi-tab interface (Dashboard, Documents, Chat, Plans, Quizzes)
- API integration
- Session state management
- Custom CSS styling

**frontend/components/** (Optional)
- Modular UI components
- Reusable widgets
- Custom Streamlit elements

### Data Files

**data/demo.pdf**
- Sample study material for immediate testing
- Should contain educational content (e.g., computer networks notes)

**data/uploads/**
- Runtime directory for user-uploaded PDFs
- Auto-created by backend on first upload

### Configuration Files

**.env.template**
- Template for environment variables
- Documents all required configuration
- Should be committed to git

**.env**
- Actual environment variables with secrets
- Never committed to git
- Created by copying .env.template

**requirements.txt**
- All Python package dependencies
- Pinned versions for reproducibility
- Organized by category (backend, frontend, optional)

### Documentation

**README.md**
- Main project documentation
- Setup and installation instructions
- Usage guide
- API overview

**docs/API.md** (Optional)
- Detailed API documentation
- Request/response examples
- Error codes and handling

**docs/DEPLOYMENT.md** (Optional)
- Production deployment guide
- Docker configuration
- Cloud platform instructions

### Testing

**tests/**
- Unit tests for backend logic
- Integration tests for API endpoints
- RAG functionality tests

### Scripts

**scripts/setup.sh** (Unix/macOS)
```bash
#!/bin/bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.template .env
echo "Setup complete! Edit .env with your API keys."
```

**scripts/setup.bat** (Windows)
```batch
@echo off
python -m venv venv
call venv\Scripts\activate
pip install -r requirements.txt
copy .env.template .env
echo Setup complete! Edit .env with your API keys.
```

## Quick Start

1. **Initial Setup**
   ```bash
   # Unix/macOS
   chmod +x scripts/setup.sh
   ./scripts/setup.sh
   
   # Windows
   scripts\setup.bat
   ```

2. **Configure Environment**
   ```bash
   # Edit .env file with your API keys
   nano .env  # or use any text editor
   ```

3. **Run Backend**
   ```bash
   cd backend
   uvicorn main:app --reload
   ```

4. **Run Frontend** (in new terminal)
   ```bash
   cd frontend
   streamlit run app.py
   ```

## Development Workflow

### Adding New Features

1. **Backend API Endpoint**
   - Add route in `backend/main.py`
   - Define Pydantic models for request/response
   - Implement business logic
   - Test with FastAPI docs at `/docs`

2. **Frontend UI**
   - Add UI elements in appropriate tab in `frontend/app.py`
   - Create API call using `requests`
   - Update session state as needed
   - Add custom styling if required

3. **Testing**
   - Write unit tests in `tests/`
   - Run tests: `pytest tests/`
   - Test integration manually

### Best Practices

- Keep backend and frontend separated
- Use environment variables for configuration
- Follow RESTful API conventions
- Maintain consistent code style
- Document all functions and endpoints
- Handle errors gracefully
- Log important events

## Deployment Considerations

### Production Setup

1. **Database**
   - Replace in-memory storage with PostgreSQL/MongoDB
   - Add database migrations

2. **Authentication**
   - Implement JWT tokens
   - Add user registration/login
   - Secure endpoints

3. **File Storage**
   - Use cloud storage (S3, GCS) for PDFs
   - Implement file cleanup policies

4. **Scaling**
   - Deploy backend with Gunicorn/uWSGI
   - Use Redis for caching
   - Implement rate limiting

5. **Monitoring**
   - Add logging (Python logging module)
   - Set up error tracking (Sentry)
   - Monitor API performance

### Docker Deployment (Optional)

Create `docker-compose.yml`:
```yaml
version: '3.8'
services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - GOOGLE_API_KEY=${GOOGLE_API_KEY}
  
  frontend:
    build: ./frontend
    ports:
      - "8501:8501"
    depends_on:
      - backend
```

## Notes

- This structure is optimized for a hackathon prototype
- For production, consider microservices architecture
- Add more comprehensive error handling
- Implement proper logging and monitoring
- Consider adding automated tests (pytest, unittest)
- Use code formatters (black, flake8) for consistency