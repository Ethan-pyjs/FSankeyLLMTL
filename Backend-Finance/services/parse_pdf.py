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

def detect_scale_notation(text):
    """
    Detect if the document specifies financial values in millions, billions, or thousands.
    Returns a multiplication factor to use when converting values.
    """
    # Look for scale indicators commonly used in financial statements
    million_patterns = [
        r'\(in millions\)', r'\(in millions of', r'\(millions\)',
        r'expressed in millions', r'amounts in millions',
        r'in millions of dollars', r'presented in millions'
    ]
    
    billion_patterns = [
        r'\(in billions\)', r'\(in billions of', r'\(billions\)',
        r'expressed in billions', r'amounts in billions',
        r'in billions of dollars', r'presented in billions'
    ]
    
    thousand_patterns = [
        r'\(in thousands\)', r'\(in thousands of', r'\(thousands\)',
        r'expressed in thousands', r'amounts in thousands',
        r'in thousands of dollars', r'presented in thousands'
    ]
    
    # Check for millions notation first (most common)
    for pattern in million_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            print("Detected 'in millions' notation")
            return 1000000  # Multiply by 1 million
    
    # Check for billions notation
    for pattern in billion_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            print("Detected 'in billions' notation")
            return 1000000000  # Multiply by 1 billion
    
    # Check for thousands notation
    for pattern in thousand_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            print("Detected 'in thousands' notation")
            return 1000  # Multiply by 1 thousand
    
    # Default assumption if no scale notation is found
    print("No scale notation detected, assuming raw values")
    return 1  # Don't multiply

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
        "ended", "financial", "cash flow", "balance sheet", "net income", "operating income",
        "cost of goods sold", "cogs", "operating expenses", "oe",
        "net profit", "gross profit", "earnings before interest and taxes",
        "ebit", "earnings before interest taxes depreciation and amortization",
        "ebitda", "earnings per share", "eps", "dividend", "shareholder",
        "equity", "debt", "interest", "taxes", "net margin", "operating margin",
        "return on equity", "roe", "return on assets", "roa", "return on investment",
        "roi", "working capital", "current assets", "current liabilities",
        "accounts receivable", "accounts payable", "inventory", "fixed assets",
        "net cash flow", "operating cash flow", "investing cash flow",
    ]
    
    for term in financial_terms:
        # Make the term more visible by adding spaces around it
        text = re.sub(r'(\b' + term + r'\b)', r' \1 ', text, flags=re.IGNORECASE)
    
    return text

def format_financial_value(value_str, scale_factor=1):
    """
    Convert a string financial value to a numeric format.
    """
    if not value_str or value_str == "Unknown":
        return "Unknown"
        
    try:
        # If already a number, return it directly without scaling
        if isinstance(value_str, (int, float)):
            return value_str  # Don't apply scale factor to already processed numbers
            
        # Handle parentheses notation for negative numbers: (123.45) → -123.45
        original_str = str(value_str).lower()
        if '(' in original_str and ')' in original_str:
            value_str = '-' + re.sub(r'[()]', '', value_str)
        
        # Remove any non-numeric characters except decimal points and negative signs
        clean_val = re.sub(r'[^\d.-]', '', value_str)
        
        if not clean_val:
            return "Unknown"
            
        value = float(clean_val)
        
        # Check for inline scale indicators FIRST
        if "billion" in original_str or "b" in original_str.split():
            value *= 1000000000
        elif "million" in original_str or "m" in original_str.split():
            value *= 1000000
        elif "thousand" in original_str or "k" in original_str.split():
            value *= 1000
        else:
            # Only apply document-level scale factor if no inline indicator was found
            value *= scale_factor
            
        # Convert to integer if it's a whole number
        if value == int(value):
            return int(value)
        return round(value, 2)
    except:
        return "Unknown"

def extract_income_statement(pdf_bytes):
    try:
        # Extract text from PDF
        raw_text = extract_text_from_pdf(pdf_bytes)
        
        # Detect scale notation (in millions, in billions, etc.)
        scale_factor = detect_scale_notation(raw_text)
        print(f"Detected scale factor: {scale_factor}")
        
        # Clean and prepare text for extraction
        processed_text = clean_text_for_extraction(raw_text)
        
        # First attempt: Direct structured extraction with specific formatting requirements
        prompt = f"""
        Extract ONLY the income statement data from this financial document text.
        
        FORMAT INSTRUCTIONS (CRITICAL):
        1. Your response must ONLY contain a valid JSON object WITHOUT any markdown formatting
        2. Each key must be in quotes, each value must be a NUMBER (without any currency symbols) or "Unknown" in quotes
        3. DO NOT add any explanations, notes, or text outside the JSON object
        4. IMPORTANT: Look for scale notations in the document like '(in millions)' or '(in thousands)'
        5. If you see '(in millions)', multiply the returned values by 1,000,000 (e.g., 10.5 becomes 10,500,000)
        6. If you see '(in billions)', multiply the returned values by 1,000,000,000 (e.g., 10.5 becomes 10,500,000,000)
        7. If you see '(in thousands)', multiply the returned values by 1,000 (e.g., 10.5 becomes 10,500)
        8. If a value is negative, represent it as a negative number like -10.5, not with parentheses
        9. If a value is not found, use "Unknown" in quotes
        10. Ensure all keys are in snake_case (e.g., "net_income", "operating_expenses")
        
        KEYS TO EXTRACT:
        - "Revenue": The company's total income from sales
        - "Cost_of_Revenue": Direct costs attributable to the production of goods/services
        - "Gross_Profit": Revenue minus Cost of Revenue
        - "Operating_Expenses": Expenses related to normal business operations
        - "Operating_Income": Gross Profit minus Operating Expenses
        - "Net_Income": Final profit after all expenses, taxes, interest
        - Any other relevant financial metrics you can identify
        
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
            json_match = re.search(r'(\{[^{]*?"[^"]*?".*?\})', response, re.DOTALL)
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
            Revenue: [numeric value without $ signs or commas]
            Cost of Revenue: [numeric value without $ signs or commas]
            Gross Profit: [numeric value without $ signs or commas]
            Operating Expenses: [numeric value without $ signs or commas]
            Operating Income: [numeric value without $ signs or commas]
            Net Income: [numeric value without $ signs or commas]
            
            IMPORTANT: Return the values as shown in the document. Do NOT multiply by millions or billions.
            Also indicate if you see any notation like "(in millions)" or "(in billions)" in the document.
            
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
                    if key != 'Scale_Notation':  # Skip any scale notation line
                        json_data[key] = value.strip()
        
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
                        json_data[key] = value_str
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
        
        # Ensure all keys use consistent formatting (snake_case) and apply scale factor to values
        formatted_data = {}
        for key, value in json_data.items():
            formatted_key = key.replace(' ', '_')
            formatted_data[formatted_key] = format_financial_value(value, scale_factor)
            
        # Process the data for visualization
        visualization_data = process_financial_data_for_visualization(formatted_data)
        
        # Add visualization data to the response
        formatted_data["visualization_data"] = visualization_data
        
        # Before returning the formatted data, log the values
        for key, value in formatted_data.items():
            if key != "visualization_data":
                print(f"Final {key}: {value}")
                
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
            "Net_Income": "Unknown",
            "visualization_data": None
        }

def process_financial_data_for_visualization(income_statement_data: dict) -> dict:
    """
    Process income statement data into a structured format for visualization.
    Returns a dictionary containing different views of the data.
    """
    try:
        # Convert all values to numeric, handling "Unknown" values
        numeric_data = {}
        for key, value in income_statement_data.items():
            if value != "Unknown" and not isinstance(value, str):
                numeric_data[key] = float(value)
            else:
                numeric_data[key] = 0

        # Create time series format (even though we have one period)
        time_series = {
            "categories": list(numeric_data.keys()),
            "values": list(numeric_data.values()),
            "percentages": {
                "gross_margin": (numeric_data.get("Gross_Profit", 0) / numeric_data.get("Revenue", 1)) * 100 if numeric_data.get("Revenue", 0) != 0 else 0,
                "operating_margin": (numeric_data.get("Operating_Income", 0) / numeric_data.get("Revenue", 1)) * 100 if numeric_data.get("Revenue", 0) != 0 else 0,
                "net_margin": (numeric_data.get("Net_Income", 0) / numeric_data.get("Revenue", 1)) * 100 if numeric_data.get("Revenue", 0) != 0 else 0
            }
        }

        # Create waterfall data for showing how we get from revenue to net income
        waterfall_data = [
            {"name": "Revenue", "value": numeric_data.get("Revenue", 0)},
            {"name": "Cost of Revenue", "value": -numeric_data.get("Cost_of_Revenue", 0)},
            {"name": "Gross Profit", "value": numeric_data.get("Gross_Profit", 0)},
            {"name": "Operating Expenses", "value": -numeric_data.get("Operating_Expenses", 0)},
            {"name": "Operating Income", "value": numeric_data.get("Operating_Income", 0)},
            {"name": "Net Income", "value": numeric_data.get("Net_Income", 0)}
        ]

        return {
            "raw_data": numeric_data,
            "time_series": time_series,
            "waterfall": waterfall_data,
            "metrics": {
                "total_revenue": numeric_data.get("Revenue", 0),
                "total_costs": numeric_data.get("Cost_of_Revenue", 0) + numeric_data.get("Operating_Expenses", 0),
                "final_profit": numeric_data.get("Net_Income", 0),
                "margins": time_series["percentages"]
            }
        }
    except Exception as e:
        print(f"Error processing financial data for visualization: {str(e)}")
        return {
            "raw_data": income_statement_data,
            "error": f"Failed to process data for visualization: {str(e)}"
        }