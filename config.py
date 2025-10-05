import os
from dotenv import load_dotenv

load_dotenv()

# Telegram Bot
BOT_TOKEN = os.getenv('BOT_TOKEN')
ADMIN_ID = os.getenv('ADMIN_ID')  # Kutubxonachi ID

# Tarif narxlari
SUBSCRIPTION_PLANS = {
    'Free': {'price': 0, 'duration_days': 0},
    'Money': {'price': 1000, 'duration_days': 30},
    'Premium': {'price': 2000, 'duration_days': 30}
}

# Database
DATABASE_URL = 'sqlite:///library.db'

# Bildirishnoma
WARNING_DAYS = 3