import re
from typing import List

def detect_scale_notation(text: str) -> int:
    """Enhanced scale detection with multiple methods for better accuracy."""
    text = text.lower()
    
    billion_patterns = [
        r'\(in billions\)', r'\(billions\)', r'\(in bb\)',
        r'amounts.*billions', r'expressed.*billions',
        r'figures.*billions', r'numbers.*billions'
    ]
    
    million_patterns = [
        r'\(in millions\)', r'\(millions\)', r'\(in mm\)',
        r'amounts.*millions', r'expressed.*millions',
        r'figures.*millions', r'numbers.*millions'
    ]
    
    thousand_patterns = [
        r'\(in thousands\)', r'\(thousands\)', r'\(in k\)',
        r'amounts.*thousands', r'expressed.*thousands',
        r'figures.*thousands', r'numbers.*thousands'
    ]
    
    # Check first 2000 and last 2000 characters for scale notation
    header_footer_text = text[:2000] + text[-2000:]
    
    # Check for billion notation
    for pattern in billion_patterns:
        if re.search(pattern, header_footer_text):
            return 1_000_000_000
    
    # Check for million notation
    for pattern in million_patterns:
        if re.search(pattern, header_footer_text):
            return 1_000_000
    
    # Check for thousand notation
    for pattern in thousand_patterns:
        if re.search(pattern, header_footer_text):
            return 1_000
    
    # Default to no scaling if no notation is found
    return 1