import os
from dotenv import load_dotenv

# Load .env from project root
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(BASE_DIR, ".env"))

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")
BASE_CURRENCY = os.getenv("BASE_CURRENCY", "MYR")
APP_NAME = os.getenv("APP_NAME", "Finance Budget")

def is_telegram_configured():
    return bool(TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID)