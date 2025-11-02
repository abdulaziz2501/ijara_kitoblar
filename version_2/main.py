"""
Main Bot File - Botning asosiy ishga tushirish fayli
"""
import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from ijara_kitoblar.config import BOT_TOKEN, SUPER_ADMIN_ID
from bot.handlers import registration, subscription, admin
from bot.utils.notification import send_expiry_warnings, check_expired_subscriptions
from ijara_kitoblar.database.admin_manager import AdminManager
from ijara_kitoblar.database.db_manager import DatabaseManager

# Logging sozlash
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Bot va Dispatcher yaratish
bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)

storage = MemoryStorage()
dp = Dispatcher(storage=storage)


async def init_super_admin():
    """
    Bot birinchi marta ishga tushganda Super Admin yaratish
    """
    try:
        if not SUPER_ADMIN_ID:
            logger.warning("⚠️ SUPER_ADMIN_ID .env faylda belgilanmagan!")
            return
        
        admin_manager = AdminManager()
        
        # Super admin borligini tekshirish
        super_admin = admin_manager.get_super_admin()
        
        if super_admin:
            logger.info(f"✅ Super Admin mavjud: {super_admin.full_name} ({super_admin.library_id})")
            admin_manager.close()
            return
        
        # Super Admin uchun database da user yaratish kerak
        db = DatabaseManager()
        
        # Super Admin ning Library ID sini tekshirish
        super_admin_library_id = "ID0000"  # Super Admin uchun maxsus ID
        
        existing_user = db.get_user_by_library_id(super_admin_library_id)
        
        if not existing_user:
            # Super Admin userini yaratish
            user, error = db.create_user(
                first_name="Abdulaziz",
                last_name="Abduhakimov",
                phone_number="+998998832501",
                birth_year=2000,
                study_place="System Administrator",
                telegram_id=int(SUPER_ADMIN_ID)
            )
            
            if error:
                logger.error(f"❌ Super Admin user yaratishda xato: {error}")
                db.close()
                admin_manager.close()
                return
            
            # Library ID ni ID0000 ga o'zgartirish (maxsus super admin ID)
            # Bu juda muhim: Super Admin har doim ID0000 bo'ladi
            logger.info(f"✅ Super Admin user yaratildi: {user.library_id}")
        else:
            logger.info(f"✅ Super Admin user mavjud: {super_admin_library_id}")
        
        db.close()
        
        # Endi Super Admin qo'shish
        try:
            # Telegram ma'lumotlarini olish
            super_admin_info = await bot.get_chat(int(SUPER_ADMIN_ID))
            full_name = super_admin_info.full_name or "Super Admin"
            
            success, msg = admin_manager.add_super_admin(
                telegram_id=int(SUPER_ADMIN_ID),
                library_id=super_admin_library_id,
                full_name=full_name
            )
            
            if success:
                logger.info(f"✅ {msg}")
                
                # Super Admin ga xabar yuborish
                try:
                    await bot.send_message(
                        int(SUPER_ADMIN_ID),
                        "🎉 Siz Super Admin sifatida belgilangansiz!\n\n"
                        f"📚 Library ID: {super_admin_library_id}\n\n"
                        "Admin panel: /admin"
                    )
                except Exception as e:
                    logger.error(f"Super Admin ga xabar yuborishda xato: {e}")
            else:
                logger.warning(f"⚠️ {msg}")
        
        except Exception as e:
            logger.error(f"❌ Super Admin ma'lumotlarini olishda xato: {e}")
        
        admin_manager.close()
    
    except Exception as e:
        logger.error(f"❌ Super Admin yaratishda xato: {e}")


async def on_startup():
    """Bot ishga tushganda"""
    logger.info("🚀 Bot ishga tushmoqda...")
    
    # Super Admin yaratish
    await init_super_admin()
    
    logger.info("✅ Bot muvaffaqiyatli ishga tushdi!")
    
    # Background tasklar - bildirishnomalar
    asyncio.create_task(send_expiry_warnings(bot))
    asyncio.create_task(check_expired_subscriptions(bot))


async def on_shutdown():
    """Bot to'xtaganda"""
    logger.info("⏹️ Bot to'xtatilmoqda...")
    await bot.session.close()
    logger.info("✅ Bot to'xtatildi!")


async def main():
    """Asosiy funksiya"""
    # Handlerlarni ro'yxatdan o'tkazish
    dp.include_router(registration.router)
    dp.include_router(subscription.router)
    dp.include_router(admin.router)
    
    # Startup va shutdown eventlari
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    
    # Botni ishga tushirish
    try:
        logger.info("📡 Polling boshlanmoqda...")
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    except Exception as e:
        logger.error(f"❌ Botda xato: {e}")
    finally:
        await bot.session.close()


if __name__ == '__main__':
    try:
        print("=" * 50)
        print("📚 KUTUBXONA BOT")
        print("=" * 50)
        print("🤖 Bot ishga tushirilmoqda...")
        print("=" * 50)
        
        asyncio.run(main())
    
    except KeyboardInterrupt:
        logger.info("⏹️ Bot foydalanuvchi tomonidan to'xtatildi!")
    except Exception as e:
        logger.error(f"❌ Kritik xato: {e}")
