# database/db_manager.py - To'liq yangilangan versiya
import sqlite3
from datetime import datetime, timedelta
from typing import Optional, Tuple, List


class User:
    """User modeli"""

    def __init__(self, telegram_id, library_id, first_name, last_name,
                 phone_number, age, study_place, subscription_plan,
                 subscription_end_date=None, is_active=True, created_at=None):
        self.telegram_id = telegram_id
        self.library_id = library_id
        self.first_name = first_name
        self.last_name = last_name
        self.phone_number = phone_number
        self.age = age
        self.study_place = study_place
        self.subscription_plan = subscription_plan
        self.subscription_end_date = subscription_end_date
        self.is_active = is_active
        self.created_at = created_at  # Ro'yxatdan o'tgan sana
        self.registered_date = created_at  # Streamlit uchun alias


class DatabaseManager:
    def __init__(self, db_path: str = "library.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self._create_tables()

    def _create_tables(self):
        """Jadvallarni yaratish"""
        self.cursor.execute("""
                            CREATE TABLE IF NOT EXISTS users
                            (
                                id
                                INTEGER
                                PRIMARY
                                KEY
                                AUTOINCREMENT,
                                telegram_id
                                INTEGER
                                UNIQUE
                                NOT
                                NULL,
                                library_id
                                TEXT
                                UNIQUE
                                NOT
                                NULL,
                                first_name
                                TEXT
                                NOT
                                NULL,
                                last_name
                                TEXT
                                NOT
                                NULL,
                                phone_number
                                TEXT
                                NOT
                                NULL,
                                birth_year
                                INTEGER
                                NOT
                                NULL,
                                study_place
                                TEXT
                                NOT
                                NULL,
                                subscription_plan
                                TEXT
                                DEFAULT
                                'Free',
                                subscription_end_date
                                TIMESTAMP,
                                is_active
                                BOOLEAN
                                DEFAULT
                                1,
                                created_at
                                TIMESTAMP
                                DEFAULT
                                CURRENT_TIMESTAMP
                            )
                            """)
        self.conn.commit()

    def create_user(self, telegram_id: int, first_name: str, last_name: str,
                    phone_number: str, birth_year: int, study_place: str) -> Tuple[Optional[User], Optional[str]]:
        """Yangi foydalanuvchi yaratish"""
        try:
            # Mavjudligini tekshirish
            existing = self.get_user_by_telegram_id(telegram_id)
            if existing:
                return None, "Siz allaqachon ro'yxatdan o'tgansiz!"

            # Library ID generatsiya qilish
            self.cursor.execute("SELECT COUNT(*) FROM users")
            count = self.cursor.fetchone()[0]
            library_id = f"ID{count + 1:04d}"

            # Yoshni hisoblash
            current_year = datetime.now().year
            age = current_year - birth_year

            # Foydalanuvchi qo'shish
            self.cursor.execute("""
                                INSERT INTO users (telegram_id, library_id, first_name, last_name,
                                                   phone_number, birth_year, study_place, subscription_plan)
                                VALUES (?, ?, ?, ?, ?, ?, ?, 'Free')
                                """, (telegram_id, library_id, first_name, last_name,
                                      phone_number, birth_year, study_place))

            self.conn.commit()

            user = User(
                telegram_id=telegram_id,
                library_id=library_id,
                first_name=first_name,
                last_name=last_name,
                phone_number=phone_number,
                age=age,
                study_place=study_place,
                subscription_plan='Free',
                created_at=datetime.now()
            )

            return user, None

        except Exception as e:
            return None, str(e)

    def get_user_by_telegram_id(self, telegram_id: int) -> Optional[User]:
        """Telegram ID bo'yicha foydalanuvchi topish"""
        self.cursor.execute("""
                            SELECT telegram_id,
                                   library_id,
                                   first_name,
                                   last_name,
                                   phone_number,
                                   birth_year,
                                   study_place,
                                   subscription_plan,
                                   subscription_end_date,
                                   is_active,
                                   created_at
                            FROM users
                            WHERE telegram_id = ?
                            """, (telegram_id,))

        row = self.cursor.fetchone()
        if row:
            current_year = datetime.now().year
            age = current_year - row[5]

            return User(
                telegram_id=row[0],
                library_id=row[1],
                first_name=row[2],
                last_name=row[3],
                phone_number=row[4],
                age=age,
                study_place=row[6],
                subscription_plan=row[7],
                subscription_end_date=datetime.fromisoformat(row[8]) if row[8] else None,
                is_active=row[9],
                created_at=datetime.fromisoformat(row[10]) if row[10] else None
            )
        return None

    def get_user_by_library_id(self, library_id: str) -> Optional[User]:
        """Library ID bo'yicha foydalanuvchi topish"""
        self.cursor.execute("""
                            SELECT telegram_id,
                                   library_id,
                                   first_name,
                                   last_name,
                                   phone_number,
                                   birth_year,
                                   study_place,
                                   subscription_plan,
                                   subscription_end_date,
                                   is_active,
                                   created_at
                            FROM users
                            WHERE library_id = ?
                            """, (library_id,))

        row = self.cursor.fetchone()
        if row:
            current_year = datetime.now().year
            age = current_year - row[5]

            return User(
                telegram_id=row[0],
                library_id=row[1],
                first_name=row[2],
                last_name=row[3],
                phone_number=row[4],
                age=age,
                study_place=row[6],
                subscription_plan=row[7],
                subscription_end_date=datetime.fromisoformat(row[8]) if row[8] else None,
                is_active=row[9],
                created_at=datetime.fromisoformat(row[10]) if row[10] else None
            )
        return None

    def update_subscription(self, library_id: str, plan_name: str) -> bool:
        """Obunani yangilash"""
        try:
            if plan_name == 'Free':
                # Free uchun muddat yo'q
                self.cursor.execute("""
                                    UPDATE users
                                    SET subscription_plan     = ?,
                                        subscription_end_date = NULL
                                    WHERE library_id = ?
                                    """, (plan_name, library_id))
            else:
                # Pullik rejimlar uchun 30 kunlik muddat
                end_date = datetime.now() + timedelta(days=30)
                self.cursor.execute("""
                                    UPDATE users
                                    SET subscription_plan     = ?,
                                        subscription_end_date = ?
                                    WHERE library_id = ?
                                    """, (plan_name, end_date.isoformat(), library_id))

            self.conn.commit()
            return True
        except Exception as e:
            print(f"Obunani yangilashda xato: {e}")
            return False

    def get_statistics(self) -> dict:
        """Statistika olish"""
        self.cursor.execute("SELECT COUNT(*) FROM users")
        total_users = self.cursor.fetchone()[0]

        self.cursor.execute("SELECT COUNT(*) FROM users WHERE subscription_plan = 'Free'")
        free_users = self.cursor.fetchone()[0]

        self.cursor.execute("SELECT COUNT(*) FROM users WHERE subscription_plan = 'Money'")
        money_users = self.cursor.fetchone()[0]

        self.cursor.execute("SELECT COUNT(*) FROM users WHERE subscription_plan = 'Premium'")
        premium_users = self.cursor.fetchone()[0]

        current_year = datetime.now().year
        self.cursor.execute(f"SELECT AVG({current_year} - birth_year) FROM users")
        average_age = self.cursor.fetchone()[0] or 0

        return {
            'total_users': total_users,
            'free_users': free_users,
            'money_users': money_users,
            'premium_users': premium_users,
            'average_age': round(average_age, 1)
        }

    def get_all_users(self) -> List[User]:
        """Barcha foydalanuvchilarni olish"""
        self.cursor.execute("""
                            SELECT telegram_id,
                                   library_id,
                                   first_name,
                                   last_name,
                                   phone_number,
                                   birth_year,
                                   study_place,
                                   subscription_plan,
                                   subscription_end_date,
                                   is_active,
                                   created_at
                            FROM users
                            ORDER BY created_at DESC
                            """)

        users = []
        current_year = datetime.now().year

        for row in self.cursor.fetchall():
            age = current_year - row[5]
            users.append(User(
                telegram_id=row[0],
                library_id=row[1],
                first_name=row[2],
                last_name=row[3],
                phone_number=row[4],
                age=age,
                study_place=row[6],
                subscription_plan=row[7],
                subscription_end_date=datetime.fromisoformat(row[8]) if row[8] else None,
                is_active=row[9],
                created_at=datetime.fromisoformat(row[10]) if row[10] else None
            ))

        return users

    def get_users_expiring_soon(self, warning_date: datetime) -> List[User]:
        """Obunasi tez orada tugaydigan foydalanuvchilar"""
        self.cursor.execute("""
                            SELECT telegram_id,
                                   library_id,
                                   first_name,
                                   last_name,
                                   phone_number,
                                   birth_year,
                                   study_place,
                                   subscription_plan,
                                   subscription_end_date,
                                   is_active,
                                   created_at
                            FROM users
                            WHERE subscription_end_date IS NOT NULL
                              AND subscription_end_date <= ?
                              AND subscription_end_date > ?
                              AND subscription_plan IN ('Money', 'Premium')
                            """, (warning_date.isoformat(), datetime.now().isoformat()))

        users = []
        current_year = datetime.now().year

        for row in self.cursor.fetchall():
            age = current_year - row[5]
            users.append(User(
                telegram_id=row[0],
                library_id=row[1],
                first_name=row[2],
                last_name=row[3],
                phone_number=row[4],
                age=age,
                study_place=row[6],
                subscription_plan=row[7],
                subscription_end_date=datetime.fromisoformat(row[8]) if row[8] else None,
                is_active=row[9],
                created_at=datetime.fromisoformat(row[10]) if row[10] else None
            ))

        return users

    def get_expired_subscriptions(self) -> List[User]:
        """Muddati o'tgan obunalar"""
        self.cursor.execute("""
                            SELECT telegram_id,
                                   library_id,
                                   first_name,
                                   last_name,
                                   phone_number,
                                   birth_year,
                                   study_place,
                                   subscription_plan,
                                   subscription_end_date,
                                   is_active,
                                   created_at
                            FROM users
                            WHERE subscription_end_date IS NOT NULL
                              AND subscription_end_date < ?
                              AND subscription_plan IN ('Money', 'Premium')
                            """, (datetime.now().isoformat(),))

        users = []
        current_year = datetime.now().year

        for row in self.cursor.fetchall():
            age = current_year - row[5]
            users.append(User(
                telegram_id=row[0],
                library_id=row[1],
                first_name=row[2],
                last_name=row[3],
                phone_number=row[4],
                age=age,
                study_place=row[6],
                subscription_plan=row[7],
                subscription_end_date=datetime.fromisoformat(row[8]) if row[8] else None,
                is_active=row[9],
                created_at=datetime.fromisoformat(row[10]) if row[10] else None
            ))

        return users

    def get_users_needing_warning(self) -> List[User]:
        """Ogohlantirish kerak bo'lgan foydalanuvchilar (3 kun qolgan)"""
        warning_date = datetime.now() + timedelta(days=3)
        return self.get_users_expiring_soon(warning_date)

    def close(self):
        """Database connection yopish"""
        self.conn.close()