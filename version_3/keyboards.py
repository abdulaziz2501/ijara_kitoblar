from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

main_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="📊 Bugungi statistika", callback_data="today")],
    [InlineKeyboardButton(text="📅 Kechagi statistika", callback_data="yesterday")],
    [InlineKeyboardButton(text="🔁 Taqqoslash", callback_data="compare")],
    [InlineKeyboardButton(text="📤 Export (Excel/PDF)", callback_data="export_menu")],
])
export_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="📊 Excel eksport", callback_data="exp_excel")],
    [InlineKeyboardButton(text="📄 PDF eksport", callback_data="exp_pdf")],
    [InlineKeyboardButton(text="📉 Grafik eksport", callback_data="exp_graph")],
    [InlineKeyboardButton(text="⬅️ Ortga", callback_data="back_main")],
])
