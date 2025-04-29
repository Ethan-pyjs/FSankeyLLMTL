import json
import fitz  # PyMuPDF
import re
from services.model_runner import query_model

def extract_text_from_pdf(pdf_bytes):
    """Extract text from PDF bytes with improved formatting."""
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    text = ""
    for page in doc:
        # Extract text with preservation of layout for better table detection
        text += page.get_text("text") + "\n\n"
    return text

def clean_text_for_extraction(text):
    """Preprocess text to better identify financial data."""
    # Remove multiple spaces and normalize newlines
    text = re.sub(r'\s+', ' ', text)
    # Look for common financial terms and highlight them
    financial_terms = ["revenue", "income", "expense", "profit", "loss", "cost", 
                       "total", "net", "gross", "operating", "assets", "liabilities",
                       "million", "billion", "thousand", "$", "USD", "dollars"]
    
    for term in financial_terms:
        # Make the term more visible by adding spaces around it
        text = re.sub(r'(\b' + term + r'\b)', r' \1 ', text, flags=re.IGNORECASE)
    
    return text

def format_financial_value(value_str):
    """Convert a string financial value to a numeric format in millions."""
    if not value_str or value_str == "Unknown":
        return "Unknown"
        
    try:
        # Remove any non-numeric characters except decimal points and negative signs
        clean_val = re.sub(r'[^\d.-]', '', value_str)
        value = float(clean_val)
        
        # Check if there are indicators of scale
        if "billion" in value_str.lower() or "b" in value_str.lower():
            value *= 1000  # Convert to millions
        elif "thousand" in value_str.lower() or "k" in value_str.lower():
            value /= 1000  # Convert to millions
            
        return value  # Return as number instead of string for better JSON serialization
    except:
        return "Unknown"

def extract_income_statement(pdf_bytes):
    """Extract income statement data from PDF with improved robustness."""
    try:
        # Extract text from PDF
        raw_text = extract_text_from_pdf(pdf_bytes)
        
        # Clean and prepare text for extraction
        processed_text = clean_text_for_extraction(raw_text)
        
        # First attempt: Direct structured extraction with specific formatting requirements
        prompt = f"""
        Extract ONLY the income statement data from this financial document text.
        
        FORMAT INSTRUCTIONS (CRITICAL):
        1. Your response must ONLY contain a valid JSON object WITHOUT any markdown formatting
        2. Each key must be in quotes, each value must be a number or "Unknown" in quotes
        3. DO NOT add any explanations, notes, or text outside the JSON object
        4. DO NOT format numbers with commas or currency symbols in the JSON
        5. All values should be presented in millions of dollars (e.g., $1,000,000 = 1)
        
        KEYS TO EXTRACT:
        - "Revenue": The company's total income from sales
        - "Cost_of_Revenue": Direct costs attributable to the production of goods/services
        - "Gross_Profit": Revenue minus Cost of Revenue
        - "Operating_Expenses": Expenses related to normal business operations
        - "Operating_Income": Gross Profit minus Operating Expenses
        - "Net_Income": Final profit after all expenses, taxes, interest
        
        FINANCIAL DOCUMENT TEXT:
        \"\"\"
        {processed_text[:4000]}
        \"\"\"
        
        RESPONSE (ONLY VALID JSON):
        ```json
        {{"Revenue": 1000, "Cost_of_Revenue": 600, "Gross_Profit": 400, "Operating_Expenses": 200, "Operating_Income": 200, "Net_Income": 150}}
        ```
        
        IMPORTANT: Return ONLY the JSON object, no markdown formatting, no explanations.
        """
        
        response = query_model(prompt, model="llama3.3")
        print(f"Raw model response (first 200 chars): {response[:200]}...")
        
        # Try to extract valid JSON from the response
        json_data = None
        
        # First attempt: Look for JSON block
        json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response, re.DOTALL)
        if json_match:
            try:
                json_data = json.loads(json_match.group(1))
                print("Successfully extracted JSON from code block")
            except json.JSONDecodeError:
                print("Failed to parse JSON from code block")
        
        # Second attempt: Look for a standalone JSON object
        if not json_data:
            json_match = re.search(r'(\{[^{]*?"Revenue".*?\})', response, re.DOTALL)
            if json_match:
                try:
                    json_data = json.loads(json_match.group(1))
                    print("Successfully extracted standalone JSON")
                except json.JSONDecodeError:
                    print("Failed to parse standalone JSON")
        
        # Third attempt: If we still don't have valid JSON, try a simpler approach
        if not json_data:
            print("No valid JSON found, trying key-value extraction...")
            # Fallback to key-value extraction
            fallback_prompt = f"""
            Extract these key financial values from the document:
            1. Revenue
            2. Cost of Revenue
            3. Gross Profit
            4. Operating Expenses
            5. Operating Income
            6. Net Income
            
            Format your response as:
            Revenue: [value in millions]
            Cost of Revenue: [value in millions]
            Gross Profit: [value in millions]
            Operating Expenses: [value in millions]
            Operating Income: [value in millions]
            Net Income: [value in millions]
            
            If any value can't be found, use "Unknown".
            
            Text:
            {processed_text[:4000]}
            """
            
            fallback_response = query_model(fallback_prompt, model="llama3.3")
            
            # Parse the key-value pairs
            json_data = {}
            for line in fallback_response.strip().split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip().replace(' ', '_')
                    json_data[key] = format_financial_value(value.strip())
        
        # If we still don't have data, create a default structure
        if not json_data or len(json_data) < 3:  # Ensure we have at least 3 data points
            print("Extraction failed, using default structure")
            json_data = {
                "Revenue": "Unknown",
                "Cost_of_Revenue": "Unknown",
                "Gross_Profit": "Unknown", 
                "Operating_Expenses": "Unknown",
                "Operating_Income": "Unknown",
                "Net_Income": "Unknown"
            }
        
        # Ensure all keys use consistent formatting (snake_case)
        formatted_data = {}
        for key, value in json_data.items():
            # Convert key to snake_case
            formatted_key = key.replace(' ', '_').replace('-', '_')
            # Ensure value is properly formatted - keep as number if it's a number
            if value != "Unknown" and not isinstance(value, (int, float)):
                formatted_data[formatted_key] = format_financial_value(str(value))
            else:
                formatted_data[formatted_key] = value
            
        return formatted_data
            
    except Exception as e:
        print(f"Error in extract_income_statement: {str(e)}")
        return {
            "error": f"Error processing request: {str(e)}",
            "Revenue": "Unknown",
            "Cost_of_Revenue": "Unknown",
            "Gross_Profit": "Unknown",
            "Operating_Expenses": "Unknown",
            "Operating_Income": "Unknown",
            "Net_Income": "Unknown"
        }