# Code to run LLM locally (Ollama or llama.cpp)
import subprocess

def query_model(prompt: str, model: str = "mistral") -> str:
    try:
        result = subprocess.run(
            ["ollama", "run", model],
            input=prompt.encode("utf-8"),
            capture_output=True,
            timeout=60
        )
        return result.stdout.decode("utf-8").strip()
    except subprocess.TimeoutExpired:
        return "Model query timed out."
