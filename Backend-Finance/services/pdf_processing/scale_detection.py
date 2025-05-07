import re

def detect_scale_notation(text):
    """Enhanced scale detection with multiple methods for better accuracy."""
    text = text.lower()
    
    # Pattern definitions
    billion_patterns = [
        r'\(in billions\)', r'\(billions\)', r'\(in bb\)',
        # ...existing billion patterns...
    ]
    
    million_patterns = [
        r'\(in millions\)', r'\(millions\)', r'\(in mm\)',
        # ...existing million patterns...
    ]
    
    thousand_patterns = [
        r'\(in thousands\)', r'\(thousands\)', r'\(in k\)',
        # ...existing thousand patterns...
    ]
    
    # Your existing scale detection logic
    header_footer_text = text[:2000] + text[-2000:]
    
    # ... rest of the detect_scale_notation function ...