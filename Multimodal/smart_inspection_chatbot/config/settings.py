import os  # Standard library to access operating system environment variables
from dotenv import load_dotenv  # Library to load variables from a .env file into the environment

# Load environment variables from the .env file immediately when this module is imported.
# This ensures that os.getenv() can find your keys.
load_dotenv()

class Settings:
    """
    Centralized configuration class.
    Acts as a 'Single Source of Truth' for all application settings.
    """
    
    # 1. API Key
    # Fetches the secret key from the environment. Returns None if not found.
    API_KEY = os.getenv("QUBRID_API_KEY")
    
    # 2. API Endpoint
    # Fetches the URL from .env, but provides a default fallback if it's missing.
    # This URL is the specific endpoint for Qubrid's Multimodal Chat.
    API_URL = os.getenv("QUBRID_API_URL", "https://platform.qubrid.com/api/v1/qubridai/multimodal/chat")
    
    # 3. Model ID
    # Defines exactly which AI brain to use.
    # We hardcode this here to ensure we always use the specific Qwen3-VL version tested.
    MODEL_NAME = "Qwen/Qwen3-VL-30B-A3B-Instruct" 

# Instantiate the settings class.
# Other files will import this specific instance 'settings', not the class itself.
settings = Settings()