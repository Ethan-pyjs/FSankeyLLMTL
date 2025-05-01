from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, Response
from fastapi.middleware.cors import CORSMiddleware
from services.parse_pdf import extract_income_statement
from services.generate_story import generate_story_from_json
from sse_starlette.sse import EventSourceResponse
import os
import logging
from typing import Dict, Any
import time
import asyncio
import uuid
from concurrent.futures import ThreadPoolExecutor

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

# Add a simple in-memory storage for task results
task_results: Dict[str, Any] = {}

executor = ThreadPoolExecutor()

@app.get("/api/progress/{task_id}")
async def progress(task_id: str):
    """Stream progress updates for a file processing task."""
    async def event_generator():
        while True:
            if task_id not in task_results:
                yield {
                    "data": {
                        "error": "Task not found"
                    }
                }
                break
                
            result = task_results[task_id]
            yield {
                "data": {
                    "progress": result.get("progress", 0),
                    "message": result.get("message", "Processing..."),
                    "status": result.get("status", "processing")
                }
            }
            
            if result.get("status") in ["completed", "error"]:
                break
                
            await asyncio.sleep(1)
    
    return EventSourceResponse(event_generator())

@app.post("/api/process")
async def process_pdf(file_content: bytes = Depends(validate_file)):
    """Process a PDF file to extract income statement and generate a story."""
    try:
        task_id = str(uuid.uuid4())
        # Initialize task in results
        task_results[task_id] = {
            "status": "processing",
            "progress": 0,
            "message": "Starting process..."
        }
        
        # Start background task
        asyncio.create_task(process_file_background(task_id, file_content))
        
        return {"task_id": task_id}
        
    except Exception as e:
        logger.error(f"Error processing PDF: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing document: {str(e)}")

async def process_file_background(task_id: str, file_content: bytes):
    """Process file in background and update progress."""
    try:
        start_time = time.time()
        
        # Update progress for text extraction
        task_results[task_id].update({
            "progress": 30,
            "message": "Extracting text from PDF"
        })
        # Extract structured data
        json_data = await asyncio.get_event_loop().run_in_executor(
            executor, extract_income_statement, file_content
        )
        
        # Update progress for story generation
        task_results[task_id].update({
            "progress": 70,
            "message": "Generating financial story"
        })
        # Generate story
        story = await asyncio.get_event_loop().run_in_executor(
            executor, generate_story_from_json, json_data
        )
        
        processing_time = f"{time.time() - start_time:.2f} seconds"
        
        # Store final results
        task_results[task_id] = {
            "status": "completed",
            "income_statement": json_data,
            "story": story,
            "processing_time": processing_time,
            "progress": 100,
            "message": "Analysis complete"
        }
        
    except Exception as e:
        logger.error(f"Background task error: {str(e)}")
        task_results[task_id] = {
            "status": "error",
            "error": str(e),
            "progress": 0,
            "message": f"Error: {str(e)}"
        }

@app.get("/api/result/{task_id}")
async def get_result(task_id: str):
    """Get the results for a specific task ID."""
    if task_id not in task_results:
        raise HTTPException(status_code=404, detail="Task not found")
    
    result = task_results[task_id]
    # Optionally remove the result from storage after retrieving
    del task_results[task_id]
    return result

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    # Check if ollama service is available and if the Granite models are loaded
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=2)
        models_data = response.json() if response.status_code == 200 else {}
        
        # Check if Granite models are available
        available_models = [model["name"] for model in models_data.get("models", [])]
        granite_vision_available = any("granite3.2-vision" in model.lower() for model in available_models)
        granite_8b_available = any("granite3.3:8b" in model.lower() for model in available_models)
        
        if not (granite_vision_available and granite_8b_available) and response.status_code == 200:
            missing_models = []
            if not granite_vision_available:
                missing_models.append("granite3.2-vision")
            if not granite_8b_available:
                missing_models.append("granite3.3:8B")
                
            return {
                "status": "warning",
                "timestamp": time.time(),
                "models_available": True,
                "granite_models_available": False,
                "message": f"Ollama is running but some Granite models are not installed. Run 'ollama pull {' and '.join(missing_models)}'"
            }
        
        return {
            "status": "ok",
            "timestamp": time.time(),
            "models_available": response.status_code == 200,
            "granite_vision_available": granite_vision_available,
            "granite_8b_available": granite_8b_available,
            "available_models": available_models
        }
    except Exception as e:
        return {
            "status": "error",
            "timestamp": time.time(),
            "models_available": False,
            "granite_models_available": False,
            "message": f"Could not connect to Ollama service: {str(e)}"
        }
    
# Documentation route
@app.get("/")
async def root():
    """API documentation entry point."""
    return {
        "message": "Financial Document Analyzer API (using Granite models)",
        "docs": "/docs",
        "health": "/health"
    }
    
if __name__ == "__main__":
    import uvicorn
    logger.info(f"Starting server on port {PORT}")
    uvicorn.run(app, host="0.0.0.0", port=PORT)