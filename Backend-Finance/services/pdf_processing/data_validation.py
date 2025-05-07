import re
from typing import Dict, Union, Any

def normalize_number(value_str: str) -> float:
    """Convert a string representation of a number to a float value."""
    if isinstance(value_str, (int, float)):
        return float(value_str)
    
    # Remove currency symbols and whitespace
    cleaned = re.sub(r'[^\d.-]', '', str(value_str))
    
    # Handle negative numbers in parentheses
    if value_str.strip().startswith('(') and value_str.strip().endswith(')'):
        cleaned = '-' + cleaned
    
    return float(cleaned) if cleaned else 0.0

def validate_financial_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Perform reasonableness checks on financial data."""
    validated = data.copy()
    
    # Basic validation rules
    if validated.get('Gross_Profit', 0) > validated.get('Revenue', 0):
        validated['Gross_Profit'] = validated.get('Revenue', 0) - validated.get('Cost_of_Revenue', 0)
    
    if validated.get('Operating_Income', 0) > validated.get('Gross_Profit', 0):
        validated['Operating_Income'] = validated.get('Gross_Profit', 0) - validated.get('Operating_Expenses', 0)
    
    if validated.get('Net_Income', 0) > validated.get('Operating_Income', 0):
        validated['Net_Income'] = validated.get('Operating_Income', 0)
    
    return validated

def format_financial_value(value: Union[str, float, int], scale_factor: int = 1) -> Union[float, str]:
    """Format and scale financial values."""
    if isinstance(value, str) and value.lower() == 'unknown':
        return 'Unknown'
    
    try:
        if isinstance(value, str):
            value = normalize_number(value)
        return float(value) * scale_factor
    except (ValueError, TypeError):
        return 'Unknown'

def infer_missing_values(data: Dict[str, Any]) -> Dict[str, Any]:
    """Fill in missing values using financial relationships."""
    result = data.copy()
    
    # Infer Revenue
    if 'Revenue' not in result or result['Revenue'] == 'Unknown':
        if 'Gross_Profit' in result and 'Cost_of_Revenue' in result:
            result['Revenue'] = result['Gross_Profit'] + result['Cost_of_Revenue']
    
    # Infer Gross Profit
    if 'Gross_Profit' not in result or result['Gross_Profit'] == 'Unknown':
        if 'Revenue' in result and 'Cost_of_Revenue' in result:
            result['Gross_Profit'] = result['Revenue'] - result['Cost_of_Revenue']
    
    # Infer Operating Income
    if 'Operating_Income' not in result or result['Operating_Income'] == 'Unknown':
        if 'Gross_Profit' in result and 'Operating_Expenses' in result:
            result['Operating_Income'] = result['Gross_Profit'] - result['Operating_Expenses']
    
    return result