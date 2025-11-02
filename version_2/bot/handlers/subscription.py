"""
Subscription Handler - Tariflar bilan ishlash
"""
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from ijara_kitoblar.database.db_manager import DatabaseManager
from ijara_kitoblar.config import SUBSCRIPTION_PLANS
from datetime import datetime

router = Router()


def get_subscription_keyboard(current_plan: str = None):
    """Tariflar klaviaturasi"""
    buttons = []
    
    for plan_name, plan_info in SUBSCRIPTION_PLANS.items():
        price_text = f"{plan_info['price']:,} so'm" if plan_info['price'] > 0 else "Bepul"
        
        # Hozirgi tarif belgisi
        prefix = "✅ " if plan_name == current_plan else ""
        
        if plan_name == "Free":
            emoji = "🟢"
        elif plan_name == "Money":
            emoji = "🔵"
        else:
            emoji = "🟣"
        
        button_text = f"{prefix}{emoji} {plan_name} ({price_text})"
        buttons.append([InlineKeyboardButton(text=button_text, callback_data=f"plan_{plan_name}")])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


@router.message(Command("subscription"))
async def cmd_subscription(message: Message):
    """Tariflar bo'limi"""
    db = DatabaseManager()
    user = db.get_user_by_telegram_id(message.from_user.id)
    db.close()
    
    if not user:
        await message.answer(
            "❌ Avval ro'yxatdan o'ting!\n\n"
            "/start - Boshlash"
        )
        return
    
    # Hozirgi tarif haqida ma'lumot
    subscription_info = f"📋 Hozirgi tarif: {user.subscription_plan}"
    
    if user.subscription_plan != 'Free' and user.subscription_end_date:
        days_left = (user.subscription_end_date - datetime.now()).days
        if days_left > 0:
            subscription_info += f"\n⏳ Tugashiga: {days_left} kun"
        else:
            subscription_info += "\n⚠️ Obuna muddati tugagan!"
    
    keyboard = get_subscription_keyboard(user.subscription_plan)
    
    await message.answer(
        f"{subscription_info}\n\n"
        "💡 Yangi tarifni tanlang:",
        reply_markup=keyboard
    )


@router.callback_query(F.data.startswith("plan_"))
async def process_plan_selection(callback: CallbackQuery):
    """Tarif tanlash"""
    plan_name = callback.data.split("_")[1]
    
    if plan_name not in SUBSCRIPTION_PLANS:
        await callback.answer("❌ Noto'g'ri tarif!", show_alert=True)
        return
    
    plan = SUBSCRIPTION_PLANS[plan_name]
    
    db = DatabaseManager()
    user = db.get_user_by_telegram_id(callback.from_user.id)
    
    if not user:
        await callback.answer("❌ Foydalanuvchi topilmadi!", show_alert=True)
        db.close()
        return
    
    # Free tarifga avtomatik o'tish
    if plan_name == "Free":
        success, msg = db.update_subscription(user.library_id, plan_name)
        db.close()
        
        if success:
            await callback.message.edit_text(
                f"✅ FREE TARIFGA O'TDINGIZ!\n\n"
                f"🟢 Bu tarif bepul va cheksiz.\n\n"
                f"📋 Xususiyatlar:\n"
            )
            
            for feature in plan['features']:
                await callback.message.answer(f"  • {feature}")
        else:
            await callback.message.edit_text(f"❌ {msg}")
    
    # Pullik tariflar uchun to'lov ma'lumotlari
    else:
        db.close()
        
        features_text = "\n".join([f"  ✓ {f}" for f in plan['features']])
        
        await callback.message.edit_text(
            f"{'🔵' if plan_name == 'Money' else '🟣'} {plan_name.upper()} TARIF\n\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"💰 Narx: {plan['price']:,} so'm\n"
            f"📅 Muddat: {plan['duration_days']} kun\n"
            f"━━━━━━━━━━━━━━━━━━━━\n\n"
            f"📋 XUSUSIYATLAR:\n{features_text}\n\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"💳 TO'LOV MA'LUMOTLARI:\n\n"
            f"1️⃣ To'lovni amalga oshiring\n"
            f"2️⃣ Kvitansiya rasmini adminga yuboring\n"
            f"3️⃣ Sizning Library ID ingizni ayting\n\n"
            f"📚 Library ID: {user.library_id}\n\n"
            f"✅ Admin tasdiqlashidan so'ng obunangiz\n"
            f"   faollashadi va sizga xabar keladi.\n\n"
            f"📞 Savollar bo'lsa admin bilan bog'laning."
        )
    
    await callback.answer()


@router.message(Command("mysubscription"))
async def cmd_my_subscription(message: Message):
    """Hozirgi tarif haqida to'liq ma'lumot"""
    db = DatabaseManager()
    user = db.get_user_by_telegram_id(message.from_user.id)
    db.close()
    
    if not user:
        await message.answer("❌ Avval ro'yxatdan o'ting: /start")
        return
    
    plan_name = user.subscription_plan
    plan = SUBSCRIPTION_PLANS.get(plan_name, {})
    
    if plan_name == 'Free':
        emoji = "🟢"
    elif plan_name == 'Money':
        emoji = "🔵"
    else:
        emoji = "🟣"
    
    text = (
        f"{emoji} HOZIRGI TARIF: {plan_name.upper()}\n\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"📚 Library ID: {user.library_id}\n"
    )
    
    if plan_name != 'Free' and user.subscription_end_date:
        days_left = (user.subscription_end_date - datetime.now()).days
        
        if days_left > 0:
            text += f"📅 Tugashiga: {days_left} kun\n"
            text += f"📆 Tugash sanasi: {user.subscription_end_date.strftime('%d.%m.%Y')}\n"
        else:
            text += "⚠️ Obuna muddati tugagan!\n"
            text += "💡 Tarifni yangilang: /subscription\n"
    
    text += "━━━━━━━━━━━━━━━━━━━━\n\n"
    
    # Xususiyatlar
    if 'features' in plan:
        text += "📋 XUSUSIYATLAR:\n"
        for feature in plan['features']:
            text += f"  ✓ {feature}\n"
    
    text += "\n💡 Tarifni o'zgartirish: /subscription"
    
    await message.answer(text)
