#!/usr/bin/env python3
"""
Database Initialization Script
Database ni yaratish va dastlabki sozlash uchun
"""
import sys
import os

# Loyiha root directory ni PATH ga qo'shish
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.db_manager import DatabaseManager
from database.admin_manager import AdminManager


def init_database():
    """Database ni yaratish va sozlash"""
    print("=" * 50)
    print("📊 DATABASE INITIALIZATION")
    print("=" * 50)
    
    try:
        # 1. User database yaratish
        print("\n1️⃣ Users database yaratilmoqda...")
        db = DatabaseManager()
        print("   ✅ Users jadval yaratildi!")
        db.close()
        
        # 2. Admin database yaratish
        print("\n2️⃣ Admins database yaratilmoqda...")
        admin_manager = AdminManager()
        print("   ✅ Admins jadval yaratildi!")
        admin_manager.close()
        
        print("\n" + "=" * 50)
        print("✅ DATABASE MUVAFFAQIYATLI YARATILDI!")
        print("=" * 50)
        print("\n📝 Keyingi qadamlar:")
        print("1. .env faylni to'ldiring")
        print("2. Bot ni ishga tushiring: python bot/main.py")
        print("\n")
        
        return True
    
    except Exception as e:
        print(f"\n❌ XATO: {e}")
        return False


def check_database():
    """Database mavjudligini tekshirish"""
    if os.path.exists('../library.db'):
        print("\n⚠️  DIQQAT: library.db allaqachon mavjud!")
        response = input("Qaytadan yaratishni xohlaysizmi? (y/n): ")
        
        if response.lower() == 'y':
            os.remove('../library.db')
            print("✅ Eski database o'chirildi")
            return True
        else:
            print("❌ Bekor qilindi")
            return False
    return True


def show_info():
    """Database haqida ma'lumot"""
    print("\n" + "=" * 50)
    print("📋 DATABASE MA'LUMOTLARI")
    print("=" * 50)
    
    if os.path.exists('../library.db'):
        size = os.path.getsize('../library.db')
        print(f"\n📁 Fayl: library.db")
        print(f"📊 Hajm: {size} bytes")
        
        # Statistika
        try:
            db = DatabaseManager()
            stats = db.get_statistics()
            db.close()
            
            print(f"\n👥 Foydalanuvchilar: {stats['total_users']}")
            print(f"   🟢 Free: {stats['free_users']}")
            print(f"   🔵 Money: {stats['money_users']}")
            print(f"   🟣 Premium: {stats['premium_users']}")
            
            admin_manager = AdminManager()
            admin_stats = admin_manager.get_admin_count()
            admin_manager.close()
            
            print(f"\n👨‍💼 Adminlar: {admin_stats['total']}")
            print(f"   ⭐ Super Admin: {admin_stats['super_admin']}")
            print(f"   👤 Oddiy Admin: {admin_stats['regular']}")
        
        except Exception as e:
            print(f"\n⚠️  Statistika olishda xato: {e}")
    else:
        print("\n❌ Database mavjud emas!")
        print("💡 Yaratish uchun: python init_database.py")


def main():
    """Asosiy funksiya"""
    if len(sys.argv) > 1:
        if sys.argv[1] == '--info':
            show_info()
            return
        elif sys.argv[1] == '--help':
            print("\n📖 ISHLATISH:")
            print("  python init_database.py        - Database yaratish")
            print("  python init_database.py --info - Ma'lumot ko'rish")
            print("  python init_database.py --help - Yordam")
            print()
            return
    
    # Database yaratish
    if check_database():
        init_database()


if __name__ == "__main__":
    main()
