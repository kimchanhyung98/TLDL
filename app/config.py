import os
from pathlib import Path

from dotenv import load_dotenv

dotenv_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=dotenv_path)

WHISPER_MODEL = os.getenv("WHISPER_MODEL", "whisper-1")
SUMMARY_MODEL = os.getenv("SUMMARY_MODEL", "o1")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
