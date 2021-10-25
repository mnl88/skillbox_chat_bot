from random import shuffle

from aiogram import types
from keyboards.inline.cancel_button import go_back_button
from utils.db_api.alchemy import DB


kb_input_device = types.InlineKeyboardMarkup(row_width=1)  # создаём экземпляр клавиатуры

db = DB()
input_devices = db.get_all_input_devices()
shuffle(input_devices)
for input_device in input_devices:
    button = types.InlineKeyboardButton(text=input_device.name, callback_data=input_device.id)
    kb_input_device.add(button)
kb_input_device.add(go_back_button)  # добавляем кнопку отмена
db.close()
