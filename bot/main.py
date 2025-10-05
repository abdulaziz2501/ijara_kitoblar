import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN
from bot.handlers import registration, subscription, admin
from bot.utils.notification import send_expiry_warnings, check_expired_subscriptions

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


async def on_startup():
    """Bot ishga tushganda"""
    logger.info("Bot ishga tushdi!")

    # Background tasklar
    asyncio.create_task(send_expiry_warnings(bot))
    asyncio.create_task(check_expired_subscriptions(bot))


async def on_shutdown():
    """Bot to'xtaganda"""
    logger.info("Bot to'xtatilmoqda...")
    await bot.session.close()


async def main():
    # Handlerlarni ro'yxatdan o'tkazish
    dp.include_router(registration.router)
    dp.include_router(subscription.router)
    dp.include_router(admin.router)

    # Startup va shutdown eventlari
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    # Botni ishga tushirish
    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await bot.session.close()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot to'xtatildi!")