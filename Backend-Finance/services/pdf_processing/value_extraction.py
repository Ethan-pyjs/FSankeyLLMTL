import re
from .data_validation import normalize_number

def extract_financial_values_with_patterns(text):
    """Extract financial values using regex patterns."""
    results = {}
    
    financial_patterns = {
        'Revenue': [
            r'(?:Total\s+)?Revenue[s]?[:\s]+[\$]?([\d,]+(?:\.\d+)?)',
            # ...existing patterns...
        ],
        # ...rest of the patterns...
    }
    
    # ... rest of the extraction function ...