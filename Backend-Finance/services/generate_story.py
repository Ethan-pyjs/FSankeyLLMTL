from services.model_runner import query_model

def generate_story_from_json(data):
    """
    Generate a financial narrative based on income statement data.
    The story aims to be more insightful and contextual.
    """
    # Create a more tailored prompt based on available data
    financial_metrics = []
    unknown_metrics = []
    
    # Categorize which metrics are available vs unknown
    for key, value in data.items():
        if value != "Unknown" and not isinstance(value, str):
            financial_metrics.append(f"{key.replace('_', ' ')}: {value}")
        elif value == "Unknown":
            unknown_metrics.append(key.replace('_', ' '))
    
    # Different approach based on available data
    if len(financial_metrics) >= 3:
        # We have enough data for a meaningful analysis
        metrics_text = "\n".join(financial_metrics)
        prompt = f"""
        As a financial analyst, write an engaging and informative story about a company's financial performance 
        based on the following income statement data. Make the narrative flow naturally and include insights 
        about the company's financial health and operational efficiency.
        
        Available financial metrics (in millions of dollars):
        {metrics_text}
        
        Your analysis should cover:
        1. Revenue performance and its implications
        2. Cost structure and operational efficiency 
        3. Profitability metrics and what they indicate
        4. Overall financial health assessment
        5. Potential areas of concern or strength
        
        Write in a professional but accessible style that a business executive would appreciate.
        Keep the story between 250-350 words.
        """
        
        model = "llama3.3:latest"  # Use the more advanced model for better narrative
    else:
        # Limited data scenario - focus on general financial principles
        available = ", ".join(key.replace('_', ' ') for key, value in data.items() if value != "Unknown")
        prompt = f"""
        Write a brief educational story about financial statements and their importance in business analysis.
        
        Focus on these elements that were identified in the document:
        {available}
        
        Explain why these metrics matter to investors and business leaders, and how they can be used
        to assess a company's performance. Keep the content informative and engaging.
        
        Write approximately 200-250 words in a professional but accessible style.
        """
        
        model = "llama3.3"  # Use llama3.3 instead of mistral
    
    # Get the narrative from the AI model
    story = query_model(prompt, model=model)
    
    # Clean up the response
    story = story.strip()
    
    # Add a disclaimer if we had limited data
    if len(financial_metrics) < 3:
        story += "\n\n*Note: This analysis is based on limited financial data extracted from the document. For a more comprehensive analysis, please ensure the document contains detailed income statement information.*"
    
    return story