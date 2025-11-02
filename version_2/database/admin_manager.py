"""
Admin Manager (PostgreSQL) - SQLAlchemy ORM bilan
Adminlarni boshqarish tizimi
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from typing import List, Optional, Tuple
import logging

from ijara_kitoblar.database.models import Base, Admin
from ijara_kitoblar.config import DATABASE_URL, POOL_SIZE, MAX_OVERFLOW, POOL_TIMEOUT, POOL_RECYCLE

logger = logging.getLogger(__name__)


class AdminManager:
    """PostgreSQL admin boshqarish uchun klass"""

    def __init__(self, database_url: str = None):
        """Admin Manager yaratish"""
        self.database_url = database_url or DATABASE_URL

        # Engine yaratish
        self.engine = create_engine(
            self.database_url,
            poolclass=QueuePool,
            pool_size=POOL_SIZE,
            max_overflow=MAX_OVERFLOW,
            pool_timeout=POOL_TIMEOUT,
            pool_recycle=POOL_RECYCLE,
            echo=False
        )

        # Session maker
        self.Session = sessionmaker(bind=self.engine)

        # Jadvallarni yaratish
        Base.metadata.create_all(self.engine)

    def get_session(self) -> Session:
        """Yangi session olish"""
        return self.Session()

    def add_super_admin(self, telegram_id: int, library_id: str,
                       full_name: str) -> Tuple[bool, str]:
        """Super admin qo'shish (faqat bitta bo'lishi mumkin)"""
        session = self.get_session()

        try:
            # Super admin borligini tekshirish
            existing_super = session.query(Admin).filter_by(is_super_admin=True).first()

            if existing_super:
                return False, "❌ Super admin allaqachon mavjud!"

            # Telegram ID mavjudligini tekshirish
            existing = session.query(Admin).filter_by(telegram_id=telegram_id).first()
            if existing:
                return False, "❌ Bu Telegram ID allaqachon admin!"

            # Library ID mavjudligini tekshirish
            existing = session.query(Admin).filter_by(library_id=library_id).first()
            if existing:
                return False, "❌ Bu Library ID allaqachon admin!"

            # Super admin qo'shish
            admin = Admin(
                telegram_id=telegram_id,
                library_id=library_id,
                full_name=full_name,
                is_super_admin=True,
                added_by=telegram_id
            )

            session.add(admin)
            session.commit()

            logger.info(f"✅ Super admin qo'shildi: {library_id}")
            return True, f"✅ Super admin muvaffaqiyatli qo'shildi!\n📚 ID: {library_id}"

        except Exception as e:
            session.rollback()
            logger.error(f"❌ Super admin qo'shishda xato: {e}")
            return False, f"❌ Xatolik: {str(e)}"

        finally:
            session.close()

    def add_admin(self, telegram_id: int, library_id: str,
                 full_name: str, added_by: int) -> Tuple[bool, str]:
        """Oddiy admin qo'shish"""
        session = self.get_session()

        try:
            # Qo'shayotgan odam super admin ekanligini tekshirish
            if not self.is_super_admin(added_by):
                return False, "❌ Faqat super admin yangi admin qo'sha oladi!"

            # Telegram ID mavjudligini tekshirish
            existing = session.query(Admin).filter_by(telegram_id=telegram_id).first()
            if existing:
                return False, "❌ Bu Telegram ID allaqachon admin!"

            # Library ID mavjudligini tekshirish
            existing = session.query(Admin).filter_by(library_id=library_id).first()
            if existing:
                return False, "❌ Bu Library ID allaqachon admin!"

            # Admin qo'shish
            admin = Admin(
                telegram_id=telegram_id,
                library_id=library_id,
                full_name=full_name,
                is_super_admin=False,
                added_by=added_by
            )

            session.add(admin)
            session.commit()

            logger.info(f"✅ Admin qo'shildi: {library_id}")
            return True, f"✅ Admin muvaffaqiyatli qo'shildi!\n📚 ID: {library_id}"

        except Exception as e:
            session.rollback()
            logger.error(f"❌ Admin qo'shishda xato: {e}")
            return False, f"❌ Xatolik: {str(e)}"

        finally:
            session.close()

    def remove_admin(self, library_id: str, removed_by: int) -> Tuple[bool, str]:
        """Adminni o'chirish"""
        session = self.get_session()

        try:
            # Super admin ekanligini tekshirish
            if not self.is_super_admin(removed_by):
                return False, "❌ Faqat super admin boshqa adminlarni o'chira oladi!"

            # Adminni topish
            admin = session.query(Admin).filter_by(library_id=library_id).first()
            if not admin:
                return False, f"❌ {library_id} ID li admin topilmadi!"

            # Super adminni o'chirib bo'lmaydi
            if admin.is_super_admin:
                return False, "❌ Super adminni o'chirib bo'lmaydi!"

            # Adminni o'chirish (deactivate)
            admin.is_active = False

            session.commit()
            logger.info(f"✅ Admin o'chirildi: {library_id}")
            return True, f"✅ Admin o'chirildi: {admin.full_name}"

        except Exception as e:
            session.rollback()
            logger.error(f"❌ Admin o'chirishda xato: {e}")
            return False, f"❌ Xatolik: {str(e)}"

        finally:
            session.close()

    def is_admin(self, telegram_id: int) -> bool:
        """Admin ekanligini tekshirish"""
        session = self.get_session()

        try:
            admin = session.query(Admin).filter_by(
                telegram_id=telegram_id,
                is_active=True
            ).first()
            return admin is not None
        finally:
            session.close()

    def is_super_admin(self, telegram_id: int) -> bool:
        """Super admin ekanligini tekshirish"""
        session = self.get_session()

        try:
            admin = session.query(Admin).filter_by(
                telegram_id=telegram_id,
                is_super_admin=True,
                is_active=True
            ).first()
            return admin is not None
        finally:
            session.close()

    def get_admin_by_telegram_id(self, telegram_id: int) -> Optional[Admin]:
        """Telegram ID bo'yicha admin topish"""
        session = self.get_session()

        try:
            admin = session.query(Admin).filter_by(
                telegram_id=telegram_id,
                is_active=True
            ).first()

            if admin:
                session.expunge(admin)

            return admin
        finally:
            session.close()

    def get_admin_by_library_id(self, library_id: str) -> Optional[Admin]:
        """Library ID bo'yicha admin topish"""
        session = self.get_session()

        try:
            admin = session.query(Admin).filter_by(
                library_id=library_id,
                is_active=True
            ).first()

            if admin:
                session.expunge(admin)

            return admin
        finally:
            session.close()

    def get_all_admins(self) -> List[Admin]:
        """Barcha adminlarni olish"""
        session = self.get_session()

        try:
            admins = session.query(Admin).filter_by(is_active=True).order_by(
                Admin.is_super_admin.desc(),
                Admin.added_date.asc()
            ).all()

            for admin in admins:
                session.expunge(admin)

            return admins
        finally:
            session.close()

    def get_super_admin(self) -> Optional[Admin]:
        """Super adminni olish"""
        session = self.get_session()

        try:
            admin = session.query(Admin).filter_by(
                is_super_admin=True,
                is_active=True
            ).first()

            if admin:
                session.expunge(admin)

            return admin
        finally:
            session.close()

    def get_admin_count(self) -> dict:
        """Admin statistikasi"""
        session = self.get_session()

        try:
            from sqlalchemy import func

            result = session.query(
                func.count(Admin.admin_id).label('total'),
                func.sum(func.cast(Admin.is_super_admin, 1)).label('super_admin')
            ).filter_by(is_active=True).first()

            total = result.total or 0
            super_admin = result.super_admin or 0
            regular = total - super_admin

            return {
                'total': total,
                'super_admin': super_admin,
                'regular': regular
            }
        finally:
            session.close()

    def close(self):
        """Engine ni yopish"""
        self.engine.dispose()
        logger.info("🔒 Admin Manager yopildi")


# Test uchun
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    admin_manager = AdminManager()
    print("✅ PostgreSQL Admin Manager test muvaffaqiyatli!")
    admin_manager.close()