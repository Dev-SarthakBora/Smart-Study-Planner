#!/bin/bash
# PrepPal Setup Script for Unix/macOS/Linux
# Automated environment setup and dependency installation

set -e  # Exit on error

echo "════════════════════════════════════════════════════════"
echo "🚀 PrepPal Setup - Smart Study Planner"
echo "════════════════════════════════════════════════════════"
echo ""

# Check Python version
echo "📋 Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.10 or higher."
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
REQUIRED_VERSION="3.10"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo "❌ Python $PYTHON_VERSION found, but Python $REQUIRED_VERSION or higher is required."
    exit 1
fi

echo "✅ Python $PYTHON_VERSION detected"
echo ""

# Create virtual environment
echo "📦 Creating virtual environment..."
if [ -d "venv" ]; then
    echo "⚠️  Virtual environment already exists. Skipping creation."
else
    python3 -m venv venv
    echo "✅ Virtual environment created"
fi
echo ""

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate
echo "✅ Virtual environment activated"
echo ""

# Upgrade pip
echo "⬆️  Upgrading pip..."
python -m pip install --upgrade pip --quiet
echo "✅ Pip upgraded"
echo ""

# Install dependencies
echo "📥 Installing dependencies..."
echo "   This may take a few minutes..."
pip install -r requirements.txt --quiet
echo "✅ All dependencies installed"
echo ""

# Create .env file
echo "⚙️  Setting up environment configuration..."
if [ -f ".env" ]; then
    echo "⚠️  .env file already exists. Skipping creation."
else
    cp .env.template .env
    echo "✅ Created .env file from template"
    echo "⚠️  IMPORTANT: Edit .env and add your GOOGLE_API_KEY!"
fi
echo ""

# Create data directories
echo "📁 Creating data directories..."
mkdir -p data/uploads
touch data/uploads/.gitkeep
echo "✅ Data directories created"
echo ""

# Generate demo data
echo "📄 Generating demo study material..."
if python scripts/create_demo_data.py; then
    echo "✅ Demo data created successfully"
else
    echo "⚠️  Demo data creation failed (non-critical)"
fi
echo ""

# Create test directory structure
echo "🧪 Setting up test directory..."
mkdir -p tests
touch tests/__init__.py
echo "✅ Test directory ready"
echo ""

# Summary
echo "════════════════════════════════════════════════════════"
echo "✅ Setup Complete!"
echo "════════════════════════════════════════════════════════"
echo ""
echo "📝 Next Steps:"
echo ""
echo "1️⃣  Edit .env file and add your Google API key:"
echo "   nano .env"
echo "   or"
echo "   open .env"
echo ""
echo "2️⃣  Start the backend server (Terminal 1):"
echo "   cd backend"
echo "   uvicorn main:app --reload"
echo ""
echo "3️⃣  Start the frontend (Terminal 2):"
echo "   cd frontend"
echo "   streamlit run app.py"
echo ""
echo "4️⃣  Open your browser:"
echo "   Backend API: http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
echo "   Frontend UI: http://localhost:8501"
echo ""
echo "════════════════════════════════════════════════════════"
echo "🎉 Happy Studying with PrepPal!"
echo "════════════════════════════════════════════════════════"
echo ""

# Check if we should keep terminal open
if [ -z "$PS1" ]; then
    read -p "Press Enter to continue..."
fi