# Logic to turn JSON into a story
from services.model_runner import query_model

def generate_story_from_json(data):
    prompt = f"""
    Write a detailed story about the financial performance of a company
    based on the following income statement JSON. The story should include insights about revenue, cost of revenue, gross profit, operating expenses, and net income. 
    Use a narrative style that is engaging and informative.

    {data}
    """
    return query_model(prompt, model="llama3.3")
