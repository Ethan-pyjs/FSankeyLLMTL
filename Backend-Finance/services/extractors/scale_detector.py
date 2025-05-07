"""
Module for detecting the scale notation in financial documents.
"""
import re

def detect_scale_notation(text):
    """
    Enhanced scale detection with multiple methods for better accuracy.
    
    Args:
        text: Document text to analyze
        
    Returns:
        int: Scale factor (1, 1000, 1000000, or 1000000000)
    """
    text = text.lower()
    
    # Method 1: Check for explicit scale indicators
    # First check for explicit billion indicators
    billion_patterns = [
        r'\(in billions\)', r'\(billions\)', r'\(in bb\)', r'presented in billions',
        r'amounts in billions', r'\$.*bb', r'\(bb\)', r'figures? in billions',
        r'expressed in billions', r'reported in billions', r'USD in billions',
        r'in billions of (dollars|usd|$)', r'billions of (dollars|usd|$)'
    ]
    
    # Then check for million indicators
    million_patterns = [
        r'\(in millions\)', r'\(millions\)', r'\(in mm\)', r'presented in millions',
        r'amounts in millions', r'\$.*mm', r'\(mm\)', r'figures? in millions',
        r'expressed in millions', r'reported in millions', r'USD in millions',
        r'in millions of (dollars|usd|$)', r'millions of (dollars|usd|$)'
    ]
    
    # Check for thousand indicators
    thousand_patterns = [
        r'\(in thousands\)', r'\(thousands\)', r'\(in k\)', r'presented in thousands',
        r'amounts in thousands', r'\$.*k', r'\(k\)', r'figures? in thousands',
        r'expressed in thousands', r'reported in thousands', r'USD in thousands',
        r'in thousands of (dollars|usd|$)', r'thousands of (dollars|usd|$)'
    ]
    
    print("Checking for scale notation in text...")
    
    # Make a copy of the text with special focus on headers and footnotes
    header_footer_text = text[:2000] + text[-2000:]
    
    # Check for billions first (to avoid misinterpreting "millions" in a document using billions)
    for pattern in billion_patterns:
        if re.search(pattern, header_footer_text, re.IGNORECASE):
            print("Detected billions notation in header/footer")
            return 1000000000
    
    # Then check millions
    for pattern in million_patterns:
        if re.search(pattern, header_footer_text, re.IGNORECASE):
            print("Detected millions notation in header/footer")
            return 1000000
    
    # Finally check thousands
    for pattern in thousand_patterns:
        if re.search(pattern, header_footer_text, re.IGNORECASE):
            print("Detected thousands notation in header/footer")
            return 1000
    
    # Method 2: Check common financial statement headers
    header_check = text[:1000]  # Check first 1000 characters for headers
    if re.search(r'(million|mm).*\$|^\$.*mm', header_check, re.IGNORECASE):
        print("Detected millions notation from header")
        return 1000000
    elif re.search(r'(billion|bb).*\$|^\$.*bb', header_check, re.IGNORECASE):
        print("Detected billions notation from header")
        return 1000000000
    
    # Method 3: Analyze the actual values in the document
    # Extract potential financial values (numbers with dollar signs or commas)
    values = []
    # Look for numbers that might be financial figures
    for match in re.finditer(r'\$\s*([\d,]+(?:\.\d+)?)', text):
        try:
            value = float(match.group(1).replace(',', ''))
            values.append(value)
        except ValueError:
            continue
    
    if values:
        avg_value = sum(values) / len(values)
        print(f"Average detected value: {avg_value}")
        
        # Use the average value to infer the scale
        if avg_value > 100000000000:  # Numbers in trillions
            print("Values appear to be raw (no scale factor needed)")
            return 1
        elif avg_value > 100000000:  # Numbers in hundreds of millions
            print("Values appear to be raw (no scale factor needed)")
            return 1
        elif avg_value > 10000 and avg_value < 100000:  # Likely in thousands
            print("Inferred values in thousands")
            return 1000
        elif avg_value > 10 and avg_value < 10000:  # Likely in millions
            print("Inferred values in millions")
            return 1000000
        elif avg_value < 10:  # Likely in billions
            print("Inferred values in billions")
            return 1000000000
    
    print("Using default scale (raw values)")
    return 1