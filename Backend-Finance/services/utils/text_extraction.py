"""
Utility functions for extracting and processing text from PDFs.
"""
import re
import fitz  # PyMuPDF

def extract_text_from_pdf(pdf_bytes):
    """
    Extract text from PDF bytes with improved formatting for financial statements.
    
    Args:
        pdf_bytes: Raw PDF file bytes
        
    Returns:
        str: Extracted text from the PDF
    """
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    text = ""
    for page in doc:
        # Extract text with preservation of layout for better table detection
        text += page.get_text("text") + "\n\n"
    return text

def clean_text_for_extraction(text):
    """
    Prepare text for better pattern matching and LLM extraction.
    
    Args:
        text: Raw text extracted from PDF
        
    Returns:
        str: Cleaned and processed text optimized for extraction
    """
    # Remove excess whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Make common financial terms more visible
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
        # Make the term more visible by adding spaces around it
        text = re.sub(r'(\b' + term + r'\b)', r' \1 ', text, flags=re.IGNORECASE)
    
    return text