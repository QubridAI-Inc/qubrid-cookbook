import os
from dotenv import load_dotenv

load_dotenv()

# API Keys
API_KEY = os.getenv("QUBRID_API_KEY")

# Exact Qubrid Image Generation Endpoint
GENERATION_URL = "https://platform.qubrid.com/api/v1/qubridai/image/generation"

# Model ID (Default to the one in your snippet)
MODEL_ID = "stabilityai/stable-diffusion-3.5-large"

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "assets.db")

# Directory to save generated images
GENERATED_IMAGES_DIR = os.path.join(BASE_DIR, "data", "generated")
os.makedirs(GENERATED_IMAGES_DIR, exist_ok=True)