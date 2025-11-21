from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.routers import documents, strategies, risk_assessment
from app.core.config import settings
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Financial Advisor API",
    description="RAG-powered financial advisory system with AI agents",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(documents.router, prefix="/api/v1", tags=["documents"])
app.include_router(strategies.router, prefix="/api/v1", tags=["strategies"])
app.include_router(risk_assessment.router, prefix="/api/v1", tags=["risk"])

@app.get("/")
async def root():
    """
    Root endpoint - returns basic API information
    """
    return {
        "message": "Financial Advisor API",
        "version": "1.0.0",
        "description": "RAG-powered financial advisory system"
    }

@app.get("/health")
async def health_check():
    """
    Health check endpoint to verify API is running
    """
    return {
        "status": "healthy",
        "message": "Financial Advisor API is running",
        "version": "1.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)