"""
Utility functions for processing financial numbers and values.
"""
import re

def normalize_number(value_str):
    """
    Convert a string representation of a number to a float value.
    
    Args:
        value_str: String containing a number, potentially with formatting characters
        
    Returns:
        float or None: Normalized number or None if conversion fails
    """
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

def format_financial_value(value, scale_factor=1):
    """
    Format and scale financial values.
    
    Args:
        value: Raw value to format
        scale_factor: Scaling factor to apply (e.g., 1000000 for millions)
        
    Returns:
        int, float, or str: Formatted and scaled value or "Unknown" if invalid
    """
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