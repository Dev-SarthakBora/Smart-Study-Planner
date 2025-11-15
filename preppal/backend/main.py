"""
PrepPal Backend API - Updated
FastAPI backend for RAG-based study assistant with quiz generation and study planning
Added: Agora Conversational AI REST endpoints (/start-agent, /stop-agent)
Notes:
- Provide AGORA_CUSTOMER_ID and AGORA_CUSTOMER_SECRET for REST basic auth.
- For quick tests provide AGORA_TEMP_AGENT_TOKEN env var (temporary RTC token for agent) or pass `agent_token` in /start-agent body.
- Do NOT store Customer Secret on frontend.
"""

from fastapi import FastAPI, UploadFile, File, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import numpy as np
from datetime import datetime, timedelta
import json
import uuid
import os
from dotenv import load_dotenv
import google.generativeai as genai
import fitz  # PyMuPDF for PDF processing
import base64
import requests
import logging
from fastapi.responses import JSONResponse
logger = logging.getLogger("preppal")
logging.basicConfig(level=logging.INFO)
# Load environment variables
load_dotenv()

# Configure Gemini API
GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in .env file")

genai.configure(api_key=GEMINI_API_KEY)

# Agora config (for Conversational AI REST)
AGORA_APP_ID = os.getenv("AGORA_APP_ID")
AGORA_CUSTOMER_ID = os.getenv("AGORA_CUSTOMER_ID")
AGORA_CUSTOMER_SECRET = os.getenv("AGORA_CUSTOMER_SECRET")
# Optional quick test token to allow agents to join without generating tokens
AGORA_TEMP_AGENT_TOKEN = os.getenv("AGORA_TEMP_AGENT_TOKEN")

if not AGORA_APP_ID:
    print("Warning: AGORA_APP_ID not set. Start/stop agent endpoints will fail without it.")
if not (AGORA_CUSTOMER_ID and AGORA_CUSTOMER_SECRET):
    print("Warning: AGORA_CUSTOMER_ID or AGORA_CUSTOMER_SECRET not set. Start/stop agent endpoints will fail without them.")

app = FastAPI(title="PrepPal API", version="1.1.0")

# CORS middleware for Streamlit
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============ In-Memory Storage ============
documents_store = {}  # {doc_id: {filename, chunks, embeddings(list), metadata}}
chat_history = []

# ============ Pydantic Models ============
class ChatRequest(BaseModel):
    user_id: str = "default_user"
    message: str
    doc_ids: Optional[List[str]] = None
    agent_id: Optional[str] = None
    voice: Optional[bool] = False

class ChatResponse(BaseModel):
    answer: str
    sources: List[Dict[str, Any]]
    timestamp: str

class QuizRequest(BaseModel):
    topic: Optional[str] = None
    doc_ids: Optional[List[str]] = None
    num_questions: int = 5

class QuizQuestion(BaseModel):
    question: str
    options: List[str]
    correct_index: int
    explanation: str

class QuizResponse(BaseModel):
    questions: List[QuizQuestion]

class PlanRequest(BaseModel):
    exam_date: str  # YYYY-MM-DD
    hours_per_day: float
    subjects: List[str]

class PlanResponse(BaseModel):
    plan: List[Dict[str, Any]]
    total_days: int
    total_hours: float

# ============ Helper Functions ============
@app.get("/get-temp-token")
def get_temp_token_debug():
    """
    Debug get-temp-token: returns appId and client token (falls back to agent token).
    Also returns masked values so you can see what the running process sees.
    """
    app_id = os.getenv("AGORA_APP_ID", "").strip()
    client_token = os.getenv("AGORA_TEMP_CLIENT_TOKEN", "").strip()
    agent_token = os.getenv("AGORA_TEMP_AGENT_TOKEN", "").strip()

    # Log exact presence (do NOT print secrets in logs)
    print("DEBUG env: AGORA_APP_ID present?", bool(app_id))
    print("DEBUG env: AGORA_TEMP_CLIENT_TOKEN present?", bool(client_token))
    print("DEBUG env: AGORA_TEMP_AGENT_TOKEN present?", bool(agent_token))

    if not app_id:
        return JSONResponse(status_code=400, content={"error":"AGORA_APP_ID not set in server environment"})

    # use client token if available, else agent token (local dev only)
    token = client_token or agent_token
    if not token:
        return JSONResponse(status_code=400, content={"error":"AGORA_TEMP_CLIENT_TOKEN or AGORA_TEMP_AGENT_TOKEN not set in server environment"})

    # return masked token so we can confirm it's being returned
    masked = token[:8] + "..." + token[-6:] if len(token) > 20 else "****(short)****"
    return {
        "appId": app_id,
        "token": token,                # <-- REAL TOKEN HERE
        "token_masked": masked,        # <-- for UI display
        "token_used_is_client": True
    }




def chunk_text(text: str, chunk_size: int = 200) -> List[str]:
    """Split text into chunks of approximately chunk_size words"""
    words = text.split()
    if not words:
        return [""]
    chunks = []
    for i in range(0, len(words), chunk_size):
        chunk = ' '.join(words[i:i + chunk_size])
        chunks.append(chunk)
    return chunks


def create_embeddings(texts: List[str]) -> List[List[float]]:
    """
    Create embeddings for text chunks using Gemini embedding model
    Returns list-of-lists (serializable)
    """
    try:
        embeddings_list = []
        for text in texts:
            result = genai.embed_content(
                model="models/text-embedding-004",
                content=text,
                task_type="retrieval_document"
            )
            emb = result['embedding']
            # normalize
            arr = np.array(emb)
            norm = np.linalg.norm(arr)
            if norm > 0:
                arr = arr / norm
            embeddings_list.append(arr.tolist())
        return embeddings_list
    except Exception as e:
        print(f"Error creating embeddings: {str(e)}")
        # Fallback to random embeddings if API fails
        embeddings = np.random.randn(len(texts), 768)
        embeddings = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)
        return embeddings.tolist()


def cosine_similarity(query_embedding: np.ndarray, doc_embeddings: np.ndarray) -> np.ndarray:
    """Calculate cosine similarity between query and document embeddings"""
    # query_embedding: (D,), doc_embeddings: (N,D)
    return np.dot(doc_embeddings, query_embedding)


def retrieve_relevant_chunks(query: str, doc_ids: Optional[List[str]] = None, top_k: int = 5) -> List[Dict]:
    """Retrieve top-k most relevant chunks using cosine similarity"""
    try:
        # Create query embedding with retrieval_query task type
        result = genai.embed_content(
            model="models/text-embedding-004",
            content=query,
            task_type="retrieval_query"
        )
        query_embedding = np.array(result['embedding'])
        query_embedding = query_embedding / np.linalg.norm(query_embedding)
    except Exception as e:
        print(f"Error creating query embedding: {str(e)}")
        return []

    all_chunks = []
    all_embeddings = []
    sources = []

    target_docs = doc_ids if doc_ids else list(documents_store.keys())

    for doc_id in target_docs:
        if doc_id in documents_store:
            doc = documents_store[doc_id]
            for i, chunk in enumerate(doc['chunks']):
                all_chunks.append(chunk)
                all_embeddings.append(doc['embeddings'][i])
                sources.append({
                    'doc_id': doc_id,
                    'filename': doc['filename'],
                    'chunk_index': i
                })

    if not all_embeddings:
        return []

    embeddings_matrix = np.array(all_embeddings)
    similarities = cosine_similarity(query_embedding, embeddings_matrix)

    top_indices = np.argsort(similarities)[-top_k:][::-1]

    results = []
    for idx in top_indices:
        results.append({
            'text': all_chunks[idx],
            'score': float(similarities[idx]),
            'source': sources[idx]
        })

    return results


def generate_answer_with_llm(query: str, context_chunks: List[Dict]) -> str:
    """
    Generate answer using Gemini with RAG
    """
    try:
        if not context_chunks:
            return "I don't have any study materials to reference yet. Please upload some documents first!"

        context = "\n\n".join([f"[Source: {c['source']['filename']}, Chunk {c['source']['chunk_index']}]\n{c['text']}" 
                                   for c in context_chunks])

        prompt = f"""You are PrepPal, a helpful study assistant. Answer the student's question using ONLY the information provided in the context below. If the answer cannot be found in the context, say "I couldn't find that information in your study materials."\n\nContext:\n{context}\n\nQuestion: {query}\n\nAnswer:"""

        model = genai.GenerativeModel('gemini-2.5-flash')
        response = model.generate_content(prompt)

        return response.text
    except Exception as e:
        print(f"Error generating answer: {str(e)}")
        return f"I encountered an error while generating the answer. Please try again."


def generate_quiz_with_llm(topic: str, context_chunks: List[Dict], num_questions: int = 5) -> List[QuizQuestion]:
    """
    Generate quiz questions using Gemini with structured output
    """
    try:
        context = "\n\n".join([chunk['text'] for chunk in context_chunks[:5]])  # Use top 5 chunks

        prompt = f"""You are an expert quiz generator. Based on the following study material about {topic}, create {num_questions} multiple-choice questions.\n\nStudy Material:\n{context}\n\nGenerate exactly {num_questions} multiple-choice questions in JSON format. Each question should have: question, options (4), correct_index (0-3), explanation. Return ONLY a valid JSON array of questions, no additional text."""

        model = genai.GenerativeModel('gemini-2.5-flash')
        response = model.generate_content(prompt)

        response_text = response.text.strip()
        if response_text.startswith("```json"):
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif response_text.startswith("```"):
            response_text = response_text.split("```")[1].split("```")[0].strip()

        questions_data = json.loads(response_text)

        quiz_questions = []
        for q_data in questions_data[:num_questions]:
            quiz_questions.append(QuizQuestion(
                question=q_data['question'],
                options=q_data['options'],
                correct_index=q_data['correct_index'],
                explanation=q_data['explanation']
            ))

        return quiz_questions
    except Exception as e:
        print(f"Error generating quiz: {str(e)}")
        # Fallback
        return [
            QuizQuestion(
                question=f"What is a key concept in {topic}?",
                options=["Concept A", "Concept B", "Concept C", "Concept D"],
                correct_index=0,
                explanation=f"This is a fundamental concept in {topic}."
            )
        ] * min(num_questions, 5)


def generate_study_plan(exam_date: str, hours_per_day: float, subjects: List[str]) -> List[Dict]:
    """
    Generate a personalized study plan using Gemini
    """
    try:
        exam_datetime = datetime.strptime(exam_date, "%Y-%m-%d")
        today = datetime.now()
        days_until_exam = (exam_datetime - today).days

        if days_until_exam <= 0:
            days_until_exam = 7  # Default to 1 week if date is past

        prompt = f"""Create a detailed {days_until_exam}-day study plan for the following:\n- Exam Date: {exam_date}\n- Daily Study Hours: {hours_per_day}\n- Subjects: {', '.join(subjects)}\n\nGenerate a day-by-day breakdown in JSON format. Each day should include day, subject, hours, topics (2-3), tips. Return ONLY valid JSON array, no additional text."""

        model = genai.GenerativeModel('gemini-2.5-flash')
        response = model.generate_content(prompt)

        response_text = response.text.strip()
        if response_text.startswith("```json"):
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif response_text.startswith("```"):
            response_text = response_text.split("```")[1].split("```")[0].strip()

        plan_data = json.loads(response_text)

        plan = []
        for i, day_plan in enumerate(plan_data[:days_until_exam]):
            date = today + timedelta(days=i)
            plan.append({
                "day": day_plan.get('day', i + 1),
                "date": date.strftime("%Y-%m-%d"),
                "subject": day_plan.get('subject', subjects[i % len(subjects)]),
                "hours": day_plan.get('hours', hours_per_day),
                "topics": day_plan.get('topics', []),
                "tips": day_plan.get('tips', ''),
                "completed": False
            })

        return plan
    except Exception as e:
        print(f"Error generating study plan: {str(e)}")
        # Fallback simple plan
        today = datetime.now()
        plan = []
        days = max(7, (datetime.strptime(exam_date, "%Y-%m-%d") - today).days)
        for day in range(days):
            date = today + timedelta(days=day)
            subject_index = day % len(subjects) if subjects else 0
            current_subject = subjects[subject_index] if subjects else "General Study"
            plan.append({
                "day": day + 1,
                "date": date.strftime("%Y-%m-%d"),
                "subject": current_subject,
                "hours": hours_per_day,
                "topics": [f"{current_subject} - Topic {(day // len(subjects)) + 1}"],
                "tips": "Review and practice consistently",
                "completed": False
            })
        return plan


def extract_text_from_pdf(content: bytes) -> str:
    """Extract text from PDF using PyMuPDF"""
    try:
        doc = fitz.open(stream=content, filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()
        return text.strip()
    except Exception as e:
        print(f"Error extracting PDF text: {str(e)}")
        return ""

# ============ Agora helper functions ============

def agora_basic_auth_header() -> Dict[str, str]:
    if not (AGORA_CUSTOMER_ID and AGORA_CUSTOMER_SECRET):
        raise ValueError("Agora Customer ID/Secret not configured in environment")
    pair = f"{AGORA_CUSTOMER_ID}:{AGORA_CUSTOMER_SECRET}".encode()
    token = base64.b64encode(pair).decode()
    return {"Authorization": f"Basic {token}", "Content-Type": "application/json"}

def get_tts_config():
    vendor = os.getenv("AGORA_TTS_VENDOR", "microsoft").strip().lower()
    # supported vendors we handle explicitly
    supported = {"microsoft", "elevenlabs"}
    if vendor not in supported:
        logger.warning(f"AGORA_TTS_VENDOR '{vendor}' not supported in code. Falling back to 'microsoft'.")
        vendor = "microsoft"

    if vendor == "elevenlabs":
        # ElevenLabs uses api_key + voice_id + model_id (model usually eleven_flash_v2_5)
        api_key = os.getenv("AGORA_TTS_API_KEY", "")
        voice_id = os.getenv("AGORA_TTS_VOICE_ID", "")
        model_id = os.getenv("AGORA_TTS_MODEL_ID", "eleven_flash_v2_5")
        return {
            "vendor": "elevenlabs",
            "params": {
                "api_key": api_key,
                "voice_id": voice_id,
                "model_id": model_id
            }
        }
    else:
        # Default: Microsoft Azure Speech (legacy behavior)
        return {
            "vendor": "microsoft",
            "params": {
                "key": os.getenv("AGORA_TTS_KEY", ""),
                "region": os.getenv("AGORA_TTS_REGION", "eastus"),
                "voice_name": os.getenv("AGORA_TTS_VOICE", "en-US-AndrewMultilingualNeural")
            }
        }


def agora_join(agent_name: str, channel: str, token: Optional[str]) -> Dict[str, Any]:
    """Debug version: send join and return raw response if non-200 so we can inspect error body."""
    if not AGORA_APP_ID:
        raise ValueError("AGORA_APP_ID not set")
    url = f"https://api.agora.io/api/conversational-ai-agent/v2/projects/{AGORA_APP_ID}/join"
    headers = agora_basic_auth_header()

    # build payload (same as normal)
    payload = {
        "name": agent_name,
        "properties": {
            "channel": channel,
            "token": token or AGORA_TEMP_AGENT_TOKEN,
            "agent_rtc_uid": "0",
            "remote_rtc_uids": ["*"],
            "enable_string_uid": False,
            "idle_timeout": 120,
            "llm": {
                "url": os.getenv("EXTERNAL_LLM_URL", ""),
                "api_key": os.getenv("EXTERNAL_LLM_API_KEY", ""),
                "system_messages": [{"role": "system", "content": "You are a helpful chatbot."}],
                "greeting_message": "Hello, how can I help you?",
                "failure_message": "Sorry, I don't know how to answer this question.",
                "max_history": 10,
                "params": {"model": os.getenv("EXTERNAL_LLM_MODEL", "gpt-4o-mini")}
            },
            "asr": {"language": os.getenv("AGORA_ASR_LANGUAGE", "en-US")},
            "tts": get_tts_config()
        }
    }

    # Mask sensitive fields for logs
    logged = json.loads(json.dumps(payload))
    try:
        tparams = logged["properties"]["tts"]["params"]
        if "api_key" in tparams:
            tparams["api_key"] = "****REDACTED****"
        if "key" in tparams:
            tparams["key"] = "****REDACTED****"
        if "api_key" in logged["properties"]["llm"]:
            logged["properties"]["llm"]["api_key"] = "****REDACTED****"
    except Exception:
        pass

    logger.info("Agora join payload (masked): %s", json.dumps(logged, indent=2)[:2000])

    resp = requests.post(url, headers=headers, json=payload, timeout=30)
    # if success return json
    if resp.status_code == 200:
        return resp.json()
    else:
        # return full server response for debugging (don't raise)
        logger.error("Agora join failed status=%s body=%s", resp.status_code, resp.text)
        return {"__agora_error_status": resp.status_code, "__agora_error_body": resp.text}



def agora_leave(agent_id: str) -> Dict[str, Any]:
    if not AGORA_APP_ID:
        raise ValueError("AGORA_APP_ID not set")
    url = f"https://api.agora.io/api/conversational-ai-agent/v2/projects/{AGORA_APP_ID}/agents/{agent_id}/leave"
    headers = agora_basic_auth_header()
    resp = requests.post(url, headers=headers, timeout=15)
    resp.raise_for_status()
    return resp.json()

# ============ API Endpoints ============

@app.get("/")
def read_root():
    return {
        "message": "PrepPal API is running with Gemini AI!",
        "version": "1.1.0",
        "gemini_configured": bool(GEMINI_API_KEY),
        "agora_configured": bool(AGORA_APP_ID and AGORA_CUSTOMER_ID and AGORA_CUSTOMER_SECRET)
    }


@app.post("/start-agent")
def start_agent(payload: Dict = Body(...)):
    """Start an Agora conversational AI agent. Expects JSON: { channel, agent_token (optional), name (optional) }"""
    try:
        channel = payload.get('channel')
        token = payload.get('agent_token')
        name = payload.get('name') or f"preppl-{int(time.time())}"

        if not channel:
            raise HTTPException(status_code=400, detail="channel is required")

        # If no token provided and no AGORA_TEMP_AGENT_TOKEN env var, return error
        if not (token or AGORA_TEMP_AGENT_TOKEN):
            raise HTTPException(status_code=400, detail="No agent token provided. Set AGORA_TEMP_AGENT_TOKEN or pass agent_token in request.")

        resp_json = agora_join(name, channel, token)
        # resp_json should contain agent_id and status
        return resp_json
    except HTTPException:
        raise
    except requests.HTTPError as e:
        raise HTTPException(status_code=500, detail=f"Agora API error: {str(e)} - {e.response.text if e.response is not None else ''}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Start agent failed: {str(e)}")


@app.post("/stop-agent")
def stop_agent(body: Dict = Body(...)):
    """Stop an Agora conversational AI agent. Expects JSON: { agent_id }
    """
    try:
        agent_id = body.get('agent_id')
        if not agent_id:
            raise HTTPException(status_code=400, detail="agent_id is required")

        resp_json = agora_leave(agent_id)
        return resp_json
    except HTTPException:
        raise
    except requests.HTTPError as e:
        raise HTTPException(status_code=500, detail=f"Agora API error: {str(e)} - {e.response.text if e.response is not None else ''}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Stop agent failed: {str(e)}")


@app.post("/upload")
async def upload_document(file: UploadFile = File(...), subject: Optional[str] = None):
    """Upload and process a PDF document"""
    try:
        if not file.filename.endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are supported")
        content = await file.read()
        text = extract_text_from_pdf(content)
        if not text:
            raise HTTPException(status_code=400, detail="Could not extract text from PDF. The file may be empty or corrupted.")
        doc_id = str(uuid.uuid4())
        chunks = chunk_text(text)
        embeddings = create_embeddings(chunks)
        documents_store[doc_id] = {
            'doc_id': doc_id,
            'filename': file.filename,
            'subject': subject or "General",
            'chunks': chunks,
            'embeddings': embeddings,
            'upload_date': datetime.now().isoformat(),
            'num_chunks': len(chunks)
        }
        return {
            "doc_id": doc_id,
            "filename": file.filename,
            "num_chunks": len(chunks),
            "subject": subject or "General",
            "message": "Document uploaded and processed successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    """Handle chat queries with RAG"""
    try:
        relevant_chunks = retrieve_relevant_chunks(request.message, request.doc_ids)
        answer = generate_answer_with_llm(request.message, relevant_chunks)
        sources = [
            {
                'filename': chunk['source']['filename'],
                'chunk_index': chunk['source']['chunk_index'],
                'relevance_score': chunk['score']
            }
            for chunk in relevant_chunks
        ]
        chat_entry = {
            'timestamp': datetime.now().isoformat(),
            'query': request.message,
            'answer': answer,
            'sources': sources
        }
        chat_history.append(chat_entry)
        return ChatResponse(
            answer=answer,
            sources=sources,
            timestamp=chat_entry['timestamp']
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")


@app.post("/quiz", response_model=QuizResponse)
def generate_quiz(request: QuizRequest):
    """Generate quiz questions based on documents"""
    try:
        topic = request.topic or "your study materials"
        context_chunks = []
        if request.doc_ids:
            for doc_id in request.doc_ids:
                if doc_id in documents_store:
                    doc = documents_store[doc_id]
                    for i, chunk in enumerate(doc['chunks'][:5]):
                        context_chunks.append({
                            'text': chunk,
                            'source': {'filename': doc['filename'], 'chunk_index': i}
                        })
        if not context_chunks:
            raise HTTPException(status_code=400, detail="No documents found. Please upload documents first.")
        questions = generate_quiz_with_llm(topic, context_chunks, request.num_questions)
        return QuizResponse(questions=questions)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Quiz generation failed: {str(e)}")


@app.post("/plan", response_model=PlanResponse)
def create_study_plan(request: PlanRequest):
    """Generate a personalized study plan"""
    try:
        plan = generate_study_plan(request.exam_date, request.hours_per_day, request.subjects)
        total_days = len(plan)
        total_hours = sum(day['hours'] for day in plan)
        return PlanResponse(
            plan=plan,
            total_days=total_days,
            total_hours=total_hours
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Plan generation failed: {str(e)}")


@app.get("/documents")
def list_documents():
    """List all uploaded documents"""
    return {
        "documents": [
            {
                'doc_id': doc['doc_id'],
                'filename': doc['filename'],
                'subject': doc['subject'],
                'num_chunks': doc['num_chunks'],
                'upload_date': doc['upload_date']
            }
            for doc in documents_store.values()
        ]
    }


@app.delete("/documents/{doc_id}")
def delete_document(doc_id: str):
    """Delete a document"""
    if doc_id in documents_store:
        filename = documents_store[doc_id]['filename']
        del documents_store[doc_id]
        return {"message": f"Document {filename} deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="Document not found")


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "gemini_configured": bool(GEMINI_API_KEY),
        "agora_configured": bool(AGORA_APP_ID and AGORA_CUSTOMER_ID and AGORA_CUSTOMER_SECRET),
        "documents_count": len(documents_store),
        "timestamp": datetime.now().isoformat()
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
