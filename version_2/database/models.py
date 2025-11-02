"""
Database Models - PostgreSQL
SQLAlchemy ORM modellari - faqat PostgreSQL uchun
"""
from sqlalchemy import Column, Integer, BigInteger, String, DateTime, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class User(Base):
    """
    Foydalanuvchi modeli

    MUHIM:
    - library_id - asosiy identifikator (ID0001, ID0002...)
    - telegram_id - ixtiyoriy (nullable), ba'zi foydalanuvchilar telegram orqali emas
    """
    __tablename__ = 'users'

    # Asosiy maydonlar
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Library ID - asosiy identifikator (UNIQUE va NOT NULL)
    library_id = Column(String(10), unique=True, nullable=False, index=True)

    # Telegram ID - ixtiyoriy, BigInteger ishlatamiz (Telegram ID katta)
    telegram_id = Column(BigInteger, unique=True, nullable=True, index=True)

    # Shaxsiy ma'lumotlar
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    phone_number = Column(String(20), nullable=False, index=True)
    birth_year = Column(Integer, nullable=False)
    study_place = Column(String(200), nullable=False)

    # Obuna ma'lumotlari
    subscription_plan = Column(String(20), default='Free', nullable=False)
    subscription_end_date = Column(DateTime, nullable=True)

    # Status
    is_active = Column(Boolean, default=True, nullable=False)

    # Vaqt belgilari
    registered_date = Column(DateTime, default=datetime.now, nullable=False)
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    last_warning_sent = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    def __repr__(self):
        return f"<User(library_id='{self.library_id}', name='{self.first_name} {self.last_name}')>"

    @property
    def age(self):
        """Yoshni hisoblash"""
        current_year = datetime.now().year
        return current_year - self.birth_year

    @property
    def full_name(self):
        """To'liq ism"""
        return f"{self.first_name} {self.last_name}"

    @property
    def is_subscription_expired(self):
        """Obuna muddati o'tganligini tekshirish"""
        if self.subscription_plan == 'Free':
            return False
        if not self.subscription_end_date:
            return False
        return datetime.now() > self.subscription_end_date

    @property
    def days_until_expiry(self):
        """Obuna muddati tugashiga qancha kun qolgan"""
        if self.subscription_plan == 'Free' or not self.subscription_end_date:
            return None
        delta = self.subscription_end_date - datetime.now()
        return max(0, delta.days)


class Admin(Base):
    """
    Admin modeli

    Adminlar ham kutubxona foydalanuvchilari, lekin qo'shimcha huquqlarga ega
    """
    __tablename__ = 'admins'

    # Asosiy maydonlar
    admin_id = Column(Integer, primary_key=True, autoincrement=True)

    # Telegram ID - adminlar uchun majburiy (BigInteger)
    telegram_id = Column(BigInteger, unique=True, nullable=False, index=True)

    # Library ID - User jadvalidagi library_id ga bog'langan
    library_id = Column(String(10), unique=True, nullable=False, index=True)

    # Admin ma'lumotlari
    full_name = Column(String(200), nullable=False)
    is_super_admin = Column(Boolean, default=False, nullable=False)

    # Qo'shilish ma'lumotlari
    added_date = Column(DateTime, default=datetime.now, nullable=False)
    added_by = Column(BigInteger, nullable=True)  # Qaysi admin qo'shgan (telegram_id)

    # Status
    is_active = Column(Boolean, default=True, nullable=False)

    def __repr__(self):
        admin_type = "Super Admin" if self.is_super_admin else "Admin"
        return f"<{admin_type}(library_id='{self.library_id}', name='{self.full_name}')>"


class Notification(Base):
    """
    Bildirishnomalar modeli
    Yuborilgan bildirishnomalarni kuzatish uchun
    """
    __tablename__ = 'notifications'

    id = Column(Integer, primary_key=True, autoincrement=True)
    library_id = Column(String(10), nullable=False, index=True)
    telegram_id = Column(BigInteger, nullable=True, index=True)
    notification_type = Column(String(50), nullable=False)  # 'warning', 'expired', 'approved'
    message = Column(Text, nullable=False)
    sent_date = Column(DateTime, default=datetime.now, nullable=False)
    is_read = Column(Boolean, default=False, nullable=False)

    def __repr__(self):
        return f"<Notification(library_id='{self.library_id}', type='{self.notification_type}')>"


# Index'lar avtomatik yaratiladi yuqorida index=True orqali
# Agar qo'shimcha index kerak bo'lsa:
"""
CREATE INDEX idx_users_subscription_plan ON users(subscription_plan);
CREATE INDEX idx_users_is_active ON users(is_active);
CREATE INDEX idx_users_subscription_end ON users(subscription_end_date);
CREATE INDEX idx_notifications_sent_date ON notifications(sent_date);
"""


if __name__ == "__main__":
    from sqlalchemy import create_engine
    from ijara_kitoblar.config import DATABASE_URL

    # Test - jadvallarni yaratish
    engine = create_engine(DATABASE_URL, echo=True)
    Base.metadata.create_all(engine)
    print("✅ PostgreSQL jadvallar yaratildi!")
    engine.dispose()
