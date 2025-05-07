import re
from .data_validation import normalize_number
from typing import Dict, Any

def extract_financial_values_with_patterns(text: str) -> Dict[str, Any]:
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