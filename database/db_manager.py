from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from database.models import Base, User
from config import DATABASE_URL
from datetime import datetime, timedelta


class DatabaseManager:
    def __init__(self):
        self.engine = create_engine(DATABASE_URL)
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    def generate_library_id(self):
        """Unique kutubxona ID yaratish"""
        last_user = self.session.query(User).order_by(User.id.desc()).first()

        if last_user and last_user.library_id:
            last_number = int(last_user.library_id[2:])  # ID0001 -> 1
            new_number = last_number + 1
        else:
            new_number = 1

        if new_number > 9999:
            raise ValueError("Maksimal foydalanuvchilar soni to'ldi!")

        return f"ID{new_number:04d}"

    def create_user(self, telegram_id, first_name, last_name, phone_number, birth_year):
        """Yangi foydalanuvchi yaratish"""
        # Avval tekshirish
        existing_user = self.session.query(User).filter_by(telegram_id=telegram_id).first()
        if existing_user:
            return None, "Siz allaqachon ro'yxatdan o'tgansiz!"

        current_year = datetime.now().year
        age = current_year - birth_year
        library_id = self.generate_library_id()

        new_user = User(
            telegram_id=telegram_id,
            library_id=library_id,
            first_name=first_name,
            last_name=last_name,
            phone_number=phone_number,
            birth_year=birth_year,
            age=age,
            subscription_plan='Free'
        )

        self.session.add(new_user)
        self.session.commit()
        return new_user, None

    def get_user_by_telegram_id(self, telegram_id):
        """Telegram ID orqali foydalanuvchi topish"""
        return self.session.query(User).filter_by(telegram_id=telegram_id).first()

    def get_user_by_library_id(self, library_id):
        """Kutubxona ID orqali foydalanuvchi topish"""
        return self.session.query(User).filter_by(library_id=library_id).first()

    def update_subscription(self, library_id, plan_name):
        """Obuna rejasini yangilash"""
        from config import SUBSCRIPTION_PLANS

        user = self.get_user_by_library_id(library_id)
        if not user:
            return False

        user.subscription_plan = plan_name

        if plan_name != 'Free':
            duration = SUBSCRIPTION_PLANS[plan_name]['duration_days']
            user.subscription_end_date = datetime.now() + timedelta(days=duration)
        else:
            user.subscription_end_date = None

        self.session.commit()
        return True

    def get_statistics(self):
        """Statistika olish"""
        total_users = self.session.query(func.count(User.id)).scalar()

        free_users = self.session.query(func.count(User.id)).filter_by(subscription_plan='Free').scalar()
        money_users = self.session.query(func.count(User.id)).filter_by(subscription_plan='Money').scalar()
        premium_users = self.session.query(func.count(User.id)).filter_by(subscription_plan='Premium').scalar()

        avg_age = self.session.query(func.avg(User.age)).scalar()

        return {
            'total_users': total_users,
            'free_users': free_users,
            'money_users': money_users,
            'premium_users': premium_users,
            'average_age': round(avg_age, 1) if avg_age else 0
        }

    def get_users_needing_warning(self):
        """Ogohlantirish kerak bo'lgan foydalanuvchilar"""
        from config import WARNING_DAYS

        warning_date = datetime.now() + timedelta(days=WARNING_DAYS)

        users = self.session.query(User).filter(
            User.subscription_plan != 'Free',
            User.subscription_end_date <= warning_date,
            User.subscription_end_date >= datetime.now()
        ).all()

        return users

    def get_all_users(self):
        """Barcha foydalanuvchilar"""
        return self.session.query(User).all()

    def close(self):
        self.session.close()