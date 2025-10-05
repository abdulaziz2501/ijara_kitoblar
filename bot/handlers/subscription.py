from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from database.db_manager import DatabaseManager
from config import SUBSCRIPTION_PLANS

router = Router()


@router.message(Command("subscription"))
async def cmd_subscription(message: Message):
    db = DatabaseManager()
    user = db.get_user_by_telegram_id(message.from_user.id)
    db.close()

    if not user:
        await message.answer("❌ Avval ro'yxatdan o'ting: /start")
        return

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📗 Free (0 so'm)", callback_data="plan_Free")],
        [InlineKeyboardButton(text="📘 Money (1000 so'm)", callback_data="plan_Money")],
        [InlineKeyboardButton(text="📕 Premium (2000 so'm)", callback_data="plan_Premium")]
    ])

    sub_info = ""
    if user.subscription_end_date:
        days_left = (user.subscription_end_date - datetime.now()).days
        sub_info = f"\n⏳ Obuna tugashiga: {days_left} kun"

    await message.answer(
        f"📋 Hozirgi tarif: {user.subscription_plan}{sub_info}\n\n"
        "Yangi tarifni tanlang:",
        reply_markup=keyboard
    )


@router.callback_query(F.data.startswith("plan_"))
async def process_plan_selection(callback: CallbackQuery):
    plan_name = callback.data.split("_")[1]
    plan = SUBSCRIPTION_PLANS[plan_name]

    if plan_name == "Free":
        db = DatabaseManager()
        user = db.get_user_by_telegram_id(callback.from_user.id)

        if user:
            db.update_subscription(user.library_id, plan_name)
            await callback.message.edit_text(
                f"✅ {plan_name} tarifga o'tdingiz!\n\n"
                f"Bu tarif bepul va cheksiz."
            )
        db.close()
    else:
        db = DatabaseManager()
        user = db.get_user_by_telegram_id(callback.from_user.id)
        db.close()

        await callback.message.edit_text(
            f"💳 {plan_name} tarif\n"
            f"💰 Narx: {plan['price']} so'm\n"
            f"📅 Muddat: {plan['duration_days']} kun\n\n"
            f"To'lovni amalga oshiring va kvitansiyani kutubxonachiga ko'rsating.\n\n"
            f"📚 Sizning ID raqamingiz: {user.library_id}\n\n"
            f"✅ Admin tasdiqlashidan keyin obunangiz faollashadi."
        )

    await callback.answer()