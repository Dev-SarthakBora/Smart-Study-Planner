#!/bin/bash
# Automated setup for Unix/macOS

echo "🚀 Setting up PrepPal..."

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Copy environment template
if [ ! -f .env ]; then
    cp .env.template .env
    echo "✅ Created .env file"
    echo "⚠️  Please edit .env and add your GOOGLE_API_KEY"
fi

# Create data directory
mkdir -p data/uploads

# Generate demo data
python scripts/create_demo_data.py

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env and add your GOOGLE_API_KEY"
echo "2. Run backend: cd backend && uvicorn main:app --reload"
echo "3. Run frontend: cd frontend && streamlit run app.py"