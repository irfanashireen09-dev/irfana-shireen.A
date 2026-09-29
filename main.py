from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.routes import router

app = FastAPI(
    title="LegalEase API",
    description="AI-Powered Legal Document Generator",
    version="1.0.0"
)

# --------------------------------------------
# CORS
# --------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8501",
        "http://127.0.0.1:8501"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --------------------------------------------
# Include API routes
# --------------------------------------------

app.include_router(router)

# --------------------------------------------
# Root endpoint
# --------------------------------------------

@app.get("/")
def root():
    return {
        "application": "LegalEase",
        "status": "running",
        "message": "LegalEase FastAPI backend is running",
        "docs": "/docs"
    }

# --------------------------------------------
# Health check
# --------------------------------------------

@app.get("/health")
def health():
    return {
        "status": "healthy"
    }