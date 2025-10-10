from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from database.db_manager import DatabaseManager
from datetime import datetime

router = Router()


class Registration(StatesGroup):
    first_name = State()
    last_name = State()
    phone_number = State()
    birth_year = State()
    study_place = State()  # Yangi: Qayerda o'qiydi


@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    db = DatabaseManager()
    user = db.get_user_by_telegram_id(message.from_user.id)
    db.close()

    if user:
        await message.answer(
            f"Xush kelibsiz, {user.first_name}!\n\n"
            f"📚 Kutubxona ID: {user.library_id}\n"
            f"📋 Tarif: {user.subscription_plan}\n"
            f"👤 Yosh: {user.age}\n"
            f"🎓 O'quv joyi: {user.study_place}\n\n"
            f"Yordam uchun /help buyrug'ini yuboring."
        )
    else:
        await message.answer(
            "👋 Assalomu alaykum! Kutubxona botiga xush kelibsiz!\n\n"
            "📝 Ro'yxatdan o'tish uchun ma'lumotlaringizni kiriting.\n\n"
            "Ismingizni kiriting:"
        )
        await state.set_state(Registration.first_name)


@router.message(Registration.first_name)
async def process_first_name(message: Message, state: FSMContext):
    await state.update_data(first_name=message.text)
    await message.answer("Familiyangizni kiriting:")
    await state.set_state(Registration.last_name)


@router.message(Registration.last_name)
async def process_last_name(message: Message, state: FSMContext):
    await state.update_data(last_name=message.text)

    # Telefon raqam uchun keyboard
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="📱 Telefon raqamni yuborish", request_contact=True)]],
        resize_keyboard=True
    )

    await message.answer(
        "Telefon raqamingizni yuboring:\n"
        "(Format: +998XXXXXXXXX yoki tugmani bosing)",
        reply_markup=keyboard
    )
    await state.set_state(Registration.phone_number)


@router.message(Registration.phone_number, F.contact)
async def process_phone_contact(message: Message, state: FSMContext):
    phone_number = message.contact.phone_number
    if not phone_number.startswith('+'):
        phone_number = '+' + phone_number

    await state.update_data(phone_number=phone_number)
    await message.answer(
        "Tug'ilgan yilingizni kiriting:\n(Masalan: 2000)",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(Registration.birth_year)


@router.message(Registration.phone_number, F.text)
async def process_phone_text(message: Message, state: FSMContext):
    phone_number = message.text.strip()

    if not phone_number.startswith('+'):
        phone_number = '+998' + phone_number.lstrip('998')

    await state.update_data(phone_number=phone_number)
    await message.answer(
        "Tug'ilgan yilingizni kiriting:\n(Masalan: 2000)",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(Registration.birth_year)


@router.message(Registration.birth_year)
async def process_birth_year(message: Message, state: FSMContext):
    try:
        birth_year = int(message.text)
        current_year = datetime.now().year

        if birth_year < 1900 or birth_year > current_year:
            await message.answer("❌ Noto'g'ri yil kiritdingiz. Qaytadan kiriting:")
            return

        await state.update_data(birth_year=birth_year)
        
        # Yangi: O'quv joyini so'rash
        await message.answer(
            "🎓 Qayerda o'qiysiz yoki ishlaydiz?\n"
            "(Masalan: Toshkent Davlat Universiteti, Iqtisodiyot kolleji, Ishlamayman)"
        )
        await state.set_state(Registration.study_place)

    except ValueError:
        await message.answer("❌ Iltimos, faqat raqam kiriting:")


@router.message(Registration.study_place)
async def process_study_place(message: Message, state: FSMContext):
    """Yangi: O'quv joyini qayta ishlash"""
    study_place = message.text.strip()
    
    if len(study_place) < 2:
        await message.answer("❌ Iltimos, to'g'ri o'quv joyini kiriting:")
        return
    
    await state.update_data(study_place=study_place)
    data = await state.get_data()

    db = DatabaseManager()
    user, error = db.create_user(
        telegram_id=message.from_user.id,
        first_name=data['first_name'],
        last_name=data['last_name'],
        phone_number=data['phone_number'],
        birth_year=data['birth_year'],
        study_place=data['study_place']
    )
    db.close()

    if error:
        await message.answer(f"❌ Xatolik: {error}")
        await state.clear()
        return

    # Yangi: Registratsiya tasdiqlash xabari
    await message.answer(
        "✅ SIZ MUVAFFAQIYATLI RO'YXATDAN O'TDINGIZ!\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"👤 Ism-familiya: {user.first_name} {user.last_name}\n"
        f"📚 Kutubxona ID: {user.library_id}\n"
        f"👶 Yosh: {user.age}\n"
        f"🎓 O'quv joyi: {user.study_place}\n"
        f"📋 Hozirgi tarif: {user.subscription_plan}\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "💡 Tarifni o'zgartirish: /subscription\n"
        "📖 Yordam: /help\n\n"
        "Xush kelibsiz! 🎉"
    )

    await state.clear()
