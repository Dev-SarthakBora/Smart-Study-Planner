@echo off
REM Automated setup for Windows

echo 🚀 Setting up PrepPal...

REM Create virtual environment
python -m venv venv
call venv\Scripts\activate

REM Install dependencies
python -m pip install --upgrade pip
pip install -r requirements.txt

REM Copy environment template
if not exist .env (
    copy .env.template .env
    echo ✅ Created .env file
    echo ⚠️  Please edit .env and add your GOOGLE_API_KEY
)

REM Create data directory
if not exist data\uploads mkdir data\uploads

REM Generate demo data
python scripts\create_demo_data.py

echo.
echo ✅ Setup complete!
echo.
echo Next steps:
echo 1. Edit .env and add your GOOGLE_API_KEY
echo 2. Run backend: cd backend ^&^& uvicorn main:app --reload
echo 3. Run frontend: cd frontend ^&^& streamlit run app.py
pause