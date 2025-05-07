"""
Module for extracting financial data using regex pattern matching.
"""
import re
from utils.number_processing import normalize_number

def extract_financial_values_with_patterns(text):
    """
    Extract financial values using regex patterns targeting common financial statement formats.
    
    Args:
        text: Preprocessed document text
        
    Returns:
        dict: Extracted financial values
    """
    results = {}
    
    # Define patterns for key financial metrics
    # Format is: field name -> list of regex patterns
    financial_patterns = {
        'Revenue': [
            r'(?:Total\s+)?Revenue[s]?[:\s]+[\$]?([\d,]+(?:\.\d+)?)',
            r'(?:Total\s+)?Sales[:\s]+[\$]?([\d,]+(?:\.\d+)?)',
            r'Revenue[s]?[:\s]*[\$]?([\d,]+(?:\.\d+)?)',
            r'Total\s+operating\s+revenues?[:\s]+[\$]?([\d,]+(?:\.\d+)?)',
            r'(?:Total\s+)?Net\s+Sales[:\s]+[\$]?([\d,]+(?:\.\d+)?)',
            r'(?:Automotive\s+)?Sales[:\s]+[\$]?([\d,]+(?:\.\d+)?)',
            r'Net\s+Revenue[:\s]+[\$]?([\d,]+(?:\.\d+)?)',
            r'Net\s+Sales[:\s]+[\$]?([\d,]+(?:\.\d+)?)',
            r'Net\s+Operating\s+Revenue[:\s]+[\$]?([\d,]+(?:\.\d+)?)',
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