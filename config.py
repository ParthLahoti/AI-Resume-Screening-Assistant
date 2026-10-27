from pathlib import Path
import os
from dotenv import load_dotenv

ENV_PATH = Path(__file__).resolve().parent / ".env"

def get_gemini_api_key() -> str:
    load_dotenv(dotenv_path=ENV_PATH, override=True)
    return os.getenv("GEMINI_API_KEY", "").strip()

def get_gemini_model() -> str:
    load_dotenv(dotenv_path=ENV_PATH, override=True)
    return os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite").strip()

# Gemini configuration
GEMINI_API_KEY: str = get_gemini_api_key()
GEMINI_MODEL: str = get_gemini_model()

# Input constraints (in characters)
MAX_INPUT_LENGTH: int = 15000

# API Call settings
REQUEST_TIMEOUT_SECONDS: float = 60.0
MODEL_TEMPERATURE: float = 0.2
