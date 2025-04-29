from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from services.parse_pdf import extract_income_statement
from services.generate_story import generate_story_from_json
import os

app = FastAPI()

# Get environment variables
PORT = int(os.environ.get("PORT", 8000))
FRONTEND_URL = os.environ.get("FRONTEND_URL", "http://localhost:5173")

# Enable CORS - update with your deployed frontend URL
app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL, "http://localhost:3000"],  # Add your frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/process")
async def process_pdf(file: UploadFile = File(...)):
    # Read the file content
    pdf_bytes = await file.read()
    
    # Extract income statement
    income_statement = extract_income_statement(pdf_bytes)
    
    # Generate story based on income statement
    story = generate_story_from_json(income_statement)
    
    return {
        "income_statement": income_statement,
        "story": story
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=PORT)