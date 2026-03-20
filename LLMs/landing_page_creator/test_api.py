import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("QUBRID_API_KEY")

# Initialize the OpenAI client with Qubrid base URL
client = OpenAI(
    base_url="https://platform.qubrid.com/v1",
    api_key=api_key,
)

print("Sending request using OpenAI SDK...")
try:
    stream = client.chat.completions.create(
        model="moonshotai/Kimi-K2.5",
        messages=[
          {
            "role": "user",
            "content": [
              {
                "type": "text",
                "text": "What is in this image? Describe the main elements."
              },
              {
                "type": "image_url",
                "image_url": {
                  "url": "https://cdn.britannica.com/61/93061-050-99147DCE/Statue-of-Liberty-Island-New-York-Bay.jpg"
                }
              }
            ]
          }
        ],
        max_tokens=16384,
        temperature=1,
        top_p=0.95,
        stream=True
    )

    print("Response:")
    for chunk in stream:
        if chunk.choices and chunk.choices[0].delta.content:
            print(chunk.choices[0].delta.content, end="", flush=True)
    print("\nSuccess!")
except Exception as e:
    print(f"\nError: {e}")