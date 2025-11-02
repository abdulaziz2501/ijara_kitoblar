"""
Database Manager (PostgreSQL) - SQLAlchemy ORM bilan
PostgreSQL database bilan ishlash uchun
"""
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from datetime import datetime, timedelta
from typing import Optional, Tuple, List
import logging

from ijara_kitoblar.database.models import Base, User
from ijara_kitoblar.config import DATABASE_URL, POOL_SIZE, MAX_OVERFLOW, POOL_TIMEOUT, POOL_RECYCLE

logger = logging.getLogger(__name__)


class DatabaseManager:
    """PostgreSQL database bilan ishlash uchun klass"""

    def __init__(self, database_url: str = None):
        """
        Database Manager yaratish

        Args:
            database_url: Database connection URL
        """
        self.database_url = database_url or DATABASE_URL

        # Engine yaratish (Connection pool bilan)
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
        self._create_tables()

    def _create_tables(self):
        """Barcha jadvallarni yaratish"""
        try:
            Base.metadata.create_all(self.engine)
            logger.info("✅ Database jadvallar yaratildi")
        except Exception as e:
            logger.error(f"❌ Jadval yaratishda xato: {e}")
            raise

    def get_session(self) -> Session:
        """Yangi session olish"""
        return self.Session()

    def generate_library_id(self, session: Session) -> str:
        """
        Yangi Library ID generatsiya qilish
        Format: ID0001, ID0002, ID0003...

        Args:
            session: Database session

        Returns:
            Yangi library_id
        """
        count = session.query(func.count(User.id)).scalar() or 0
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
        session = self.get_session()

        try:
            # Telegram ID bo'lsa, mavjudligini tekshirish
            if telegram_id:
                existing = session.query(User).filter_by(telegram_id=telegram_id).first()
                if existing:
                    return None, f"❌ Bu Telegram akkaunt allaqachon ro'yxatdan o'tgan!\n📚 Library ID: {existing.library_id}"

            # Telefon raqam mavjudligini tekshirish
            existing = session.query(User).filter_by(phone_number=phone_number).first()
            if existing:
                return None, f"❌ Bu telefon raqam allaqachon ro'yxatdan o'tgan!\n📚 Library ID: {existing.library_id}"

            # Library ID generatsiya qilish
            library_id = self.generate_library_id(session)

            # Foydalanuvchi yaratish
            user = User(
                library_id=library_id,
                telegram_id=telegram_id,
                first_name=first_name,
                last_name=last_name,
                phone_number=phone_number,
                birth_year=birth_year,
                study_place=study_place,
                subscription_plan='Free',
                is_active=True
            )

            session.add(user)
            session.commit()
            session.refresh(user)

            logger.info(f"✅ Yangi foydalanuvchi yaratildi: {library_id}")
            return user, None

        except Exception as e:
            session.rollback()
            logger.error(f"❌ Foydalanuvchi yaratishda xato: {e}")
            return None, f"❌ Xatolik yuz berdi: {str(e)}"

        finally:
            session.close()

    def get_user_by_library_id(self, library_id: str) -> Optional[User]:
        """Library ID bo'yicha foydalanuvchi topish"""
        session = self.get_session()

        try:
            user = session.query(User).filter_by(library_id=library_id).first()
            if user:
                # Session dan detach qilish
                session.expunge(user)
            return user
        finally:
            session.close()

    def add_user(self, library_id, full_name, phone_number=None, telegram_id=None):
        session = self.Session()
        try:
            new_user = User(
                library_id=library_id,
                full_name=full_name,
                phone_number=phone_number,
                telegram_id=telegram_id
            )
            session.add(new_user)
            session.commit()  # <-- MUHIM
            print("✅ User added successfully")
        except Exception as e:
            session.rollback()
            print("❌ Error adding user:", e)
        finally:
            session.close()


    def get_user_by_telegram_id(self, telegram_id: int) -> Optional[User]:
        """Telegram ID bo'yicha foydalanuvchi topish"""
        session = self.get_session()

        try:
            user = session.query(User).filter_by(telegram_id=telegram_id).first()
            if user:
                session.expunge(user)
            return user
        finally:
            session.close()

    def get_user_by_phone(self, phone_number: str) -> Optional[User]:
        """Telefon raqam bo'yicha foydalanuvchi topish"""
        session = self.get_session()

        try:
            user = session.query(User).filter_by(phone_number=phone_number).first()
            if user:
                session.expunge(user)
            return user
        finally:
            session.close()

    def link_telegram_account(self, library_id: str, telegram_id: int) -> Tuple[bool, str]:
        """Mavjud foydalanuvchiga Telegram akkauntni bog'lash"""
        session = self.get_session()

        try:
            user = session.query(User).filter_by(library_id=library_id).first()
            if not user:
                return False, f"❌ {library_id} ID li foydalanuvchi topilmadi!"

            if user.telegram_id:
                return False, "❌ Bu Library ID allaqachon Telegram ga bog'langan!"

            # Boshqa foydalanuvchida bu Telegram ID borligini tekshirish
            existing = session.query(User).filter_by(telegram_id=telegram_id).first()
            if existing:
                return False, f"❌ Bu Telegram akkaunt boshqa ID ga bog'langan: {existing.library_id}"

            user.telegram_id = telegram_id
            user.updated_at = datetime.now()

            session.commit()
            logger.info(f"✅ Telegram bog'landi: {library_id} -> {telegram_id}")
            return True, f"✅ Telegram akkaunt muvaffaqiyatli bog'landi!\n📚 Library ID: {library_id}"

        except Exception as e:
            session.rollback()
            logger.error(f"❌ Telegram bog'lashda xato: {e}")
            return False, f"❌ Xatolik: {str(e)}"

        finally:
            session.close()

    def update_subscription(self, library_id: str, plan_name: str,
                            duration_days: int = 30) -> Tuple[bool, str]:
        """Obunani yangilash"""
        session = self.get_session()

        try:
            user = session.query(User).filter_by(library_id=library_id).first()
            if not user:
                return False, f"❌ {library_id} ID li foydalanuvchi topilmadi!"

            if plan_name not in ['Free', 'Money', 'Premium']:
                return False, "❌ Noto'g'ri tarif nomi!"

            user.subscription_plan = plan_name

            if plan_name == 'Free':
                user.subscription_end_date = None
            else:
                user.subscription_end_date = datetime.now() + timedelta(days=duration_days)

            user.updated_at = datetime.now()

            session.commit()
            logger.info(f"✅ Obuna yangilandi: {library_id} -> {plan_name}")
            return True, f"✅ Obuna yangilandi: {plan_name}"

        except Exception as e:
            session.rollback()
            logger.error(f"❌ Obuna yangilashda xato: {e}")
            return False, f"❌ Xatolik: {str(e)}"

        finally:
            session.close()

    def get_all_users(self, active_only: bool = True) -> List[User]:
        """Barcha foydalanuvchilarni olish"""
        session = self.get_session()

        try:
            query = session.query(User)

            if active_only:
                query = query.filter_by(is_active=True)

            users = query.order_by(User.registered_date.desc()).all()

            # Session dan detach qilish
            for user in users:
                session.expunge(user)

            return users
        finally:
            session.close()

    def get_statistics(self) -> dict:
        """Statistika olish"""
        session = self.get_session()

        try:
            total_users = session.query(func.count(User.id)).filter_by(is_active=True).scalar() or 0
            free_users = session.query(func.count(User.id)).filter_by(subscription_plan='Free',
                                                                      is_active=True).scalar() or 0
            money_users = session.query(func.count(User.id)).filter_by(subscription_plan='Money',
                                                                       is_active=True).scalar() or 0
            premium_users = session.query(func.count(User.id)).filter_by(subscription_plan='Premium',
                                                                         is_active=True).scalar() or 0
            telegram_users = session.query(func.count(User.id)).filter(User.telegram_id.isnot(None),
                                                                       User.is_active == True).scalar() or 0

            # O'rtacha yosh
            current_year = datetime.now().year
            avg_birth_year = session.query(func.avg(User.birth_year)).filter_by(is_active=True).scalar()
            average_age = round(current_year - avg_birth_year, 1) if avg_birth_year else 0

            return {
                'total_users': total_users,
                'free_users': free_users,
                'money_users': money_users,
                'premium_users': premium_users,
                'telegram_users': telegram_users,
                'average_age': average_age
            }
        finally:
            session.close()

    def get_users_expiring_soon(self, warning_days: int = 3) -> List[User]:
        """Obunasi tez orada tugaydigan foydalanuvchilar"""
        session = self.get_session()

        try:
            warning_date = datetime.now() + timedelta(days=warning_days)

            users = session.query(User).filter(
                User.subscription_end_date.isnot(None),
                User.subscription_end_date <= warning_date,
                User.subscription_end_date > datetime.now(),
                User.subscription_plan.in_(['Money', 'Premium']),
                User.is_active == True
            ).all()

            for user in users:
                session.expunge(user)

            return users
        finally:
            session.close()

    def get_expired_subscriptions(self) -> List[User]:
        """Muddati o'tgan obunalar"""
        session = self.get_session()

        try:
            users = session.query(User).filter(
                User.subscription_end_date.isnot(None),
                User.subscription_end_date < datetime.now(),
                User.subscription_plan.in_(['Money', 'Premium']),
                User.is_active == True
            ).all()

            for user in users:
                session.expunge(user)

            return users
        finally:
            session.close()

    def search_users(self, query: str) -> List[User]:
        """Foydalanuvchilarni qidirish"""
        session = self.get_session()

        try:
            search_pattern = f"%{query}%"

            users = session.query(User).filter(
                (User.library_id.ilike(search_pattern) |
                 User.first_name.ilike(search_pattern) |
                 User.last_name.ilike(search_pattern) |
                 User.phone_number.ilike(search_pattern)),
                User.is_active == True
            ).order_by(User.registered_date.desc()).limit(50).all()

            for user in users:
                session.expunge(user)

            return users
        finally:
            session.close()

    def deactivate_user(self, library_id: str) -> Tuple[bool, str]:
        """Foydalanuvchini deaktiv qilish"""
        session = self.get_session()

        try:
            user = session.query(User).filter_by(library_id=library_id).first()
            if not user:
                return False, f"❌ {library_id} ID li foydalanuvchi topilmadi!"

            user.is_active = False
            user.updated_at = datetime.now()

            session.commit()
            logger.info(f"✅ Foydalanuvchi deaktiv qilindi: {library_id}")
            return True, f"✅ Foydalanuvchi deaktiv qilindi: {user.full_name}"

        except Exception as e:
            session.rollback()
            logger.error(f"❌ Deaktiv qilishda xato: {e}")
            return False, f"❌ Xatolik: {str(e)}"

        finally:
            session.close()

    def activate_user(self, library_id: str) -> Tuple[bool, str]:
        """Foydalanuvchini aktiv qilish"""
        session = self.get_session()

        try:
            user = session.query(User).filter_by(library_id=library_id).first()
            if not user:
                return False, f"❌ {library_id} ID li foydalanuvchi topilmadi!"

            user.is_active = True
            user.updated_at = datetime.now()

            session.commit()
            logger.info(f"✅ Foydalanuvchi aktiv qilindi: {library_id}")
            return True, "✅ Foydalanuvchi aktiv qilindi!"

        except Exception as e:
            session.rollback()
            logger.error(f"❌ Aktiv qilishda xato: {e}")
            return False, f"❌ Xatolik: {str(e)}"

        finally:
            session.close()


    def close(self):
        """Engine ni yopish"""
        self.engine.dispose()
        logger.info("🔒 Database connection yopildi")


# Test uchun
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    db = DatabaseManager()
    print("✅ PostgreSQL Database Manager test muvaffaqiyatli!")
    db.close()