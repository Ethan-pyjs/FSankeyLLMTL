# Route(s) for handling file upload & processing
from fastapi import APIRouter, UploadFile, File
from services.parse_pdf import extract_income_statement
from services.generate_story import generate_story_from_json


router = APIRouter()


@router.post("/process")
async def process_file(file: UploadFile = File(...)):
    text = await file.read()
    # Extract structured data
    json_data = extract_income_statement(text)
    # Generate story
    story = generate_story_from_json(json_data)
    return {"income_statement": json_data, "story": story}