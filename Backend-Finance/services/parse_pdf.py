# Logic to extract text/income statement
import json
from services.model_runner import query_model
import fitz  # PyMuPDF

def extract_text_from_pdf(pdf_bytes):
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    return "\n".join(page.get_text() for page in doc)

def extract_income_statement(pdf_bytes):
    text = extract_text_from_pdf(pdf_bytes)
    prompt = f"""
    From the following text of a financial 10-K, extract the income statement in JSON format.
    Focus on Revenue, Cost of Revenue, Gross Profit, Operating Expenses, Net Income, and anything clearly labeled.

    Text:
    \"\"\"{text}\"\"\"
    """
    response = query_model(prompt, model="mistral")
    try:
        # Clean up and extract the JSON part
        json_start = response.find("{")
        json_data = json.loads(response[json_start:])
        return json_data
    except Exception:
        return {"error": "Failed to parse JSON from model response."}
