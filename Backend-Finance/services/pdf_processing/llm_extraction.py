from services.model_runner import query_model
import json
import re
from typing import Dict, Any

def extract_llm_financial_data(text: str) -> Dict[str, Any]:
    """Extract financial data using LLM."""
    print("Attempting to extract financial data using LLM...")
    
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
    {text[:12000]}
    \"\"\"
    
    IMPORTANT: Return ONLY the JSON object, no markdown formatting, no explanations.
    """
    
    response = query_model(prompt, model="granite3.2-vision")
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