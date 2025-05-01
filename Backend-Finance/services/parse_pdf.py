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
    """Enhanced scale detection that looks for more variations of scale indicators."""
    text = text.lower()
    
    # Expanded patterns for better detection
    million_patterns = [
        r'\(in millions\)', r'\(millions\)', r'\(in mm\)', r'presented in millions',
        r'amounts in millions', r'\$.*mm', r'\(mm\)', r'figures? in millions',
        r'expressed in millions', r'reported in millions'
    ]
    
    billion_patterns = [
        r'\(in billions\)', r'\(billions\)', r'\(in bb\)', r'presented in billions',
        r'amounts in billions', r'\$.*bb', r'\(bb\)', r'figures? in billions',
        r'expressed in billions', r'reported in billions'
    ]
    
    thousand_patterns = [
        r'\(in thousands\)', r'\(thousands\)', r'\(in k\)', r'presented in thousands',
        r'amounts in thousands', r'\$.*k', r'\(k\)', r'figures? in thousands',
        r'expressed in thousands', r'reported in thousands'
    ]
    
    print("Checking for scale notation in text...")
    
    # Check for billions first (to avoid misinterpreting "millions" in a document using billions)
    for pattern in billion_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            print("Detected billions notation")
            return 1000000000
    
    # Then check millions
    for pattern in million_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            print("Detected millions notation")
            return 1000000
    
    # Finally check thousands
    for pattern in thousand_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            print("Detected thousands notation")
            return 1000
    
    # Additional check for common headers with scales
    header_check = text[:1000]  # Check first 1000 characters for headers
    if re.search(r'(million|mm).*\$|^\$.*mm', header_check, re.IGNORECASE):
        print("Detected millions notation from header")
        return 1000000
    elif re.search(r'(billion|bb).*\$|^\$.*bb', header_check, re.IGNORECASE):
        print("Detected billions notation from header")
        return 1000000000
    
    print("No scale notation detected, checking for value patterns...")
    # If no explicit notation, try to infer from the values themselves
    numbers = re.findall(r'\$?[\d,]+\.?\d*\s*[mbk]?', text.lower())
    if numbers:
        has_m = any('m' in n.lower() for n in numbers)
        has_b = any('b' in n.lower() for n in numbers)
        has_k = any('k' in n.lower() for n in numbers)
        if has_b:
            print("Inferred billions from values")
            return 1000000000
        elif has_m:
            print("Inferred millions from values")
            return 1000000
        elif has_k:
            print("Inferred thousands from values")
            return 1000
    
    print("Using default scale (raw values)")
    return 1

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
    """Enhanced financial value formatting with better scale detection."""
    if not value_str or value_str == "Unknown":
        return "Unknown"
    
    try:
        # If already a number, apply scale factor directly
        if isinstance(value_str, (int, float)):
            return value_str * scale_factor
        
        # Convert string to lowercase for easier pattern matching
        original_str = str(value_str).lower().strip()
        
        # Handle parentheses notation for negative numbers
        is_negative = '(' in original_str and ')' in original_str
        clean_str = re.sub(r'[(),]', '', original_str)
        
        # Extract the numeric part and any scale indicators
        match = re.search(r'([\d.]+)\s*([mbk])?', clean_str)
        if not match:
            return "Unknown"
        
        value = float(match.group(1))
        scale_indicator = match.group(2) if match.group(2) else ''
        
        # Apply scale based on indicator in the value itself
        if scale_indicator == 'b':
            value *= 1000000000
        elif scale_indicator == 'm':
            value *= 1000000
        elif scale_indicator == 'k':
            value *= 1000
        else:
            # If no scale indicator in the value, apply the document-level scale factor
            value *= scale_factor
        
        # Apply negative if indicated by parentheses
        if is_negative:
            value = -value
        
        # Return as integer if whole number, otherwise round to 2 decimal places
        return int(value) if value.is_integer() else round(value, 2)
        
    except Exception as e:
        print(f"Error formatting value '{value_str}': {str(e)}")
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
        
        # Before returning formatted_data, log the values
        print("\nFinal processed values:")
        for key, value in formatted_data.items():
            if key != "visualization_data":
                print(f"{key}: {value:,}")
                
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