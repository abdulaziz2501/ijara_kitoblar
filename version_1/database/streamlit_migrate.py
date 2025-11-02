#!/usr/bin/env python3
"""
Streamlit Dashboard uchun Database Migration
----------------------------------------------
created_at ustunini qo'shish va tekshirish
"""

import sqlite3
import sys
from pathlib import Path
from datetime import datetime


def migrate_for_streamlit(db_path: str = "library.db"):
    """Streamlit dashboard uchun kerakli ustunlarni qo'shish"""

    print("🔧 Streamlit Dashboard Migration Boshlandi...")
    print(f"📁 Database: {db_path}\n")

    if not Path(db_path).exists():
        print(f"❌ Database topilmadi: {db_path}")
        print("💡 Avval botni ishga tushirib, database yarating")
        return False

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # 1. created_at ustunini qo'shish
        print("1️⃣ created_at ustunini tekshirish...")
        cursor.execute("PRAGMA table_info(users)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]

        if 'created_at' not in column_names:
            print("   ⏳ created_at ustunini qo'shish...")
            cursor.execute("""
                           ALTER TABLE users
                               ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                           """)
            conn.commit()
            print("   ✅ created_at ustuni qo'shildi")

            # Mavjud foydalanuvchilar uchun hozirgi vaqtni o'rnatish
            cursor.execute("""
                           UPDATE users
                           SET created_at = CURRENT_TIMESTAMP
                           WHERE created_at IS NULL
                           """)
            conn.commit()
            print("   ✅ Mavjud foydalanuvchilar uchun sana o'rnatildi")
        else:
            print("   ℹ️ created_at ustuni allaqachon mavjud")

        # 2. study_place ustunini tekshirish
        print("\n2️⃣ study_place ustunini tekshirish...")
        if 'study_place' not in column_names:
            print("   ⚠️ study_place ustuni topilmadi!")
            print("   💡 Avval asosiy migration skriptini ishga tushiring:")
            print("   python migrate_database.py")
        else:
            print("   ✅ study_place ustuni mavjud")

            # study_place bo'sh bo'lganlarni to'ldirish
            cursor.execute("""
                           SELECT COUNT(*)
                           FROM users
                           WHERE study_place IS NULL
                              OR study_place = ''
                           """)
            empty_count = cursor.fetchone()[0]

            if empty_count > 0:
                cursor.execute("""
                               UPDATE users
                               SET study_place = 'Kiritilmagan'
                               WHERE study_place IS NULL
                                  OR study_place = ''
                               """)
                conn.commit()
                print(f"   ✅ {empty_count} ta bo'sh maydon to'ldirildi")

        # 3. Statistika
        print("\n📊 Database Statistikasi:")

        cursor.execute("SELECT COUNT(*) FROM users")
        total = cursor.fetchone()[0]
        print(f"   👥 Jami foydalanuvchilar: {total}")

        cursor.execute("""
                       SELECT COUNT(*)
                       FROM users
                       WHERE created_at IS NOT NULL
                       """)
        with_date = cursor.fetchone()[0]
        print(f"   📅 Sana bilan: {with_date}")

        cursor.execute("""
                       SELECT COUNT(*)
                       FROM users
                       WHERE study_place IS NOT NULL
                         AND study_place != 'Kiritilmagan'
                       """)
        with_study = cursor.fetchone()[0]
        print(f"   🎓 O'quv joyi bilan: {with_study}")

        # 4. Test query
        print("\n🧪 Test Query:")
        cursor.execute("""
                       SELECT library_id, first_name, study_place, created_at
                       FROM users LIMIT 3
                       """)

        test_users = cursor.fetchall()
        if test_users:
            print("   ✅ Ma'lumotlar to'g'ri o'qilmoqda:")
            for user in test_users:
                lib_id, name, study, created = user
                print(f"      • {lib_id} - {name} - {study} - {created}")

        conn.close()

        print("\n✅ Migration muvaffaqiyatli yakunlandi!")
        print("🚀 Endi Streamlit Dashboard'ni ishga tushirishingiz mumkin:")
        print("   streamlit run streamlit_app.py")

        return True

    except Exception as e:
        print(f"\n❌ Xatolik: {e}")
        print(f"📝 Xatolik turi: {type(e).__name__}")
        return False


def test_streamlit_compatibility(db_path: str = "library.db"):
    """Streamlit bilan mos kelishini tekshirish"""

    print("\n🔍 Streamlit Moslik Tekshiruvi...\n")

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Kerakli barcha ustunlarni tekshirish
        required_columns = [
            'telegram_id', 'library_id', 'first_name', 'last_name',
            'phone_number', 'birth_year', 'study_place',
            'subscription_plan', 'subscription_end_date',
            'is_active', 'created_at'
        ]

        cursor.execute("PRAGMA table_info(users)")
        columns = cursor.fetchall()
        existing_columns = [col[1] for col in columns]

        missing = []
        for req_col in required_columns:
            if req_col in existing_columns:
                print(f"   ✅ {req_col}")
            else:
                print(f"   ❌ {req_col} - TOPILMADI")
                missing.append(req_col)

        if missing:
            print(f"\n⚠️ {len(missing)} ta ustun topilmadi!")
            print("💡 Migration skriptlarini ishga tushiring:")
            if 'study_place' in missing:
                print("   python migrate_database.py")
            if 'created_at' in missing:
                print("   python migrate_streamlit.py")
        else:
            print("\n✅ Barcha kerakli ustunlar mavjud!")
            print("🎉 Dashboard ishga tushirishga tayyor!")

        conn.close()
        return len(missing) == 0

    except Exception as e:
        print(f"\n❌ Xatolik: {e}")
        return False


def main():
    """Asosiy funksiya"""

    print("=" * 70)
    print("📊 STREAMLIT DASHBOARD - DATABASE MIGRATION")
    print("=" * 70)

    db_path = "../bot/library.db"

    # Argumentlarni tekshirish
    if len(sys.argv) > 1:
        if sys.argv[1] == "--test":
            test_streamlit_compatibility(db_path)
            return
        else:
            db_path = sys.argv[1]

    # Migration
    success = migrate_for_streamlit(db_path)

    if success:
        print("\n" + "=" * 70)

        # Test
        print("\n🧪 Mos kelishini tekshirish...")
        test_streamlit_compatibility(db_path)

        print("\n" + "=" * 70)
        print("🎊 TAYYOR!")
        print("=" * 70)
    else:
        print("\n" + "=" * 70)
        print("❌ Migration amalga oshmadi")
        print("=" * 70)
        sys.exit(1)


if __name__ == "__main__":
    main()