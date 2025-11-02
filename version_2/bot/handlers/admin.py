"""
Admin Handler - Admin paneli va boshqaruv
Ko'p adminlar, super admin tizimi bilan
"""
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from datetime import datetime

from ijara_kitoblar.database.db_manager import DatabaseManager
from ijara_kitoblar.database.admin_manager import AdminManager

router = Router()


# FSM States
class AdminStates(StatesGroup):
    """Admin qo'shish uchun state'lar"""
    waiting_for_library_id = State()
    waiting_for_approval = State()


def get_admin_keyboard():
    """Admin panel klaviaturasi"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 Statistika", callback_data="admin_stats")],
        [InlineKeyboardButton(text="👥 Foydalanuvchilar", callback_data="admin_users")],
        [InlineKeyboardButton(text="➕ Foydalanuvchi qo'shish", callback_data="admin_add_user")],
        [InlineKeyboardButton(text="✅ Tarifni tasdiqlash", callback_data="admin_approve")],
        [InlineKeyboardButton(text="🔍 Qidirish", callback_data="admin_search")],
    ])
    return keyboard


def get_super_admin_keyboard():
    """Super Admin panel klaviaturasi"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 Statistika", callback_data="admin_stats")],
        [InlineKeyboardButton(text="👥 Foydalanuvchilar", callback_data="admin_users")],
        [InlineKeyboardButton(text="➕ Foydalanuvchi qo'shish", callback_data="admin_add_user")],
        [InlineKeyboardButton(text="✅ Tarifni tasdiqlash", callback_data="admin_approve")],
        [InlineKeyboardButton(text="🔍 Qidirish", callback_data="admin_search")],
        [InlineKeyboardButton(text="👨‍💼 Adminlar", callback_data="super_admin_list")],
        [InlineKeyboardButton(text="➕ Admin qo'shish", callback_data="super_add_admin")],
    ])
    return keyboard


@router.message(Command("admin"))
async def cmd_admin(message: Message):
    """Admin panel - barcha adminlar uchun"""
    admin_manager = AdminManager()

    # Admin ekanligini tekshirish
    if not admin_manager.is_admin(message.from_user.id):
        await message.answer("❌ Sizda admin huquqi yo'q!")
        admin_manager.close()
        return

    # Admin ma'lumotlarini olish
    admin = admin_manager.get_admin_by_telegram_id(message.from_user.id)

    # Super admin bo'lsa qo'shimcha tugmalar
    if admin.is_super_admin:
        keyboard = get_super_admin_keyboard()
        welcome_text = (
            "🔐 SUPER ADMIN PANEL\n\n"
            f"👤 {admin.full_name}\n"
            f"📚 Library ID: {admin.library_id}\n\n"
            "Kerakli bo'limni tanlang:"
        )
    else:
        keyboard = get_admin_keyboard()
        welcome_text = (
            "🔐 ADMIN PANEL\n\n"
            f"👤 {admin.full_name}\n"
            f"📚 Library ID: {admin.library_id}\n\n"
            "Kerakli bo'limni tanlang:"
        )

    await message.answer(welcome_text, reply_markup=keyboard)
    admin_manager.close()


@router.callback_query(F.data == "admin_stats")
async def admin_statistics(callback: CallbackQuery):
    """Statistika ko'rsatish"""
    admin_manager = AdminManager()

    if not admin_manager.is_admin(callback.from_user.id):
        await callback.answer("❌ Ruxsat yo'q!", show_alert=True)
        admin_manager.close()
        return

    db = DatabaseManager()
    stats = db.get_statistics()
    admin_stats = admin_manager.get_admin_count()

    text = (
        "📊 STATISTIKA\n\n"
        "👥 FOYDALANUVCHILAR:\n"
        f"├─ Jami: {stats['total_users']}\n"
        f"├─ 🟢 Free: {stats['free_users']}\n"
        f"├─ 🔵 Money: {stats['money_users']}\n"
        f"├─ 🟣 Premium: {stats['premium_users']}\n"
        f"└─ 📱 Telegram: {stats['telegram_users']}\n\n"
        f"📈 O'rtacha yosh: {stats['average_age']} yosh\n\n"
        "👨‍💼 ADMINLAR:\n"
        f"├─ Jami: {admin_stats['total']}\n"
        f"├─ Super Admin: {admin_stats['super_admin']}\n"
        f"└─ Oddiy Admin: {admin_stats['regular']}"
    )

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Orqaga", callback_data="admin_back")]
    ])

    await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer()

    db.close()
    admin_manager.close()


@router.callback_query(F.data == "admin_users")
async def admin_users_list(callback: CallbackQuery):
    """Foydalanuvchilar ro'yxati"""
    admin_manager = AdminManager()

    if not admin_manager.is_admin(callback.from_user.id):
        await callback.answer("❌ Ruxsat yo'q!", show_alert=True)
        admin_manager.close()
        return

    db = DatabaseManager()
    users = db.get_all_users()
    db.close()
    admin_manager.close()

    if not users:
        await callback.message.edit_text("📂 Hozircha foydalanuvchilar yo'q")
        return

    text = "👥 FOYDALANUVCHILAR RO'YXATI\n\n"

    for user in users[:15]:  # Faqat 15 tasini ko'rsatish
        telegram_status = "✅" if user.telegram_id else "📵"
        text += (
            f"📚 {user.library_id} {telegram_status}\n"
            f"   👤 {user.full_name}\n"
            f"   📋 {user.subscription_plan}\n"
            f"   📞 {user.phone_number}\n\n"
        )

    if len(users) > 15:
        text += f"\n... va yana {len(users) - 15} ta foydalanuvchi\n"
        text += "\nQidirish uchun: /search [ism yoki ID]"

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Orqaga", callback_data="admin_back")]
    ])

    await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer()


@router.callback_query(F.data == "admin_approve")
async def admin_approve_subscription(callback: CallbackQuery):
    """Tarifni tasdiqlash"""
    admin_manager = AdminManager()

    if not admin_manager.is_admin(callback.from_user.id):
        await callback.answer("❌ Ruxsat yo'q!", show_alert=True)
        admin_manager.close()
        return

    admin_manager.close()

    await callback.message.edit_text(
        "✅ TARIFNI TASDIQLASH\n\n"
        "Buyruq formatida yuboring:\n\n"
        "📝 Format:\n"
        "/approve ID0001 Money\n"
        "yoki\n"
        "/approve ID0001 Premium\n"
        "yoki\n"
        "/approve ID0001 Free\n\n"
        "💡 Maslahat: ID raqamni to'g'ri kiriting!"
    )
    await callback.answer()


@router.message(Command("approve"))
async def process_approve(message: Message):
    """Tarifni tasdiqlash jarayoni"""
    admin_manager = AdminManager()

    if not admin_manager.is_admin(message.from_user.id):
        await message.answer("❌ Sizda admin huquqi yo'q!")
        admin_manager.close()
        return

    admin_manager.close()

    try:
        parts = message.text.split()
        if len(parts) != 3:
            await message.answer(
                "❌ Noto'g'ri format!\n\n"
                "✅ To'g'ri format:\n"
                "/approve ID0001 Money\n\n"
                "Tarif turlari: Free, Money, Premium"
            )
            return

        library_id = parts[1].upper()
        plan_name = parts[2].capitalize()

        if plan_name not in ['Free', 'Money', 'Premium']:
            await message.answer(
                "❌ Noto'g'ri tarif nomi!\n\n"
                "Faqat quyidagilar:\n"
                "• Free\n"
                "• Money\n"
                "• Premium"
            )
            return

        db = DatabaseManager()
        user = db.get_user_by_library_id(library_id)

        if not user:
            await message.answer(f"❌ {library_id} ID raqamli foydalanuvchi topilmadi!")
            db.close()
            return

        success, msg = db.update_subscription(library_id, plan_name)
        db.close()

        if success:
            await message.answer(
                f"✅ MUVAFFAQIYATLI TASDIQLANDI!\n\n"
                f"👤 {user.full_name}\n"
                f"📚 Library ID: {library_id}\n"
                f"📋 Yangi tarif: {plan_name}\n"
                f"📅 Muddat: 30 kun\n"
                f"📞 Telefon: {user.phone_number}"
            )

            # Agar foydalanuvchida telegram bo'lsa, unga xabar yuborish
            if user.telegram_id:
                try:
                    from bot.main import bot
                    await bot.send_message(
                        user.telegram_id,
                        f"✅ TARIFINGIZ TASDIQLANDI!\n\n"
                        f"📋 Yangi tarif: {plan_name}\n"
                        f"📅 Amal qilish muddati: 30 kun\n\n"
                        f"🎉 Kutubxonadan to'liq foydalanishingiz mumkin!"
                    )
                except Exception as e:
                    print(f"Foydalanuvchiga xabar yuborishda xato: {e}")
        else:
            await message.answer(msg)

    except Exception as e:
        await message.answer(f"❌ Xatolik yuz berdi: {str(e)}")


@router.callback_query(F.data == "admin_search")
async def admin_search_info(callback: CallbackQuery):
    """Qidirish haqida ma'lumot"""
    admin_manager = AdminManager()

    if not admin_manager.is_admin(callback.from_user.id):
        await callback.answer("❌ Ruxsat yo'q!", show_alert=True)
        admin_manager.close()
        return

    admin_manager.close()

    await callback.message.edit_text(
        "🔍 QIDIRISH\n\n"
        "Foydalanuvchilarni qidirish uchun\n"
        "quyidagi buyruqlardan foydalaning:\n\n"
        "📝 Format:\n"
        "/search Abdulloh\n"
        "/search ID0001\n"
        "/search +998901234567\n\n"
        "Qidirish bo'yicha natijalar\n"
        "maksimal 10 ta ko'rsatiladi."
    )
    await callback.answer()


@router.callback_query(F.data == "admin_add_user")
async def admin_add_user_callback(callback: CallbackQuery, state: FSMContext):
    """Foydalanuvchi qo'shishni boshlash"""
    admin_manager = AdminManager()

    if not admin_manager.is_admin(callback.from_user.id):
        await callback.answer("❌ Ruxsat yo'q!", show_alert=True)
        admin_manager.close()
        return

    admin_manager.close()

    await callback.message.edit_text(
        "➕ YANGI FOYDALANUVCHI QO'SHISH\n\n"
        "Bu foydalanuvchi Telegram orqali emas,\n"
        "to'g'ridan-to'g'ri kutubxonada ro'yxatdan o'tadi.\n\n"
        "Boshlash uchun buyruq yuboring:\n"
        "/adduser\n\n"
        "yoki\n\n"
        "Streamlit Dashboard dan foydalaning."
    )
    await callback.answer()


@router.message(Command("search"))
async def search_users(message: Message):
    """Foydalanuvchilarni qidirish"""
    admin_manager = AdminManager()

    if not admin_manager.is_admin(message.from_user.id):
        await message.answer("❌ Sizda admin huquqi yo'q!")
        admin_manager.close()
        return

    admin_manager.close()

    try:
        parts = message.text.split(maxsplit=1)
        if len(parts) < 2:
            await message.answer(
                "🔍 QIDIRISH\n\n"
                "Format:\n"
                "/search Abdulloh\n"
                "/search ID0001\n"
                "/search +998901234567"
            )
            return

        query = parts[1]

        db = DatabaseManager()
        users = db.search_users(query)
        db.close()

        if not users:
            await message.answer(f"❌ '{query}' bo'yicha natija topilmadi")
            return

        text = f"🔍 QIDIRUV NATIJALARI: '{query}'\n\n"

        for user in users[:10]:
            telegram_status = "✅" if user.telegram_id else "📵"
            text += (
                f"📚 {user.library_id} {telegram_status}\n"
                f"   👤 {user.full_name}\n"
                f"   📋 {user.subscription_plan}\n"
                f"   📞 {user.phone_number}\n"
                f"   🎓 {user.study_place}\n\n"
            )

        if len(users) > 10:
            text += f"\n... va yana {len(users) - 10} ta natija"

        await message.answer(text)

    except Exception as e:
        await message.answer(f"❌ Xatolik: {str(e)}")


# ========================================
# SUPER ADMIN FUNKTSIYALARI
# ========================================

@router.callback_query(F.data == "super_admin_list")
async def super_admin_list(callback: CallbackQuery):
    """Adminlar ro'yxati (faqat super admin)"""
    admin_manager = AdminManager()

    if not admin_manager.is_super_admin(callback.from_user.id):
        await callback.answer("❌ Faqat Super Admin!", show_alert=True)
        admin_manager.close()
        return

    admins = admin_manager.get_all_admins()

    if not admins:
        await callback.message.edit_text("📂 Adminlar yo'q")
        admin_manager.close()
        return

    text = "👨‍💼 ADMINLAR RO'YXATI\n\n"

    for admin in admins:
        admin_type = "⭐ SUPER" if admin.is_super_admin else "👤"
        text += (
            f"{admin_type} {admin.library_id}\n"
            f"   📝 {admin.full_name}\n"
            f"   📅 {admin.added_date.strftime('%d.%m.%Y')}\n\n"
        )

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Admin qo'shish", callback_data="super_add_admin")],
        [InlineKeyboardButton(text="➖ Admin o'chirish", callback_data="super_remove_admin")],
        [InlineKeyboardButton(text="🔙 Orqaga", callback_data="admin_back")]
    ])

    await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer()
    admin_manager.close()


@router.callback_query(F.data == "super_add_admin")
async def super_add_admin_start(callback: CallbackQuery, state: FSMContext):
    """Admin qo'shishni boshlash"""
    admin_manager = AdminManager()

    if not admin_manager.is_super_admin(callback.from_user.id):
        await callback.answer("❌ Faqat Super Admin!", show_alert=True)
        admin_manager.close()
        return

    admin_manager.close()

    await callback.message.edit_text(
        "➕ YANGI ADMIN QO'SHISH\n\n"
        "Yangi adminning Library ID sini kiriting:\n\n"
        "Format: /addadmin ID0001\n\n"
        "💡 Eslatma: Bu ID allaqachon ro'yxatdan o'tgan\n"
        "foydalanuvchiga tegishli bo'lishi kerak!"
    )
    await callback.answer()


@router.message(Command("addadmin"))
async def process_add_admin(message: Message):
    """Admin qo'shish jarayoni"""
    admin_manager = AdminManager()

    if not admin_manager.is_super_admin(message.from_user.id):
        await message.answer("❌ Faqat Super Admin yangi admin qo'sha oladi!")
        admin_manager.close()
        return

    try:
        parts = message.text.split()
        if len(parts) != 2:
            await message.answer(
                "❌ Noto'g'ri format!\n\n"
                "✅ To'g'ri format:\n"
                "/addadmin ID0001"
            )
            admin_manager.close()
            return

        library_id = parts[1].upper()

        # Foydalanuvchini topish
        db = DatabaseManager()
        user = db.get_user_by_library_id(library_id)

        if not user:
            await message.answer(f"❌ {library_id} ID raqamli foydalanuvchi topilmadi!")
            db.close()
            admin_manager.close()
            return

        # Telegram ID borligini tekshirish
        if not user.telegram_id:
            await message.answer(
                f"❌ Bu foydalanuvchi Telegram ga bog'lanmagan!\n\n"
                f"👤 {user.full_name}\n"
                f"📚 {library_id}\n\n"
                "Admin bo'lishi uchun avval Telegram akkauntni bog'lashi kerak."
            )
            db.close()
            admin_manager.close()
            return

        db.close()

        # Admin qo'shish
        success, msg = admin_manager.add_admin(
            telegram_id=user.telegram_id,
            library_id=library_id,
            full_name=user.full_name,
            added_by=message.from_user.id
        )

        if success:
            await message.answer(
                f"✅ YANGI ADMIN QO'SHILDI!\n\n"
                f"👤 {user.full_name}\n"
                f"📚 Library ID: {library_id}\n"
                f"📱 Telegram: @{message.from_user.username or 'N/A'}\n\n"
                "Admin endi /admin buyrug'i orqali\n"
                "admin paneliga kirishi mumkin!"
            )

            # Yangi adminga xabar yuborish
            try:
                from bot.main import bot
                await bot.send_message(
                    user.telegram_id,
                    f"🎉 TABRIKLAYMIZ!\n\n"
                    f"Siz admin huquqiga ega bo'ldingiz!\n\n"
                    f"Admin panelga kirish uchun:\n"
                    f"/admin buyrug'ini yuboring.\n\n"
                    f"📚 Library ID: {library_id}"
                )
            except Exception as e:
                print(f"Adminga xabar yuborishda xato: {e}")
        else:
            await message.answer(msg)

        admin_manager.close()

    except Exception as e:
        await message.answer(f"❌ Xatolik: {str(e)}")
        admin_manager.close()


@router.callback_query(F.data == "super_remove_admin")
async def super_remove_admin_start(callback: CallbackQuery):
    """Admin o'chirishni boshlash"""
    admin_manager = AdminManager()

    if not admin_manager.is_super_admin(callback.from_user.id):
        await callback.answer("❌ Faqat Super Admin!", show_alert=True)
        admin_manager.close()
        return

    admin_manager.close()

    await callback.message.edit_text(
        "➖ ADMIN O'CHIRISH\n\n"
        "O'chiriladigan adminning Library ID sini kiriting:\n\n"
        "Format: /removeadmin ID0001\n\n"
        "⚠️ Super adminni o'chirib bo'lmaydi!"
    )
    await callback.answer()


@router.message(Command("removeadmin"))
async def process_remove_admin(message: Message):
    """Admin o'chirish jarayoni"""
    admin_manager = AdminManager()

    if not admin_manager.is_super_admin(message.from_user.id):
        await message.answer("❌ Faqat Super Admin admin o'chira oladi!")
        admin_manager.close()
        return

    try:
        parts = message.text.split()
        if len(parts) != 2:
            await message.answer(
                "❌ Noto'g'ri format!\n\n"
                "✅ To'g'ri format:\n"
                "/removeadmin ID0001"
            )
            admin_manager.close()
            return

        library_id = parts[1].upper()

        success, msg = admin_manager.remove_admin(
            library_id=library_id,
            removed_by=message.from_user.id
        )

        await message.answer(msg)
        admin_manager.close()

    except Exception as e:
        await message.answer(f"❌ Xatolik: {str(e)}")
        admin_manager.close()


# ========================================
# FOYDALANUVCHI QO'SHISH (BARCHA ADMINLAR)
# ========================================

class AddUserStates(StatesGroup):
    """Yangi foydalanuvchi qo'shish uchun state'lar"""
    first_name = State()
    last_name = State()
    phone_number = State()
    birth_year = State()
    study_place = State()


@router.message(Command("adduser"))
async def cmd_add_user_start(message: Message, state: FSMContext):
    """Admin tomonidan yangi foydalanuvchi qo'shish"""
    admin_manager = AdminManager()

    if not admin_manager.is_admin(message.from_user.id):
        await message.answer("❌ Sizda admin huquqi yo'q!")
        admin_manager.close()
        return

    admin_manager.close()

    await message.answer(
        "➕ YANGI FOYDALANUVCHI QO'SHISH\n\n"
        "Bu foydalanuvchi Telegram orqali emas,\n"
        "to'g'ridan-to'g'ri kutubxonada ro'yxatdan o'tadi.\n\n"
        "1️⃣ Foydalanuvchi ismini kiriting:\n\n"
        "❌ Bekor qilish: /cancel"
    )
    await state.set_state(AddUserStates.first_name)


@router.message(AddUserStates.first_name)
async def process_add_user_first_name(message: Message, state: FSMContext):
    """Ismni qabul qilish"""
    first_name = message.text.strip()

    if len(first_name) < 2:
        await message.answer("❌ Ism kamida 2 ta harfdan iborat bo'lishi kerak. Qaytadan kiriting:")
        return

    await state.update_data(first_name=first_name)
    await message.answer("2️⃣ Familiyasini kiriting:")
    await state.set_state(AddUserStates.last_name)


@router.message(AddUserStates.last_name)
async def process_add_user_last_name(message: Message, state: FSMContext):
    """Familiyani qabul qilish"""
    last_name = message.text.strip()

    if len(last_name) < 2:
        await message.answer("❌ Familiya kamida 2 ta harfdan iborat bo'lishi kerak. Qaytadan kiriting:")
        return

    await state.update_data(last_name=last_name)
    await message.answer(
        "3️⃣ Telefon raqamini kiriting:\n\n"
        "Format: +998901234567"
    )
    await state.set_state(AddUserStates.phone_number)


@router.message(AddUserStates.phone_number)
async def process_add_user_phone(message: Message, state: FSMContext):
    """Telefon raqamni qabul qilish"""
    phone_number = message.text.strip()

    # Telefon raqamni formatlash
    if not phone_number.startswith('+'):
        if phone_number.startswith('998'):
            phone_number = '+' + phone_number
        else:
            phone_number = '+998' + phone_number.lstrip('0')

    # Telefon raqam formatini tekshirish
    if len(phone_number.replace('+', '')) < 12:
        await message.answer(
            "❌ Noto'g'ri telefon raqam!\n\n"
            "To'g'ri format: +998901234567\n"
            "Qaytadan kiriting:"
        )
        return

    await state.update_data(phone_number=phone_number)
    await message.answer("4️⃣ Tug'ilgan yilini kiriting:\n\nMasalan: 2000")
    await state.set_state(AddUserStates.birth_year)


@router.message(AddUserStates.birth_year)
async def process_add_user_birth_year(message: Message, state: FSMContext):
    """Tug'ilgan yilni qabul qilish"""
    try:
        birth_year = int(message.text.strip())
        current_year = datetime.now().year

        if birth_year < 1940 or birth_year > current_year - 5:
            await message.answer(
                f"❌ Noto'g'ri yil!\n\n"
                f"Yil 1940 dan {current_year - 5} gacha bo'lishi kerak.\n"
                f"Qaytadan kiriting:"
            )
            return

        await state.update_data(birth_year=birth_year)
        await message.answer(
            "5️⃣ Qayerda o'qiydi yoki ishlaydi?\n\n"
            "Masalan:\n"
            "• Toshkent Davlat Universiteti\n"
            "• Iqtisodiyot kolleji\n"
            "• O'qimayman / Ishlamayman"
        )
        await state.set_state(AddUserStates.study_place)

    except ValueError:
        await message.answer("❌ Iltimos, faqat raqam kiriting!")


@router.message(AddUserStates.study_place)
async def process_add_user_study_place(message: Message, state: FSMContext):
    """O'quv joyini qabul qilish va foydalanuvchini yaratish"""
    study_place = message.text.strip()

    if len(study_place) < 2:
        await message.answer("❌ Iltimos, to'g'ri ma'lumot kiriting:")
        return

    await state.update_data(study_place=study_place)
    data = await state.get_data()

    # Database ga saqlash (Telegram ID siz)
    db = DatabaseManager()
    user, error = db.create_user(
        first_name=data['first_name'],
        last_name=data['last_name'],
        phone_number=data['phone_number'],
        birth_year=data['birth_year'],
        study_place=data['study_place'],
        telegram_id=None  # Admin qo'shgan, Telegram yo'q
    )
    db.close()

    if error:
        await message.answer(f"❌ Xatolik yuz berdi:\n{error}")
        await state.clear()
        return

    # Muvaffaqiyatli qo'shildi
    await message.answer(
        "✅ FOYDALANUVCHI MUVAFFAQIYATLI QO'SHILDI!\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"👤 {user.full_name}\n"
        f"📚 Library ID: {user.library_id}\n"
        f"👶 Yosh: {user.age}\n"
        f"🎓 {user.study_place}\n"
        f"📞 {user.phone_number}\n"
        f"📋 Tarif: {user.subscription_plan}\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        f"🆔 Library ID: {user.library_id}\n\n"
        "📝 Bu ID ni foydalanuvchiga bering!\n"
        "Foydalanuvchi keyinchalik /link buyrug'i orqali\n"
        "o'z Telegram akkauntini bog'lashi mumkin.\n\n"
        "💡 Tarifni tasdiqlash: /approve {user.library_id} Money"
    )

    await state.clear()


@router.callback_query(F.data == "admin_back")
async def admin_back(callback: CallbackQuery):
    """Orqaga qaytish"""
    admin_manager = AdminManager()

    admin = admin_manager.get_admin_by_telegram_id(callback.from_user.id)

    if admin.is_super_admin:
        keyboard = get_super_admin_keyboard()
        text = "🔐 SUPER ADMIN PANEL\n\nKerakli bo'limni tanlang:"
    else:
        keyboard = get_admin_keyboard()
        text = "🔐 ADMIN PANEL\n\nKerakli bo'limni tanlang:"

    await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer()
    admin_manager.close()