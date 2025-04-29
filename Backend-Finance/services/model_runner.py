import os
import requests
import openai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def query_model(prompt: str, model: str = "mistral") -> str:
    # Get environment type, defaulting to cloud in production
    env_type = os.environ.get("ENVIRONMENT", "cloud")
    
    if env_type == "local":
        # Use local Ollama (for development only)
        url = "http://localhost:11434/api/generate"
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False
        }
        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()
            return response.json().get("response", "").strip()
        except requests.RequestException as e:
            return f"Error querying model: {e}"
    else:
        # Use OpenAI API for cloud deployment
        openai_api_key = os.environ.get("OPENAI_API_KEY")
        if not openai_api_key:
            return "Error: OPENAI_API_KEY environment variable not set"
        
        client = openai.OpenAI(api_key=openai_api_key)
        
        # Map local model names to OpenAI models
        model_mapping = {
            "mistral": "gpt-3.5-turbo",
            "llama3": "gpt-4",
            # Add more mappings as needed
        }
        
        openai_model = model_mapping.get(model, "gpt-3.5-turbo")
        
        try:
            response = client.chat.completions.create(
                model=openai_model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=500
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"Error querying OpenAI: {e}"