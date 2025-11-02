"""
Registration Handler - Ro'yxatdan o'tish va bog'lash
Yangi foydalanuvchilar ro'yxatdan o'tishi va mavjud foydalanuvchilar
Library ID ga telegram akkauntni bog'lashi mumkin
"""
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from ijara_kitoblar.database.db_manager import DatabaseManager
from datetime import datetime

router = Router()


class Registration(StatesGroup):
    """Yangi foydalanuvchi ro'yxatdan o'tish"""
    first_name = State()
    last_name = State()
    phone_number = State()
    birth_year = State()
    study_place = State()


class LinkAccount(StatesGroup):
    """Mavjud Library ID ga telegram bog'lash"""
    library_id = State()
    phone_verification = State()


@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    """Start buyrug'i - ro'yxatdan o'tish yoki akkaunt ma'lumotlari"""
    db = DatabaseManager()
    user = db.get_user_by_telegram_id(message.from_user.id)
    db.close()
    
    if user:
        # Foydalanuvchi allaqachon ro'yxatdan o'tgan
        await message.answer(
            f"👋 Xush kelibsiz, {user.first_name}!\n\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"📚 Library ID: {user.library_id}\n"
            f"📋 Tarif: {user.subscription_plan}\n"
            f"👤 Yosh: {user.age}\n"
            f"🎓 {user.study_place}\n"
            f"📞 {user.phone_number}\n"
            f"━━━━━━━━━━━━━━━━━━━━\n\n"
            f"💡 Tarifni o'zgartirish: /subscription\n"
            f"📖 Yordam: /help\n"
            f"🔗 Library ID ni bog'lash: /link"
        )
    else:
        # Yangi foydalanuvchi
        await message.answer(
            "👋 Assalomu alaykum! Kutubxona botiga xush kelibsiz!\n\n"
            "📝 IKKI XIL RO'YXATDAN O'TISH:\n\n"
            "1️⃣ YANGI RO'YXAT (Kutubxonada hali ID yo'q)\n"
            "   └─ /register - Yangi ro'yxatdan o'tish\n\n"
            "2️⃣ MAVJUD AKKAUNTNI BOG'LASH\n"
            "   └─ /link - Library ID ni bog'lash\n\n"
            "💡 Agar sizda allaqachon Library ID bor bo'lsa,\n"
            "uni Telegram akkauntingizga bog'lashingiz mumkin."
        )


@router.message(Command("register"))
async def cmd_register(message: Message, state: FSMContext):
    """Yangi ro'yxatdan o'tish boshlash"""
    db = DatabaseManager()
    user = db.get_user_by_telegram_id(message.from_user.id)
    db.close()
    
    if user:
        await message.answer(
            f"✅ Siz allaqachon ro'yxatdan o'tgansiz!\n\n"
            f"📚 Library ID: {user.library_id}\n"
            f"👤 {user.full_name}"
        )
        return
    
    await message.answer(
        "📝 YANGI RO'YXATDAN O'TISH\n\n"
        "Ma'lumotlaringizni kiriting.\n\n"
        "1️⃣ Ismingizni kiriting:"
    )
    await state.set_state(Registration.first_name)


@router.message(Registration.first_name)
async def process_first_name(message: Message, state: FSMContext):
    """Ismni qabul qilish"""
    first_name = message.text.strip()
    
    if len(first_name) < 2:
        await message.answer("❌ Ism kamida 2 ta harfdan iborat bo'lishi kerak. Qaytadan kiriting:")
        return
    
    await state.update_data(first_name=first_name)
    await message.answer("2️⃣ Familiyangizni kiriting:")
    await state.set_state(Registration.last_name)


@router.message(Registration.last_name)
async def process_last_name(message: Message, state: FSMContext):
    """Familiyani qabul qilish"""
    last_name = message.text.strip()
    
    if len(last_name) < 2:
        await message.answer("❌ Familiya kamida 2 ta harfdan iborat bo'lishi kerak. Qaytadan kiriting:")
        return
    
    await state.update_data(last_name=last_name)
    
    # Telefon raqam uchun keyboard
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="📱 Telefon raqamni yuborish", request_contact=True)]],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    
    await message.answer(
        "3️⃣ Telefon raqamingizni yuboring:\n\n"
        "Format: +998XXXXXXXXX\n"
        "yoki tugmani bosing 👇",
        reply_markup=keyboard
    )
    await state.set_state(Registration.phone_number)


@router.message(Registration.phone_number, F.contact)
async def process_phone_contact(message: Message, state: FSMContext):
    """Kontakt orqali telefon qabul qilish"""
    phone_number = message.contact.phone_number
    if not phone_number.startswith('+'):
        phone_number = '+' + phone_number
    
    await state.update_data(phone_number=phone_number)
    await message.answer(
        "4️⃣ Tug'ilgan yilingizni kiriting:\n\n"
        "Masalan: 2000",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(Registration.birth_year)


@router.message(Registration.phone_number, F.text)
async def process_phone_text(message: Message, state: FSMContext):
    """Matn orqali telefon qabul qilish"""
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
    await message.answer(
        "4️⃣ Tug'ilgan yilingizni kiriting:\n\n"
        "Masalan: 2000",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(Registration.birth_year)


@router.message(Registration.birth_year)
async def process_birth_year(message: Message, state: FSMContext):
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
            "5️⃣ Qayerda o'qiysiz yoki ishlaydiz?\n\n"
            "Masalan:\n"
            "• Toshkent Davlat Universiteti\n"
            "• Iqtisodiyot kolleji\n"
            "• IT Park\n"
            "• O'qimayman / Ishlamayman"
        )
        await state.set_state(Registration.study_place)
    
    except ValueError:
        await message.answer("❌ Iltimos, faqat raqam kiriting!")


@router.message(Registration.study_place)
async def process_study_place(message: Message, state: FSMContext):
    """O'quv joyini qabul qilish va ro'yxatdan o'tkazish"""
    study_place = message.text.strip()
    
    if len(study_place) < 2:
        await message.answer("❌ Iltimos, to'g'ri ma'lumot kiriting:")
        return
    
    await state.update_data(study_place=study_place)
    data = await state.get_data()
    
    # Database ga saqlash
    db = DatabaseManager()
    user, error = db.create_user(
        first_name=data['first_name'],
        last_name=data['last_name'],
        phone_number=data['phone_number'],
        birth_year=data['birth_year'],
        study_place=data['study_place'],
        telegram_id=message.from_user.id
    )
    db.close()
    
    if error:
        await message.answer(f"❌ Xatolik yuz berdi:\n{error}")
        await state.clear()
        return
    
    # Muvaffaqiyatli ro'yxatdan o'tdi
    await message.answer(
        "✅ MUVAFFAQIYATLI RO'YXATDAN O'TDINGIZ!\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"👤 {user.full_name}\n"
        f"📚 Library ID: {user.library_id}\n"
        f"👶 Yosh: {user.age}\n"
        f"🎓 {user.study_place}\n"
        f"📞 {user.phone_number}\n"
        f"📋 Tarif: {user.subscription_plan}\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        f"🆔 Sizning noyob ID raqamingiz: {user.library_id}\n\n"
        "💡 Bu ID ni eslab qoling! Keyinchalik\n"
        "boshqa qurilmalardan ham bog'lashingiz mumkin.\n\n"
        "📝 Keyingi qadamlar:\n"
        "1️⃣ /subscription - Tarifni tanlash\n"
        "2️⃣ /help - Yordam olish\n\n"
        "🎉 Kutubxonadan foydalanishga xush kelibsiz!"
    )
    
    await state.clear()


# ========================================
# LIBRARY ID NI BOG'LASH
# ========================================

@router.message(Command("link"))
async def cmd_link(message: Message, state: FSMContext):
    """Mavjud Library ID ni Telegram ga bog'lash"""
    db = DatabaseManager()
    user = db.get_user_by_telegram_id(message.from_user.id)
    db.close()
    
    if user:
        await message.answer(
            f"✅ Sizning Telegram akkauntingiz allaqachon bog'langan!\n\n"
            f"📚 Library ID: {user.library_id}\n"
            f"👤 {user.full_name}"
        )
        return
    
    await message.answer(
        "🔗 LIBRARY ID NI BOG'LASH\n\n"
        "Agar sizda allaqachon Library ID bor bo'lsa,\n"
        "uni bu Telegram akkauntga bog'lashingiz mumkin.\n\n"
        "📚 Library ID ingizni kiriting:\n\n"
        "Format: ID0001\n\n"
        "❌ Bekor qilish: /cancel"
    )
    await state.set_state(LinkAccount.library_id)


@router.message(LinkAccount.library_id)
async def process_link_library_id(message: Message, state: FSMContext):
    """Library ID ni qabul qilish"""
    library_id = message.text.strip().upper()
    
    # Format tekshirish
    if not library_id.startswith('ID') or len(library_id) != 6:
        await message.answer(
            "❌ Noto'g'ri format!\n\n"
            "To'g'ri format: ID0001\n"
            "Qaytadan kiriting:"
        )
        return
    
    # Library ID mavjudligini tekshirish
    db = DatabaseManager()
    user = db.get_user_by_library_id(library_id)
    
    if not user:
        await message.answer(
            f"❌ {library_id} ID raqamli foydalanuvchi topilmadi!\n\n"
            "ID raqamni to'g'ri kiriting yoki\n"
            "yangi ro'yxatdan o'ting: /register"
        )
        db.close()
        await state.clear()
        return
    
    # Allaqachon bog'langanligini tekshirish
    if user.telegram_id:
        await message.answer(
            f"❌ Bu Library ID allaqachon boshqa Telegram\n"
            f"akkauntga bog'langan!\n\n"
            f"Agar bu sizning ID ingiz bo'lsa,\n"
            f"admin bilan bog'laning."
        )
        db.close()
        await state.clear()
        return
    
    db.close()
    
    # Telefon raqam orqali tasdiqlash
    await state.update_data(library_id=library_id, user_data=user)
    
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="📱 Telefon raqamni yuborish", request_contact=True)]],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    
    await message.answer(
        f"✅ {library_id} ID topildi!\n\n"
        f"👤 {user.full_name}\n"
        f"📞 {user.phone_number}\n\n"
        f"🔐 TASDIQLASH:\n"
        f"Telefon raqamingizni yuboring (tugmani bosing):",
        reply_markup=keyboard
    )
    await state.set_state(LinkAccount.phone_verification)


@router.message(LinkAccount.phone_verification, F.contact)
async def process_link_phone_verification(message: Message, state: FSMContext):
    """Telefon raqam orqali tasdiqlash"""
    data = await state.get_data()
    library_id = data['library_id']
    user = data['user_data']
    
    phone_number = message.contact.phone_number
    if not phone_number.startswith('+'):
        phone_number = '+' + phone_number
    
    # Telefon raqamni solishtirish
    user_phone = user.phone_number.replace(' ', '').replace('-', '')
    input_phone = phone_number.replace(' ', '').replace('-', '')
    
    if user_phone != input_phone:
        await message.answer(
            "❌ Telefon raqam mos kelmadi!\n\n"
            f"Ro'yxatdagi raqam: {user.phone_number}\n"
            f"Yuborilgan raqam: {phone_number}\n\n"
            "Iltimos, to'g'ri telefon raqamni yuboring yoki\n"
            "admin bilan bog'laning.",
            reply_markup=ReplyKeyboardRemove()
        )
        return
    
    # Telegram akkauntni bog'lash
    db = DatabaseManager()
    success, msg = db.link_telegram_account(library_id, message.from_user.id)
    db.close()
    
    if success:
        await message.answer(
            "✅ MUVAFFAQIYATLI BOG'LANDI!\n\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            f"👤 {user.full_name}\n"
            f"📚 Library ID: {library_id}\n"
            f"📱 Telegram: @{message.from_user.username or 'N/A'}\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            "🎉 Endi botdan to'liq foydalanishingiz mumkin!\n\n"
            "📝 Buyruqlar:\n"
            "• /subscription - Tarifni ko'rish/o'zgartirish\n"
            "• /profile - Profilni ko'rish\n"
            "• /help - Yordam",
            reply_markup=ReplyKeyboardRemove()
        )
    else:
        await message.answer(
            f"❌ {msg}",
            reply_markup=ReplyKeyboardRemove()
        )
    
    await state.clear()


@router.message(Command("cancel"))
async def cmd_cancel(message: Message, state: FSMContext):
    """Jarayonni bekor qilish"""
    current_state = await state.get_state()
    
    if current_state is None:
        await message.answer("Hozir hech qanday jarayon yo'q.")
        return
    
    await state.clear()
    await message.answer(
        "❌ Jarayon bekor qilindi.\n\n"
        "Qaytadan boshlash uchun:\n"
        "• /register - Yangi ro'yxat\n"
        "• /link - Library ID ni bog'lash",
        reply_markup=ReplyKeyboardRemove()
    )


@router.message(Command("profile"))
async def cmd_profile(message: Message):
    """Profil ma'lumotlarini ko'rsatish"""
    db = DatabaseManager()
    user = db.get_user_by_telegram_id(message.from_user.id)
    db.close()
    
    if not user:
        await message.answer(
            "❌ Siz hali ro'yxatdan o'tmagansiz!\n\n"
            "/start - Boshlash"
        )
        return
    
    subscription_info = ""
    if user.subscription_plan != 'Free' and user.subscription_end_date:
        days_left = user.subscription_end_date - datetime.now()
        subscription_info = f"\n📅 Amal qilish muddati: {days_left.days} kun"
    
    await message.answer(
        "👤 PROFIL MA'LUMOTLARI\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"📚 Library ID: {user.library_id}\n"
        f"👤 Ism: {user.full_name}\n"
        f"📞 Telefon: {user.phone_number}\n"
        f"👶 Yosh: {user.age}\n"
        f"🎓 {user.study_place}\n"
        f"📋 Tarif: {user.subscription_plan}{subscription_info}\n"
        f"📅 Ro'yxatdan o'tgan: {user.created_at.strftime('%d.%m.%Y')}\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "💡 Buyruqlar:\n"
        "• /subscription - Tarifni o'zgartirish\n"
        "• /help - Yordam"
    )


@router.message(Command("help"))
async def cmd_help(message: Message):
    """Yordam buyrug'i"""
    help_text = (
        "📖 YORDAM BO'LIMI\n\n"
        "🔹 ASOSIY BUYRUQLAR:\n"
        "• /start - Botni ishga tushirish\n"
        "• /register - Yangi ro'yxatdan o'tish\n"
        "• /link - Library ID ni bog'lash\n"
        "• /profile - Profil ma'lumotlari\n"
        "• /subscription - Tariflar\n"
        "• /help - Yordam\n\n"
        "🔹 ADMIN BUYRUQLARI:\n"
        "• /admin - Admin panel\n\n"
        "📞 Qo'llab-quvvatlash:\n"
        "Savollaringiz bo'lsa, admin bilan bog'laning."
    )
    
    await message.answer(help_text)
