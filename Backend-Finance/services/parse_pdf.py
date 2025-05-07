import json
import fitz  # PyMuPDF
import re
from services.model_runner import query_model

def extract_text_from_pdf(pdf_bytes):
    """Extract text from PDF bytes."""
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text("text") + "\n\n"
    return text

def detect_scale_notation(text):
    """Detect if numbers are in millions, billions, etc."""
    text = text.lower()
    
    billion_patterns = [
        r'\(in billions\)', r'\(billions\)', r'\(in bb\)',
        r'amounts.*billions', r'expressed.*billions',
        r'figures.*billions', r'numbers.*billions'
    ]
    
    million_patterns = [
        r'\(in millions\)', r'\(millions\)', r'\(in mm\)',
        r'amounts.*millions', r'expressed.*millions',
        r'figures.*millions', r'numbers.*millions'
    ]
    
    thousand_patterns = [
        r'\(in thousands\)', r'\(thousands\)', r'\(in k\)',
        r'amounts.*thousands', r'expressed.*thousands',
        r'figures.*thousands', r'numbers.*thousands'
    ]
    
    header_footer_text = text[:2000] + text[-2000:]
    
    for pattern in billion_patterns:
        if re.search(pattern, header_footer_text):
            return 1_000_000_000
    
    for pattern in million_patterns:
        if re.search(pattern, header_footer_text):
            return 1_000_000
    
    for pattern in thousand_patterns:
        if re.search(pattern, header_footer_text):
            return 1_000
    
    return 1

def clean_text_for_extraction(text):
    """Prepare text for pattern matching."""
    text = re.sub(r'\s+', ' ', text)
    financial_terms = [
        "revenue", "total revenue", "sales", "net sales",
        "cost of revenue", "cost of goods sold", "cogs",
        "gross profit", "gross margin",
        "operating expenses", "total operating expenses", "opex",
        "operating income", "operating profit", "ebit",
        "net income", "net profit", "net earnings"
    ]
    
    for term in financial_terms:
        text = re.sub(r'(\b' + term + r'\b)', r' \1 ', text, flags=re.IGNORECASE)
    
    return text

def extract_financial_values_with_patterns(text):
    """Extract financial values using regex patterns."""
    results = {}
    
    financial_patterns = {
        'Revenue': [
            r'(?:Total\s+)?Revenue[s]?[:\s]+[\$]?([\d,]+(?:\.\d+)?)',
            r'Total Sales[:\s]+[\$]?([\d,]+(?:\.\d+)?)',
            r'Net Sales[:\s]+[\$]?([\d,]+(?:\.\d+)?)'
        ],
        'Cost_of_Revenue': [
            r'Cost of Revenue[:\s]+[\$]?([\d,]+(?:\.\d+)?)',
            r'Cost of Sales[:\s]+[\$]?([\d,]+(?:\.\d+)?)',
            r'COGS[:\s]+[\$]?([\d,]+(?:\.\d+)?)'
        ],
        'Gross_Profit': [
            r'Gross Profit[:\s]+[\$]?([\d,]+(?:\.\d+)?)',
            r'Gross Margin[:\s]+[\$]?([\d,]+(?:\.\d+)?)'
        ],
        'Operating_Expenses': [
            r'(?:Total\s+)?Operating Expenses[:\s]+[\$]?([\d,]+(?:\.\d+)?)',
            r'Total Expenses[:\s]+[\$]?([\d,]+(?:\.\d+)?)',
            r'Operating Costs[:\s]+[\$]?([\d,]+(?:\.\d+)?)'
        ],
        'Operating_Income': [
            r'Operating Income[:\s]+[\$]?([\d,]+(?:\.\d+)?)',
            r'Operating Profit[:\s]+[\$]?([\d,]+(?:\.\d+)?)',
            r'EBIT[:\s]+[\$]?([\d,]+(?:\.\d+)?)'
        ],
        'Net_Income': [
            r'Net Income[:\s]+[\$]?([\d,]+(?:\.\d+)?)',
            r'Net Profit[:\s]+[\$]?([\d,]+(?:\.\d+)?)',
            r'Net Earnings[:\s]+[\$]?([\d,]+(?:\.\d+)?)'
        ]
    }
    
    for key, patterns in financial_patterns.items():
        for pattern in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                value = match.group(1)
                if value:
                    try:
                        numeric_value = normalize_number(value)
                        if key not in results or numeric_value > results[key]:
                            results[key] = numeric_value
                    except ValueError:
                        continue
    
    return results

def normalize_number(value_str):
    """Convert a string representation of a number to a float value."""
    if isinstance(value_str, (int, float)):
        return float(value_str)
    
    cleaned = re.sub(r'[^\d.-]', '', str(value_str))
    
    if value_str.strip().startswith('(') and value_str.strip().endswith(')'):
        cleaned = '-' + cleaned
    
    return float(cleaned) if cleaned else 0.0

def extract_llm_financial_data(text):
    """Extract financial data using LLM."""
    prompt = f"""Extract the following financial values from the text in pure numbers (no currency symbols or commas):
    - Revenue
    - Cost of Revenue
    - Gross Profit
    - Operating Expenses
    - Operating Income
    - Net Income

    Text: {text}

    Return the values in JSON format."""
    
    try:
        response = query_model(prompt)
        return json.loads(response)
    except Exception as e:
        print(f"Error in LLM extraction: {str(e)}")
        return {}

def validate_financial_data(data):
    """Perform reasonableness checks on financial data."""
    validated = data.copy()
    
    if validated.get('Gross_Profit', 0) > validated.get('Revenue', 0):
        validated['Gross_Profit'] = validated.get('Revenue', 0) - validated.get('Cost_of_Revenue', 0)
    
    if validated.get('Operating_Income', 0) > validated.get('Gross_Profit', 0):
        validated['Operating_Income'] = validated.get('Gross_Profit', 0) - validated.get('Operating_Expenses', 0)
    
    if validated.get('Net_Income', 0) > validated.get('Operating_Income', 0):
        validated['Net_Income'] = validated.get('Operating_Income', 0)
    
    return validated

def format_financial_value(value, scale_factor=1):
    """Format and scale financial values."""
    if isinstance(value, str) and value.lower() == 'unknown':
        return 'Unknown'
    
    try:
        if isinstance(value, str):
            value = normalize_number(value)
        return float(value) * scale_factor
    except (ValueError, TypeError):
        return 'Unknown'

def infer_missing_values(data):
    """Fill in missing values using financial relationships."""
    result = data.copy()
    
    if 'Revenue' not in result or result['Revenue'] == 'Unknown':
        if 'Gross_Profit' in result and 'Cost_of_Revenue' in result:
            result['Revenue'] = result['Gross_Profit'] + result['Cost_of_Revenue']
    
    if 'Gross_Profit' not in result or result['Gross_Profit'] == 'Unknown':
        if 'Revenue' in result and 'Cost_of_Revenue' in result:
            result['Gross_Profit'] = result['Revenue'] - result['Cost_of_Revenue']
    
    if 'Operating_Income' not in result or result['Operating_Income'] == 'Unknown':
        if 'Gross_Profit' in result and 'Operating_Expenses' in result:
            result['Operating_Income'] = result['Gross_Profit'] - result['Operating_Expenses']
    
    return result

def extract_income_statement(pdf_bytes):
    """Main function to extract and process income statement data."""
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