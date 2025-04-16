# app.py or main.py
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from services.parse_pdf import extract_income_statement
from services.generate_story import generate_story_from_json
import io

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # Add your frontend URL
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)