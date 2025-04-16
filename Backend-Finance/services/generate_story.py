# Logic to turn JSON into a story
from services.model_runner import query_model

def generate_story_from_json(data):
    prompt = f"""
    Write a short and engaging story (approx. 150 words) about the financial performance of a company
    based on the following income statement JSON:

    {data}
    """
    return query_model(prompt, model="llama3")
