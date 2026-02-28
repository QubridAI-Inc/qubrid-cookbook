import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

class Settings:
    BASE_DIR  = Path(__file__).resolve().parent.parent
    INPUT_DIR = BASE_DIR / "data" / "inputs"
    DB_PATH   = BASE_DIR / "data" / "history.db"

    API_KEY      = os.getenv("QUBRID_API_KEY")

    WHISPER_URL   = os.getenv("WHISPER_API_URL", "https://platform.qubrid.com/api/v1/qubridai/audio/transcribe")
    WHISPER_MODEL = os.getenv("WHISPER_MODEL", "openai/whisper-large-v3")

    LLM_BASE_URL = os.getenv("LLM_BASE_URL", "https://platform.qubrid.com/v1")
    LLM_MODEL    = os.getenv("LLM_MODEL", "openai/gpt-oss-120b")

    def setup_directories(self):
        self.INPUT_DIR.mkdir(parents=True, exist_ok=True)
        self.DB_PATH.parent.mkdir(parents=True, exist_ok=True)

config = Settings()
