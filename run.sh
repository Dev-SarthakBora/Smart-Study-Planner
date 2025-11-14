#!/bin/bash
# Quick Run Script for PrepPal
# Starts both backend and frontend in one command

set -e

echo "🚀 Starting PrepPal..."
echo ""

# Kill any existing processes on the ports
echo "🧹 Cleaning up existing processes..."
lsof -ti:8000 | xargs kill -9 2>/dev/null || true
lsof -ti:8501 | xargs kill -9 2>/dev/null || true
sleep 1

# Activate virtual environment
if [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "❌ Virtual environment not found. Run setup.sh first!"
    exit 1
fi

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Creating from template..."
    cp .env.template .env
    echo "❌ Please edit .env and add your GOOGLE_API_KEY, then run again."
    exit 1
fi

# Start backend in background
echo "🔧 Starting backend server..."
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000 > ../logs/backend.log 2>&1 &
BACKEND_PID=$!
cd ..

# Wait for backend to start
echo "⏳ Waiting for backend to initialize..."
sleep 3

# Check if backend is running
if ! curl -s http://localhost:8000 > /dev/null; then
    echo "❌ Backend failed to start. Check logs/backend.log"
    kill $BACKEND_PID 2>/dev/null || true
    exit 1
fi

echo "✅ Backend running (PID: $BACKEND_PID)"

# Start frontend in background
echo "🎨 Starting frontend..."
cd frontend
streamlit run app.py > ../logs/frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..

echo "✅ Frontend running (PID: $FRONTEND_PID)"
echo ""
echo "═══════════════════════════════════════════════════"
echo "✅ PrepPal is running!"
echo "═══════════════════════════════════════════════════"
echo ""
echo "📍 Backend API:  http://localhost:8000"
echo "📍 API Docs:     http://localhost:8000/docs"
echo "📍 Frontend UI:  http://localhost:8501"
echo ""
echo "📋 Backend PID:  $BACKEND_PID"
echo "📋 Frontend PID: $FRONTEND_PID"
echo ""
echo "📁 Logs:"
echo "   Backend:  logs/backend.log"
echo "   Frontend: logs/frontend.log"
echo ""
echo "Press Ctrl+C to stop all services"
echo "═══════════════════════════════════════════════════"
echo ""

# Create stop function
cleanup() {
    echo ""
    echo "🛑 Stopping PrepPal..."
    kill $BACKEND_PID 2>/dev/null || true
    kill $FRONTEND_PID 2>/dev/null || true
    echo "✅ All services stopped"
    exit 0
}

# Trap Ctrl+C
trap cleanup INT TERM

# Wait for processes
wait