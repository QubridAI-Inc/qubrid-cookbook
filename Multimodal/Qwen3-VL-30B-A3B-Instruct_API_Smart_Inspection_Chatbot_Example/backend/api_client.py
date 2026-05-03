import requests  # Standard library for making HTTP requests (GET, POST)
import json  # Used for parsing JSON responses from the API
import re  # Regular expressions (not strictly used here but good for text parsing)
import time  # Used to track how long the API call takes (Latency)
from config.settings import settings  # Import API keys and URLs from the settings file
from backend.schemas import ChatResponse, UsageMetrics  # Import the strict data models
from backend.utils import encode_image_to_base64  # Helper to convert image bytes to string

def chat_with_industrial_ai(
    current_question: str, 
    image_file, 
    chat_history: list, 
    system_prompt: str
) -> ChatResponse:
    """
    Sends the user's question + image + history to the AI API and returns the answer.
    Also calculates performance metrics like Latency and Tokens/Sec.
    """
    
    # 1. Start the stopwatch to measure Latency
    start_time = time.time()  # <--- Start Timer

    # 2. Prepare the Request Headers
    # This tells the server who we are (API Key) and what we are sending (JSON)
    headers = {
        "Authorization": f"Bearer {settings.API_KEY}",
        "Content-Type": "application/json"
    }

    # 3. Build the Conversation History
    # Start with the "System Prompt" (The Guardrails & Identity)
    messages = [{"role": "system", "content": system_prompt}]
    
    # Append all previous messages so the AI remembers the conversation context
    for msg in chat_history:
        messages.append({"role": msg["role"], "content": msg["content"]})

    # 4. Add the User's Current Input (Text + Image)
    # The 'user' message is a list that can contain both text and image parts
    user_content = [{"type": "text", "text": current_question}]
    
    # If an image file was provided, encode it to Base64 and add it
    if image_file:
        base64_img = encode_image_to_base64(image_file)
        user_content.append({
            "type": "image_url", 
            "image_url": {"url": f"data:image/jpeg;base64,{base64_img}"}
        })

    # Append this combined user message to the list
    messages.append({"role": "user", "content": user_content})

    # 5. Construct the API Payload
    # This dictionary matches the standard OpenAI/Qubrid API format
    payload = {
        "model": settings.MODEL_NAME, # Which AI brain to use (e.g., Qwen-VL-Max)
        "messages": messages,         # The full conversation thread
        "max_tokens": 2048,           # Limit the response length
        "temperature": 0.6,           # Creativity setting (0.6 is balanced)
        "stream": False               # Wait for the full answer (no streaming)
    }

    try:
        # 6. Send the POST Request
        # This is where the code waits for the server to reply
        response = requests.post(settings.API_URL, headers=headers, json=payload)
        
        # 7. Stop the stopwatch
        # Calculate how many seconds passed since step 1
        end_time = time.time()
        latency = round(end_time - start_time, 2)
        # -------------------------------

        # 8. Check for Errors
        # If the server returned 400, 401, 500, etc., raise an error
        if response.status_code != 200:
            raise RuntimeError(f"API Error: {response.text}")

        # 9. Parse the JSON Response
        data = response.json()
        
        # Extract the AI's text answer. 
        # Handles different API response formats (some nest it under 'choices', some under 'content')
        if 'choices' in data:
            content = data['choices'][0]['message']['content']
        elif 'content' in data:
            content = data['content']
        else:
            content = "Error: No content returned."

        # 10. Extract Token Usage Stats
        # Defaults to 0 if the API doesn't send usage data
        raw_usage = data.get("usage", {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0})
        total_tokens = raw_usage.get('total_tokens', 0)
        
        # 11. Calculate Throughput (Speed)
        # Tokens per Second = Total Tokens / Time Taken
        # We add a check (latency > 0) to avoid "Division by Zero" errors
        tps = round(total_tokens / latency, 2) if latency > 0 else 0

        # 12. Package the Metrics
        # Store all the stats in the Pydantic model defined in schemas.py
        metrics = UsageMetrics(
            prompt_tokens=raw_usage.get('prompt_tokens', 0),
            completion_tokens=raw_usage.get('completion_tokens', 0),
            total_tokens=total_tokens,
            latency=latency,
            throughput=tps
        )

        # 13. Return the Final Result
        # Returns a clean object containing the text answer and the metrics
        return ChatResponse(content=content, usage=metrics)

    except Exception as e:
        # If anything goes wrong (network fail, bad JSON), crash gracefully with a message
        raise RuntimeError(f"Connection failed: {str(e)}")