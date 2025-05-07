import json
import fitz  # PyMuPDF
import re
from services.model_runner import query_model
from .pdf_processing.text_extraction import extract_text_from_pdf, clean_text_for_extraction
from .pdf_processing.scale_detection import detect_scale_notation
from .pdf_processing.value_extraction import extract_financial_values_with_patterns
from .pdf_processing.data_validation import validate_financial_data, format_financial_value, infer_missing_values
from .pdf_processing.data_processing import process_financial_data_for_visualization
from .pdf_processing.llm_extraction import extract_llm_financial_data

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