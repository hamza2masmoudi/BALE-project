
import os
import requests
from dotenv import load_dotenv
load_dotenv()
def test_connection():
endpoint = os.getenv("LOCAL_LLM_ENDPOINT", "http://localhost:8000/v1/chat/completions")
model = os.getenv("LOCAL_LLM_MODEL", "qwen2.5-32b-instruct")
print(f"Testing Connection to: {endpoint} (Model: {model})")
payload = {
"model": model,
"messages": [{"role": "user", "content": "Hello! Are you online?"}],
"temperature": 0.1,
"max_tokens": 50
}
try:
response = requests.post(endpoint, json=payload, timeout=60)
response.raise_for_status()
print(" SUCCESS: Connection Established")
print("Response:", response.json()["choices"][0]["message"]["content"])
except requests.exceptions.ConnectionError:
print(" FAIL: Connection Refused. Is the server running?")
except Exception as e:
print(f" FAIL: Error {e}")
if __name__ == "__main__":
test_connection()
