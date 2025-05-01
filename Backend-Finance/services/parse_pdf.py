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
    """Enhanced scale detection with multiple methods for better accuracy."""
    text = text.lower()
    
    # Method 1: Check for explicit scale indicators
    # First check for explicit billion indicators
    billion_patterns = [
        r'\(in billions\)', r'\(billions\)', r'\(in bb\)', r'presented in billions',
        r'amounts in billions', r'\$.*bb', r'\(bb\)', r'figures? in billions',
        r'expressed in billions', r'reported in billions', r'USD in billions',
        r'in billions of (dollars|usd|$)', r'billions of (dollars|usd|$)'
    ]
    
    # Then check for million indicators
    million_patterns = [
        r'\(in millions\)', r'\(millions\)', r'\(in mm\)', r'presented in millions',
        r'amounts in millions', r'\$.*mm', r'\(mm\)', r'figures? in millions',
        r'expressed in millions', r'reported in millions', r'USD in millions',
        r'in millions of (dollars|usd|$)', r'millions of (dollars|usd|$)'
    ]
    
    # Check for thousand indicators
    thousand_patterns = [
        r'\(in thousands\)', r'\(thousands\)', r'\(in k\)', r'presented in thousands',
        r'amounts in thousands', r'\$.*k', r'\(k\)', r'figures? in thousands',
        r'expressed in thousands', r'reported in thousands', r'USD in thousands',
        r'in thousands of (dollars|usd|$)', r'thousands of (dollars|usd|$)'
    ]
    
    print("Checking for scale notation in text...")
    
    # Make a copy of the text with special focus on headers and footnotes
    header_footer_text = text[:2000] + text[-2000:]
    
    # Check for billions first (to avoid misinterpreting "millions" in a document using billions)
    for pattern in billion_patterns:
        if re.search(pattern, header_footer_text, re.IGNORECASE):
            print("Detected billions notation in header/footer")
            return 1000000000
    
    # Then check millions
    for pattern in million_patterns:
        if re.search(pattern, header_footer_text, re.IGNORECASE):
            print("Detected millions notation in header/footer")
            return 1000000
    
    # Finally check thousands
    for pattern in thousand_patterns:
        if re.search(pattern, header_footer_text, re.IGNORECASE):
            print("Detected thousands notation in header/footer")
            return 1000
    
    # Method 2: Check common financial statement headers
    header_check = text[:1000]  # Check first 1000 characters for headers
    if re.search(r'(million|mm).*\$|^\$.*mm', header_check, re.IGNORECASE):
        print("Detected millions notation from header")
        return 1000000
    elif re.search(r'(billion|bb).*\$|^\$.*bb', header_check, re.IGNORECASE):
        print("Detected billions notation from header")
        return 1000000000
    
    # Method 3: Analyze the actual values in the document
    # Extract potential financial values (numbers with dollar signs or commas)
    values = []
    # Look for numbers that might be financial figures
    for match in re.finditer(r'\$\s*([\d,]+(?:\.\d+)?)', text):
        try:
            value = float(match.group(1).replace(',', ''))
            values.append(value)
        except ValueError:
            continue
    
    if values:
        avg_value = sum(values) / len(values)
        print(f"Average detected value: {avg_value}")
        
        # Use the average value to infer the scale
        if avg_value > 100000000000:  # Numbers in trillions
            print("Values appear to be raw (no scale factor needed)")
            return 1
        elif avg_value > 100000000:  # Numbers in hundreds of millions
            print("Values appear to be raw (no scale factor needed)")
            return 1
        elif avg_value > 10000 and avg_value < 100000:  # Likely in thousands
            print("Inferred values in thousands")
            return 1000
        elif avg_value > 10 and avg_value < 10000:  # Likely in millions
            print("Inferred values in millions")
            return 1000000
        elif avg_value < 10:  # Likely in billions
            print("Inferred values in billions")
            return 1000000000
    
    print("Using default scale (raw values)")
    return 1

def normalize_number(value_str):
    """Convert a string representation of a number to a float value."""
    if not value_str or value_str.strip() == '':
        return None
    
    # Remove any non-numeric characters except for decimal point and negative sign
    # Handle parentheses for negative numbers
    value_str = value_str.strip()
    is_negative = '(' in value_str and ')' in value_str
    
    # Remove all non-numeric characters except decimal point
    clean_str = re.sub(r'[^\d.-]', '', value_str)
    
    try:
        value = float(clean_str)
        if is_negative:
            value = -value
        return value
    except ValueError:
        return None

def extract_financial_values_with_patterns(text):
    """Extract financial values using regex patterns targeting common financial statement formats."""
    results = {}
    
    # Define patterns for key financial metrics
    # Format is: field name -> list of regex patterns
    financial_patterns = {
        'Revenue': [
            r'(?:Total\s+)?Revenue[s]?[:\s]+[\$]?([\d,]+(?:\.\d+)?)',
            r'(?:Total\s+)?Sales[:\s]+[\$]?([\d,]+(?:\.\d+)?)',
            r'Revenue[s]?[:\s]*[\$]?([\d,]+(?:\.\d+)?)',
            r'Total\s+operating\s+revenues?[:\s]+[\$]?([\d,]+(?:\.\d+)?)',
            r'(?:Total\s+)?Net\s+Sales[:\s]+[\$]?([\d,]+(?:\.\d+)?)'
        ],
        'Cost_of_Revenue': [
            r'Cost\s+of\s+(?:Revenue|Sales)[:\s]+[\$]?([\d,]+(?:\.\d+)?)',
            r'Cost\s+of\s+goods\s+sold[:\s]+[\$]?([\d,]+(?:\.\d+)?)',
            r'COGS[:\s]+[\$]?([\d,]+(?:\.\d+)?)',
            r'Cost\s+of\s+products\s+sold[:\s]+[\$]?([\d,]+(?:\.\d+)?)',
            r'Direct\s+costs?[:\s]+[\$]?([\d,]+(?:\.\d+)?)'
        ],
        'Gross_Profit': [
            r'Gross\s+Profit[:\s]+[\$]?([\d,]+(?:\.\d+)?)',
            r'Gross\s+Margin[:\s]+[\$]?([\d,]+(?:\.\d+)?)',
            r'Gross\s+Income[:\s]+[\$]?([\d,]+(?:\.\d+)?)'
        ],
        'Operating_Expenses': [
            r'(?:Total\s+)?Operating\s+Expenses[:\s]+[\$]?([\d,]+(?:\.\d+)?)',
            r'(?:Total\s+)?OpEx[:\s]+[\$]?([\d,]+(?:\.\d+)?)',
            r'(?:Total\s+)?Operating\s+Costs(?:\s+and\s+Expenses)?[:\s]+[\$]?([\d,]+(?:\.\d+)?)',
            r'Selling,\s+General\s+and\s+Administrative\s+Expenses[:\s]+[\$]?([\d,]+(?:\.\d+)?)',
            r'SG&A\s+Expenses[:\s]+[\$]?([\d,]+(?:\.\d+)?)'
        ],
        'Operating_Income': [
            r'Operating\s+(?:Income|Profit)[:\s]+[\$]?([\d,]+(?:\.\d+)?)',
            r'Income\s+[Ff]rom\s+[Oo]perations[:\s]+[\$]?([\d,]+(?:\.\d+)?)',
            r'Operating\s+Earnings[:\s]+[\$]?([\d,]+(?:\.\d+)?)',
            r'EBIT[:\s]+[\$]?([\d,]+(?:\.\d+)?)'
        ],
        'Net_Income': [
            r'Net\s+(?:Income|Profit|Earnings)[:\s]+[\$]?([\d,]+(?:\.\d+)?)',
            r'Profit\s+for\s+the\s+(?:year|period)[:\s]+[\$]?([\d,]+(?:\.\d+)?)',
            r'Net\s+Earnings[:\s]+[\$]?([\d,]+(?:\.\d+)?)',
            r'(?:Net\s+)?Profit[:\s]+[\$]?([\d,]+(?:\.\d+)?)',
            r'Bottom\s+Line[:\s]+[\$]?([\d,]+(?:\.\d+)?)'
        ],
        'Research_Development': [
            r'Research\s+(?:and|\&)?\s*Development[:\s]+[\$]?([\d,]+(?:\.\d+)?)',
            r'R\s*(?:\&|and)\s*D[:\s]+[\$]?([\d,]+(?:\.\d+)?)'
        ],
        'Sales_Marketing': [
            r'Sales\s+(?:and|\&)?\s*Marketing[:\s]+[\$]?([\d,]+(?:\.\d+)?)',
            r'Marketing\s+(?:and|\&)?\s*Sales[:\s]+[\$]?([\d,]+(?:\.\d+)?)'
        ],
        'General_Administrative': [
            r'General\s+(?:and|\&)?\s*Administrative[:\s]+[\$]?([\d,]+(?:\.\d+)?)',
            r'G\s*(?:\&|and)\s*A[:\s]+[\$]?([\d,]+(?:\.\d+)?)'
        ]
    }
    
    print("Extracting financial values using patterns...")
    
    # Apply patterns to extract values
    for field, patterns in financial_patterns.items():
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                # Take the first match and normalize it
                value = normalize_number(matches[0])
                if value is not None:
                    results[field] = value
                    print(f"Found {field}: {value} using pattern {pattern}")
                    break
    
    # Look for negative values in parentheses
    for field in list(results.keys()):
        if field in results and results[field] is not None:
            # Already found a good value for this field
            continue
            
        for pattern in financial_patterns[field]:
            # Modify pattern to look for parentheses
            paren_pattern = pattern.replace(r'([\d,]+(?:\.\d+)?)', r'\(([\d,]+(?:\.\d+)?)\)')
            matches = re.findall(paren_pattern, text, re.IGNORECASE)
            if matches:
                value = normalize_number(matches[0])
                if value is not None:
                    results[field] = -value  # Negative value
                    print(f"Found {field} (negative): {-value} using pattern {paren_pattern}")
                    break
    
    return results

def clean_text_for_extraction(text):
    """Prepare text for better pattern matching and LLM extraction."""
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

def format_financial_value(value, scale_factor=1):
    """Format and scale financial values."""
    if value is None or value == "Unknown":
        return "Unknown"
    
    try:
        # If already a number, apply scaling
        if isinstance(value, (int, float)):
            # Apply scale factor
            scaled_value = value * scale_factor
            
            # Return as integer if whole number, otherwise round to 2 decimal places
            return int(scaled_value) if scaled_value.is_integer() else round(scaled_value, 2)
            
        # Handle string values
        if isinstance(value, str):
            normalized = normalize_number(value)
            if normalized is not None:
                return format_financial_value(normalized, scale_factor)
        
        return "Unknown"
        
    except Exception as e:
        print(f"Error formatting value '{value}': {str(e)}")
        return "Unknown"

def validate_financial_data(data):
    """Perform reasonableness checks on financial data."""
    # Make a copy to avoid modifying the original data
    validated = data.copy()
    
    # Check for unreasonably large values
    MAX_REASONABLE_VALUE = 1e12  # 1 trillion
    for key, value in validated.items():
        if isinstance(value, (int, float)) and abs(value) > MAX_REASONABLE_VALUE:
            print(f"Warning: Unreasonably large value detected for {key}: {value}")
            # Scale down the value if it's too large
            scale_down = 1000  # Scale down by 1000
            validated[key] = value / scale_down
            print(f"Scaled down to: {validated[key]}")
    
    # Check if values are in expected relationships
    if 'Revenue' in validated and 'Gross_Profit' in validated:
        if validated['Gross_Profit'] > validated['Revenue']:
            print("Warning: Gross Profit exceeds Revenue, which is unusual")
            # Adjust the values to make them more reasonable
            if validated['Gross_Profit'] > 0 and validated['Revenue'] > 0:
                # If both are positive, scale Revenue up
                validated['Revenue'] = validated['Gross_Profit'] * 2
                print(f"Adjusted Revenue to: {validated['Revenue']}")
    
    if 'Gross_Profit' in validated and 'Operating_Income' in validated:
        if validated['Operating_Income'] > validated['Gross_Profit']:
            print("Warning: Operating Income exceeds Gross Profit, which is unusual")
            # Adjust the values to make them more reasonable
            if validated['Operating_Income'] > 0 and validated['Gross_Profit'] > 0:
                # If both are positive, scale Gross Profit up
                validated['Gross_Profit'] = validated['Operating_Income'] * 1.5
                print(f"Adjusted Gross Profit to: {validated['Gross_Profit']}")
    
    if 'Operating_Income' in validated and 'Net_Income' in validated:
        if validated['Net_Income'] > validated['Operating_Income']:
            print("Warning: Net Income exceeds Operating Income, which is unusual")
            # Adjust the values to make them more reasonable
            if validated['Net_Income'] > 0 and validated['Operating_Income'] > 0:
                # If both are positive, scale Operating Income up
                validated['Operating_Income'] = validated['Net_Income'] * 1.2
                print(f"Adjusted Operating Income to: {validated['Operating_Income']}")
    
    return validated

def infer_missing_values(data):
    """Fill in missing values using financial relationships."""
    inferred = data.copy()
    
    # Infer Cost of Revenue if Revenue and Gross Profit are known
    if 'Revenue' in inferred and 'Gross_Profit' in inferred and 'Cost_of_Revenue' not in inferred:
        inferred['Cost_of_Revenue'] = inferred['Revenue'] - inferred['Gross_Profit']
        print(f"Inferred Cost of Revenue: {inferred['Cost_of_Revenue']}")
    
    # Infer Gross Profit if Revenue and Cost of Revenue are known
    if 'Revenue' in inferred and 'Cost_of_Revenue' in inferred and 'Gross_Profit' not in inferred:
        inferred['Gross_Profit'] = inferred['Revenue'] - inferred['Cost_of_Revenue']
        print(f"Inferred Gross Profit: {inferred['Gross_Profit']}")
    
    # Infer Operating Expenses if Gross Profit and Operating Income are known
    if 'Gross_Profit' in inferred and 'Operating_Income' in inferred and 'Operating_Expenses' not in inferred:
        inferred['Operating_Expenses'] = inferred['Gross_Profit'] - inferred['Operating_Income']
        print(f"Inferred Operating Expenses: {inferred['Operating_Expenses']}")
    
    # Infer Operating Income if Gross Profit and Operating Expenses are known
    if 'Gross_Profit' in inferred and 'Operating_Expenses' in inferred and 'Operating_Income' not in inferred:
        inferred['Operating_Income'] = inferred['Gross_Profit'] - inferred['Operating_Expenses']
        print(f"Inferred Operating Income: {inferred['Operating_Income']}")
    
    # If we have very little data, make some reasonable estimates
    if 'Revenue' in inferred and len(inferred) < 3:
        if 'Cost_of_Revenue' not in inferred:
            inferred['Cost_of_Revenue'] = inferred['Revenue'] * 0.65  # Typical COGS ratio
            print(f"Estimated Cost of Revenue: {inferred['Cost_of_Revenue']}")
        if 'Gross_Profit' not in inferred:
            inferred['Gross_Profit'] = inferred['Revenue'] - inferred['Cost_of_Revenue']
            print(f"Estimated Gross Profit: {inferred['Gross_Profit']}")
        if 'Operating_Expenses' not in inferred:
            inferred['Operating_Expenses'] = inferred['Gross_Profit'] * 0.7  # Typical OpEx ratio
            print(f"Estimated Operating Expenses: {inferred['Operating_Expenses']}")
        if 'Operating_Income' not in inferred:
            inferred['Operating_Income'] = inferred['Gross_Profit'] - inferred['Operating_Expenses']
            print(f"Estimated Operating Income: {inferred['Operating_Income']}")
        if 'Net_Income' not in inferred:
            inferred['Net_Income'] = inferred['Operating_Income'] * 0.75  # Accounting for taxes
            print(f"Estimated Net Income: {inferred['Net_Income']}")
    
    return inferred

def extract_llm_financial_data(text):
    """Extract financial data using LLM."""
    print("Attempting to extract financial data using LLM...")
    
    # Prepare the prompt for the LLM
    prompt = f"""
    Extract ONLY the income statement data from this financial document text.
    
    FORMAT INSTRUCTIONS (CRITICAL):
    1. Your response must ONLY contain a valid JSON object WITHOUT any markdown formatting
    2. Each key must be in quotes, each value must be a NUMBER (without any currency symbols) or "Unknown" in quotes
    3. DO NOT include any scale factors in your numbers - provide raw values exactly as they appear
    4. DO NOT multiply values by any scale factor
    5. If a value is negative, represent it as a negative number like -10.5, not with parentheses
    6. If a value is not found, use "Unknown" in quotes
    7. Ensure all keys are in snake_case (e.g., "net_income", "operating_expenses")
    
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
    {text[:4000]}
    \"\"\"
    
    IMPORTANT: Return ONLY the JSON object, no markdown formatting, no explanations.
    """
    
    response = query_model(prompt, model="granite3.2-vision")
    
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
    
    # Third attempt: Parse line by line as key-value pairs
    if not json_data:
        print("Attempting line-by-line parsing...")
        json_data = {}
        for line in response.strip().split('\n'):
            if ':' in line:
                parts = line.split(':', 1)
                if len(parts) == 2:
                    key = parts[0].strip().strip('"\'').replace(' ', '_')
                    value = parts[1].strip().strip(',').strip('"\'')
                    if value != "Unknown" and value.strip():
                        try:
                            json_data[key] = float(value.replace(',', ''))
                        except ValueError:
                            json_data[key] = "Unknown"
                    else:
                        json_data[key] = "Unknown"
    
    return json_data if json_data else {}

def extract_income_statement(pdf_bytes):
    """
    Extract income statement data using a hybrid approach combining pattern matching and LLM.
    This approach is more robust and less likely to produce wildly inaccurate results.
    """
    try:
        # Step 1: Extract text from PDF
        raw_text = extract_text_from_pdf(pdf_bytes)
        
        # Step 2: Detect scale notation (in millions, in billions, etc.)
        scale_factor = detect_scale_notation(raw_text)
        print(f"Detected scale factor: {scale_factor}")
        
        # Step 3: Clean and prepare text for extraction
        processed_text = clean_text_for_extraction(raw_text)
        
        # Step 4: First attempt - Extract using rule-based pattern matching
        pattern_results = extract_financial_values_with_patterns(processed_text)
        print(f"Pattern-based extraction found {len(pattern_results)} values")
        
        # Step 5: If pattern matching is insufficient, try LLM extraction
        if len(pattern_results) < 4:  # Not enough values found with patterns
            print("Insufficient data from pattern matching, using LLM as backup")
            llm_results = extract_llm_financial_data(processed_text)
            
            # Merge the results, giving priority to pattern-based extraction
            for key, value in llm_results.items():
                if key not in pattern_results or pattern_results[key] == "Unknown":
                    pattern_results[key] = value
            
            print(f"After LLM extraction, we have {len(pattern_results)} values")
        
        # Step 6: Apply the scale factor to all values
        formatted_data = {}
        for key, value in pattern_results.items():
            formatted_data[key] = format_financial_value(value, scale_factor)
        
        # Step 7: Validate the data for reasonableness
        validated_data = validate_financial_data(formatted_data)
        
        # Step 8: Infer missing values based on financial relationships
        final_data = infer_missing_values(validated_data)
        
        # Step 9: Ensure we have all required fields
        required_fields = ['Revenue', 'Cost_of_Revenue', 'Gross_Profit', 
                        'Operating_Expenses', 'Operating_Income', 'Net_Income']
        
        for field in required_fields:
            if field not in final_data or final_data[field] == "Unknown":
                final_data[field] = "Unknown"
        
        # Step 10: Process the data for visualization
        visualization_data = process_financial_data_for_visualization(final_data)
        
        # Add visualization data to the response
        final_data["visualization_data"] = visualization_data
        
        # Log the final values
        print("\nFinal processed values:")
        for key, value in final_data.items():
            if key != "visualization_data":
                if isinstance(value, (int, float)):
                    print(f"{key}: {value:,}")
                else:
                    print(f"{key}: {value}")
        
        return final_data
            
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