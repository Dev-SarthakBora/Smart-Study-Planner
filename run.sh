#!/bin/bash
# Quick run script for development

echo "🚀 Starting PrepPal..."

# Kill any existing processes
pkill -f "uvicorn backend.main:app"
pkill -f "streamlit run"

# Start backend in background
echo "Starting backend..."
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
cd ..

# Wait for backend to start
sleep 3

# Start frontend
echo "Starting frontend..."
cd frontend
streamlit run app.py &
FRONTEND_PID=$!
cd ..

echo ""
echo "✅ PrepPal is running!"
echo "Backend PID: $BACKEND_PID"
echo "Frontend PID: $FRONTEND_PID"
echo ""
echo "Backend API: http://localhost:8000"
echo "Frontend UI: http://localhost:8501"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for Ctrl+C
trap "kill $BACKEND_PID $FRONTEND_PID; exit" INT
wait