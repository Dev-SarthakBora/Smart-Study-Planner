@echo off
REM PrepPal Setup Script for Windows
REM Automated environment setup and dependency installation

echo ================================================================
echo 🚀 PrepPal Setup - Smart Study Planner
echo ================================================================
echo.

REM Check Python installation
echo 📋 Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH.
    echo Please install Python 3.10 or higher from python.org
    pause
    exit /b 1
)

for /f "tokens=2" %%v in ('python --version 2^>^&1') do set PYTHON_VERSION=%%v
echo ✅ Python %PYTHON_VERSION% detected
echo.

REM Create virtual environment
echo 📦 Creating virtual environment...
if exist "venv\" (
    echo ⚠️  Virtual environment already exists. Skipping creation.
) else (
    python -m venv venv
    echo ✅ Virtual environment created
)
echo.

REM Activate virtual environment
echo 🔌 Activating virtual environment...
call venv\Scripts\activate.bat
echo ✅ Virtual environment activated
echo.

REM Upgrade pip
echo ⬆️  Upgrading pip...
python -m pip install --upgrade pip --quiet
echo ✅ Pip upgraded
echo.

REM Install dependencies
echo 📥 Installing dependencies...
echo    This may take a few minutes...
pip install -r requirements.txt --quiet
if errorlevel 1 (
    echo ❌ Failed to install dependencies
    pause
    exit /b 1
)
echo ✅ All dependencies installed
echo.

REM Create .env file
echo ⚙️  Setting up environment configuration...
if exist ".env" (
    echo ⚠️  .env file already exists. Skipping creation.
) else (
    copy .env.template .env >nul
    echo ✅ Created .env file from template
    echo ⚠️  IMPORTANT: Edit .env and add your GOOGLE_API_KEY!
)
echo.

REM Create data directories
echo 📁 Creating data directories...
if not exist "data\uploads\" mkdir data\uploads
type nul > data\uploads\.gitkeep
echo ✅ Data directories created
echo.

REM Generate demo data
echo 📄 Generating demo study material...
python scripts\create_demo_data.py
if errorlevel 1 (
    echo ⚠️  Demo data creation failed (non-critical)
) else (
    echo ✅ Demo data created successfully
)
echo.

REM Create test directory structure
echo 🧪 Setting up test directory...
if not exist "tests\" mkdir tests
type nul > tests\__init__.py
echo ✅ Test directory ready
echo.

REM Summary
echo ================================================================
echo ✅ Setup Complete!
echo ================================================================
echo.
echo 📝 Next Steps:
echo.
echo 1️⃣  Edit .env file and add your Google API key:
echo    notepad .env
echo.
echo 2️⃣  Start the backend server (Command Prompt 1):
echo    cd backend
echo    uvicorn main:app --reload
echo.
echo 3️⃣  Start the frontend (Command Prompt 2):
echo    cd frontend
echo    streamlit run app.py
echo.
echo 4️⃣  Open your browser:
echo    Backend API: http://localhost:8000
echo    API Docs: http://localhost:8000/docs
echo    Frontend UI: http://localhost:8501
echo.
echo ================================================================
echo 🎉 Happy Studying with PrepPal!
echo ================================================================
echo.

pause