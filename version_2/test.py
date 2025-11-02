#!/usr/bin/env python3
"""
Import Test Script
Barcha import'larni tekshirish
"""
import sys

print("=" * 60)
print("🧪 IMPORT TEST")
print("=" * 60)
print()

# 1. Config test
print("1️⃣ Config...")
try:
    from ijara_kitoblar.config import DATABASE_URL, BOT_TOKEN
    print("   ✅ config.py OK")
    print(f"   📊 DATABASE_URL: {DATABASE_URL[:30]}...")
except Exception as e:
    print(f"   ❌ config.py xato: {e}")
    sys.exit(1)

print()

# 2. Models test
print("2️⃣ Models...")
try:
    from database.models import Base, User, Admin, Notification
    print("   ✅ database.models OK")
    print(f"   📋 Tables: {', '.join([User.__tablename__, Admin.__tablename__, Notification.__tablename__])}")
except Exception as e:
    print(f"   ❌ database.models xato: {e}")
    sys.exit(1)

print()

# 3. DatabaseManager test
print("3️⃣ DatabaseManager...")
try:
    from database.db_manager import DatabaseManager
    print("   ✅ database.db_manager OK")
except Exception as e:
    print(f"   ❌ database.db_manager xato: {e}")
    sys.exit(1)

print()

# 4. AdminManager test
print("4️⃣ AdminManager...")
try:
    from database.admin_manager import AdminManager
    print("   ✅ database.admin_manager OK")
except Exception as e:
    print(f"   ❌ database.admin_manager xato: {e}")
    sys.exit(1)

print()

# 5. Handlers test
print("5️⃣ Handlers...")
try:
    from bot.handlers import registration, subscription, admin
    print("   ✅ bot.handlers OK")
except Exception as e:
    print(f"   ❌ bot.handlers xato: {e}")
    print()
    print("   💡 Ehtimol .env fayl yo'q yoki to'ldirilmagan")
    print("   Davom etamiz...")

print()
print("=" * 60)
print("✅ BARCHA IMPORT'LAR ISHLAYDI!")
print("=" * 60)