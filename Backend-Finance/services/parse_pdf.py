# Logic to extract text/income statement
import json
from services.model_runner import query_model
import fitz  # PyMuPDF

def extract_text_from_pdf(pdf_bytes):
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    return "\n".join(page.get_text() for page in doc)

def extract_income_statement(pdf_bytes):
    text = extract_text_from_pdf(pdf_bytes)
    
    # Use a more explicit prompt to force JSON output
    prompt = f"""
    Extract the income statement data from this financial document and return it ONLY as a JSON object.
    
    Rules:
    1. Your response must ONLY contain a valid JSON object, nothing else
    2. Do not include any explanations, markdown formatting, or text outside the JSON
    3. Use double quotes for keys and string values
    4. Include fields like "Revenue", "Cost_of_Revenue", "Gross_Profit", "Operating_Expenses", "Net_Income" if available
    
    Financial Document Text:
    \"\"\"{text}\"\"\"
    """
    
    try:
        response = query_model(prompt, model="mistral")
        print(f"Raw model response (first 200 chars): {response[:200]}...")
        
        # If the response doesn't start with a curly brace, we need to create our own JSON
        if not response.strip().startswith("{"):
            print("Response is not JSON, extracting information to create JSON")
            
            # Let's use the model again but with a different approach
            structured_prompt = f"""
            From this text, extract the following financial data points as key-value pairs:
            - Revenue
            - Cost of Revenue
            - Gross Profit
            - Operating Expenses
            - Net Income
            
            For each value, extract just the number in millions of dollars.
            Format each line as "Key: Value" without any additional text.
            
            Example format:
            Revenue: 123456
            Cost of Revenue: 45678
            
            Text: \"\"\"{text}\"\"\"
            """
            
            structured_response = query_model(structured_prompt, model="mistral")
            print(f"Structured response: {structured_response}")
            
            # Convert the structured response to JSON
            json_data = {}
            for line in structured_response.strip().split("\n"):
                if ":" in line:
                    key, value = line.split(":", 1)
                    json_data[key.strip()] = value.strip()
            
            return json_data
            
        else:
            # Try to parse the JSON response
            try:
                json_data = json.loads(response)
                return json_data
            except json.JSONDecodeError:
                # Extract JSON part if possible
                json_start = response.find("{")
                json_end = response.rfind("}") + 1
                if json_start >= 0 and json_end > json_start:
                    try:
                        json_data = json.loads(response[json_start:json_end])
                        return json_data
                    except json.JSONDecodeError:
                        pass
                
                # If all else fails, create a default structure
                return {
                    "Revenue": "Unknown",
                    "Cost of Revenue": "Unknown",
                    "Gross Profit": "Unknown",
                    "Operating Expenses": "Unknown",
                    "Net Income": "Unknown",
                    "note": "Data extracted from financial document"
                }
                
    except Exception as e:
        print(f"Error in extract_income_statement: {str(e)}")
        return {"error": f"Error processing request: {str(e)}"}