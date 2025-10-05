from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from database.db_manager import DatabaseManager
from config import ADMIN_ID

router = Router()


def is_admin(user_id: int) -> bool:
    """Admin ekanligini tekshirish"""
    return str(user_id) == str(ADMIN_ID)


@router.message(Command("admin"))
async def cmd_admin(message: Message):
    if not is_admin(message.from_user.id):
        await message.answer("❌ Sizda admin huquqi yo'q!")
        return

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 Statistika", callback_data="admin_stats")],
        [InlineKeyboardButton(text="👥 Foydalanuvchilar ro'yxati", callback_data="admin_users")],
        [InlineKeyboardButton(text="✅ Tarifni tasdiqlash", callback_data="admin_approve")]
    ])

    await message.answer(
        "🔐 Admin panel\n\n"
        "Kerakli bo'limni tanlang:",
        reply_markup=keyboard
    )


@router.callback_query(F.data == "admin_stats")
async def admin_statistics(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Ruxsat yo'q!", show_alert=True)
        return

    db = DatabaseManager()
    stats = db.get_statistics()
    db.close()

    text = (
        "📊 STATISTIKA\n\n"
        f"👥 Jami foydalanuvchilar: {stats['total_users']}\n"
        f"📗 Free: {stats['free_users']}\n"
        f"📘 Money: {stats['money_users']}\n"
        f"📕 Premium: {stats['premium_users']}\n\n"
        f"📈 O'rtacha yosh: {stats['average_age']} yosh"
    )

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Orqaga", callback_data="admin_back")]
    ])

    await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer()


@router.callback_query(F.data == "admin_users")
async def admin_users_list(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Ruxsat yo'q!", show_alert=True)
        return

    db = DatabaseManager()
    users = db.get_all_users()
    db.close()

    if not users:
        await callback.message.edit_text("📝 Hozircha foydalanuvchilar yo'q")
        return

    text = "👥 FOYDALANUVCHILAR RO'YXATI\n\n"

    for user in users[:20]:  # Faqat 20 tasini ko'rsatish
        status = "✅" if user.is_active else "❌"
        text += (
            f"{status} {user.library_id}\n"
            f"   👤 {user.first_name} {user.last_name}\n"
            f"   📋 {user.subscription_plan}\n"
            f"   📞 {user.phone_number}\n\n"
        )

    if len(users) > 20:
        text += f"\n... va yana {len(users) - 20} ta foydalanuvchi"

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Orqaga", callback_data="admin_back")]
    ])

    await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer()


@router.callback_query(F.data == "admin_approve")
async def admin_approve_subscription(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Ruxsat yo'q!", show_alert=True)
        return

    await callback.message.edit_text(
        "✅ Tarifni tasdiqlash\n\n"
        "Foydalanuvchi ID raqamini kiriting:\n"
        "Format: /approve ID0001 Money\n\n"
        "yoki\n\n"
        "/approve ID0001 Premium"
    )
    await callback.answer()


@router.message(Command("approve"))
async def process_approve(message: Message):
    if not is_admin(message.from_user.id):
        await message.answer("❌ Sizda admin huquqi yo'q!")
        return

    try:
        parts = message.text.split()
        if len(parts) != 3:
            await message.answer(
                "❌ Noto'g'ri format!\n\n"
                "To'g'ri format:\n"
                "/approve ID0001 Money"
            )
            return

        library_id = parts[1]
        plan_name = parts[2]

        if plan_name not in ['Free', 'Money', 'Premium']:
            await message.answer("❌ Noto'g'ri tarif nomi! (Free, Money, Premium)")
            return

        db = DatabaseManager()
        user = db.get_user_by_library_id(library_id)

        if not user:
            await message.answer(f"❌ {library_id} ID raqamli foydalanuvchi topilmadi!")
            db.close()
            return

        success = db.update_subscription(library_id, plan_name)
        db.close()

        if success:
            await message.answer(
                f"✅ Muvaffaqiyatli!\n\n"
                f"👤 {user.first_name} {user.last_name}\n"
                f"📚 ID: {library_id}\n"
                f"📋 Yangi tarif: {plan_name}\n"
                f"📅 Muddat: 30 kun"
            )

            # Foydalanuvchiga xabar yuborish
            try:
                from bot.main import bot
                await bot.send_message(
                    user.telegram_id,
                    f"✅ Tarifingiz tasdiqlandi!\n\n"
                    f"📋 Yangi tarif: {plan_name}\n"
                    f"📅 Amal qilish muddati: 30 kun\n\n"
                    f"Kutubxonadan foydalanishingiz mumkin!"
                )
            except:
                pass
        else:
            await message.answer("❌ Xatolik yuz berdi!")

    except Exception as e:
        await message.answer(f"❌ Xatolik: {str(e)}")


@router.callback_query(F.data == "admin_back")
async def admin_back(callback: CallbackQuery):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 Statistika", callback_data="admin_stats")],
        [InlineKeyboardButton(text="👥 Foydalanuvchilar ro'yxati", callback_data="admin_users")],
        [InlineKeyboardButton(text="✅ Tarifni tasdiqlash", callback_data="admin_approve")]
    ])

    await callback.message.edit_text(
        "🔐 Admin panel\n\n"
        "Kerakli bo'limni tanlang:",
        reply_markup=keyboard
    )
    await callback.answer()