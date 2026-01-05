
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

load_dotenv()

def test_mistral():
    print("Testing Mistral...")
    key = os.getenv("MISTRAL_API_KEY")
    if not key:
        print("MISTRAL_API_KEY not found")
        return
    
    llm = ChatOpenAI(
        api_key=key,
        base_url="https://api.mistral.ai/v1",
        model="mistral-large-latest",
        temperature=0.1
    )
    try:
        res = llm.invoke([HumanMessage(content="Hello")])
        print(f"Mistral Success: {res.content}")
    except Exception as e:
        print(f"Mistral Failed: {e}")

def test_deepseek():
    print("Testing DeepSeek...")
    key = os.getenv("DEEPSEEK_API_KEY")
    if not key:
        print("DEEPSEEK_API_KEY not found")
        return

    llm = ChatOpenAI(
        api_key=key,
        base_url="https://api.deepseek.com",
        model="deepseek-chat",
        temperature=0.7
    )
    try:
        res = llm.invoke([HumanMessage(content="Hello")])
        print(f"DeepSeek Success: {res.content}")
    except Exception as e:
        print(f"DeepSeek Failed: {e}")

if __name__ == "__main__":
    test_mistral()
    test_deepseek()
