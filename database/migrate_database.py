#!/usr/bin/env python3
"""
Database Migration Script
-------------------------
Mavjud database'ga study_place ustunini qo'shish
"""

import sqlite3
import sys
from pathlib import Path


def migrate_database(db_path: str = "library.db"):
    """Database'ni yangilash"""
    
    print("🔧 Database migration boshlandi...")
    print(f"📁 Database fayl: {db_path}")
    
    # Database mavjudligini tekshirish
    if not Path(db_path).exists():
        print(f"❌ Database fayli topilmadi: {db_path}")
        print("💡 Agar bot hali ishga tushmagan bo'lsa, avval uni ishga tushiring")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 1. study_place ustunini qo'shish
        print("\n1️⃣ study_place ustunini qo'shish...")
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN study_place TEXT DEFAULT 'Kiritilmagan'")
            conn.commit()
            print("   ✅ study_place ustuni muvaffaqiyatli qo'shildi")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e).lower():
                print("   ℹ️ study_place ustuni allaqachon mavjud")
            else:
                raise
        
        # 2. Mavjud foydalanuvchilar uchun standart qiymat
        print("\n2️⃣ Mavjud foydalanuvchilar uchun standart qiymat...")
        cursor.execute("SELECT COUNT(*) FROM users WHERE study_place IS NULL OR study_place = ''")
        empty_count = cursor.fetchone()[0]
        
        if empty_count > 0:
            cursor.execute("UPDATE users SET study_place = 'Kiritilmagan' WHERE study_place IS NULL OR study_place = ''")
            conn.commit()
            print(f"   ✅ {empty_count} ta foydalanuvchi uchun standart qiymat o'rnatildi")
        else:
            print("   ℹ️ Barcha foydalanuvchilarda study_place to'ldirilgan")
        
        # 3. Database statistikasi
        print("\n📊 Database statistikasi:")
        cursor.execute("SELECT COUNT(*) FROM users")
        total_users = cursor.fetchone()[0]
        print(f"   👥 Jami foydalanuvchilar: {total_users}")
        
        cursor.execute("SELECT COUNT(*) FROM users WHERE study_place != 'Kiritilmagan'")
        filled_count = cursor.fetchone()[0]
        print(f"   ✏️ O'quv joyi to'ldirilgan: {filled_count}")
        
        cursor.execute("SELECT COUNT(*) FROM users WHERE subscription_plan = 'Free'")
        free_users = cursor.fetchone()[0]
        print(f"   🟢 Free foydalanuvchilar: {free_users}")
        
        cursor.execute("SELECT COUNT(*) FROM users WHERE subscription_plan IN ('Money', 'Premium')")
        paid_users = cursor.fetchone()[0]
        print(f"   💎 Pullik foydalanuvchilar: {paid_users}")
        
        conn.close()
        
        print("\n✅ Migration muvaffaqiyatli yakunlandi!")
        print("🚀 Endi botni ishga tushirishingiz mumkin")
        return True
        
    except Exception as e:
        print(f"\n❌ Xatolik yuz berdi: {e}")
        print(f"📝 Xatolik turi: {type(e).__name__}")
        return False


def check_database_structure(db_path: str = "library.db"):
    """Database strukturasini tekshirish"""
    
    print("\n🔍 Database strukturasini tekshirish...")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Ustunlarni olish
        cursor.execute("PRAGMA table_info(users)")
        columns = cursor.fetchall()
        
        print("\n📋 Users jadvalidagi ustunlar:")
        for col in columns:
            col_id, name, type_, not_null, default, pk = col
            nullable = "NOT NULL" if not_null else "NULL"
            default_val = f"DEFAULT {default}" if default else ""
            print(f"   • {name} ({type_}) {nullable} {default_val}")
        
        # study_place borligini tekshirish
        has_study_place = any(col[1] == 'study_place' for col in columns)
        
        if has_study_place:
            print("\n✅ study_place ustuni mavjud")
        else:
            print("\n⚠️ study_place ustuni topilmadi")
            print("💡 Migration skriptini ishga tushiring")
        
        conn.close()
        return has_study_place
        
    except Exception as e:
        print(f"\n❌ Xatolik: {e}")
        return False


def main():
    """Asosiy funksiya"""
    
    print("=" * 60)
    print("📚 KUTUBXONA BOT - DATABASE MIGRATION")
    print("=" * 60)
    
    # Database yo'lini belgilash
    db_path = "../bot/library.db"
    
    # Argumentlarni tekshirish
    if len(sys.argv) > 1:
        if sys.argv[1] == "--check":
            check_database_structure(db_path)
            return
        else:
            db_path = sys.argv[1]
    
    # Migration bajarish
    success = migrate_database(db_path)
    
    if success:
        print("\n" + "=" * 60)
        print("🎉 Barcha o'zgarishlar muvaffaqiyatli amalga oshirildi!")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("❌ Migration amalga oshmadi")
        print("=" * 60)
        sys.exit(1)


if __name__ == "__main__":
    main()
