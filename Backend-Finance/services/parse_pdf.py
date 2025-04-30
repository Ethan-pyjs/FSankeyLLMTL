import json
import fitz  # PyMuPDF
import re
from services.model_runner import query_model

def extract_text_from_pdf(pdf_bytes):
    """Extract text from PDF bytes with improved formatting for financial statements."""
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    text = ""
    for page in doc:
        # Extract text with preservation of layout for better table detection
        text += page.get_text("text") + "\n\n"
    return text

def clean_text_for_extraction(text):
    """Preprocess text to better identify financial data with improved financial marker detection."""
    # Remove multiple spaces and normalize newlines
    text = re.sub(r'\s+', ' ', text)
    
    # Look for common financial terms and highlight them
    financial_terms = [
        "revenue", "income", "expense", "profit", "loss", "cost", 
        "total", "net", "gross", "operating", "assets", "liabilities",
        "million", "billion", "thousand", "$", "USD", "dollars",
        # Additional terms to improve recognition
        "consolidated", "statement", "fiscal year", "quarter", 
        "ended", "financial", "cash flow", "balance sheet"
    ]
    
    for term in financial_terms:
        # Make the term more visible by adding spaces around it
        text = re.sub(r'(\b' + term + r'\b)', r' \1 ', text, flags=re.IGNORECASE)
    
    return text

def format_financial_value(value_str):
    """
    Convert a string financial value to a numeric format in millions.
    Enhanced to handle more financial notation patterns.
    """
    if not value_str or value_str == "Unknown":
        return "Unknown"
        
    try:
        # Check if string already represents a number (float or int)
        try:
            if isinstance(value_str, (int, float)):
                return value_str
        except:
            pass
            
        # Detect common financial notation patterns
        original_str = value_str.lower()
        
        # Handle parentheses notation for negative numbers: (123.45) → -123.45
        if '(' in original_str and ')' in original_str:
            value_str = '-' + re.sub(r'[()]', '', value_str)
        
        # Remove any non-numeric characters except decimal points and negative signs
        clean_val = re.sub(r'[^\d.-]', '', value_str)
        
        if not clean_val:
            return "Unknown"
            
        value = float(clean_val)
        
        # Check if there are indicators of scale
        if "billion" in original_str or "b" in original_str.split():
            value *= 1000  # Convert to millions
        elif "thousand" in original_str or "k" in original_str.split():
            value /= 1000  # Convert to millions
            
        # Round to 2 decimal places for cleaner values
        return round(value, 2)
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
        2. Each key must be in quotes, each value must be a number (without any currency symbols) or "Unknown" in quotes
        3. DO NOT add any explanations, notes, or text outside the JSON object
        5. All values should be presented in millions of dollars (e.g., $1,000,000 = 1), if not then apply the conversion.
        6. If a value is negative, represent it as a negative number like -10.5, not with parentheses
        
        KEYS TO EXTRACT:
        - "Revenue": The company's total income from sales
        - "Cost_of_Revenue": Direct costs attributable to the production of goods/services
        - "Gross_Profit": Revenue minus Cost of Revenue
        - "Operating_Expenses": Expenses related to normal business operations
        - "Operating_Income": Gross Profit minus Operating Expenses
        - "Net_Income": Final profit after all expenses, taxes, interest
        - ANy other relevant financial metrics you can identify
        
        FINANCIAL DOCUMENT TEXT:
        \"\"\"
        {processed_text[:4000]}
        \"\"\"
        
        IMPORTANT: Return ONLY the JSON object, no markdown formatting, no explanations.
        """
        
        response = query_model(prompt, model="granite3.2-vision")
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
            # Fallback to key-value extraction with more specific formatting guidance
            fallback_prompt = f"""
            Extract these key financial values from the document:
            1. Revenue
            2. Cost of Revenue
            3. Gross Profit
            4. Operating Expenses
            5. Operating Income
            6. Net Income
            
            Format your response exactly as:
            Revenue: [numeric value in millions, without $ signs or commas]
            Cost of Revenue: [numeric value in millions, without $ signs or commas]
            Gross Profit: [numeric value in millions, without $ signs or commas]
            Operating Expenses: [numeric value in millions, without $ signs or commas]
            Operating Income: [numeric value in millions, without $ signs or commas]
            Net Income: [numeric value in millions, without $ signs or commas]
            
            If any value can't be found, use "Unknown". Do not include any additional text or explanations.
            
            Text:
            {processed_text[:4000]}
            """
            
            fallback_response = query_model(fallback_prompt, model="granite3.2-vision")
            
            # Parse the key-value pairs
            json_data = {}
            for line in fallback_response.strip().split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip().replace(' ', '_')
                    json_data[key] = format_financial_value(value.strip())
        
        # Fourth attempt: Try a more targeted search for specific financial items
        if not json_data or len(json_data) < 3:
            print("Using specific financial pattern recognition as last resort")
            
            patterns = {
                'Revenue': [r'(?:Total\s+)?Revenue[s]?[:\s]+[\$]?([\d,]+(?:\.\d+)?(?:\s*(?:million|billion|thousand|[mMbBkK]))?)', 
                           r'(?:Total\s+)?Sales[:\s]+[\$]?([\d,]+(?:\.\d+)?(?:\s*(?:million|billion|thousand|[mMbBkK]))?)'],
                'Cost_of_Revenue': [r'Cost\s+of\s+(?:Revenue|Sales)[:\s]+[\$]?([\d,]+(?:\.\d+)?(?:\s*(?:million|billion|thousand|[mMbBkK]))?)',
                                   r'COGS[:\s]+[\$]?([\d,]+(?:\.\d+)?(?:\s*(?:million|billion|thousand|[mMbBkK]))?)'],
                'Gross_Profit': [r'Gross\s+Profit[:\s]+[\$]?([\d,]+(?:\.\d+)?(?:\s*(?:million|billion|thousand|[mMbBkK]))?)'],
                'Operating_Expenses': [r'(?:Total\s+)?Operating\s+Expenses[:\s]+[\$]?([\d,]+(?:\.\d+)?(?:\s*(?:million|billion|thousand|[mMbBkK]))?)'],
                'Operating_Income': [r'Operating\s+(?:Income|Profit)[:\s]+[\$]?([\d,]+(?:\.\d+)?(?:\s*(?:million|billion|thousand|[mMbBkK]))?)'],
                'Net_Income': [r'Net\s+(?:Income|Profit|Earnings)[:\s]+[\$]?([\d,]+(?:\.\d+)?(?:\s*(?:million|billion|thousand|[mMbBkK]))?)',
                              r'(?:Net\s+)?Profit\s+[:\s]+[\$]?([\d,]+(?:\.\d+)?(?:\s*(?:million|billion|thousand|[mMbBkK]))?)']
            }
            
            json_data = {}
            for key, pattern_list in patterns.items():
                for pattern in pattern_list:
                    matches = re.findall(pattern, processed_text, re.IGNORECASE)
                    if matches:
                        # Take the first match
                        value_str = matches[0]
                        json_data[key] = format_financial_value(value_str)
                        break
                
                # If no match found, set to Unknown
                if key not in json_data:
                    json_data[key] = "Unknown"
        
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
            
            # Handle values that might have come through with currency symbols or commas
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