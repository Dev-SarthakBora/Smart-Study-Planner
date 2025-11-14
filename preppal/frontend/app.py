"""
PrepPal Streamlit Frontend
Smart Study Planner with RAG Chat, Quiz Generation, and Study Planning
"""

import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta
import json
from typing import List, Dict
import time

# ============ Configuration ============
API_BASE_URL = "http://localhost:8000"

# ============ Page Config ============
st.set_page_config(
    page_title="PrepPal - Your Smart Study Partner",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============ Custom CSS ============
st.markdown("""
<style>
    /* Main gradient header */
    .main-header {
        background: linear-gradient(90deg, #00D4FF 0%, #B100FF 50%, #FF00E5 100%);
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    
    .main-header h1 {
        color: white;
        margin: 0;
        font-size: 2.5rem;
        font-weight: bold;
    }
    
    .main-header p {
        color: white;
        margin: 5px 0 0 0;
        font-size: 1rem;
    }
    
    /* Navigation tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background-color: #f0f0f0;
        padding: 10px;
        border-radius: 10px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: white;
        border: 2px solid black;
        border-radius: 8px;
        padding: 10px 20px;
        font-weight: bold;
    }
    
    /* Chat messages */
    .user-message {
        background-color: #FFE600;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
        border: 2px solid black;
    }
    
    .bot-message {
        background-color: #00D4FF;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
        border: 2px solid black;
    }
    
    /* Buttons */
    .stButton>button {
        background-color: #FFE600;
        color: black;
        border: 2px solid black;
        border-radius: 8px;
        font-weight: bold;
        padding: 10px 20px;
    }
    
    .stButton>button:hover {
        background-color: #FF00E5;
        color: white;
    }
    
    /* Progress bar */
    .stProgress > div > div > div {
        background-color: #FFE600;
    }
    
    /* Info boxes */
    .info-box {
        background-color: #FFE600;
        padding: 20px;
        border-radius: 10px;
        border: 3px solid black;
        margin: 10px 0;
    }
    
    .info-box h3 {
        margin: 0 0 10px 0;
        color: black;
    }
</style>
""", unsafe_allow_html=True)

# ============ Session State Initialization ============
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'uploaded_docs' not in st.session_state:
    st.session_state.uploaded_docs = []
if 'current_plan' not in st.session_state:
    st.session_state.current_plan = None
if 'quiz_questions' not in st.session_state:
    st.session_state.quiz_questions = []
if 'quiz_answers' not in st.session_state:
    st.session_state.quiz_answers = {}
if 'voice_enabled' not in st.session_state:
    st.session_state.voice_enabled = False

# ============ Header ============
st.markdown("""
<div class="main-header">
    <h1>⚡ PrepPal</h1>
    <p>YOUR SMART STUDY PARTNER</p>
</div>
""", unsafe_allow_html=True)

# ============ Navigation Tabs ============
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🏠 Dashboard", 
    "📚 Documents", 
    "💬 Chat", 
    "📅 Study Plans", 
    "🧠 Quizzes"
])

# ============ TAB 1: Dashboard ============
with tab1:
    st.markdown("## Welcome Back! 👋")
    st.markdown("Ready to crush your study goals? Let's make learning awesome!")
    
    # Quick stats
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="info-box" style="background: linear-gradient(135deg, #00D4FF 0%, #0099CC 100%);">
            <h3>📚 Documents</h3>
            <h1 style="margin:0; font-size: 3rem;">{}</h1>
        </div>
        """.format(len(st.session_state.uploaded_docs)), unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="info-box" style="background: linear-gradient(135deg, #FF00E5 0%, #CC00B8 100%);">
            <h3>💬 Chat Sessions</h3>
            <h1 style="margin:0; font-size: 3rem;">{}</h1>
        </div>
        """.format(len(st.session_state.chat_history)), unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="info-box" style="background: linear-gradient(135deg, #FFE600 0%, #CCB800 100%);">
            <h3>📅 Study Plans</h3>
            <h1 style="margin:0; font-size: 3rem;">{}</h1>
        </div>
        """.format(1 if st.session_state.current_plan else 0), unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="info-box" style="background: linear-gradient(135deg, #00FF88 0%, #00CC6E 100%);">
            <h3>🧠 Quizzes Taken</h3>
            <h1 style="margin:0; font-size: 3rem;">{}</h1>
        </div>
        """.format(len(st.session_state.quiz_answers)), unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Quick Actions
    st.markdown("## ⚡ Quick Actions")
    
    action_col1, action_col2 = st.columns(2)
    
    with action_col1:
        if st.button("📤 Upload Document", use_container_width=True):
            st.switch_page
        
        if st.button("📅 Create Study Plan", use_container_width=True):
            st.switch_page
    
    with action_col2:
        if st.button("💬 Ask PrepPal", use_container_width=True):
            st.switch_page
        
        if st.button("🧠 Take Quiz", use_container_width=True):
            st.switch_page

# ============ TAB 2: Documents ============
with tab2:
    st.markdown("""
    <div class="info-box" style="background: linear-gradient(135deg, #00D4FF 0%, #00A8CC 100%);">
        <h2 style="color: white; margin: 0;">📚 STUDY MATERIALS</h2>
        <p style="color: white; margin: 5px 0 0 0;">Upload your notes and PDFs here</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Upload section
    st.markdown("### 📤 UPLOAD NEW DOCUMENT")
    
    uploaded_file = st.file_uploader(
        "Choose a PDF file",
        type=['pdf'],
        help="PDF files only"
    )
    
    col1, col2 = st.columns([3, 1])
    with col1:
        doc_subject = st.text_input(
            "Subject (Optional)",
            placeholder="e.g., Physics, Mathematics, Biology"
        )
    
    with col2:
        st.write("")  # Spacing
        st.write("")  # Spacing
        upload_button = st.button("📤 UPLOAD & PROCESS", use_container_width=True)
    
    if upload_button and uploaded_file:
        with st.spinner("Processing your document..."):
            try:
                # Upload to backend
                files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
                data = {"subject": doc_subject} if doc_subject else {}
                
                response = requests.post(
                    f"{API_BASE_URL}/upload",
                    files=files,
                    data=data
                )
                
                if response.status_code == 200:
                    result = response.json()
                    st.session_state.uploaded_docs.append(result)
                    st.success(f"✅ {result['filename']} uploaded successfully! Processed {result['num_chunks']} chunks.")
                else:
                    st.error(f"Upload failed: {response.text}")
            except Exception as e:
                st.error(f"Error: {str(e)}")
    
    st.markdown("---")
    
    # Documents list
    st.markdown("### 📑 YOUR DOCUMENTS")
    
    if st.session_state.uploaded_docs:
        for doc in st.session_state.uploaded_docs:
            with st.container():
                col1, col2, col3 = st.columns([3, 1, 1])
                
                with col1:
                    st.markdown(f"""
                    <div style="background: white; padding: 15px; border: 2px solid black; border-radius: 8px;">
                        <h4 style="margin: 0;">📄 {doc['filename']}</h4>
                        <p style="margin: 5px 0 0 0; color: #666;">{doc['subject']} • {doc['num_chunks']} pages</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    if st.button("👁️ VIEW", key=f"view_{doc['doc_id']}"):
                        st.info("Document viewer coming soon!")
                
                with col3:
                    if st.button("🗑️ DELETE", key=f"delete_{doc['doc_id']}"):
                        try:
                            response = requests.delete(f"{API_BASE_URL}/documents/{doc['doc_id']}")
                            if response.status_code == 200:
                                st.session_state.uploaded_docs = [
                                    d for d in st.session_state.uploaded_docs 
                                    if d['doc_id'] != doc['doc_id']
                                ]
                                st.rerun()
                        except Exception as e:
                            st.error(f"Delete failed: {str(e)}")
    else:
        st.info("📭 No documents uploaded yet. Upload your first study material above!")

# ============ TAB 3: Chat ============
with tab3:
    st.markdown("""
    <div class="info-box" style="background: linear-gradient(135deg, #FF00E5 0%, #CC00B8 100%);">
        <h2 style="color: white; margin: 0;">💬 ASK PREPPAL</h2>
        <p style="color: white; margin: 5px 0 0 0;">Your AI study buddy is here to help!</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Voice toggle
    col1, col2 = st.columns([5, 1])
    with col2:
        if st.button("🎤" if not st.session_state.voice_enabled else "🔇"):
            st.session_state.voice_enabled = not st.session_state.voice_enabled
            if st.session_state.voice_enabled:
                st.info("🎤 Voice mode enabled! (Integration with Agora SDK required)")
    
    # Document selector
    st.markdown("### Chat with:")
    if st.session_state.uploaded_docs:
        doc_options = ["All Documents"] + [doc['filename'] for doc in st.session_state.uploaded_docs]
        selected_doc = st.selectbox("Select document", doc_options, label_visibility="collapsed")
    else:
        st.warning("⚠️ No documents uploaded. Upload documents to chat with your study materials!")
        selected_doc = None
    
    # Chat history display
    st.markdown("### 💬 Conversation")
    chat_container = st.container()
    
    with chat_container:
        if not st.session_state.chat_history:
            st.markdown("""
            <div class="bot-message">
                <p style="margin: 0;"><strong>🤖 PrepPal:</strong></p>
                <p style="margin: 5px 0 0 0;">Hi there! It seems I don't have any study materials to reference at the moment. However, I'm here to help with any questions you might have! What would you like to know?</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            for msg in st.session_state.chat_history:
                # User message
                st.markdown(f"""
                <div class="user-message">
                    <p style="margin: 0;"><strong>👤 You:</strong></p>
                    <p style="margin: 5px 0 0 0;">{msg['query']}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Bot message
                sources_text = ""
                if msg.get('sources'):
                    sources_text = "<br><small>📚 Sources: " + ", ".join([
                        f"{s['filename']} (chunk {s['chunk_index']})" 
                        for s in msg['sources'][:3]
                    ]) + "</small>"
                
                st.markdown(f"""
                <div class="bot-message">
                    <p style="margin: 0;"><strong>🤖 PrepPal:</strong></p>
                    <p style="margin: 5px 0 0 0;">{msg['answer']}</p>
                    {sources_text}
                </div>
                """, unsafe_allow_html=True)
    
    # Chat input
    st.markdown("---")
    col1, col2 = st.columns([5, 1])
    
    with col1:
        user_query = st.text_input(
            "Type your question here...",
            placeholder="Ask anything about your study materials...",
            label_visibility="collapsed",
            key="chat_input"
        )
    
    with col2:
        send_button = st.button("📤 Send", use_container_width=True)
    
    if send_button and user_query:
        with st.spinner("🤔 Thinking..."):
            try:
                # Prepare request
                doc_ids = None
                if selected_doc and selected_doc != "All Documents":
                    doc_ids = [
                        doc['doc_id'] for doc in st.session_state.uploaded_docs 
                        if doc['filename'] == selected_doc
                    ]
                
                # Send to backend
                response = requests.post(
                    f"{API_BASE_URL}/chat",
                    json={
                        "user_id": "default_user",
                        "message": user_query,
                        "doc_ids": doc_ids
                    }
                )
                
                if response.status_code == 200:
                    result = response.json()
                    st.session_state.chat_history.append({
                        'query': user_query,
                        'answer': result['answer'],
                        'sources': result['sources'],
                        'timestamp': result['timestamp']
                    })
                    st.rerun()
                else:
                    st.error(f"Chat failed: {response.text}")
            except Exception as e:
                st.error(f"Error: {str(e)}")

# ============ TAB 4: Study Plans ============
with tab4:
    st.markdown("""
    <div class="info-box" style="background: linear-gradient(135deg, #FFE600 0%, #CCB800 100%);">
        <h2 style="color: black; margin: 0;">📅 STUDY PLANS</h2>
        <p style="color: black; margin: 5px 0 0 0;">Let AI organize your study schedule</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Plan creation form
    st.markdown("### ➕ CREATE NEW PLAN")
    
    col1, col2 = st.columns(2)
    
    with col1:
        exam_date = st.date_input(
            "📆 Exam Date",
            min_value=datetime.now().date(),
            value=datetime.now().date() + timedelta(days=30)
        )
        
        hours_per_day = st.slider(
            "⏰ Study Hours per Day",
            min_value=1.0,
            max_value=12.0,
            value=4.0,
            step=0.5
        )
    
    with col2:
        subjects_input = st.text_area(
            "📚 Subjects (one per line)",
            placeholder="Mathematics\nPhysics\nChemistry\nBiology",
            height=120
        )
    
    if st.button("🎯 GENERATE PLAN", use_container_width=True):
        subjects = [s.strip() for s in subjects_input.split('\n') if s.strip()]
        
        if not subjects:
            st.warning("⚠️ Please enter at least one subject!")
        else:
            with st.spinner("🤖 Creating your personalized study plan..."):
                try:
                    response = requests.post(
                        f"{API_BASE_URL}/plan",
                        json={
                            "exam_date": exam_date.strftime("%Y-%m-%d"),
                            "hours_per_day": hours_per_day,
                            "subjects": subjects
                        }
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        st.session_state.current_plan = result
                        st.success(f"✅ Study plan created! {result['total_days']} days, {result['total_hours']} total hours.")
                        st.rerun()
                    else:
                        st.error(f"Plan creation failed: {response.text}")
                except Exception as e:
                    st.error(f"Error: {str(e)}")
    
    st.markdown("---")
    
    # Display current plan
    st.markdown("### 📋 YOUR PLAN")
    
    if st.session_state.current_plan:
        plan_data = st.session_state.current_plan['plan']
        
        # Progress overview
        total_days = st.session_state.current_plan['total_days']
        completed_days = sum(1 for day in plan_data if day.get('completed', False))
        progress = completed_days / total_days if total_days > 0 else 0
        
        st.markdown(f"**Progress:** {completed_days}/{total_days} days completed")
        st.progress(progress)
        
        # Plan table
        df = pd.DataFrame(plan_data)
        df_display = df[['day', 'date', 'subject', 'hours', 'topics']]
        df_display.columns = ['Day', 'Date', 'Subject', 'Hours', 'Topics']
        
        st.dataframe(df_display, use_container_width=True, hide_index=True)
        
        # Actions
        if st.button("🗑️ Clear Plan"):
            st.session_state.current_plan = None
            st.rerun()
    else:
        st.info("📭 No study plan yet. Create your first personalized schedule above!")

# ============ TAB 5: Quizzes ============
with tab5:
    st.markdown("""
    <div class="info-box" style="background: linear-gradient(135deg, #00FF88 0%, #00CC6E 100%);">
        <h2 style="color: black; margin: 0;">🧠 QUIZ TIME!</h2>
        <p style="color: black; margin: 5px 0 0 0;">Test your knowledge with AI-generated questions</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Quiz generation
    st.markdown("### ➕ CREATE NEW QUIZ")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        quiz_topic = st.text_input(
            "Topic (Optional)",
            placeholder="e.g., Photosynthesis, Newton's Laws, Algebra"
        )
    
    with col2:
        num_questions = st.selectbox("Questions", [3, 5, 10], index=1)
    
    if st.button("🎲 GENERATE QUIZ", use_container_width=True):
        with st.spinner("🤖 Generating quiz questions..."):
            try:
                doc_ids = [doc['doc_id'] for doc in st.session_state.uploaded_docs]
                
                response = requests.post(
                    f"{API_BASE_URL}/quiz",
                    json={
                        "topic": quiz_topic or None,
                        "doc_ids": doc_ids if doc_ids else None,
                        "num_questions": num_questions
                    }
                )
                
                if response.status_code == 200:
                    result = response.json()
                    st.session_state.quiz_questions = result['questions']
                    st.session_state.quiz_answers = {}
                    st.success(f"✅ Quiz generated with {len(result['questions'])} questions!")
                    st.rerun()
                else:
                    st.error(f"Quiz generation failed: {response.text}")
            except Exception as e:
                st.error(f"Error: {str(e)}")
    
    st.markdown("---")
    
    # Display quiz
    if st.session_state.quiz_questions:
        st.markdown("### 📝 YOUR QUIZ")
        
        for i, question in enumerate(st.session_state.quiz_questions):
            st.markdown(f"**Question {i+1}:** {question['question']}")
            
            answer = st.radio(
                f"Select your answer:",
                options=question['options'],
                key=f"q_{i}",
                label_visibility="collapsed"
            )
            
            st.session_state.quiz_answers[i] = question['options'].index(answer)
            
            st.markdown("---")
        
        # Submit quiz
        if st.button("✅ SUBMIT QUIZ", use_container_width=True):
            correct = 0
            for i, question in enumerate(st.session_state.quiz_questions):
                if st.session_state.quiz_answers.get(i) == question['correct_index']:
                    correct += 1
            
            score = (correct / len(st.session_state.quiz_questions)) * 100
            
            st.markdown(f"""
            <div class="info-box" style="background: {'linear-gradient(135deg, #00FF88 0%, #00CC6E 100%)' if score >= 70 else 'linear-gradient(135deg, #FF6B6B 0%, #EE5A52 100%)'};">
                <h2 style="color: white; margin: 0;">Your Score: {score:.0f}%</h2>
                <p style="color: white; margin: 5px 0 0 0;">{correct} out of {len(st.session_state.quiz_questions)} correct</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Show explanations
            st.markdown("### 📚 Explanations")
            for i, question in enumerate(st.session_state.quiz_questions):
                user_answer = st.session_state.quiz_answers.get(i)
                correct_answer = question['correct_index']
                is_correct = user_answer == correct_answer
                
                st.markdown(f"""
                **Question {i+1}:** {question['question']}
                
                {'✅' if is_correct else '❌'} Your answer: {question['options'][user_answer] if user_answer is not None else 'Not answered'}
                
                ✔️ Correct answer: {question['options'][correct_answer]}
                
                💡 Explanation: {question['explanation']}
                """)
                st.markdown("---")
    else:
        st.info("📭 No quiz available. Generate your first quiz above!")

# ============ Footer ============
st.markdown("---")
st.markdown("""
<div style="text-align: center; background: linear-gradient(90deg, #00D4FF 0%, #B100FF 100%); padding: 20px; border-radius: 10px;">
    <h3 style="color: white; margin: 0;">BUILT FOR HACKATHON 2025 🚀</h3>
    <p style="color: white; margin: 5px 0 0 0;">PrepPal - Learn Smarter, Not Harder</p>
</div>
""", unsafe_allow_html=True)