import openai
import os

# Optional: load environment variables from a .env file
from dotenv import load_dotenv
load_dotenv()

# Get your OpenAI API key from environment variables
openai.api_key = os.getenv("OPENAI_API_KEY")

# Run a simple test to verify the API key works
try:
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful car diagnostic assistant."},
            {"role": "user", "content": "Explain OBD2 code P0300 in simple terms."}
        ]
    )

    print("API connection successful! Response:")
    print(response['choices'][0]['message']['content'])

except Exception as e:
    print("API connection failed.")
    print("Error:", e)
