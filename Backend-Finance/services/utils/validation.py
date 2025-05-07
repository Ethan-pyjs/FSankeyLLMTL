"""
Utility functions for validating financial data for reasonableness.
"""

def validate_financial_data(data):
    """
    Perform reasonableness checks on financial data.
    
    Args:
        data: Dictionary of financial data to validate
        
    Returns:
        dict: Validated and potentially adjusted financial data
    """
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