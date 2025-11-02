from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True, nullable=False)
    library_id = Column(String(10), unique=True, nullable=False)  # ID0001 formatida
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    phone_number = Column(String(20), nullable=False)
    birth_year = Column(Integer, nullable=False)
    age = Column(Integer, nullable=False)
    subscription_plan = Column(String(20), default='Free')
    subscription_end_date = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    registered_date = Column(DateTime, default=datetime.now)
    last_warning_sent = Column(DateTime, nullable=True)

    def __repr__(self):
        return f"<User(library_id='{self.library_id}', name='{self.first_name} {self.last_name}')>"