# Financial Advisor Backend

A RAG-powered financial advisory system built with FastAPI, LangChain, and Pinecone.

## Features

- RAG pipeline for analyzing financial policy documents
- AI agents for personalized financial strategies
- Risk profile assessment
- Compliance checking with 95% accuracy
- Dockerized deployment

## Tech Stack

- **Backend**: Python, FastAPI
- **AI/ML**: LangChain, RAG
- **Vector Database**: Pinecone
- **Containerization**: Docker

## Setup

1. Create virtual environment:
```bash
python -m venv fino-env
```

2. Activate environment:
```bash
fino-env\Scripts\activate  # Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables (see .env.example)

5. Run the application:
```bash
uvicorn main:app --reload
```

## API Endpoints

- `POST /analyze-document` - Analyze financial documents for compliance
- `POST /generate-strategy` - Generate personalized financial strategy
- `POST /assess-risk` - Assess user risk profile
- `GET /health` - Health check endpoint

## Docker

Build and run with Docker:
```bash
docker build -t financial-advisor .
docker run -p 8000:8000 financial-advisor
```