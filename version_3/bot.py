import json
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, CallbackQuery
from aiogram.filters import Command
import os
from dotenv import load_dotenv


load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# === JSON helpers ===

def load_json(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def parse_data(text):
    data = {}
    for line in text.split("\n"):
        if "audio" in line and ":" in line:
            name = line.split(":")[0].strip("• ").strip()
            audio_count = int(line.split(":")[1].split("audio")[0].strip())
            data[name] = audio_count
    return data


# === Main menu ===

def main_menu():
    kb = [
        [InlineKeyboardButton(text="📥 Kechagi roʻyxat", callback_data="set_yesterday")],
        [InlineKeyboardButton(text="📤 Bugungi roʻyxat", callback_data="set_today")],
        [InlineKeyboardButton(text="📊 Farqni hisoblash", callback_data="diff")],
        [InlineKeyboardButton(text="👥 Kuzatiladigan userlar", callback_data="tracked")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)


@dp.message(Command("start"))
async def start(message: Message):
    await message.answer("Asosiy menyu:", reply_markup=main_menu())


# === Kechagi ro'yxatni yuklash ===

@dp.callback_query(lambda c: c.data == "set_yesterday")
async def cb_set_yesterday(callback: CallbackQuery):
    await callback.message.answer("Kechagi roʼyxatni shu xabarga reply qilib yuboring.")
    await callback.answer()


@dp.message()
async def catch_replies(message: Message):
    if not message.reply_to_message:
        return

    reply_text = message.reply_to_message.text

    if reply_text and "Kechagi roʼyxatni" in reply_text:
        data = load_json("data.json")
        parsed = parse_data(message.text)
        data["yesterday"] = parsed
        save_json("data.json", data)
        await message.answer("Kechagi roʻyxat saqlandi.", reply_markup=main_menu())
        return

    if reply_text and "Bugungi roʼyxatni" in reply_text:
        parsed = parse_data(message.text)
        save_json("today.json", parsed)
        await message.answer("Bugungi roʻyxat saqlandi.", reply_markup=main_menu())
        return


# === Bugungi ro'yxatni yuklash ===

@dp.callback_query(lambda c: c.data == "set_today")
async def cb_set_today(callback: CallbackQuery):
    await callback.message.answer("Bugungi roʼyxatni shu xabarga reply qilib yuboring.")
    await callback.answer()


# === Farqni hisoblash ===

@dp.callback_query(lambda c: c.data == "diff")
async def cb_diff(callback: CallbackQuery):

    data = load_json("data.json")
    yesterday = data.get("yesterday", {})
    today = load_json("today.json")
    tracked = load_json("tracked.json")

    if not today:
        await callback.message.answer("Bugungi roʻyxat hali kiritilmagan.")
        await callback.answer()
        return

    text = "📊 Bugun qo‘shilgan audio soni:\n\n"

    for user in tracked:
        old = yesterday.get(user, 0)
        new = today.get(user, 0)
        diff = new - old

        text += f"• {user}: {diff} ta\n"

        data["total"][user] = data["total"].get(user, 0) + max(diff, 0)

    save_json("data.json", data)

    await callback.message.answer(text)
    await callback.answer()



# === Kuzatiladigan userlar menyusi ===

@dp.callback_query(lambda c: c.data == "tracked")
async def cb_tracked(callback: CallbackQuery):
    tracked = load_json("tracked.json")

    kb = [
        [InlineKeyboardButton(text="➕ User qo‘shish", callback_data="add_user")],
        [InlineKeyboardButton(text="❌ User o‘chirish", callback_data="remove_user")],
        [InlineKeyboardButton(text="⬅️ Orqaga", callback_data="back")]
    ]

    text = "👥 Kuzatiladigan userlar:\n\n" + "\n".join([f"• {u}" for u in tracked])

    await callback.message.answer(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=kb))
    await callback.answer()


# === User qo'shish ===

@dp.callback_query(lambda c: c.data == "add_user")
async def cb_add_user(callback: CallbackQuery):
    await callback.message.answer("Qo‘shmoqchi bo‘lgan username’ni yuboring.")
    await callback.answer()
    bot.state = "adding_user"


@dp.message()
async def handle_user_add_remove(message: Message):
    if not hasattr(bot, "state"):
        return

    state = bot.state

    if state == "adding_user":
        user = message.text.strip()
        tracked = load_json("tracked.json")
        if user not in tracked:
            tracked.append(user)
            save_json("tracked.json", tracked)
            await message.answer(f"➕ {user} ro‘yxatga qo‘shildi!", reply_markup=main_menu())
        else:
            await message.answer("Bu user allaqachon ro‘yxatda.")
        bot.state = None

    elif state == "removing_user":
        user = message.text.strip()
        tracked = load_json("tracked.json")
        if user in tracked:
            tracked.remove(user)
            save_json("tracked.json", tracked)
            await message.answer(f"❌ {user} ro‘yxatdan olib tashlandi.", reply_markup=main_menu())
        else:
            await message.answer("Bunday user ro‘yxatda yo‘q.")
        bot.state = None


# === User o‘chirish ===

@dp.callback_query(lambda c: c.data == "remove_user")
async def cb_remove_user(callback: CallbackQuery):
    await callback.message.answer("O‘chirmoqchi bo‘lgan username’ni yuboring.")
    await callback.answer()
    bot.state = "removing_user"



# === Orqaga qaytish ===

@dp.callback_query(lambda c: c.data == "back")
async def cb_back(callback: CallbackQuery):
    await callback.message.answer("Asosiy menyu:", reply_markup=main_menu())
    await callback.answer()


# === Run bot ===
if __name__ == "__main__":
    import asyncio
    asyncio.run(dp.start_polling(bot))
