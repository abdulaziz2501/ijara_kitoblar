"""
Loyiha konfiguratsiyasi
Bu faylda botning asosiy sozlamalari joylashgan
"""
import os
from dotenv import load_dotenv

# .env fayldan ma'lumotlarni yuklash
load_dotenv()

# ========================================
# TELEGRAM BOT SOZLAMALARI
# ========================================

# Bot token - @BotFather dan olinadi
BOT_TOKEN = os.getenv('BOT_TOKEN')

# Super Admin - Bu birinchi admin bo'lib, boshqa adminlarni qo'sha oladi
# Faqat bitta super admin bo'lishi mumkin
SUPER_ADMIN_ID = os.getenv('SUPER_ADMIN_ID')  # Telegram ID

# ========================================
# DATABASE SOZLAMALARI (PostgreSQL)
# ========================================

# Database type (sqlite yoki postgresql)
DB_TYPE = os.getenv('DB_TYPE', 'postgresql')  # Default: postgresql

# PostgreSQL sozlamalari
POSTGRES_HOST = os.getenv('POSTGRES_HOST', 'localhost')
POSTGRES_PORT = os.getenv('POSTGRES_PORT', '5432')
POSTGRES_DB = os.getenv('POSTGRES_DB', 'library')
POSTGRES_USER = os.getenv('POSTGRES_USER', 'postgres')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD', '')

DATABASE_URL = f'postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}'
# SQLite sozlamalari (fallback)
# SQLITE_DB = os.getenv('SQLITE_DB', 'library.db')
#
# # Database URL yaratish
# if DB_TYPE == 'postgresql':
#     DATABASE_URL = f'postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}'
# else:
#     DATABASE_URL = f'sqlite:///{SQLITE_DB}'

# Database path (SQLite uchun)
# DATABASE_PATH = SQLITE_DB

# ========================================
# TARIF REJALARI
# ========================================

SUBSCRIPTION_PLANS = {
    'Free': {
        'price': 0,
        'duration_days': 0,  # Cheksiz
        'features': [
            'Asosiy xizmatlar',
            'Cheklangan kitoblar',
            'Oddiy qo\'llab-quvvatlash'
        ]
    },
    'Money': {
        'price': 50000,  # 50,000 so'm
        'duration_days': 30,
        'features': [
            'Barcha kitoblar',
            'Kitoblarni yuklab olish',
            '24/7 qo\'llab-quvvatlash',
            'Prioritet xizmat'
        ]
    },
    'Premium': {
        'price': 100000,  # 100,000 so'm
        'duration_days': 30,
        'features': [
            'Barcha kitoblar',
            'Audio kitoblar',
            'Video darsliklar',
            'VIP qo\'llab-quvvatlash',
            'Shaxsiy konsultatsiya',
            'Chegirmalar'
        ]
    }
}

# ========================================
# BILDIRISHNOMA SOZLAMALARI
# ========================================

# Obuna muddati tugashidan necha kun oldin ogohlantirish
WARNING_DAYS = 3

# Bildirishnomalarni tekshirish oralig'i (soatlarda)
CHECK_INTERVAL_HOURS = 6

# ========================================
# LIBRARY ID SOZLAMALARI
# ========================================

# Library ID formati
LIBRARY_ID_PREFIX = "ID"  # ID0001, ID0002...
LIBRARY_ID_LENGTH = 4     # 0001, 0002... (4 xonali)

# ========================================
# LOGGING SOZLAMALARI
# ========================================

LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

# ========================================
# ADMIN PANEL SOZLAMALARI
# ========================================

# Bir sahifada ko'rsatiladigan foydalanuvchilar soni
USERS_PER_PAGE = 20

# ========================================
# XAVFSIZLIK SOZLAMALARI
# ========================================

# Telegram ID ni majburiy qilish (False bo'lsa, telegram_id bo'lmasligi mumkin)
REQUIRE_TELEGRAM_ID = False

# Ro'yxatdan o'tishda telefon raqamini majburiy qilish
REQUIRE_PHONE_VERIFICATION = True

# ========================================
# CONNECTION POOL SOZLAMALARI (PostgreSQL)
# ========================================

# Connection pool parametrlari
POOL_SIZE = 10  # Maksimal connection'lar soni
MAX_OVERFLOW = 20  # Qo'shimcha connection'lar
POOL_TIMEOUT = 30  # Timeout (soniyalarda)
POOL_RECYCLE = 3600  # Connection'ni qayta ishlatish vaqti (1 soat)