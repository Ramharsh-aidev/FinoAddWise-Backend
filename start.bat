@echo off
REM Financial Advisor API Startup Script for Windows

echo 🚀 Starting Financial Advisor API...

REM Check if virtual environment exists
if not exist "fino-env" (
    echo Creating virtual environment...  
    python -m venv fino-env
)

REM Activate virtual environment
call fino-env\Scripts\activate.bat

REM Install dependencies
echo 📦 Installing dependencies...
pip install -r requirements.txt

REM Check environment variables
if "%OPENAI_API_KEY%"=="" (
    echo ⚠️  Warning: OPENAI_API_KEY not set
    echo Please set your OpenAI API key in the .env file
)

if "%PINECONE_API_KEY%"=="" (
    echo ⚠️  Warning: PINECONE_API_KEY not set  
    echo Please set your Pinecone API key in the .env file
)

REM Start the application
echo 🔥 Starting FastAPI server...
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

pause