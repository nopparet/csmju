import os
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_USER = os.getenv("DB_USER", "kiosk")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "cs_kiosk")

DATABASE_URL = (
    f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"
)

CHECKIN_EARLY_MIN = int(os.getenv("CHECKIN_EARLY_MIN", "15"))
CHECKIN_LATE_MIN = int(os.getenv("CHECKIN_LATE_MIN", "30"))
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
