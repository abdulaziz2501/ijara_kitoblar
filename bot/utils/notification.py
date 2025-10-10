import asyncio
from datetime import datetime, timedelta
from database.db_manager import DatabaseManager


async def send_expiry_warnings(bot):
    """Obuna tugashiga 3 kun qolganda ogohlantirish yuborish"""
    while True:
        try:
            db = DatabaseManager()
            
            # 3 kun qolganlarni topish
            warning_date = datetime.now() + timedelta(days=3)
            users = db.get_users_expiring_soon(warning_date)
            
            for user in users:
                if user.subscription_plan in ['Money', 'Premium']:
                    days_left = (user.subscription_end_date - datetime.now()).days
                    
                    try:
                        await bot.send_message(
                            user.telegram_id,
                            f"⚠️ OGOHLANTIRISH!\n\n"
                            f"📋 Sizning {user.subscription_plan} obunangiz tugashiga {days_left} kun qoldi!\n\n"
                            f"💡 Obunani uzaytirish uchun: /subscription\n\n"
                            f"📌 Agar obuna tugasa, avtomatik ravishda Free rejimga o'tasiz."
                        )
                    except Exception as e:
                        print(f"Xabar yuborishda xato (user {user.telegram_id}): {e}")
            
            db.close()
            
        except Exception as e:
            print(f"Ogohlantirish yuborishda xato: {e}")
        
        # Har kuni bir marta tekshirish
        await asyncio.sleep(86400)  # 24 soat


async def check_expired_subscriptions(bot):
    """Muddati o'tgan obunalarni tekshirish va Free rejimga o'tkazish"""
    while True:
        try:
            db = DatabaseManager()
            
            # Muddati o'tganlarni topish
            expired_users = db.get_expired_subscriptions()
            
            for user in expired_users:
                if user.subscription_plan in ['Money', 'Premium']:
                    # Avtomatik Free rejimga o'tkazish
                    old_plan = user.subscription_plan
                    db.update_subscription(user.library_id, 'Free')
                    
                    try:
                        await bot.send_message(
                            user.telegram_id,
                            f"📢 OBUNA TUGADI!\n\n"
                            f"❌ Sizning {old_plan} obunangiz muddati tugadi.\n"
                            f"✅ Avtomatik ravishda Free rejimga o'tdingiz.\n\n"
                            f"💰 Yangi obuna sotib olish: /subscription\n\n"
                            f"📚 Free rejimda kutubxonadan cheklangan foydalanishingiz mumkin."
                        )
                    except Exception as e:
                        print(f"Xabar yuborishda xato (user {user.telegram_id}): {e}")
            
            db.close()
            
        except Exception as e:
            print(f"Obunalarni tekshirishda xato: {e}")
        
        # Har 6 soatda bir marta tekshirish
        await asyncio.sleep(21600)  # 6 soat
