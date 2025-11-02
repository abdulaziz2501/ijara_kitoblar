"""
Notification Utils - Bildirishnomalar yuborish
"""
import asyncio
from datetime import datetime, timedelta
from ijara_kitoblar.database.db_manager import DatabaseManager
import logging

logger = logging.getLogger(__name__)


async def send_expiry_warnings(bot):
    """
    Obuna tugashiga 3 kun qolganda ogohlantirish yuborish
    Har kuni bir marta ishlaydi
    """
    logger.info("📢 Bildirishnoma tizimi ishga tushdi (Ogohlantirish)")
    
    while True:
        try:
            db = DatabaseManager()
            
            # 3 kun qolganlarni topish
            warning_days = 3
            users = db.get_users_expiring_soon(warning_days)
            
            sent_count = 0
            error_count = 0
            
            for user in users:
                # Faqat Telegram ID bor foydalanuvchilarga yuborish
                if not user.telegram_id:
                    continue
                
                if user.subscription_plan in ['Money', 'Premium'] and user.subscription_end_date:
                    days_left = (user.subscription_end_date - datetime.now()).days
                    
                    if days_left < 0:
                        continue  # Muddati allaqachon o'tgan
                    
                    try:
                        await bot.send_message(
                            user.telegram_id,
                            f"⚠️ OGOHLANTIRISH!\n\n"
                            f"━━━━━━━━━━━━━━━━━━━━\n"
                            f"📚 Library ID: {user.library_id}\n"
                            f"👤 {user.full_name}\n"
                            f"📋 Tarif: {user.subscription_plan}\n"
                            f"━━━━━━━━━━━━━━━━━━━━\n\n"
                            f"⏰ Obunangiz tugashiga {days_left} kun qoldi!\n\n"
                            f"💡 Obunani uzaytirish uchun:\n"
                            f"   /subscription\n\n"
                            f"📌 Agar obuna tugasa, avtomatik ravishda\n"
                            f"   Free rejimga o'tasiz."
                        )
                        sent_count += 1
                        await asyncio.sleep(0.5)  # Rate limiting
                    
                    except Exception as e:
                        error_count += 1
                        logger.error(f"Xabar yuborishda xato (user {user.library_id}): {e}")
            
            db.close()
            
            if sent_count > 0 or error_count > 0:
                logger.info(f"✅ Ogohlantirish yuborildi: {sent_count} ta, Xatolar: {error_count} ta")
        
        except Exception as e:
            logger.error(f"❌ Ogohlantirish yuborishda xato: {e}")
        
        # Har kuni bir marta tekshirish (24 soat)
        await asyncio.sleep(86400)


async def check_expired_subscriptions(bot):
    """
    Muddati o'tgan obunalarni tekshirish va Free rejimga o'tkazish
    Har 6 soatda bir marta ishlaydi
    """
    logger.info("📢 Bildirishnoma tizimi ishga tushdi (Muddat tekshirish)")
    
    while True:
        try:
            db = DatabaseManager()
            
            # Muddati o'tganlarni topish
            expired_users = db.get_expired_subscriptions()
            
            updated_count = 0
            error_count = 0
            
            for user in expired_users:
                if user.subscription_plan in ['Money', 'Premium']:
                    # Avtomatik Free rejimga o'tkazish
                    old_plan = user.subscription_plan
                    success, msg = db.update_subscription(user.library_id, 'Free')
                    
                    if success:
                        updated_count += 1
                        
                        # Faqat Telegram ID bor bo'lsa xabar yuborish
                        if user.telegram_id:
                            try:
                                await bot.send_message(
                                    user.telegram_id,
                                    f"📢 OBUNA TUGADI!\n\n"
                                    f"━━━━━━━━━━━━━━━━━━━━\n"
                                    f"📚 Library ID: {user.library_id}\n"
                                    f"👤 {user.full_name}\n"
                                    f"━━━━━━━━━━━━━━━━━━━━\n\n"
                                    f"❌ Sizning {old_plan} obunangiz muddati tugadi.\n"
                                    f"✅ Avtomatik ravishda Free rejimga o'tdingiz.\n\n"
                                    f"💰 Yangi obuna sotib olish:\n"
                                    f"   /subscription\n\n"
                                    f"📚 Free rejimda kutubxonadan cheklangan\n"
                                    f"   foydalanishingiz mumkin."
                                )
                                await asyncio.sleep(0.5)  # Rate limiting
                            
                            except Exception as e:
                                error_count += 1
                                logger.error(f"Xabar yuborishda xato (user {user.library_id}): {e}")
                        else:
                            # Telegram ID yo'q bo'lsa faqat log qilish
                            logger.info(f"📝 {user.library_id} ({user.full_name}) - Free rejimga o'tdi (Telegram yo'q)")
            
            db.close()
            
            if updated_count > 0 or error_count > 0:
                logger.info(f"✅ Free rejimga o'tkazildi: {updated_count} ta, Xatolar: {error_count} ta")
        
        except Exception as e:
            logger.error(f"❌ Obunalarni tekshirishda xato: {e}")
        
        # Har 6 soatda bir marta tekshirish
        await asyncio.sleep(21600)


async def send_notification_to_user(bot, library_id: str, message: str) -> bool:
    """
    Foydalanuvchiga bildirishnoma yuborish
    
    Args:
        bot: Bot instance
        library_id: Library ID
        message: Yuborish uchun xabar
        
    Returns:
        bool: Muvaffaqiyatli yuborildi yoki yo'q
    """
    try:
        db = DatabaseManager()
        user = db.get_user_by_library_id(library_id)
        db.close()
        
        if not user:
            logger.warning(f"⚠️ Foydalanuvchi topilmadi: {library_id}")
            return False
        
        if not user.telegram_id:
            logger.warning(f"⚠️ Telegram ID yo'q: {library_id}")
            return False
        
        await bot.send_message(user.telegram_id, message)
        logger.info(f"✅ Xabar yuborildi: {library_id}")
        return True
    
    except Exception as e:
        logger.error(f"❌ Xabar yuborishda xato ({library_id}): {e}")
        return False


async def send_notification_to_admins(bot, message: str):
    """
    Barcha adminlarga bildirishnoma yuborish
    
    Args:
        bot: Bot instance
        message: Yuborish uchun xabar
    """
    try:
        from ijara_kitoblar.database.admin_manager import AdminManager
        
        admin_manager = AdminManager()
        admins = admin_manager.get_all_admins()
        admin_manager.close()
        
        sent_count = 0
        
        for admin in admins:
            try:
                await bot.send_message(admin.telegram_id, message)
                sent_count += 1
                await asyncio.sleep(0.3)  # Rate limiting
            except Exception as e:
                logger.error(f"Admin ga xabar yuborishda xato ({admin.library_id}): {e}")
        
        logger.info(f"✅ Adminlarga xabar yuborildi: {sent_count}/{len(admins)}")
    
    except Exception as e:
        logger.error(f"❌ Adminlarga xabar yuborishda xato: {e}")
