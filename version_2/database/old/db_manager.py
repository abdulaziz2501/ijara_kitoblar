"""
Database Manager - Ma'lumotlar bazasi bilan ishlash uchun asosiy klass
Library ID asosida ishlaydi, telegram_id ixtiyoriy
"""
import sqlite3
from datetime import datetime, timedelta
from typing import Optional, Tuple, List


class User:
    """User modeli - oddiy Python klass"""
    
    def __init__(self, library_id, first_name, last_name, phone_number, 
                 birth_year, study_place, subscription_plan='Free',
                 telegram_id=None, subscription_end_date=None, 
                 is_active=True, created_at=None):
        self.library_id = library_id
        self.telegram_id = telegram_id  # Ixtiyoriy
        self.first_name = first_name
        self.last_name = last_name
        self.phone_number = phone_number
        self.birth_year = birth_year
        self.study_place = study_place
        self.subscription_plan = subscription_plan
        self.subscription_end_date = subscription_end_date
        self.is_active = is_active
        self.created_at = created_at or datetime.now()
        self.registered_date = self.created_at  # Streamlit uchun alias
    
    @property
    def age(self):
        """Yoshni hisoblash"""
        current_year = datetime.now().year
        return current_year - self.birth_year
    
    @property
    def full_name(self):
        """To'liq ism"""
        return f"{self.first_name} {self.last_name}"
    
    def __repr__(self):
        return f"<User({self.library_id}: {self.full_name})>"


class DatabaseManager:
    """Database bilan ishlash uchun asosiy klass"""
    
    def __init__(self, db_path: str = "library.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self._create_tables()
    
    def _create_tables(self):
        """Barcha jadvallarni yaratish"""
        
        # Users jadvali
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                library_id TEXT UNIQUE NOT NULL,
                telegram_id INTEGER UNIQUE,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                phone_number TEXT NOT NULL,
                birth_year INTEGER NOT NULL,
                study_place TEXT NOT NULL,
                subscription_plan TEXT DEFAULT 'Free',
                subscription_end_date TIMESTAMP,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Index yaratish tezroq qidirish uchun
        self.cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_library_id 
            ON users(library_id)
        """)
        
        self.cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_telegram_id 
            ON users(telegram_id)
        """)
        
        self.conn.commit()
    
    def generate_library_id(self) -> str:
        """
        Yangi Library ID generatsiya qilish
        Format: ID0001, ID0002, ID0003...
        
        Returns:
            Yangi library_id
        """
        self.cursor.execute("SELECT COUNT(*) FROM users")
        count = self.cursor.fetchone()[0]
        return f"ID{count + 1:04d}"
    
    def create_user(self, first_name: str, last_name: str, phone_number: str,
                   birth_year: int, study_place: str, 
                   telegram_id: Optional[int] = None) -> Tuple[Optional[User], Optional[str]]:
        """
        Yangi foydalanuvchi yaratish
        
        Args:
            first_name: Ism
            last_name: Familiya
            phone_number: Telefon raqam
            birth_year: Tug'ilgan yil
            study_place: O'qish joyi
            telegram_id: Telegram ID (ixtiyoriy)
            
        Returns:
            (User object yoki None, Xato xabari yoki None)
        """
        try:
            # Telegram ID bo'lsa, mavjudligini tekshirish
            if telegram_id:
                self.cursor.execute(
                    "SELECT library_id FROM users WHERE telegram_id = ?", 
                    (telegram_id,)
                )
                existing = self.cursor.fetchone()
                if existing:
                    return None, f"❌ Bu Telegram akkaunt allaqachon ro'yxatdan o'tgan!\n📚 Library ID: {existing[0]}"
            
            # Telefon raqam mavjudligini tekshirish
            self.cursor.execute(
                "SELECT library_id FROM users WHERE phone_number = ?", 
                (phone_number,)
            )
            existing = self.cursor.fetchone()
            if existing:
                return None, f"❌ Bu telefon raqam allaqachon ro'yxatdan o'tgan!\n📚 Library ID: {existing[0]}"
            
            # Library ID generatsiya qilish
            library_id = self.generate_library_id()
            
            # Foydalanuvchi qo'shish
            self.cursor.execute("""
                INSERT INTO users (
                    library_id, telegram_id, first_name, last_name,
                    phone_number, birth_year, study_place, subscription_plan
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, 'Free')
            """, (library_id, telegram_id, first_name, last_name,
                  phone_number, birth_year, study_place))
            
            self.conn.commit()
            
            # User object yaratish va qaytarish
            user = User(
                library_id=library_id,
                telegram_id=telegram_id,
                first_name=first_name,
                last_name=last_name,
                phone_number=phone_number,
                birth_year=birth_year,
                study_place=study_place,
                subscription_plan='Free',
                created_at=datetime.now()
            )
            
            return user, None
            
        except Exception as e:
            return None, f"❌ Xatolik yuz berdi: {str(e)}"
    
    def get_user_by_library_id(self, library_id: str) -> Optional[User]:
        """
        Library ID bo'yicha foydalanuvchi topish
        
        Args:
            library_id: Library ID (masalan ID0001)
            
        Returns:
            User object yoki None
        """
        self.cursor.execute("""
            SELECT library_id, telegram_id, first_name, last_name,
                   phone_number, birth_year, study_place, subscription_plan,
                   subscription_end_date, is_active, created_at
            FROM users
            WHERE library_id = ?
        """, (library_id,))
        
        row = self.cursor.fetchone()
        if row:
            return User(
                library_id=row[0],
                telegram_id=row[1],
                first_name=row[2],
                last_name=row[3],
                phone_number=row[4],
                birth_year=row[5],
                study_place=row[6],
                subscription_plan=row[7],
                subscription_end_date=datetime.fromisoformat(row[8]) if row[8] else None,
                is_active=row[9],
                created_at=datetime.fromisoformat(row[10]) if row[10] else None
            )
        return None
    
    def get_user_by_telegram_id(self, telegram_id: int) -> Optional[User]:
        """
        Telegram ID bo'yicha foydalanuvchi topish
        
        Args:
            telegram_id: Telegram ID
            
        Returns:
            User object yoki None
        """
        self.cursor.execute("""
            SELECT library_id, telegram_id, first_name, last_name,
                   phone_number, birth_year, study_place, subscription_plan,
                   subscription_end_date, is_active, created_at
            FROM users
            WHERE telegram_id = ?
        """, (telegram_id,))
        
        row = self.cursor.fetchone()
        if row:
            return User(
                library_id=row[0],
                telegram_id=row[1],
                first_name=row[2],
                last_name=row[3],
                phone_number=row[4],
                birth_year=row[5],
                study_place=row[6],
                subscription_plan=row[7],
                subscription_end_date=datetime.fromisoformat(row[8]) if row[8] else None,
                is_active=row[9],
                created_at=datetime.fromisoformat(row[10]) if row[10] else None
            )
        return None
    
    def get_user_by_phone(self, phone_number: str) -> Optional[User]:
        """
        Telefon raqam bo'yicha foydalanuvchi topish
        
        Args:
            phone_number: Telefon raqam
            
        Returns:
            User object yoki None
        """
        self.cursor.execute("""
            SELECT library_id, telegram_id, first_name, last_name,
                   phone_number, birth_year, study_place, subscription_plan,
                   subscription_end_date, is_active, created_at
            FROM users
            WHERE phone_number = ?
        """, (phone_number,))
        
        row = self.cursor.fetchone()
        if row:
            return User(
                library_id=row[0],
                telegram_id=row[1],
                first_name=row[2],
                last_name=row[3],
                phone_number=row[4],
                birth_year=row[5],
                study_place=row[6],
                subscription_plan=row[7],
                subscription_end_date=datetime.fromisoformat(row[8]) if row[8] else None,
                is_active=row[9],
                created_at=datetime.fromisoformat(row[10]) if row[10] else None
            )
        return None
    
    def link_telegram_account(self, library_id: str, telegram_id: int) -> Tuple[bool, str]:
        """
        Mavjud foydalanuvchiga Telegram akkauntni bog'lash
        
        Args:
            library_id: Library ID
            telegram_id: Telegram ID
            
        Returns:
            (success: bool, message: str)
        """
        try:
            # Foydalanuvchi mavjudligini tekshirish
            user = self.get_user_by_library_id(library_id)
            if not user:
                return False, f"❌ {library_id} ID li foydalanuvchi topilmadi!"
            
            # Telegram ID allaqachon bog'langanligini tekshirish
            if user.telegram_id:
                return False, "❌ Bu Library ID allaqachon Telegram ga bog'langan!"
            
            # Boshqa foydalanuvchida bu Telegram ID borligini tekshirish
            existing = self.get_user_by_telegram_id(telegram_id)
            if existing:
                return False, f"❌ Bu Telegram akkaunt boshqa ID ga bog'langan: {existing.library_id}"
            
            # Telegram ID ni bog'lash
            self.cursor.execute("""
                UPDATE users 
                SET telegram_id = ?, updated_at = CURRENT_TIMESTAMP
                WHERE library_id = ?
            """, (telegram_id, library_id))
            
            self.conn.commit()
            return True, f"✅ Telegram akkaunt muvaffaqiyatli bog'landi!\n📚 Library ID: {library_id}"
            
        except Exception as e:
            return False, f"❌ Xatolik: {str(e)}"
    
    def update_subscription(self, library_id: str, plan_name: str, 
                          duration_days: int = 30) -> Tuple[bool, str]:
        """
        Obunani yangilash
        
        Args:
            library_id: Library ID
            plan_name: Tarif nomi (Free, Money, Premium)
            duration_days: Muddat (kunlarda)
            
        Returns:
            (success: bool, message: str)
        """
        try:
            user = self.get_user_by_library_id(library_id)
            if not user:
                return False, f"❌ {library_id} ID li foydalanuvchi topilmadi!"
            
            if plan_name not in ['Free', 'Money', 'Premium']:
                return False, "❌ Noto'g'ri tarif nomi!"
            
            if plan_name == 'Free':
                # Free uchun muddat yo'q
                self.cursor.execute("""
                    UPDATE users
                    SET subscription_plan = ?,
                        subscription_end_date = NULL,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE library_id = ?
                """, (plan_name, library_id))
            else:
                # Pullik rejimlar uchun muddat belgilash
                end_date = datetime.now() + timedelta(days=duration_days)
                self.cursor.execute("""
                    UPDATE users
                    SET subscription_plan = ?,
                        subscription_end_date = ?,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE library_id = ?
                """, (plan_name, end_date.isoformat(), library_id))
            
            self.conn.commit()
            return True, f"✅ Obuna yangilandi: {plan_name}"
            
        except Exception as e:
            return False, f"❌ Xatolik: {str(e)}"
    
    def get_all_users(self, active_only: bool = True) -> List[User]:
        """
        Barcha foydalanuvchilarni olish
        
        Args:
            active_only: Faqat faol foydalanuvchilarni olish
            
        Returns:
            List[User]
        """
        query = """
            SELECT library_id, telegram_id, first_name, last_name,
                   phone_number, birth_year, study_place, subscription_plan,
                   subscription_end_date, is_active, created_at
            FROM users
        """
        
        if active_only:
            query += " WHERE is_active = 1"
        
        query += " ORDER BY created_at DESC"
        
        self.cursor.execute(query)
        
        users = []
        for row in self.cursor.fetchall():
            users.append(User(
                library_id=row[0],
                telegram_id=row[1],
                first_name=row[2],
                last_name=row[3],
                phone_number=row[4],
                birth_year=row[5],
                study_place=row[6],
                subscription_plan=row[7],
                subscription_end_date=datetime.fromisoformat(row[8]) if row[8] else None,
                is_active=row[9],
                created_at=datetime.fromisoformat(row[10]) if row[10] else None
            ))
        
        return users
    
    def get_statistics(self) -> dict:
        """Statistika olish"""
        self.cursor.execute("SELECT COUNT(*) FROM users WHERE is_active = 1")
        total_users = self.cursor.fetchone()[0]
        
        self.cursor.execute("SELECT COUNT(*) FROM users WHERE subscription_plan = 'Free' AND is_active = 1")
        free_users = self.cursor.fetchone()[0]
        
        self.cursor.execute("SELECT COUNT(*) FROM users WHERE subscription_plan = 'Money' AND is_active = 1")
        money_users = self.cursor.fetchone()[0]
        
        self.cursor.execute("SELECT COUNT(*) FROM users WHERE subscription_plan = 'Premium' AND is_active = 1")
        premium_users = self.cursor.fetchone()[0]
        
        self.cursor.execute("SELECT COUNT(*) FROM users WHERE telegram_id IS NOT NULL AND is_active = 1")
        telegram_users = self.cursor.fetchone()[0]
        
        current_year = datetime.now().year
        self.cursor.execute(f"SELECT AVG({current_year} - birth_year) FROM users WHERE is_active = 1")
        average_age = self.cursor.fetchone()[0] or 0
        
        return {
            'total_users': total_users,
            'free_users': free_users,
            'money_users': money_users,
            'premium_users': premium_users,
            'telegram_users': telegram_users,
            'average_age': round(average_age, 1)
        }
    
    def get_users_expiring_soon(self, warning_days: int = 3) -> List[User]:
        """
        Obunasi tez orada tugaydigan foydalanuvchilar
        
        Args:
            warning_days: Necha kun qolganida ogohlantirish
            
        Returns:
            List[User]
        """
        warning_date = datetime.now() + timedelta(days=warning_days)
        
        self.cursor.execute("""
            SELECT library_id, telegram_id, first_name, last_name,
                   phone_number, birth_year, study_place, subscription_plan,
                   subscription_end_date, is_active, created_at
            FROM users
            WHERE subscription_end_date IS NOT NULL
              AND subscription_end_date <= ?
              AND subscription_end_date > ?
              AND subscription_plan IN ('Money', 'Premium')
              AND is_active = 1
        """, (warning_date.isoformat(), datetime.now().isoformat()))
        
        users = []
        for row in self.cursor.fetchall():
            users.append(User(
                library_id=row[0],
                telegram_id=row[1],
                first_name=row[2],
                last_name=row[3],
                phone_number=row[4],
                birth_year=row[5],
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
            SELECT library_id, telegram_id, first_name, last_name,
                   phone_number, birth_year, study_place, subscription_plan,
                   subscription_end_date, is_active, created_at
            FROM users
            WHERE subscription_end_date IS NOT NULL
              AND subscription_end_date < ?
              AND subscription_plan IN ('Money', 'Premium')
              AND is_active = 1
        """, (datetime.now().isoformat(),))
        
        users = []
        for row in self.cursor.fetchall():
            users.append(User(
                library_id=row[0],
                telegram_id=row[1],
                first_name=row[2],
                last_name=row[3],
                phone_number=row[4],
                birth_year=row[5],
                study_place=row[6],
                subscription_plan=row[7],
                subscription_end_date=datetime.fromisoformat(row[8]) if row[8] else None,
                is_active=row[9],
                created_at=datetime.fromisoformat(row[10]) if row[10] else None
            ))
        
        return users
    
    def search_users(self, query: str) -> List[User]:
        """
        Foydalanuvchilarni qidirish
        
        Args:
            query: Qidiruv so'zi (ism, familiya, library_id, telefon)
            
        Returns:
            List[User]
        """
        search_pattern = f"%{query}%"
        
        self.cursor.execute("""
            SELECT library_id, telegram_id, first_name, last_name,
                   phone_number, birth_year, study_place, subscription_plan,
                   subscription_end_date, is_active, created_at
            FROM users
            WHERE (library_id LIKE ? 
                   OR first_name LIKE ? 
                   OR last_name LIKE ? 
                   OR phone_number LIKE ?)
              AND is_active = 1
            ORDER BY created_at DESC
            LIMIT 50
        """, (search_pattern, search_pattern, search_pattern, search_pattern))
        
        users = []
        for row in self.cursor.fetchall():
            users.append(User(
                library_id=row[0],
                telegram_id=row[1],
                first_name=row[2],
                last_name=row[3],
                phone_number=row[4],
                birth_year=row[5],
                study_place=row[6],
                subscription_plan=row[7],
                subscription_end_date=datetime.fromisoformat(row[8]) if row[8] else None,
                is_active=row[9],
                created_at=datetime.fromisoformat(row[10]) if row[10] else None
            ))
        
        return users
    
    def deactivate_user(self, library_id: str) -> Tuple[bool, str]:
        """
        Foydalanuvchini deaktiv qilish
        
        Args:
            library_id: Library ID
            
        Returns:
            (success: bool, message: str)
        """
        try:
            user = self.get_user_by_library_id(library_id)
            if not user:
                return False, f"❌ {library_id} ID li foydalanuvchi topilmadi!"
            
            self.cursor.execute("""
                UPDATE users
                SET is_active = 0, updated_at = CURRENT_TIMESTAMP
                WHERE library_id = ?
            """, (library_id,))
            
            self.conn.commit()
            return True, f"✅ Foydalanuvchi deaktiv qilindi: {user.full_name}"
            
        except Exception as e:
            return False, f"❌ Xatolik: {str(e)}"
    
    def activate_user(self, library_id: str) -> Tuple[bool, str]:
        """
        Foydalanuvchini aktiv qilish
        
        Args:
            library_id: Library ID
            
        Returns:
            (success: bool, message: str)
        """
        try:
            self.cursor.execute("""
                UPDATE users
                SET is_active = 1, updated_at = CURRENT_TIMESTAMP
                WHERE library_id = ?
            """, (library_id,))
            
            self.conn.commit()
            return True, "✅ Foydalanuvchi aktiv qilindi!"
            
        except Exception as e:
            return False, f"❌ Xatolik: {str(e)}"
    
    def close(self):
        """Database connection yopish"""
        self.conn.close()


# Test uchun
if __name__ == "__main__":
    db = DatabaseManager()
    print("✅ Database Manager test muvaffaqiyatli!")
    db.close()
