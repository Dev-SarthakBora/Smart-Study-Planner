
# PrepPal - Smart Study Planner 🚀

**Your AI-Powered Study Partner for Smarter Learning**

PrepPal is a comprehensive study assistant that uses RAG (Retrieval-Augmented Generation) to help students learn from their study materials through intelligent chat, automated quiz generation, and personalized study planning.

## ✨ Features

- **📚 Document Upload & Processing**: Upload PDF study materials with automatic text extraction and chunking
- **💬 RAG-Powered Chat**: Ask questions and get answers based on your uploaded documents
- **🧠 AI Quiz Generation**: Generate customized quizzes from your study materials
- **📅 Smart Study Planning**: Create personalized day-by-day study schedules
- **🎤 Voice Integration**: (Integration points for Agora Conversational AI)
- **📊 Progress Tracking**: Monitor your learning progress with statistics and analytics

## 🏗️ Architecture

### Tech Stack

**Backend:**
- FastAPI (REST API)
- Google Generative AI (Gemini) for LLM
- NumPy for vector operations
- Pydantic for data validation

**Frontend:**
- Streamlit (Interactive UI)
- Custom CSS with vibrant gradient themes
- Responsive layout matching the design specs

**Data:**
- In-memory storage (Python dictionaries)
- Optional SQLite for persistence
- Vector embeddings for semantic search

## 📦 Installation

### Prerequisites

- Python 3.10 or higher
- pip package manager
- Google API Key (for Gemini)

### Setup Steps

1. **Clone the repository**
```bash
git clone <your-repo-url>
cd preppal
```

2. **Create virtual environment**
```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment variables**

Create a `.env` file in the root directory:

```env
# Google Generative AI
GOOGLE_API_KEY=your_google_api_key_here

# Agora (Optional - for voice features)
AGORA_APP_ID=your_agora_app_id
AGORA_APP_CERT=your_agora_app_certificate

# API Configuration
API_HOST=localhost
API_PORT=8000
```

5. **Prepare demo data** (Optional)

Place a sample PDF in `data/demo.pdf` for immediate testing.

## 🚀 Running the Application

### Start Backend Server

In one terminal:

```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

API Documentation: `http://localhost:8000/docs`

### Start Frontend

In another terminal:

```bash
cd frontend
streamlit run app.py
```

The app will open automatically in your browser at `http://localhost:8501`

## 📖 Usage Guide

### 1. Upload Documents

- Navigate to the **Documents** tab
- Click "Choose a PDF file" and select your study material
- (Optional) Enter a subject name
- Click "UPLOAD & PROCESS"
- The system will extract text and create embeddings

### 2. Chat with PrepPal

- Go to the **Chat** tab
- Select which document(s) to query (or "All Documents")
- Type your question in the input box
- Click "Send" or press Enter
- PrepPal will retrieve relevant information and answer based on your materials

### 3. Generate Quizzes

- Navigate to the **Quizzes** tab
- Enter a topic (optional) or leave blank to quiz on all materials
- Select number of questions (3, 5, or 10)
- Click "GENERATE QUIZ"
- Answer the multiple-choice questions
- Click "SUBMIT QUIZ" to see your score and explanations

### 4. Create Study Plans

- Go to the **Study Plans** tab
- Set your exam date
- Choose daily study hours (1-12 hours)
- List your subjects (one per line)
- Click "GENERATE PLAN"
- View your personalized day-by-day schedule

### 5. Dashboard Overview

- The **Dashboard** tab shows:
  - Total documents uploaded
  - Number of chat sessions
  - Active study plans
  - Quizzes taken
  - Quick action buttons for all features

## 🎤 Voice Integration (Agora)

Voice features are designed to integrate with Agora Conversational AI:

### Setup for Voice (Optional)

1. Sign up at [Agora.io](https://www.agora.io/)
2. Create a project and get credentials
3. Add credentials to `.env`:
   ```env
   AGORA_APP_ID=your_app_id
   AGORA_APP_CERT=your_certificate
   ```

### Voice Flow

1. Click the microphone icon in the chat interface
2. Speak your question
3. Audio is transcribed using speech-to-text
4. Text is sent to the chat endpoint
5. Response is converted to speech and played back

**Note:** Full Agora integration requires additional SDK setup. The prototype includes integration points and fallback mechanisms.

## 🔧 API Endpoints

### Document Management

- `POST /upload` - Upload and process a PDF document
- `GET /documents` - List all uploaded documents
- `DELETE /documents/{doc_id}` - Delete a document

### Chat & RAG

- `POST /chat` - Send a query and get RAG-based answer
  ```json
  {
    "user_id": "string",
    "message": "string",
    "doc_ids": ["string"] // optional
  }
  ```

### Quiz Generation

- `POST /quiz` - Generate quiz questions
  ```json
  {
    "topic": "string", // optional
    "doc_ids": ["string"], // optional
    "num_questions": 5
  }
  ```

### Study Planning

- `POST /plan` - Create a study plan
  ```json
  {
    "exam_date": "2025-12-31",
    "hours_per_day": 4.0,
    "subjects": ["Math", "Physics"]
  }
  ```

## 🎨 Design Philosophy

PrepPal uses a bold, modern design inspired by the provided mockups:

- **Color Palette**: Cyan (#00D4FF), Magenta (#FF00E5), Yellow (#FFE600)
- **Gradients**: Dynamic backgrounds for energy and engagement
- **Bold Borders**: 2-3px black borders for clarity
- **Typography**: Clean, sans-serif fonts with bold headers
- **Layout**: Responsive grid with clear information hierarchy

## 🔐 Security Notes

- Never commit `.env` file to version control
- Keep API keys secure
- In production, use proper authentication
- Implement rate limiting for API endpoints
- Validate and sanitize all user inputs

## 🚧 Known Limitations (Prototype)

1. **Embeddings**: Currently uses random vectors; replace with actual Gemini embeddings
2. **LLM Responses**: Uses stub responses; integrate real Gemini API calls
3. **PDF Parsing**: Basic implementation; enhance with PyMuPDF for production
4. **Storage**: In-memory only; add database persistence for production
5. **Voice**: Integration points provided; requires Agora SDK setup
6. **Authentication**: No user auth in prototype; add for multi-user deployment

## 🛠️ Development Roadmap

### Phase 1 (Current - Prototype)
- ✅ Core backend API
- ✅ Streamlit frontend
- ✅ Document upload
- ✅ RAG chat interface
- ✅ Quiz generation
- ✅ Study planning

### Phase 2 (Production)
- [ ] Real Gemini embeddings integration
- [ ] Full LLM response generation
- [ ] Database persistence (PostgreSQL)
- [ ] User authentication & authorization
- [ ] Advanced PDF parsing with images
- [ ] Full Agora voice integration

### Phase 3 (Advanced)
- [ ] Mobile app (React Native)
- [ ] Collaborative study groups
- [ ] Spaced repetition algorithm
- [ ] Performance analytics dashboard
- [ ] Multi-language support
- [ ] Flashcard generation

## 🤝 Contributing

This is a hackathon project. To contribute:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details

## 🎓 Credits

**Built for Hackathon 2025**

PrepPal - Learn Smarter, Not Harder

Created with ❤️ using FastAPI, Streamlit, and Google Generative AI

## 📞 Support

For questions or issues:
- Open an issue on GitHub
- Contact: [your-email@example.com]

---

**Happy Studying! 📚✨**