import os
from dotenv import load_dotenv

load_dotenv()

# Telegram Bot
BOT_TOKEN = os.getenv('BOT_TOKEN')
ADMIN_IDS = os.getenv('ADMIN_IDS')  # Kutubxonachi ID

# Tarif narxlari
SUBSCRIPTION_PLANS = {
    'Free': {
        'price': 0,
        'duration_days': 0,  # Cheksiz
        'features': ['Asosiy xizmatlar']
    },
    'Money': {
        'price': 1000,
        'duration_days': 30,
        'features': ['Barcha kitoblar', '24/7 qo\'llab-quvvatlash']
    },
    'Premium': {
        'price': 2000,
        'duration_days': 30,
        'features': ['Barcha kitoblar', 'Audio kitoblar', 'VIP qo\'llab-quvvatlash']
    }
}

# Database
DATABASE_URL = 'sqlite:///library.db'

# Bildirishnoma
WARNING_DAYS = 3