#!/bin/bash

# Financial Advisor API Startup Script

echo "🚀 Starting Financial Advisor API..."

# Check if virtual environment exists
if [ ! -d "fino-env" ]; then
    echo "Creating virtual environment..."
    python -m venv fino-env
fi

# Activate virtual environment
source fino-env/bin/activate  # Linux/Mac
# fino-env\Scripts\activate  # Windows

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Check environment variables
if [ -z "$OPENAI_API_KEY" ]; then
    echo "⚠️  Warning: OPENAI_API_KEY not set"
    echo "Please set your OpenAI API key in the .env file"
fi

if [ -z "$PINECONE_API_KEY" ]; then
    echo "⚠️  Warning: PINECONE_API_KEY not set"
    echo "Please set your Pinecone API key in the .env file"
fi

# Start the application
echo "🔥 Starting FastAPI server..."
uvicorn main:app --host 0.0.0.0 --port 8000 --reload