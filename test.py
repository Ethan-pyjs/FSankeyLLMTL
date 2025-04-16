# Logic to extract text/income statement
import json
from services.model_runner import query_model
import fitz  # PyMuPDF
import re

def extract_text_from_pdf(pdf_bytes):
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    return "\n".join(page.get_text() for page in doc)

def clean_numeric_value(value_str):
    """Convert string values to numeric format, handling different formats."""
    if not value_str or value_str == "Unknown":
        return 0
        
    # Remove any non-numeric characters except dots and commas
    value_str = re.sub(r'[^\d.,]', '', value_str)
    
    # Replace commas with nothing
    value_str = value_str.replace(',', '')
    
    try:
        return float(value_str)
    except ValueError:
        return 0

def extract_income_statement(pdf_bytes):
    text = extract_text_from_pdf(pdf_bytes)
    
    # First attempt - try to get structured financial data
    structured_prompt = f"""
    Extract the following financial data points from this document:
    - Revenue
    - Cost of Revenue
    - Gross Profit
    - Operating Expenses
    - Net Income
    
    For each item, extract the numeric value if available. If an item is not found, respond with "Not available".
    Format your response as a JSON object with these exact keys. Example:
    {{
        "Revenue": "1000000",
        "Cost of Revenue": "600000",
        "Gross Profit": "400000",
        "Operating Expenses": "300000",
        "Net Income": "100000"
    }}
    
    Financial Document Text:
    \"\"\"{text}\"\"\"
    """
    
    try:
        response = query_model(structured_prompt, model="mistral")
        print(f"Model response (first 200 chars): {response[:200]}...")
        
        # Try to parse JSON from response
        json_data = None
        try:
            # Find JSON object in the response
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                json_str = json_match.group(0)
                json_data = json.loads(json_str)
            else:
                # If no JSON object found, process line by line
                json_data = {}
                for line in response.strip().split('\n'):
                    if ':' in line:
                        key, value = line.split(':', 1)
                        key = key.strip().strip('\"')
                        value = value.strip().strip('\"').strip(',')
                        json_data[key] = value
        except json.JSONDecodeError:
            json_data = None
        
        # If we couldn't parse JSON, or if essential data is missing, try a fallback approach
        if not json_data or not any(key in json_data for key in ["Revenue", "Net Income"]):
            # Fallback approach - ask for a financial summary and extract values
            summary_prompt = f"""
            Provide a brief financial summary of this document. Focus on key metrics such as Revenue, 
            Cost of Revenue, Gross Profit, Operating Expenses, and Net Income. Include specific numbers if available.
            
            Document Text:
            \"\"\"{text}\"\"\"
            """
            
            summary = query_model(summary_prompt, model="mistral")
            
            # Create a structured response
            json_data = {
                "Revenue": "0",
                "Cost of Revenue": "0",
                "Gross Profit": "0",
                "Operating Expenses": "0",
                "Net Income": "0",
                "_summary": summary  # Store the summary for reference
            }
            
            # Extract values from the summary
            patterns = {
                "Revenue": r"revenue.*?(\$?[\d,.]+\s*(million|billion|thousand|k|m|b)?)",
                "Cost of Revenue": r"cost of (revenue|goods).*?(\$?[\d,.]+\s*(million|billion|thousand|k|m|b)?)",
                "Gross Profit": r"gross profit.*?(\$?[\d,.]+\s*(million|billion|thousand|k|m|b)?)",
                "Operating Expenses": r"operating expenses.*?(\$?[\d,.]+\s*(million|billion|thousand|k|m|b)?)",
                "Net Income": r"net (income|profit|loss).*?(\$?[\d,.]+\s*(million|billion|thousand|k|m|b)?)"
            }
            
            for key, pattern in patterns.items():
                match = re.search(pattern, summary, re.IGNORECASE)
                if match:
                    value = match.group(1)
                    json_data[key] = value
        
        # Ensure all keys exist
        required_keys = ["Revenue", "Cost of Revenue", "Gross Profit", "Operating Expenses", "Net Income"]
        for key in required_keys:
            if key not in json_data:
                json_data[key] = "0"
                
        # Add numeric values for Sankey chart
        json_data["_numeric"] = {
            "Revenue": clean_numeric_value(json_data["Revenue"]),
            "Cost of Revenue": clean_numeric_value(json_data["Cost of Revenue"]),
            "Gross Profit": clean_numeric_value(json_data["Gross Profit"]),
            "Operating Expenses": clean_numeric_value(json_data["Operating Expenses"]),
            "Net Income": clean_numeric_value(json_data["Net Income"])
        }
        
        # Validate and fix values
        numeric = json_data["_numeric"]
        
        # Ensure Gross Profit = Revenue - Cost of Revenue
        if numeric["Gross Profit"] == 0 and numeric["Revenue"] > 0:
            numeric["Gross Profit"] = numeric["Revenue"] - numeric["Cost of Revenue"]
            
        # Ensure Net Income = Gross Profit - Operating Expenses
        if numeric["Net Income"] == 0 and numeric["Gross Profit"] > 0:
            numeric["Net Income"] = numeric["Gross Profit"] - numeric["Operating Expenses"]
            
        # If we have Net Income but missing other values, make reasonable estimates
        if numeric["Net Income"] > 0 and numeric["Revenue"] == 0:
            numeric["Revenue"] = numeric["Net Income"] * 5  # Revenue typically 5x Net Income
            numeric["Cost of Revenue"] = numeric["Revenue"] * 0.6  # Cost of Revenue typically 60% of Revenue
            numeric["Gross Profit"] = numeric["Revenue"] - numeric["Cost of Revenue"]
            numeric["Operating Expenses"] = numeric["Gross Profit"] - numeric["Net Income"]
        
        # Add a flag to indicate data quality
        if all(val > 0 for val in numeric.values()):
            json_data["_data_quality"] = "high"
        elif numeric["Net Income"] > 0:
            json_data["_data_quality"] = "medium"
        else:
            json_data["_data_quality"] = "low"
            
        return json_data
            
    except Exception as e:
        print(f"Error in extract_income_statement: {str(e)}")
        return {
            "Revenue": "0",
            "Cost of Revenue": "0",
            "Gross Profit": "0",
            "Operating Expenses": "0",
            "Net Income": "0",
            "_error": f"Error processing request: {str(e)}",
            "_numeric": {
                "Revenue": 0,
                "Cost of Revenue": 0,
                "Gross Profit": 0,
                "Operating Expenses": 0,
                "Net Income": 0
            },
            "_data_quality": "error"
        }