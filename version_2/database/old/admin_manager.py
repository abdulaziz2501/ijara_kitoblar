"""
Admin Manager - Adminlarni boshqarish tizimi
Bu modul adminlarni qo'shish, o'chirish va tekshirish uchun ishlatiladi
"""
import sqlite3
from typing import List, Optional, Tuple
from datetime import datetime


class Admin:
    """Admin modeli"""
    
    def __init__(self, admin_id: int, telegram_id: int, library_id: str,
                 full_name: str, is_super_admin: bool = False, 
                 added_date: datetime = None, added_by: int = None):
        self.admin_id = admin_id
        self.telegram_id = telegram_id
        self.library_id = library_id
        self.full_name = full_name
        self.is_super_admin = is_super_admin
        self.added_date = added_date or datetime.now()
        self.added_by = added_by  # Qaysi admin qo'shgan


class AdminManager:
    """Adminlarni boshqarish uchun klass"""
    
    def __init__(self, db_path: str = "library.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self._create_admin_table()
    
    def _create_admin_table(self):
        """Admin jadvali yaratish"""
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS admins (
                admin_id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id INTEGER UNIQUE NOT NULL,
                library_id TEXT UNIQUE NOT NULL,
                full_name TEXT NOT NULL,
                is_super_admin BOOLEAN DEFAULT 0,
                added_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                added_by INTEGER,
                is_active BOOLEAN DEFAULT 1,
                FOREIGN KEY (library_id) REFERENCES users(library_id)
            )
        """)
        self.conn.commit()
    
    def add_super_admin(self, telegram_id: int, library_id: str, 
                       full_name: str) -> Tuple[bool, str]:
        """
        Super admin qo'shish (faqat bitta bo'lishi mumkin)
        
        Args:
            telegram_id: Telegram ID
            library_id: Library ID (masalan ID0001)
            full_name: To'liq ismi
            
        Returns:
            (success: bool, message: str)
        """
        try:
            # Super admin borligini tekshirish
            self.cursor.execute(
                "SELECT COUNT(*) FROM admins WHERE is_super_admin = 1"
            )
            count = self.cursor.fetchone()[0]
            
            if count > 0:
                return False, "❌ Super admin allaqachon mavjud!"
            
            # Telegram ID mavjudligini tekshirish
            existing = self.get_admin_by_telegram_id(telegram_id)
            if existing:
                return False, "❌ Bu Telegram ID allaqachon admin!"
            
            # Library ID mavjudligini tekshirish
            existing = self.get_admin_by_library_id(library_id)
            if existing:
                return False, "❌ Bu Library ID allaqachon admin!"
            
            # Super admin qo'shish
            self.cursor.execute("""
                INSERT INTO admins (telegram_id, library_id, full_name, 
                                  is_super_admin, added_by)
                VALUES (?, ?, ?, 1, ?)
            """, (telegram_id, library_id, full_name, telegram_id))
            
            self.conn.commit()
            return True, f"✅ Super admin muvaffaqiyatli qo'shildi!\n📚 ID: {library_id}"
            
        except Exception as e:
            return False, f"❌ Xatolik: {str(e)}"
    
    def add_admin(self, telegram_id: int, library_id: str, 
                 full_name: str, added_by: int) -> Tuple[bool, str]:
        """
        Oddiy admin qo'shish (faqat super admin qo'sha oladi)
        
        Args:
            telegram_id: Yangi admin Telegram ID si
            library_id: Library ID
            full_name: To'liq ismi
            added_by: Qo'shayotgan adminning Telegram ID si
            
        Returns:
            (success: bool, message: str)
        """
        try:
            # Qo'shayotgan odam super admin ekanligini tekshirish
            if not self.is_super_admin(added_by):
                return False, "❌ Faqat super admin yangi admin qo'sha oladi!"
            
            # Telegram ID mavjudligini tekshirish
            existing = self.get_admin_by_telegram_id(telegram_id)
            if existing:
                return False, "❌ Bu Telegram ID allaqachon admin!"
            
            # Library ID mavjudligini tekshirish
            existing = self.get_admin_by_library_id(library_id)
            if existing:
                return False, "❌ Bu Library ID allaqachon admin!"
            
            # Admin qo'shish
            self.cursor.execute("""
                INSERT INTO admins (telegram_id, library_id, full_name, 
                                  is_super_admin, added_by)
                VALUES (?, ?, ?, 0, ?)
            """, (telegram_id, library_id, full_name, added_by))
            
            self.conn.commit()
            return True, f"✅ Admin muvaffaqiyatli qo'shildi!\n📚 ID: {library_id}"
            
        except Exception as e:
            return False, f"❌ Xatolik: {str(e)}"
    
    def remove_admin(self, library_id: str, removed_by: int) -> Tuple[bool, str]:
        """
        Adminni o'chirish (faqat super admin o'chira oladi)
        
        Args:
            library_id: O'chiriladigan admin Library ID si
            removed_by: O'chiruvchi super admin Telegram ID si
            
        Returns:
            (success: bool, message: str)
        """
        try:
            # Super admin ekanligini tekshirish
            if not self.is_super_admin(removed_by):
                return False, "❌ Faqat super admin boshqa adminlarni o'chira oladi!"
            
            # Adminni topish
            admin = self.get_admin_by_library_id(library_id)
            if not admin:
                return False, f"❌ {library_id} ID li admin topilmadi!"
            
            # Super adminni o'chirib bo'lmaydi
            if admin.is_super_admin:
                return False, "❌ Super adminni o'chirib bo'lmaydi!"
            
            # Adminni o'chirish (actually deactivate)
            self.cursor.execute("""
                UPDATE admins 
                SET is_active = 0 
                WHERE library_id = ?
            """, (library_id,))
            
            self.conn.commit()
            return True, f"✅ Admin o'chirildi: {admin.full_name}"
            
        except Exception as e:
            return False, f"❌ Xatolik: {str(e)}"
    
    def is_admin(self, telegram_id: int) -> bool:
        """
        Telegram ID admin ekanligini tekshirish
        
        Args:
            telegram_id: Tekshiriladigan Telegram ID
            
        Returns:
            Admin bo'lsa True, aks holda False
        """
        self.cursor.execute("""
            SELECT COUNT(*) FROM admins 
            WHERE telegram_id = ? AND is_active = 1
        """, (telegram_id,))
        
        count = self.cursor.fetchone()[0]
        return count > 0
    
    def is_super_admin(self, telegram_id: int) -> bool:
        """
        Super admin ekanligini tekshirish
        
        Args:
            telegram_id: Tekshiriladigan Telegram ID
            
        Returns:
            Super admin bo'lsa True, aks holda False
        """
        self.cursor.execute("""
            SELECT COUNT(*) FROM admins 
            WHERE telegram_id = ? AND is_super_admin = 1 AND is_active = 1
        """, (telegram_id,))
        
        count = self.cursor.fetchone()[0]
        return count > 0
    
    def get_admin_by_telegram_id(self, telegram_id: int) -> Optional[Admin]:
        """Telegram ID bo'yicha admin topish"""
        self.cursor.execute("""
            SELECT admin_id, telegram_id, library_id, full_name, 
                   is_super_admin, added_date, added_by
            FROM admins
            WHERE telegram_id = ? AND is_active = 1
        """, (telegram_id,))
        
        row = self.cursor.fetchone()
        if row:
            return Admin(
                admin_id=row[0],
                telegram_id=row[1],
                library_id=row[2],
                full_name=row[3],
                is_super_admin=bool(row[4]),
                added_date=datetime.fromisoformat(row[5]) if row[5] else None,
                added_by=row[6]
            )
        return None
    
    def get_admin_by_library_id(self, library_id: str) -> Optional[Admin]:
        """Library ID bo'yicha admin topish"""
        self.cursor.execute("""
            SELECT admin_id, telegram_id, library_id, full_name, 
                   is_super_admin, added_date, added_by
            FROM admins
            WHERE library_id = ? AND is_active = 1
        """, (library_id,))
        
        row = self.cursor.fetchone()
        if row:
            return Admin(
                admin_id=row[0],
                telegram_id=row[1],
                library_id=row[2],
                full_name=row[3],
                is_super_admin=bool(row[4]),
                added_date=datetime.fromisoformat(row[5]) if row[5] else None,
                added_by=row[6]
            )
        return None
    
    def get_all_admins(self) -> List[Admin]:
        """Barcha adminlarni olish"""
        self.cursor.execute("""
            SELECT admin_id, telegram_id, library_id, full_name, 
                   is_super_admin, added_date, added_by
            FROM admins
            WHERE is_active = 1
            ORDER BY is_super_admin DESC, added_date ASC
        """)
        
        admins = []
        for row in self.cursor.fetchall():
            admins.append(Admin(
                admin_id=row[0],
                telegram_id=row[1],
                library_id=row[2],
                full_name=row[3],
                is_super_admin=bool(row[4]),
                added_date=datetime.fromisoformat(row[5]) if row[5] else None,
                added_by=row[6]
            ))
        
        return admins
    
    def get_super_admin(self) -> Optional[Admin]:
        """Super adminni olish"""
        self.cursor.execute("""
            SELECT admin_id, telegram_id, library_id, full_name, 
                   is_super_admin, added_date, added_by
            FROM admins
            WHERE is_super_admin = 1 AND is_active = 1
            LIMIT 1
        """)
        
        row = self.cursor.fetchone()
        if row:
            return Admin(
                admin_id=row[0],
                telegram_id=row[1],
                library_id=row[2],
                full_name=row[3],
                is_super_admin=bool(row[4]),
                added_date=datetime.fromisoformat(row[5]) if row[5] else None,
                added_by=row[6]
            )
        return None
    
    def get_admin_count(self) -> dict:
        """Admin statistikasi"""
        self.cursor.execute("""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN is_super_admin = 1 THEN 1 ELSE 0 END) as super_admin,
                SUM(CASE WHEN is_super_admin = 0 THEN 1 ELSE 0 END) as regular
            FROM admins
            WHERE is_active = 1
        """)
        
        row = self.cursor.fetchone()
        return {
            'total': row[0],
            'super_admin': row[1] or 0,
            'regular': row[2] or 0
        }
    
    def close(self):
        """Database connection yopish"""
        self.conn.close()
