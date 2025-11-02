#!/usr/bin/env python3
"""
PostgreSQL Database Setup Script
PostgreSQL database yaratish va sozlash uchun
"""
import sys
import os
import psycopg2
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Loyiha root directory ni PATH ga qo'shish
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ijara_kitoblar.config import POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD
from database.models import Base
from sqlalchemy import create_engine


def check_postgres_connection():
    """PostgreSQL server ishlayotganligini tekshirish"""
    try:
        conn = psycopg2.connect(
            host=POSTGRES_HOST,
            port=POSTGRES_PORT,
            user=POSTGRES_USER,
            password=POSTGRES_PASSWORD,
            database='postgres'  # Default database
        )
        conn.close()
        return True, None
    except Exception as e:
        return False, str(e)


def create_database():
    """Database yaratish"""
    try:
        # Postgres default database ga ulanish
        conn = psycopg2.connect(
            host=POSTGRES_HOST,
            port=POSTGRES_PORT,
            user=POSTGRES_USER,
            password=POSTGRES_PASSWORD,
            database='postgres'
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()

        # Database mavjudligini tekshirish
        cursor.execute(
            "SELECT 1 FROM pg_database WHERE datname = %s",
            (POSTGRES_DB,)
        )
        exists = cursor.fetchone()

        if exists:
            print(f"ℹ️  Database '{POSTGRES_DB}' allaqachon mavjud")
        else:
            # Database yaratish
            cursor.execute(
                sql.SQL("CREATE DATABASE {}").format(
                    sql.Identifier(POSTGRES_DB)
                )
            )
            print(f"✅ Database '{POSTGRES_DB}' yaratildi")

        cursor.close()
        conn.close()
        return True, None

    except Exception as e:
        return False, str(e)


def create_tables():
    """Jadvallarni yaratish (SQLAlchemy orqali)"""
    try:
        from ijara_kitoblar.config import DATABASE_URL

        engine = create_engine(DATABASE_URL, echo=False)
        Base.metadata.create_all(engine)
        engine.dispose()

        print("✅ Barcha jadvallar yaratildi")
        return True, None

    except Exception as e:
        return False, str(e)


def show_connection_info():
    """Connection ma'lumotlarini ko'rsatish"""
    print("\n" + "=" * 60)
    print("📊 POSTGRESQL CONNECTION INFO")
    print("=" * 60)
    print(f"Host:     {POSTGRES_HOST}")
    print(f"Port:     {POSTGRES_PORT}")
    print(f"Database: {POSTGRES_DB}")
    print(f"User:     {POSTGRES_USER}")
    print(f"Password: {'*' * len(POSTGRES_PASSWORD) if POSTGRES_PASSWORD else 'NOT SET'}")
    print("=" * 60)


def main():
    """Asosiy funksiya"""
    print("=" * 60)
    print("🐘 POSTGRESQL DATABASE SETUP")
    print("=" * 60)
    print()

    # Connection ma'lumotlarini ko'rsatish
    show_connection_info()
    print()

    # 1. PostgreSQL connection tekshirish
    print("1️⃣ PostgreSQL server ni tekshirish...")
    success, error = check_postgres_connection()

    if not success:
        print(f"❌ PostgreSQL serverga ulanib bo'lmadi!")
        print(f"   Xato: {error}")
        print()
        print("💡 Yechimlar:")
        print("   1. PostgreSQL server ishga tushirilganligini tekshiring")
        print("   2. .env fayldagi sozlamalarni tekshiring")
        print("   3. PostgreSQL serverni ishga tushiring:")
        print("      - Linux: sudo systemctl start postgresql")
        print("      - Mac: brew services start postgresql")
        print("      - Windows: pg_ctl start")
        print()
        return False

    print("   ✅ PostgreSQL server ishlayapti")
    print()

    # 2. Database yaratish
    print("2️⃣ Database yaratish...")
    success, error = create_database()

    if not success:
        print(f"   ❌ Database yaratishda xato: {error}")
        return False

    print()

    # 3. Jadvallarni yaratish
    print("3️⃣ Jadvallarni yaratish...")
    success, error = create_tables()

    if not success:
        print(f"   ❌ Jadval yaratishda xato: {error}")
        return False

    print()
    print("=" * 60)
    print("✅ POSTGRESQL MUVAFFAQIYATLI SOZLANDI!")
    print("=" * 60)
    print()
    print("📝 Keyingi qadamlar:")
    print("   1. Botni ishga tushiring: python bot/main.py")
    print("   2. Dashboard ishga tushiring: ./run_dashboard.sh")
    print()
    print("🔍 Database ma'lumotlarini ko'rish:")
    print(f"   psql -h {POSTGRES_HOST} -p {POSTGRES_PORT} -U {POSTGRES_USER} -d {POSTGRES_DB}")
    print()

    return True


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⏹️  Setup bekor qilindi")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Kutilmagan xato: {e}")
        sys.exit(1)