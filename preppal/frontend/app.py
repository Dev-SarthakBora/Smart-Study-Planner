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
import uuid

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
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 25px;
        border-radius: 20px;
        margin-bottom: 30px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.15);
        text-align: center;
    }
    
    .main-header h1 {
        color: white;
        margin: 0;
        font-size: 3rem;
        font-weight: 800;
        text-shadow: 2px 2px 8px rgba(0, 0, 0, 0.3);
    }
    
    .main-header p {
        color: white;
        margin: 10px 0 0 0;
        font-size: 1.2rem;
        opacity: 0.95;
        font-weight: 500;
    }
    
    /* Navigation tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 4px;
        background-color: #f8f9fa;
        padding: 8px;
        border-radius: 15px;
        margin-bottom: 25px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: white;
        border-radius: 12px;
        padding: 15px 25px;
        font-weight: 600;
        margin: 0 2px;
        transition: all 0.3s ease;
        border: 2px solid transparent;
        color: #6c757d;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background-color: #e9ecef;
        color: #495057;
        transform: translateY(-2px);
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border-color: #5a67d8 !important;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    /* Chat messages */
    .user-message {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 18px 20px;
        border-radius: 20px 20px 5px 20px;
        margin: 15px 0;
        color: white;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.2);
        max-width: 85%;
        margin-left: auto;
    }
    
    .bot-message {
        background: white;
        padding: 18px 20px;
        border-radius: 20px 20px 20px 5px;
        margin: 15px 0;
        border: 2px solid #e9ecef;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
        max-width: 85%;
    }
    
    .message-time {
        font-size: 0.75rem;
        opacity: 0.7;
        margin-top: 8px;
    }
    
    .sources-badge {
        background: linear-gradient(135deg, #ffd89b 0%, #19547b 100%);
        color: white;
        padding: 4px 12px;
        border-radius: 15px;
        font-size: 0.75rem;
        margin-top: 10px;
        display: inline-block;
    }
    
    /* Buttons */
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 12px;
        font-weight: 600;
        padding: 12px 24px;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
        background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
        color: white;
    }
    
    /* Primary action buttons */
    .primary-button {
        background: linear-gradient(135deg, #ff6b6b 0%, #ee5a52 100%) !important;
    }
    
    .primary-button:hover {
        background: linear-gradient(135deg, #ee5a52 0%, #ff6b6b 100%) !important;
    }
    
    /* Progress bar */
    .stProgress > div > div > div {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Info boxes */
    .info-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 25px;
        border-radius: 20px;
        color: white;
        margin: 15px 0;
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.2);
    }
    
    .info-box h2 {
        margin: 0 0 10px 0;
        font-weight: 700;
    }
    
    /* Dashboard cards */
    .dashboard-card {
        background: white;
        padding: 25px;
        border-radius: 20px;
        border: none;
        margin: 10px 0;
        transition: all 0.3s ease;
        box-shadow: 0 5px 20px rgba(0, 0, 0, 0.08);
        text-align: center;
    }
    
    .dashboard-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 35px rgba(0, 0, 0, 0.15);
    }
    
    /* Scrollable chat container */
    .chat-container {
        height: 500px;
        overflow-y: auto;
        padding: 20px;
        border-radius: 20px;
        background: #f8f9fa;
        margin-bottom: 20px;
        border: 2px solid #e9ecef;
    }
    
    /* Chat session buttons */
    .chat-session {
        padding: 15px;
        margin: 8px 0;
        border-radius: 15px;
        border: 2px solid #e9ecef;
        background: white;
        cursor: pointer;
        transition: all 0.3s ease;
        text-align: left;
    }
    
    .chat-session:hover {
        border-color: #667eea;
        background: #f0f4ff;
        transform: translateX(5px);
    }
    
    .chat-session.active {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-color: #5a67d8;
    }
    
    /* Input fields */
    .stTextInput>div>div>input {
        border-radius: 12px;
        border: 2px solid #e9ecef;
        padding: 12px 16px;
        font-size: 1rem;
    }
    
    .stTextInput>div>div>input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.2);
    }
    
    /* File uploader */
    .stFileUploader>div>div {
        border: 2px dashed #667eea;
        border-radius: 15px;
        background: #f8f9fa;
    }
    
    /* Sidebar */
    .css-1d391kg {
        background: linear-gradient(180deg, #f8f9fa 0%, #ffffff 100%);
    }
    
    /* Dark theme support */
    @media (prefers-color-scheme: dark) {
        .dashboard-card {
            background: #2d3748;
            color: white;
        }
        
        .chat-container {
            background: #2d3748;
            border-color: #4a5568;
        }
        
        .chat-session {
            background: #2d3748;
            border-color: #4a5568;
            color: white;
        }
        
        .bot-message {
            background: #4a5568;
            color: white;
            border-color: #718096;
        }
    }
    
    /* Scrollbar styling */
    .chat-container::-webkit-scrollbar {
        width: 8px;
    }
    
    .chat-container::-webkit-scrollbar-track {
        background: #f1f1f1;
        border-radius: 10px;
    }
    
    .chat-container::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
    }
    
    .chat-container::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
    }
</style>
""", unsafe_allow_html=True)

# ============ Session State Initialization ============
if 'chat_sessions' not in st.session_state:
    st.session_state.chat_sessions = {}
if 'current_chat_id' not in st.session_state:
    st.session_state.current_chat_id = None
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

def create_new_chat():
    """Create a new chat session"""
    chat_id = str(uuid.uuid4())[:8]
    st.session_state.chat_sessions[chat_id] = {
        'name': f"Chat {len(st.session_state.chat_sessions) + 1}",
        'history': [],
        'created_at': datetime.now().strftime("%H:%M"),
        'documents': []
    }
    st.session_state.current_chat_id = chat_id
    return chat_id

# ============ Header ============
st.markdown("""
<div class="main-header">
    <h1>⚡ PrepPal</h1>
    <p>YOUR SMART STUDY PARTNER - Learn Smarter, Not Harder</p>
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
    st.markdown("## 🎯 Quick Access Dashboard")
    st.markdown("Everything you need to ace your studies in one place!")
    
    # Quick stats in cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="dashboard-card">
            <h3 style="color: #667eea; margin: 0 0 15px 0; font-size: 2.5rem;">📚</h3>
            <h4 style="margin: 0 0 10px 0; color: inherit;">Documents</h4>
            <h1 style="margin: 10px 0; color: inherit; font-size: 2.2rem;">{len(st.session_state.uploaded_docs)}</h1>
            <p style="margin: 0; color: #666; font-size: 0.9rem;">Uploaded files</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        total_chats = sum(len(session['history']) for session in st.session_state.chat_sessions.values())
        st.markdown(f"""
        <div class="dashboard-card">
            <h3 style="color: #764ba2; margin: 0 0 15px 0; font-size: 2.5rem;">💬</h3>
            <h4 style="margin: 0 0 10px 0; color: inherit;">Chat Sessions</h4>
            <h1 style="margin: 10px 0; color: inherit; font-size: 2.2rem;">{len(st.session_state.chat_sessions)}</h1>
            <p style="margin: 0; color: #666; font-size: 0.9rem;">Active conversations</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="dashboard-card">
            <h3 style="color: #ff6b6b; margin: 0 0 15px 0; font-size: 2.5rem;">📅</h3>
            <h4 style="margin: 0 0 10px 0; color: inherit;">Study Plans</h4>
            <h1 style="margin: 10px 0; color: inherit; font-size: 2.2rem;">{1 if st.session_state.current_plan else 0}</h1>
            <p style="margin: 0; color: #666; font-size: 0.9rem;">Active plans</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="dashboard-card">
            <h3 style="color: #00d4ff; margin: 0 0 15px 0; font-size: 2.5rem;">🧠</h3>
            <h4 style="margin: 0 0 10px 0; color: inherit;">Quizzes</h4>
            <h1 style="margin: 10px 0; color: inherit; font-size: 2.2rem;">{len(st.session_state.quiz_answers)}</h1>
            <p style="margin: 0; color: #666; font-size: 0.9rem;">Completed</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Quick Actions in a grid layout
    st.markdown("## ⚡ Quick Actions")
    
    action_col1, action_col2, action_col3, action_col4 = st.columns(4)
    
    with action_col1:
        if st.button("📤 Upload Document", use_container_width=True, key="dash_upload"):
            st.switch_page("pages/documents.py")
    
    with action_col2:
        if st.button("📅 Create Study Plan", use_container_width=True, key="dash_plan"):
            st.switch_page("pages/study_plans.py")
    
    with action_col3:
        if st.button("💬 New Chat", use_container_width=True, key="dash_chat"):
            create_new_chat()
            st.switch_page("pages/chat.py")
    
    with action_col4:
        if st.button("🧠 Generate Quiz", use_container_width=True, key="dash_quiz"):
            st.switch_page("pages/quizzes.py")
    
    # Recent Activity Section
    st.markdown("---")
    st.markdown("## 📈 Recent Activity")
    
    if st.session_state.uploaded_docs or st.session_state.chat_sessions:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📚 Recent Documents")
            if st.session_state.uploaded_docs:
                for doc in list(st.session_state.uploaded_docs)[-3:]:
                    st.markdown(f"""
                    <div class="dashboard-card">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <span style="font-weight: 600;">{doc['filename']}</span>
                            <span style="font-size: 0.8rem; color: #666;">{doc['subject']}</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No documents uploaded yet")
        
        with col2:
            st.markdown("### 💬 Recent Chats")
            if st.session_state.chat_sessions:
                for chat_id, session in list(st.session_state.chat_sessions.items())[-3:]:
                    last_msg = session['history'][-1]['query'][:50] + "..." if session['history'] else "No messages yet"
                    st.markdown(f"""
                    <div class="dashboard-card">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <span style="font-weight: 600;">{session['name']}</span>
                            <span style="font-size: 0.8rem; color: #666;">{session['created_at']}</span>
                        </div>
                        <p style="margin: 5px 0 0 0; font-size: 0.9rem; color: #666;">{last_msg}</p>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No chat sessions yet")
    else:
        st.info("🎯 Get started by uploading documents or starting a chat!")

# ============ TAB 2: Documents ============
with tab2:
    st.markdown("""
    <div class="info-box">
        <h2>📚 STUDY MATERIALS</h2>
        <p style="margin: 5px 0 0 0; opacity: 0.9;">Upload your notes and PDFs to build your knowledge base</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Upload section with enhanced UI
    st.markdown("### 📤 Upload New Document")
    
    with st.container():
        col1, col2 = st.columns([2, 1])
        
        with col1:
            uploaded_file = st.file_uploader(
                "Choose a PDF file",
                type=['pdf'],
                help="Upload your study materials in PDF format",
                label_visibility="collapsed"
            )
        
        with col2:
            doc_subject = st.text_input(
                "Subject/Topic",
                placeholder="e.g., Physics, Mathematics...",
                label_visibility="collapsed"
            )
    
    if st.button("🚀 UPLOAD & PROCESS", use_container_width=True, type="primary") and uploaded_file:
        with st.spinner("🔄 Processing your document..."):
            try:
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
                    st.success(f"✅ **{result['filename']}** uploaded successfully! Processed {result['num_chunks']} knowledge chunks.")
                else:
                    st.error(f"❌ Upload failed: {response.text}")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
    
    st.markdown("---")
    
    # Documents grid view
    st.markdown("### 📑 Your Document Library")
    
    if st.session_state.uploaded_docs:
        # Grid layout for documents
        cols = st.columns(3)
        for i, doc in enumerate(st.session_state.uploaded_docs):
            with cols[i % 3]:
                with st.container():
                    st.markdown(f"""
                    <div class="dashboard-card">
                        <div style="text-align: center;">
                            <h3 style="margin: 0 0 10px 0; color: #667eea; font-size: 2rem;">📄</h3>
                            <h4 style="margin: 0 0 8px 0; font-size: 1rem;">{doc['filename'][:20]}{'...' if len(doc['filename']) > 20 else ''}</h4>
                            <p style="margin: 0 0 8px 0; font-size: 0.9rem; color: #666;">{doc['subject']}</p>
                            <p style="margin: 0; font-size: 0.8rem; color: #999;">{doc['num_chunks']} chunks</p>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("👁️ View", key=f"view_{doc['doc_id']}", use_container_width=True):
                            st.info("🔍 Document viewer coming soon!")
                    with col2:
                        if st.button("🗑️", key=f"delete_{doc['doc_id']}", use_container_width=True):
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
        st.info("""
        📭 **No documents uploaded yet!**
        
        Get started by:
        1. Uploading your PDF notes above
        2. Adding relevant subjects/topics
        3. Building your personal knowledge base
        """)

# ============ TAB 3: Chat (IMPROVED) ============
with tab3:
    st.markdown("""
    <div class="info-box">
        <h2>💬 SMART CHAT</h2>
        <p style="margin: 5px 0 0 0; opacity: 0.9;">Chat with your AI study assistant about your materials</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize current chat if none exists
    if not st.session_state.current_chat_id and not st.session_state.chat_sessions:
        create_new_chat()
    
    # Chat sidebar for session management
    with st.sidebar:
        st.markdown("### 💭 Chat Sessions")
        
        # New chat button
        if st.button("🆕 New Chat Session", use_container_width=True, type="primary"):
            create_new_chat()
            st.rerun()
        
        st.markdown("---")
        
        # Chat sessions list
        for chat_id, session in st.session_state.chat_sessions.items():
            is_active = chat_id == st.session_state.current_chat_id
            
            if st.button(
                f"💬 {session['name']} • {session['created_at']}",
                key=f"chat_btn_{chat_id}",
                use_container_width=True,
                type="primary" if is_active else "secondary"
            ):
                st.session_state.current_chat_id = chat_id
                st.rerun()
        
        st.markdown("---")
        st.markdown("### 📊 Chat Stats")
        current_chat = st.session_state.chat_sessions.get(st.session_state.current_chat_id, {})
        messages_count = len(current_chat.get('history', []))
        st.write(f"**Messages:** {messages_count}")
        st.write(f"**Documents:** {len(st.session_state.uploaded_docs)}")
    
    # Main chat area
    col1, col2, col3 = st.columns([3, 1, 1])
    
    with col1:
        st.markdown(f"#### 💬 {st.session_state.chat_sessions.get(st.session_state.current_chat_id, {}).get('name', 'New Chat')}")

import streamlit.components.v1 as components

components.html(f"""
<style>
  .big-mic-wrap {{ display:flex; align-items:center; gap:12px; margin: 12px 0; }}
  .big-mic {{ width:96px; height:96px; border-radius:48px; display:flex; align-items:center; justify-content:center;
    background: linear-gradient(135deg,#667eea,#764ba2); box-shadow: 0 12px 30px rgba(102,126,234,0.25); cursor:pointer; }}
  .big-mic-icon {{ font-size:44px; color:#fff; }}
  .pp-modal {{ position: fixed; inset: 0; display:none; align-items:center; justify-content:center; background: rgba(0,0,0,0.55); z-index:9999; }}
  .pp-panel {{ width:720px; max-width:95%; background:#fff; border-radius:12px; padding:18px; box-shadow: 0 20px 60px rgba(0,0,0,0.3); }}
  .pp-row {{ display:flex; gap:12px; align-items:center; margin-top:12px; }}
  .pp-field input {{ padding:8px; width:360px; border-radius:8px; border:1px solid #e6e6e6; }}
  .pp-actions button {{ padding:10px 14px; border-radius:8px; border:none; cursor:pointer; }}
  .pp-primary {{ background: linear-gradient(135deg,#667eea,#764ba2); color:white; }}
  .pp-danger {{ background:#ff6b6b; color:white; }}
  .pp-status {{ margin-top:10px; color:#333; font-size:0.95rem; }}
  .pp-debug {{ margin-top:8px; font-family:monospace; font-size:0.85rem; color:#444; white-space:pre-wrap; max-height:120px; overflow:auto; background:#f7f7f7; padding:8px; border-radius:6px; border:1px solid #eee; }}
</style>

<div class="big-mic-wrap">
  <div role="button" id="ppOpen" class="big-mic" title="Click to talk to PrepPal">
    <div class="big-mic-icon">🎙️</div>
  </div>
  <div style="display:flex; flex-direction:column;">
    <div style="font-weight:700; font-size:1.05rem;">Voice Chat</div>
    <div style="color:#666; font-size:0.9rem;">Click to open voice window and start talking</div>
  </div>
</div>

<div id="ppModal" class="pp-modal" aria-hidden="true">
  <div class="pp-panel" role="dialog" aria-modal="true">
    <h3>Talk to PrepPal — Live Voice</h3>
    <div style="margin-top:8px;">Channel: <input id="ppChannel" value="preppl_channel" /></div>
    <div class="pp-row">
      <div class="pp-actions">
        <button id="ppJoin" class="pp-primary">Join & Start Mic</button>
        <button id="ppLeave" class="pp-danger">Leave</button>
        <button id="ppClose">Close</button>
      </div>
      <div id="ppStatus" class="pp-status">Status: Idle</div>
    </div>

    <div style="margin-top:12px; font-size:0.9rem; color:#444;">
      <strong>Note:</strong> Grant microphone access when prompted. Ensure the PrepPal agent is started on the server in the same channel.
    </div>

    <div class="pp-debug" id="ppDebug">Debug output will appear here after fetching token...</div>
  </div>
</div>

<!-- Agora Web NG SDK -->
<script src="https://download.agora.io/sdk/release/AgoraRTC_N.js"></script>

<script>
(function() {{
  // MUST match your Python API base string exactly
  const API_BASE = "{API_BASE_URL}";

  const modal = document.getElementById('ppModal');
  const openBtn = document.getElementById('ppOpen');
  const closeBtn = document.getElementById('ppClose');
  const joinBtn = document.getElementById('ppJoin');
  const leaveBtn = document.getElementById('ppLeave');
  const statusEl = document.getElementById('ppStatus');
  const debugEl = document.getElementById('ppDebug');
  const channelInput = document.getElementById('ppChannel');

  let client = null;
  let localAudioTrack = null;
  let joined = false;
  let lastToken = null;
  let lastAppId = null;

  function debug(msg) {{
    console.log('[PrepPal debug]', msg);
    debugEl.textContent = typeof msg === 'string' ? msg : JSON.stringify(msg, null, 2);
  }}

  openBtn.addEventListener('click', () => {{
    modal.style.display = 'flex';
    modal.setAttribute('aria-hidden', 'false');
    debug('Modal opened');
    statusEl.textContent = 'Status: Idle';
  }});

  closeBtn.addEventListener('click', async () => {{
    await leaveChannel();
    modal.style.display = 'none';
    modal.setAttribute('aria-hidden', 'true');
    debug('Modal closed');
  }});

  async function fetchToken() {{
    debug('Fetching token from: ' + API_BASE + '/get-temp-token');
    statusEl.textContent = 'Status: Fetching token...';
    try {{
      const res = await fetch(API_BASE + '/get-temp-token', {{ credentials: 'include' }});
      const text = await res.text();
      debug('HTTP ' + res.status + ' response body:\\n' + text);
      if (!res.ok) {{
        // show full body for easier debugging
        statusEl.textContent = 'Status: Token fetch failed (see debug)';
        debug('Token fetch failed: ' + text);
        return null;
      }}
      // parse JSON if possible
      let data = null;
      try {{
        data = JSON.parse(text);
      }} catch (e) {{
        debug('Failed to parse JSON: ' + e + '\\nBody:' + text);
        statusEl.textContent = 'Status: Token parse failed (see debug)';
        return null;
      }}
      // show what server returned in UI
      statusEl.textContent = 'Status: Token fetched';
      debug('Parsed response:\\n' + JSON.stringify(data, null, 2));
      if (!data.appId || (!data.token && !data.token_masked)) {{
        statusEl.textContent = 'Status: Server returned no appId/token. Check /get-temp-token';
        return null;
      }}
      // prefer token field if present else fallback to token_masked presence (masked only used for debug)
      lastAppId = data.appId;
      // If server returned only masked token, we still proceed (we expect real token in production)
      lastToken = data.token || (data.token_masked ? null : null);
      // show masked token if it exists
      debug('appId: ' + data.appId + '\\ntoken_masked: ' + (data.token_masked || '(none)') + '\\ntoken_used_is_client: ' + (data.token_used_is_client));
      // return whole object so joinChannel can decide
      return data;
    }} catch (err) {{
      debug('Fetch exception: ' + err);
      statusEl.textContent = 'Status: Token fetch exception (see debug)';
      return null;
    }}
  }}

  async function joinChannel() {{
    if (joined) {{
      debug('Already joined');
      return;
    }}
    statusEl.textContent = 'Status: Fetching token...';
    const channel = channelInput.value || 'preppl_channel';
    const data = await fetchToken();
    if (!data) return;

    // If server gave only masked token (debug endpoint), we must call the same endpoint that returns real token in production.
    // For now if data.token is absent, attempt to read the token from a field 'token' (if present) else abort.
    if (!data.token) {{
      // If you see this message, your server returned only a masked token for debug.
      statusEl.textContent = 'Status: Server returned masked token only; ensure /get-temp-token returns real token field "token"';
      debug('Aborting join: no usable token in server response.');
      return;
    }}

    const APPID = data.appId;
    const TOKEN = data.token; // real token must be here (not token_masked)
    debug('Using APPID:' + APPID + ' TOKEN masked:' + (data.token_masked || '(no masked)'));

    try {{
      client = AgoraRTC.createClient({{ mode: 'rtc', codec: 'vp8' }});
      client.on('user-published', async (user, mediaType) => {{
        try {{
          await client.subscribe(user, mediaType);
          if (mediaType === 'audio') {{
            const remoteAudioTrack = user.audioTrack;
            remoteAudioTrack.play();
            console.log('Playing remote audio');
          }}
        }} catch(e) {{
          console.error('subscribe error', e);
        }}
      }});

      client.on('user-unpublished', (user) => {{
        console.log('user unpublished', user);
      }});

      statusEl.textContent = 'Status: Joining channel...';
      const uid = await client.join(APPID, channel, TOKEN, null);
      localAudioTrack = await AgoraRTC.createMicrophoneAudioTrack();
      await client.publish([localAudioTrack]);
      joined = true;
      statusEl.textContent = 'Status: Joined. Microphone ON (UID=' + uid + ')';
      debug('Joined channel ' + channel + ' uid=' + uid);
    }} catch (err) {{
      console.error('joinChannel error', err);
      statusEl.textContent = 'Status: Join failed — see debug';
      debug('joinChannel error: ' + (err.message || err));
    }}
  }}

  async function leaveChannel() {{
    if (!joined) return;
    try {{
      if (localAudioTrack) {{
        localAudioTrack.close();
        localAudioTrack = null;
      }}
      await client.leave();
      joined = false;
      statusEl.textContent = 'Status: Left channel';
      debug('Left channel');
    }} catch (err) {{
      console.error('leaveChannel error', err);
      statusEl.textContent = 'Status: Leave failed';
      debug('leaveChannel error: ' + (err.message || err));
    }}
  }}

  joinBtn.addEventListener('click', joinChannel);
  leaveBtn.addEventListener('click', leaveChannel);

}})();
</script>
""", height=320, scrolling=True)



  
   # ---------- Agora Agent Controls (add inside Chat tab near voice toggle) ----------
if 'agora_agent' not in st.session_state:
    st.session_state.agora_agent = {"agent_id": None, "status": None, "channel": None}

st.markdown("### 🔌 Agora Conversational AI (voice agent)")
col_a, col_b = st.columns([3,2])
with col_a:
    channel_name = st.text_input("Agora channel name", value=st.session_state.agora_agent.get("channel") or "preppl_channel")
with col_b:
    if st.session_state.voice_enabled:
        if st.button("🔴 Stop Agora Agent", use_container_width=True):
            agent_id = st.session_state.agora_agent.get("agent_id")
            if agent_id:
                try:
                    resp = requests.post(f"{API_BASE_URL}/stop-agent", json={"agent_id": agent_id}, timeout=15)
                    if resp.status_code == 200:
                        st.session_state.agora_agent = {"agent_id": None, "status": None, "channel": None}
                        st.success("Agora agent stopped.")
                    else:
                        st.error(f"Stop failed: {resp.text}")
                except Exception as e:
                    st.error(f"Error stopping agent: {e}")
            else:
                st.info("No agent running.")
    else:
        if st.button("🟢 Start Agora Agent (voice)", use_container_width=True):
            # start agent flow
            try:
                # pass agent token if you have it; if not pass None and backend must generate/accept temporary token
                payload = {
                    "channel": channel_name,
                    "agent_token": None,   # optional: put token string or leave None
                    "name": f"preppl-{int(time.time())}"
                }
                resp = requests.post(f"{API_BASE_URL}/start-agent", json=payload, timeout=15)
                if resp.status_code == 200:
                    data = resp.json()
                    st.session_state.agora_agent = {
                        "agent_id": data.get("agent_id"),
                        "status": data.get("status"),
                        "channel": channel_name
                    }
                    st.session_state.voice_enabled = True
                    st.success(f"Agent started: {data.get('agent_id')}")
                else:
                    st.error(f"Start failed: {resp.text}")
            except Exception as e:
                st.error(f"Error starting agent: {e}")

# show agent status
if st.session_state.agora_agent.get("agent_id"):
    st.info(f"Agora Agent: `{st.session_state.agora_agent['agent_id']}` — status: {st.session_state.agora_agent['status']} — channel: {st.session_state.agora_agent['channel']}")
else:
    st.write("No Agora agent running.")

    
    with col3:
        if st.button("🗑️ Clear Chat", use_container_width=True):
            if st.session_state.current_chat_id in st.session_state.chat_sessions:
                st.session_state.chat_sessions[st.session_state.current_chat_id]['history'] = []
                st.rerun()
    
    # Document selector with improved UI
    if st.session_state.uploaded_docs:
        doc_options = ["All Documents"] + [doc['filename'] for doc in st.session_state.uploaded_docs]
        selected_doc = st.selectbox(
            "📚 Chat with specific document:",
            doc_options, 
            help="Choose which documents to reference in this chat"
        )
    else:
        selected_doc = None
        st.warning("⚠️ Upload documents to enable smart chat with your materials!")
    
    # Enhanced chat container with better styling
    current_chat = st.session_state.chat_sessions.get(st.session_state.current_chat_id, {})
    chat_history = current_chat.get('history', [])
    
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    
    if not chat_history:
        st.markdown("""
        <div class="bot-message">
            <div style="display: flex; align-items: center; margin-bottom: 10px;">
                <div style="width: 32px; height: 32px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 50%; display: flex; align-items: center; justify-content: center; margin-right: 10px;">
                    <span style="color: white; font-size: 0.8rem;">AI</span>
                </div>
                <strong>PrepPal Assistant</strong>
            </div>
            <p style="margin: 0; line-height: 1.5;">Hello! I'm your AI study assistant. I can help you:</p>
            <ul style="margin: 10px 0 0 0; padding-left: 20px; line-height: 1.5;">
                <li>Answer questions about your uploaded materials</li>
                <li>Explain complex concepts in simple terms</li>
                <li>Generate study plans and summaries</li>
                <li>Create quiz questions to test your knowledge</li>
            </ul>
            <p style="margin: 10px 0 0 0; line-height: 1.5;">What would you like to learn today?</p>
            <div class="message-time">Just now</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        for msg in chat_history:
            # User message
            st.markdown(f"""
            <div class="user-message">
                <div style="display: flex; align-items: center; margin-bottom: 8px;">
                    <div style="width: 32px; height: 32px; background: rgba(255, 255, 255, 0.2); border-radius: 50%; display: flex; align-items: center; justify-content: center; margin-right: 10px;">
                        <span style="color: white; font-size: 0.8rem;">You</span>
                    </div>
                    <strong>You</strong>
                </div>
                <p style="margin: 0; line-height: 1.5;">{msg['query']}</p>
                <div class="message-time">{msg.get('timestamp', 'Recently')}</div>
            </div>
            """, unsafe_allow_html=True)
            
            # Bot message
            sources_text = ""
            if msg.get('sources'):
                sources_text = f"""
                <div class="sources-badge">
                    📚 Sources: {len(msg['sources'])} document{'' if len(msg['sources']) == 1 else 's'}
                </div>
                """
            
            st.markdown(f"""
            <div class="bot-message">
                <div style="display: flex; align-items: center; margin-bottom: 8px;">
                    <div style="width: 32px; height: 32px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 50%; display: flex; align-items: center; justify-content: center; margin-right: 10px;">
                        <span style="color: white; font-size: 0.8rem;">AI</span>
                    </div>
                    <strong>PrepPal</strong>
                </div>
                <p style="margin: 0; line-height: 1.5;">{msg['answer']}</p>
                {sources_text}
                <div class="message-time">{msg.get('timestamp', 'Recently')}</div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Enhanced chat input with quick actions
    st.markdown("#### 💭 Your Message")
    
    # Quick action buttons

    
    # Chat input
    user_query = st.text_area(
        "Type your message here...",
        placeholder="Ask anything about your study materials, request explanations, or ask for examples...",
        height=100,
        key="chat_input",
        label_visibility="collapsed"
    )
    
    col1, col2 = st.columns([4, 1])
    
    with col1:
        if st.button("🚀 Send Message", use_container_width=True, type="primary") and user_query:
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
                        
                        # Update current chat history
                        if st.session_state.current_chat_id in st.session_state.chat_sessions:
                            st.session_state.chat_sessions[st.session_state.current_chat_id]['history'].append({
                                'query': user_query,
                                'answer': result['answer'],
                                'sources': result['sources'],
                                'timestamp': result['timestamp']
                            })
                        
                        st.rerun()
                    else:
                        st.error(f"❌ Chat failed: {response.text}")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
    
    with col2:
        if st.button("🔄 Clear", use_container_width=True):
            st.session_state.chat_input = ""
            st.rerun()

# ============ TAB 4: Study Plans ============
with tab4:
    st.markdown("""
    <div class="info-box">
        <h2>📅 STUDY PLANS</h2>
        <p style="margin: 5px 0 0 0; opacity: 0.9;">AI-powered personalized study schedules</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Plan creation form
    st.markdown("### 🎯 Create New Study Plan")
    
    with st.container():
        col1, col2 = st.columns(2)
        
        with col1:
            exam_date = st.date_input(
                "📆 Exam Date",
                min_value=datetime.now().date(),
                value=datetime.now().date() + timedelta(days=30),
                help="When is your exam?"
            )
            
            hours_per_day = st.slider(
                "⏰ Study Hours per Day",
                min_value=1.0,
                max_value=12.0,
                value=4.0,
                step=0.5,
                help="How many hours can you study daily?"
            )
        
        with col2:
            subjects_input = st.text_area(
                "📚 Subjects & Topics",
                placeholder="Mathematics - Algebra, Calculus\nPhysics - Mechanics, Optics\nChemistry - Organic, Inorganic",
                height=120,
                help="Enter subjects and specific topics (one per line)"
            )
    
    if st.button("🚀 GENERATE SMART PLAN", use_container_width=True, type="primary"):
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
                        st.success(f"✅ Study plan created! **{result['total_days']} days**, **{result['total_hours']} total hours** of focused study.")
                        st.rerun()
                    else:
                        st.error(f"❌ Plan creation failed: {response.text}")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
    
    st.markdown("---")
    
    # Display current plan
    st.markdown("### 📋 Your Study Plan")
    
    if st.session_state.current_plan:
        plan_data = st.session_state.current_plan['plan']
        
        # Progress overview
        total_days = st.session_state.current_plan['total_days']
        completed_days = sum(1 for day in plan_data if day.get('completed', False))
        progress = completed_days / total_days if total_days > 0 else 0
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Days", total_days)
        with col2:
            st.metric("Completed Days", completed_days)
        with col3:
            st.metric("Progress", f"{progress:.1%}")
        
        st.progress(progress)
        
        # Interactive plan table
        st.markdown("#### 📅 Daily Schedule")
        for i, day in enumerate(plan_data):
            with st.expander(f"Day {day['day']}: {day['date']} - {day['subject']} ({day['hours']} hours)"):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"**Topics:** {day['topics']}")
                with col2:
                    completed = st.checkbox(
                        "Completed", 
                        value=day.get('completed', False),
                        key=f"day_{i}_completed"
                    )
                    if completed != day.get('completed', False):
                        plan_data[i]['completed'] = completed
                        st.rerun()
        
        # Plan actions
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 Update Progress", use_container_width=True):
                st.success("Progress updated!")
        with col2:
            if st.button("🗑️ Clear Plan", use_container_width=True):
                st.session_state.current_plan = None
                st.rerun()
    else:
        st.info("""
        📭 **No study plan yet!**
        
        Create your first AI-powered study plan:
        1. Set your exam date
        2. Choose daily study hours  
        3. List your subjects & topics
        4. Generate personalized schedule
        """)

# ============ TAB 5: Quizzes ============
with tab5:
    st.markdown("""
    <div class="info-box">
        <h2>🧠 QUIZ MASTER</h2>
        <p style="margin: 5px 0 0 0; opacity: 0.9;">Test your knowledge with AI-generated quizzes</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Quiz generation
    st.markdown("### 🎲 Create New Quiz")
    
    with st.container():
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            quiz_topic = st.text_input(
                "Quiz Topic",
                placeholder="e.g., Photosynthesis, Newton's Laws, Algebra",
                help="Specific topic or leave blank for general quiz"
            )
        
        with col2:
            num_questions = st.selectbox("Questions", [3, 5, 10, 15], index=1)
        
        with col3:
            difficulty = st.selectbox("Difficulty", ["Easy", "Medium", "Hard"], index=1)
    
    if st.button("🚀 GENERATE QUIZ", use_container_width=True, type="primary"):
        with st.spinner("🤖 Generating quiz questions..."):
            try:
                doc_ids = [doc['doc_id'] for doc in st.session_state.uploaded_docs]
                
                response = requests.post(
                    f"{API_BASE_URL}/quiz",
                    json={
                        "topic": quiz_topic or None,
                        "doc_ids": doc_ids if doc_ids else None,
                        "num_questions": num_questions,
                        "difficulty": difficulty
                    }
                )
                
                if response.status_code == 200:
                    result = response.json()
                    st.session_state.quiz_questions = result['questions']
                    st.session_state.quiz_answers = {}
                    st.success(f"✅ Quiz generated with **{len(result['questions'])} {difficulty.lower()}** questions!")
                    st.rerun()
                else:
                    st.error(f"❌ Quiz generation failed: {response.text}")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
    
    st.markdown("---")
    
    # Display quiz
    if st.session_state.quiz_questions:
        st.markdown("### 📝 Your Quiz")
        
        for i, question in enumerate(st.session_state.quiz_questions):
            with st.container():
                st.markdown(f"#### ❓ Question {i+1}")
                st.markdown(f"**{question['question']}**")
                
                # Enhanced options with better styling
                options = question['options']
                selected_option = st.radio(
                    f"Select your answer for question {i+1}:",
                    options=options,
                    key=f"q_{i}",
                    label_visibility="collapsed"
                )
                
                st.session_state.quiz_answers[i] = options.index(selected_option)
                
                st.markdown("---")
        
        # Submit quiz
        if st.button("✅ SUBMIT QUIZ", use_container_width=True, type="primary"):
            correct = 0
            results = []
            
            for i, question in enumerate(st.session_state.quiz_questions):
                user_answer = st.session_state.quiz_answers.get(i)
                correct_answer = question['correct_index']
                is_correct = user_answer == correct_answer
                
                if is_correct:
                    correct += 1
                
                results.append({
                    'question': question['question'],
                    'user_answer': question['options'][user_answer] if user_answer is not None else 'Not answered',
                    'correct_answer': question['options'][correct_answer],
                    'is_correct': is_correct,
                    'explanation': question['explanation']
                })
            
            score = (correct / len(st.session_state.quiz_questions)) * 100
            
            # Score display
            if score >= 80:
                st.balloons()
                st.markdown(f"""
                <div class="info-box" style="background: linear-gradient(135deg, #00b09b 0%, #96c93d 100%);">
                    <h2>🎉 Excellent! {score:.0f}%</h2>
                    <p style="margin: 5px 0 0 0; opacity: 0.9;">{correct} out of {len(st.session_state.quiz_questions)} correct - You're crushing it!</p>
                </div>
                """, unsafe_allow_html=True)
            elif score >= 60:
                st.markdown(f"""
                <div class="info-box" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
                    <h2>👍 Good Job! {score:.0f}%</h2>
                    <p style="margin: 5px 0 0 0; opacity: 0.9;">{correct} out of {len(st.session_state.quiz_questions)} correct - Keep practicing!</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="info-box" style="background: linear-gradient(135deg, #ff6b6b 0%, #ee5a52 100%);">
                    <h2>💪 Keep Learning! {score:.0f}%</h2>
                    <p style="margin: 5px 0 0 0; opacity: 0.9;">{correct} out of {len(st.session_state.quiz_questions)} correct - Review and try again!</p>
                </div>
                """, unsafe_allow_html=True)
            
            # Detailed results
            st.markdown("### 📚 Review Answers")
            for i, result in enumerate(results):
                with st.expander(f"Question {i+1}: {'✅' if result['is_correct'] else '❌'}"):
                    st.write(f"**Your answer:** {result['user_answer']}")
                    st.write(f"**Correct answer:** {result['correct_answer']}")
                    st.write(f"**Explanation:** {result['explanation']}")
    else:
        st.info("""
        📭 **No quiz available!**
        
        Generate your first quiz by:
        1. Choosing a topic (optional)
        2. Selecting number of questions
        3. Setting difficulty level
        4. Generating from your study materials
        """)

# ============ Footer ============
st.markdown("---")
st.markdown("""
<div style="text-align: center; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; border-radius: 20px; margin-top: 30px;">
    <h3 style="color: white; margin: 0;">BUILT FOR HACKATHON 2025 🚀</h3>
    <p style="color: white; margin: 10px 0 0 0; font-size: 1.1rem;">PrepPal - Learn Smarter, Not Harder</p>
    <p style="color: white; margin: 5px 0 0 0; opacity: 0.8;">AI-Powered Study Assistant</p>
</div>
""", unsafe_allow_html=True)