import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')  # Исправлено: добавлено имя переменной
DATABASE_PATH = 'bot.db'
MAX_GENERATION_PER_MINUTE = 10
ADMIN_IDS = []

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN not found! Check .env file")

print(f"Configuration loaded. Token: {BOT_TOKEN[:10]}...")