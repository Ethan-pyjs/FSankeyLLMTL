import fitz

def extract_text_from_pdf(pdf_bytes):
    """Extract text from PDF bytes with improved formatting for financial statements."""
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text("text") + "\n\n"
    return text

def clean_text_for_extraction(text):
    """Prepare text for better pattern matching and LLM extraction."""
    import re
    
    text = re.sub(r'\s+', ' ', text)
    financial_terms = [
        "revenue", "total revenue", "sales", "net sales",
        "cost of revenue", "cost of goods sold", "cogs",
        "gross profit", "gross margin",
        "operating expenses", "total operating expenses", "opex",
        "operating income", "operating profit", "ebit",
        "net income", "net profit", "net earnings",
        "research and development", "r&d",
        "selling, general and administrative", "sg&a"
    ]
    
    for term in financial_terms:
        text = re.sub(r'(\b' + term + r'\b)', r' \1 ', text, flags=re.IGNORECASE)
    
    return text