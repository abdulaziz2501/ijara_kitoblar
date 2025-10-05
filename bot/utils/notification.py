import asyncio
from datetime import datetime, timedelta
from database.db_manager import DatabaseManager
from config import WARNING_DAYS
import logging

logger = logging.getLogger(__name__)


async def send_expiry_warnings(bot):
    """Muddati tugayotgan obunalar haqida ogohlantirish"""
    while True:
        try:
            db = DatabaseManager()
            users_to_warn = db.get_users_needing_warning()

            for user in users_to_warn:
                # Oldingi ogohlantirish yuborilganini tekshirish
                if user.last_warning_sent:
                    hours_since_warning = (datetime.now() - user.last_warning_sent).total_seconds() / 3600
                    if hours_since_warning < 24:  # 24 soatda bir marta
                        continue

                days_left = (user.subscription_end_date - datetime.now()).days

                try:
                    await bot.send_message(
                        user.telegram_id,
                        f"⚠️ OGOHLANTIRISH\n\n"
                        f"Hurmatli {user.first_name}!\n\n"
                        f"📋 {user.subscription_plan} tarifingiz {days_left} kundan keyin tugaydi.\n"
                        f"📅 Tugash sanasi: {user.subscription_end_date.strftime('%d.%m.%Y')}\n\n"
                        f"Obunani yangilash uchun /subscription buyrug'ini yuboring."
                    )

                    # SMS yuborish (ixtiyoriy - SMS API kerak)
                    # await send_sms(user.phone_number, f"Kutubxona obunangiz {days_left} kundan keyin tugaydi.")

                    # Oxirgi ogohlantirish vaqtini yangilash
                    user.last_warning_sent = datetime.now()
                    db.session.commit()

                    logger.info(f"Ogohlantirish yuborildi: {user.library_id}")

                except Exception as e:
                    logger.error(f"Ogohlantirish yuborishda xatolik {user.library_id}: {e}")

            db.close()

            # Har 6 soatda bir marta tekshirish
            await asyncio.sleep(21600)

        except Exception as e:
            logger.error(f"Bildirishnoma tizimida xatolik: {e}")
            await asyncio.sleep(3600)


async def check_expired_subscriptions(bot):
    """Muddati o'tgan obunalarni tekshirish"""
    while True:
        try:
            db = DatabaseManager()
            all_users = db.get_all_users()

            for user in all_users:
                if user.subscription_plan != 'Free' and user.subscription_end_date:
                    if user.subscription_end_date < datetime.now():
                        # Free tarifga o'tkazish
                        user.subscription_plan = 'Free'
                        user.subscription_end_date = None
                        db.session.commit()

                        try:
                            await bot.send_message(
                                user.telegram_id,
                                f"⚠️ Obunangiz tugadi!\n\n"
                                f"Siz Free tarifga o'tdingiz.\n\n"
                                f"Yangi obunani /subscription orqali sotib olishingiz mumkin."
                            )
                        except:
                            pass

            db.close()

            # Har kuni bir marta tekshirish
            await asyncio.sleep(86400)

        except Exception as e:
            logger.error(f"Obunalarni tekshirishda xatolik: {e}")
            await asyncio.sleep(3600)