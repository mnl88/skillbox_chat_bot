from random import shuffle

from aiogram import types
from keyboards.inline.cancel_button import go_back_button
from utils.db_api.alchemy import DB


kb_platform = types.InlineKeyboardMarkup(row_width=1)  # создаём экземпляр клавиатуры

db = DB()
platforms = db.get_all_platforms()
shuffle(platforms)
for platform in platforms:
    button = types.InlineKeyboardButton(text=platform.name, callback_data=platform.id)
    kb_platform.add(button)
kb_platform.add(go_back_button)  # добавляем кнопку отмена
db.close()
