"""Configuration management for NutriVision AI"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Application configuration"""
    
    # API Configuration
    API_KEY = os.getenv("QUBRID_API_KEY")
    MODEL_NAME = os.getenv("QUBRID_MODEL")
    API_ENDPOINT = os.getenv("QUBRID_API_ENDPOINT")
    
    # App Configuration
    PAGE_TITLE = "NutriVision AI - Food Nutrition Analyzer"
    PAGE_ICON = "🍽️"
    
    # API Settings
    MAX_TOKENS = 4096
    TEMPERATURE = 0.7
    TOP_P = 0.9
    PRESENCE_PENALTY = 0
    TIMEOUT = 60
    
    @staticmethod
    def validate():
        """Validate required configuration"""
        if not Config.API_KEY:
            raise ValueError("QUBRID_API_KEY not found in .env file")
        if not Config.MODEL_NAME:
            raise ValueError("QUBRID_MODEL not found in .env file")
        if not Config.API_ENDPOINT:
            raise ValueError("QUBRID_API_ENDPOINT not found in .env file")
