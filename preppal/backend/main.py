"""
PrepPal Backend API
FastAPI backend for RAG-based study assistant with quiz generation and study planning
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

# Load environment variables
load_dotenv()

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
    return chunks

def create_embeddings(texts: List[str]) -> np.ndarray:
    """
    Create embeddings for text chunks
    In production, use google-generativeai embeddings
    For prototype, returns random embeddings
    """
    # Stub: Generate random embeddings (768 dimensions)
    # Replace with: genai.embed_content(model="models/embedding-001", content=texts)
    embeddings = np.random.randn(len(texts), 768)
    # Normalize embeddings
    embeddings = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)
    return embeddings

def cosine_similarity(query_embedding: np.ndarray, doc_embeddings: np.ndarray) -> np.ndarray:
    """Calculate cosine similarity between query and document embeddings"""
    similarities = np.dot(doc_embeddings, query_embedding)
    return similarities

def retrieve_relevant_chunks(query: str, doc_ids: Optional[List[str]] = None, top_k: int = 5) -> List[Dict]:
    """Retrieve top-k most relevant chunks using cosine similarity"""
    # Create query embedding
    query_embedding = create_embeddings([query])[0]
    
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
    Generate answer using LLM with RAG
    In production, use google-generativeai
    """
    # Build context from retrieved chunks
    context = "\n\n".join([f"[Source: {c['source']['filename']}, Chunk {c['source']['chunk_index']}]\n{c['text']}" 
                           for c in context_chunks])
    
    # Prompt template for RAG
    prompt = f"""You are PrepPal, a helpful study assistant. Answer the student's question using ONLY the information provided in the context below. If the answer cannot be found in the context, say "I couldn't find that information in your study materials."

Context:
{context}

Question: {query}

Answer:"""
    
    # Stub: Mock LLM response
    # Replace with: genai.GenerativeModel('gemini-pro').generate_content(prompt)
    if not context_chunks:
        return "I don't have any study materials to reference yet. Please upload some documents first!"
    
    return f"Based on your study materials, here's what I found: The documents cover information related to '{query}'. [This is a prototype response - in production, Gemini would provide a detailed answer based on the context.]"

def generate_quiz_with_llm(topic: str, context_chunks: List[Dict], num_questions: int = 5) -> List[QuizQuestion]:
    """
    Generate quiz questions using LLM
    In production, use google-generativeai with structured output
    """
    # Stub: Mock quiz generation
    # Replace with proper Gemini API call requesting JSON output
    
    quiz_questions = [
        QuizQuestion(
            question=f"What is the key concept related to {topic}?",
            options=["Option A", "Option B", "Option C", "Option D"],
            correct_index=0,
            explanation=f"This concept is fundamental to understanding {topic}."
        ),
        QuizQuestion(
            question=f"Which statement best describes {topic}?",
            options=["Statement 1", "Statement 2", "Statement 3", "Statement 4"],
            correct_index=1,
            explanation=f"This accurately captures the essence of {topic}."
        ),
        QuizQuestion(
            question=f"How does {topic} apply in practice?",
            options=["Application A", "Application B", "Application C", "Application D"],
            correct_index=2,
            explanation=f"Practical application of {topic} is demonstrated here."
        ),
        QuizQuestion(
            question=f"What is the relationship between {topic} and related concepts?",
            options=["Relationship 1", "Relationship 2", "Relationship 3", "Relationship 4"],
            correct_index=0,
            explanation=f"Understanding connections helps master {topic}."
        ),
        QuizQuestion(
            question=f"Which scenario best illustrates {topic}?",
            options=["Scenario A", "Scenario B", "Scenario C", "Scenario D"],
            correct_index=3,
            explanation=f"This example clearly demonstrates {topic}."
        )
    ]
    
    return quiz_questions[:num_questions]

def generate_study_plan(exam_date: str, hours_per_day: float, subjects: List[str]) -> List[Dict]:
    """
    Generate a day-by-day study plan
    In production, use google-generativeai for personalized planning
    """
    try:
        exam_datetime = datetime.strptime(exam_date, "%Y-%m-%d")
        today = datetime.now()
        days_until_exam = (exam_datetime - today).days
        
        if days_until_exam <= 0:
            days_until_exam = 7  # Default to 1 week if date is past
        
        plan = []
        total_hours = days_until_exam * hours_per_day
        hours_per_subject = total_hours / len(subjects) if subjects else 0
        
        for day in range(days_until_exam):
            date = today + timedelta(days=day)
            subject_index = day % len(subjects) if subjects else 0
            current_subject = subjects[subject_index] if subjects else "General Study"
            
            plan.append({
                "day": day + 1,
                "date": date.strftime("%Y-%m-%d"),
                "subject": current_subject,
                "hours": hours_per_day,
                "topics": [f"{current_subject} - Topic {(day // len(subjects)) + 1}" if subjects else "Review materials"],
                "completed": False
            })
        
        return plan
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid date format: {str(e)}")

# ============ API Endpoints ============

@app.get("/")
def read_root():
    return {"message": "PrepPal API is running!", "version": "1.0.0"}

@app.post("/upload")
async def upload_document(file: UploadFile = File(...), subject: Optional[str] = None):
    """Upload and process a PDF document"""
    try:
        # Read file content
        content = await file.read()
        
        # Extract text from PDF (stub - in production use PyMuPDF)
        # Replace with: import fitz; doc = fitz.open(stream=content, filetype="pdf")
        text = f"Sample text content from {file.filename}. This is a prototype. In production, actual PDF text would be extracted using PyMuPDF. The document covers various topics including data communication, computer networks, and networking protocols."
        
        # Generate unique document ID
        doc_id = str(uuid.uuid4())
        
        # Chunk the text
        chunks = chunk_text(text)
        
        # Create embeddings
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
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    """Handle chat queries with RAG"""
    try:
        # Retrieve relevant chunks
        relevant_chunks = retrieve_relevant_chunks(request.message, request.doc_ids)
        
        # Generate answer using LLM
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
                    for i, chunk in enumerate(doc['chunks'][:3]):  # Use first 3 chunks
                        context_chunks.append({
                            'text': chunk,
                            'source': {'filename': doc['filename'], 'chunk_index': i}
                        })
        
        # Generate quiz questions
        questions = generate_quiz_with_llm(topic, context_chunks, request.num_questions)
        
        return QuizResponse(questions=questions)
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)