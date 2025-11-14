"""
PrepPal Backend API
FastAPI backend for RAG-based study assistant with quiz generation and study planning
Now fully integrated with Google Gemini AI
"""

from fastapi import FastAPI, UploadFile, File, HTTPException
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

# Load environment variables
load_dotenv()

# Configure Gemini API
GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in .env file")

genai.configure(api_key=GEMINI_API_KEY)

app = FastAPI(title="PrepPal API", version="1.0.0")

# CORS middleware for Streamlit
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============ In-Memory Storage ============
documents_store = {}  # {doc_id: {filename, chunks, embeddings, metadata}}
chat_history = []

# ============ Pydantic Models ============

class ChatRequest(BaseModel):
    user_id: str = "default_user"
    message: str
    doc_ids: Optional[List[str]] = None

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

def chunk_text(text: str, chunk_size: int = 500) -> List[str]:
    """Split text into chunks of approximately chunk_size words"""
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size):
        chunk = ' '.join(words[i:i + chunk_size])
        chunks.append(chunk)
    return chunks if chunks else [""]

def create_embeddings(texts: List[str]) -> np.ndarray:
    """
    Create embeddings for text chunks using Gemini embedding model
    """
    try:
        embeddings_list = []
        for text in texts:
            result = genai.embed_content(
                model="models/text-embedding-004",
                content=text,
                task_type="retrieval_document"
            )
            embeddings_list.append(result['embedding'])
        
        embeddings = np.array(embeddings_list)
        # Normalize embeddings
        embeddings = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)
        return embeddings
    except Exception as e:
        print(f"Error creating embeddings: {str(e)}")
        # Fallback to random embeddings if API fails
        embeddings = np.random.randn(len(texts), 768)
        embeddings = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)
        return embeddings

def cosine_similarity(query_embedding: np.ndarray, doc_embeddings: np.ndarray) -> np.ndarray:
    """Calculate cosine similarity between query and document embeddings"""
    similarities = np.dot(doc_embeddings, query_embedding)
    return similarities

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
    
    # Collect all chunks and embeddings
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
    
    # Calculate similarities
    embeddings_matrix = np.array(all_embeddings)
    similarities = cosine_similarity(query_embedding, embeddings_matrix)
    
    # Get top-k indices
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
        # Build context from retrieved chunks
        context = "\n\n".join([f"[Source: {c['source']['filename']}, Chunk {c['source']['chunk_index']}]\n{c['text']}" 
                               for c in context_chunks])
        
        # Prompt template for RAG
        prompt = f"""You are PrepPal, a helpful study assistant. Answer the student's question using ONLY the information provided in the context below. If the answer cannot be found in the context, say "I couldn't find that information in your study materials."

Context:
{context}

Question: {query}

Answer:"""
        
        if not context_chunks:
            return "I don't have any study materials to reference yet. Please upload some documents first!"
        
        # Generate response using Gemini
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
        # Build context from chunks
        context = "\n\n".join([chunk['text'] for chunk in context_chunks[:5]])  # Use top 5 chunks
        
        prompt = f"""You are an expert quiz generator. Based on the following study material about {topic}, create {num_questions} multiple-choice questions.

Study Material:
{context}

Generate exactly {num_questions} multiple-choice questions in JSON format. Each question should have:
- question: A clear, specific question
- options: Exactly 4 answer options (as an array)
- correct_index: The index (0-3) of the correct answer
- explanation: A brief explanation of why the answer is correct

Return ONLY a valid JSON array of questions, no additional text. Format:
[
  {{
    "question": "Question text here?",
    "options": ["Option A", "Option B", "Option C", "Option D"],
    "correct_index": 0,
    "explanation": "Explanation here."
  }}
]"""

        model = genai.GenerativeModel('gemini-2.5-flash')
        response = model.generate_content(prompt)
        
        # Parse JSON response
        response_text = response.text.strip()
        # Remove markdown code blocks if present
        if response_text.startswith("```json"):
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif response_text.startswith("```"):
            response_text = response_text.split("```")[1].split("```")[0].strip()
        
        questions_data = json.loads(response_text)
        
        # Convert to QuizQuestion objects
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
        # Fallback to generic questions
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
        
        # Generate plan with Gemini
        prompt = f"""Create a detailed {days_until_exam}-day study plan for the following:
- Exam Date: {exam_date}
- Daily Study Hours: {hours_per_day}
- Subjects: {', '.join(subjects)}

Generate a day-by-day breakdown in JSON format. Each day should include:
- day: day number (1 to {days_until_exam})
- subject: which subject to focus on
- hours: study hours for that day
- topics: array of 2-3 specific topics to cover
- tips: a brief study tip for that day

Distribute subjects evenly across days. Return ONLY valid JSON array, no additional text:
[
  {{
    "day": 1,
    "subject": "Subject Name",
    "hours": {hours_per_day},
    "topics": ["Topic 1", "Topic 2"],
    "tips": "Study tip here"
  }}
]"""

        model = genai.GenerativeModel('gemini-2.5-flash')
        response = model.generate_content(prompt)
        
        # Parse response
        response_text = response.text.strip()
        if response_text.startswith("```json"):
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif response_text.startswith("```"):
            response_text = response_text.split("```")[1].split("```")[0].strip()
        
        plan_data = json.loads(response_text)
        
        # Add dates and completed status
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
        # Fallback to simple plan
        plan = []
        for day in range(days_until_exam):
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

# ============ API Endpoints ============

@app.get("/")
def read_root():
    return {
        "message": "PrepPal API is running with Gemini AI!", 
        "version": "1.0.0",
        "gemini_configured": bool(GEMINI_API_KEY)
    }

@app.post("/upload")
async def upload_document(file: UploadFile = File(...), subject: Optional[str] = None):
    """Upload and process a PDF document"""
    try:
        # Validate file type
        if not file.filename.endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are supported")
        
        # Read file content
        content = await file.read()
        
        # Extract text from PDF
        text = extract_text_from_pdf(content)
        
        if not text:
            raise HTTPException(status_code=400, detail="Could not extract text from PDF. The file may be empty or corrupted.")
        
        # Generate unique document ID
        doc_id = str(uuid.uuid4())
        
        # Chunk the text
        chunks = chunk_text(text)
        
        # Create embeddings using Gemini
        embeddings = create_embeddings(chunks)
        
        # Store document
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
        # Retrieve relevant chunks
        relevant_chunks = retrieve_relevant_chunks(request.message, request.doc_ids)
        
        # Generate answer using Gemini
        answer = generate_answer_with_llm(request.message, relevant_chunks)
        
        # Format sources
        sources = [
            {
                'filename': chunk['source']['filename'],
                'chunk_index': chunk['source']['chunk_index'],
                'relevance_score': chunk['score']
            }
            for chunk in relevant_chunks
        ]
        
        # Store in chat history
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
        # Determine topic
        topic = request.topic or "your study materials"
        
        # Retrieve relevant context
        context_chunks = []
        if request.doc_ids:
            for doc_id in request.doc_ids:
                if doc_id in documents_store:
                    doc = documents_store[doc_id]
                    for i, chunk in enumerate(doc['chunks'][:5]):  # Use first 5 chunks
                        context_chunks.append({
                            'text': chunk,
                            'source': {'filename': doc['filename'], 'chunk_index': i}
                        })
        
        if not context_chunks:
            raise HTTPException(status_code=400, detail="No documents found. Please upload documents first.")
        
        # Generate quiz questions using Gemini
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
        "documents_count": len(documents_store),
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)