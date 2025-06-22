import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get API key
api_key = os.getenv('GEMINI_API_KEY')
print(f"API Key found: {'Yes' if api_key else 'No'}")

# Configure the API
genai.configure(api_key=api_key)

# List available models
print("\nAvailable Models:")
for m in genai.list_models():
    print(f"- {m.name}")

# Test the API with gemini-2.0-flash
try:
    model = genai.GenerativeModel('gemini-2.0-flash')
    response = model.generate_content("What is the capital of France?")
    print("\nAPI Test Response:")
    print(response.text)
except Exception as e:
    print("\nError testing API:")
    print(str(e)) 