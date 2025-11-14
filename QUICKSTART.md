# PrepPal Quick Start Guide 🚀

Get PrepPal up and running in 5 minutes!

## Prerequisites

- Python 3.10+ installed
- pip package manager
- Google API key (get it free from [Google AI Studio](https://makersuite.google.com/app/apikey))

## 5-Minute Setup

### Step 1: Install Dependencies (2 min)

```bash
# Create and activate virtual environment
python -m venv venv

# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate

# Install packages
pip install -r requirements.txt
```

### Step 2: Configure API Keys (1 min)

```bash
# Copy environment template
cp .env.template .env

# Edit .env and add your Google API key
# On Windows: notepad .env
# On macOS/Linux: nano .env
```

Add your API key:
```env
GOOGLE_API_KEY=your_actual_api_key_here
```

### Step 3: Create Demo Data (30 sec)

```bash
# Generate sample study material
python scripts/create_demo_data.py
```

### Step 4: Start Backend (30 sec)

Open a terminal and run:

```bash
cd backend
uvicorn main:app --reload
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Application startup complete.
```

### Step 5: Start Frontend (30 sec)

Open a **NEW** terminal and run:

```bash
cd frontend
streamlit run app.py
```

Your browser should automatically open to `http://localhost:8501`

## First Steps in PrepPal

### 1. Upload a Document (30 seconds)

1. Click on the **Documents** tab
2. Click "Choose a PDF file"
3. Select `data/demo.pdf` (or your own PDF)
4. Click "UPLOAD & PROCESS"
5. Wait for "✅ Upload successful!"

### 2. Chat with Your Study Material (1 minute)

1. Go to the **Chat** tab
2. Type a question like:
   - "What is the OSI model?"
   - "Explain TCP vs UDP"
   - "What are the types of network topologies?"
3. Click "Send" or press Enter
4. PrepPal will answer based on your uploaded documents!

### 3. Generate a Quiz (1 minute)

1. Navigate to the **Quizzes** tab
2. (Optional) Enter a topic like "Network Security"
3. Select number of questions (5 recommended)
4. Click "GENERATE QUIZ"
5. Answer the multiple choice questions
6. Click "SUBMIT QUIZ" to see your score and explanations

### 4. Create a Study Plan (1 minute)

1. Go to the **Study Plans** tab
2. Set your exam date (e.g., 30 days from today)
3. Choose study hours per day (e.g., 4 hours)
4. Enter subjects, one per line:
   ```
   Computer Networks
   Operating Systems
   Database Management
   Software Engineering
   ```
5. Click "GENERATE PLAN"
6. View your personalized day-by-day schedule!

## Troubleshooting

### Backend won't start

**Error:** `ModuleNotFoundError: No module named 'fastapi'`

**Solution:** Make sure you activated your virtual environment and installed requirements:
```bash
# Activate venv first!
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

pip install -r requirements.txt
```

### Frontend won't start

**Error:** `ModuleNotFoundError: No module named 'streamlit'`

**Solution:** Same as above - activate venv and install requirements.

### Can't upload PDF

**Error:** "Upload failed"

**Solution:** 
1. Check that backend is running (`http://localhost:8000`)
2. Visit `http://localhost:8000/docs` to verify API is accessible
3. Make sure the PDF is valid and under 10MB

### API Key Issues

**Error:** "Invalid API key"

**Solution:**
1. Get a valid key from [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Make sure it's correctly pasted in `.env` file
3. No quotes needed: `GOOGLE_API_KEY=AIzaSy...` ✅
4. Not: `GOOGLE_API_KEY="AIzaSy..."` ❌

### Port Already in Use

**Error:** `Address already in use`

**Solution:**

For backend (port 8000):
```bash
# Find and kill process
# On macOS/Linux:
lsof -ti:8000 | xargs kill -9

# On Windows:
netstat -ano | findstr :8000
taskkill /PID <PID_NUMBER> /F
```

For frontend (port 8501):
```bash
# Same as above, but use 8501 instead of 8000
```

## Testing Without Google API Key

For quick testing without a real API key:

1. The prototype uses stub functions for LLM calls
2. You'll get mock responses, but all features work
3. To use real AI responses, add a valid Google API key

## Next Steps

### Explore Advanced Features

1. **Voice Integration**
   - Click the microphone icon in Chat
   - Requires Agora SDK setup (see README.md)

2. **Multiple Documents**
   - Upload several PDFs
   - Chat with "All Documents" or select specific ones

3. **Custom Study Plans**
   - Experiment with different exam dates
   - Adjust study hours
   - Try different subject combinations

### Customize PrepPal

1. **Change Colors**
   - Edit CSS in `frontend/app.py`
   - Modify the `<style>` section

2. **Add Features**
   - Backend: Add routes in `backend/main.py`
   - Frontend: Add tabs/sections in `frontend/app.py`

3. **Improve RAG**
   - Replace stub embeddings with real Gemini embeddings
   - Adjust chunk size and overlap
   - Tune top-k retrieval

## Production Deployment

For production use:

1. **Add Database**
   - Replace in-memory storage with PostgreSQL
   - Persist user data and documents

2. **Add Authentication**
   - Implement user login/signup
   - Secure API endpoints with JWT

3. **Deploy to Cloud**
   - Backend: Deploy on Railway, Render, or AWS
   - Frontend: Deploy on Streamlit Cloud or Heroku

See `README.md` and `docs/DEPLOYMENT.md` for details.

## Common Commands Reference

```bash
# Start Backend
cd backend && uvicorn main:app --reload

# Start Frontend
cd frontend && streamlit run app.py

# Run Tests (if you add them)
pytest tests/

# Check API Documentation
# Open: http://localhost:8000/docs

# Generate Demo Data
python scripts/create_demo_data.py

# Check Installed Packages
pip list

# Update Dependencies
pip install --upgrade -r requirements.txt
```

## Get Help

- 📖 Full Documentation: `README.md`
- 🏗️ Architecture: `PROJECT_STRUCTURE.md`
- 🐛 Issues: Check `TROUBLESHOOTING.md`
- 💬 Questions: Open an issue on GitHub

## Tips for Best Results

1. **Upload Quality Documents**
   - Clear, well-formatted PDFs work best
   - Avoid scanned images (OCR needed)
   - Text-based PDFs are ideal

2. **Ask Specific Questions**
   - "What is TCP?" ✅
   - "Tell me everything" ❌

3. **Use Subject Tags**
   - Tag documents when uploading
   - Makes retrieval more accurate

4. **Regular Study Schedule**
   - Create realistic study plans
   - Check in daily
   - Track progress

5. **Quiz Yourself Often**
   - Generate quizzes on weak topics
   - Review explanations carefully
   - Retake quizzes to improve

---

**Happy Studying! 📚✨**

You're now ready to use PrepPal effectively. Remember: Learn Smarter, Not Harder!