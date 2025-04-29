from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from services.parse_pdf import extract_income_statement
from services.generate_story import generate_story_from_json
import os
import logging
from typing import Dict, Any
import time

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("financial-analyzer-api")

app = FastAPI(
    title="Financial Document Analyzer API",
    description="API for analyzing financial documents, extracting income statements, and generating insights",
    version="1.0.0"
)

# Get environment variables
PORT = int(os.environ.get("PORT", 8000))
FRONTEND_URL = os.environ.get("FRONTEND_URL", "http://localhost:5173")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL, "http://localhost:3000", "http://localhost:5173", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def validate_file(file: UploadFile = File(...)) -> bytes:
    """Validate that the uploaded file is a PDF and return its contents."""
    # Check file size (10MB limit)
    content = await file.read()
    if len(content) > 10 * 1024 * 1024:  # 10MB
        raise HTTPException(status_code=400, detail="File too large (max 10MB)")
    
    # Check file type
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted")
    
    return content

@app.post("/api/process")
async def process_pdf(file_content: bytes = Depends(validate_file)):
    """Process a PDF file to extract income statement and generate a story."""
    try:
        start_time = time.time()
        logger.info("Starting financial document analysis")
        
        # Extract income statement
        logger.info("Extracting income statement")
        income_statement = extract_income_statement(file_content)
        
        # Generate story based on income statement
        logger.info("Generating financial story")
        story = generate_story_from_json(income_statement)
        
        elapsed = time.time() - start_time
        logger.info(f"Analysis completed in {elapsed:.2f} seconds")
        
        # Check if we have valid data
        if "error" in income_statement and len(income_statement) <= 2:
            logger.warning("Error in income statement extraction")
            raise HTTPException(
                status_code=422, 
                detail="Could not extract financial data from the provided document"
            )
        
        return {
            "income_statement": income_statement,
            "story": story,
            "processing_time": f"{elapsed:.2f} seconds"
        }
        
    except Exception as e:
        logger.error(f"Error processing PDF: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing document: {str(e)}")

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    # Check if ollama service is available
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=2)
        models_available = response.status_code == 200
    except:
        models_available = False
    
    return {
        "status": "ok",
        "timestamp": time.time(),
        "models_available": models_available
    }

# Documentation route
@app.get("/")
async def root():
    """API documentation entry point."""
    return {
        "message": "Financial Document Analyzer API",
        "docs": "/docs",
        "health": "/health"
    }

if __name__ == "__main__":
    import uvicorn
    logger.info(f"Starting server on port {PORT}")
    uvicorn.run(app, host="0.0.0.0", port=PORT)