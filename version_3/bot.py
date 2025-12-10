import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from export import export_excel, export_pdf, export_graph
from aiogram.types import InputFile

from config import BOT_TOKEN
from database import init_db
from stats_logic import save_today, get_today, get_yesterday, calculate_diff, get_all, calculate_diff_all
from keyboards import main_menu

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

init_db()


@dp.message(CommandStart())
async def start(msg: types.Message):
    await msg.answer("Statistika botiga xush kelibsiz!", reply_markup=main_menu)


@dp.callback_query(lambda c: c.data == "today")
async def today_stats(call: types.CallbackQuery):
    today = get_today()
    msg = "\n".join([f"{u}: {c} ta audio" for u, c in today.items()])
    await call.message.edit_text("📊 Bugungi statistika:\n\n" + msg, reply_markup=main_menu)


@dp.callback_query(lambda c: c.data == "yesterday")
async def yesterday_stats(call: types.CallbackQuery):
    yesterday = get_yesterday()
    msg = "\n".join([f"{u}: {c} ta audio" for u, c in yesterday.items()])
    await call.message.edit_text("📅 Kechagi statistika:\n\n" + msg, reply_markup=main_menu)


@dp.callback_query(lambda c: c.data == "compare")
async def compare(call: types.CallbackQuery):
    today = get_today()
    yesterday = get_yesterday()
    diff = calculate_diff(today, yesterday)

    msg = "\n".join([f"{u}: +{d}" for u, d in diff.items()])
    await call.message.edit_text("🔁 Farq:\n\n" + msg, reply_markup=main_menu)


@dp.callback_query(lambda c: c.data == "all")
async def all(call: types.CallbackQuery):
    today = get_today()
    all = get_all()
    diff = calculate_diff_all(today, all)

    msg = "\n".join([f"{u}: +{d}" for u, d in diff.items()])
    await call.message.edit_text("🔁 Farq:\n\n" + msg, reply_markup=main_menu)

@dp.message()
async def update_stats(msg: types.Message):
    text = msg.text
    parsed = {}

    for line in text.split("\n"):
        if "audio" in line:
            name = line.split(":")[0].strip("• ").strip()
            count = int(line.split(":")[1].split("audio")[0].strip())
            parsed[name] = count

    save_today(parsed)
    await msg.answer("Bugungi ma'lumot saqlandi.", reply_markup=main_menu)



async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
