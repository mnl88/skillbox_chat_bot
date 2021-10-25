from aiogram import types
from aiogram.utils import callback_data
from keyboards.inline import cancel_button

callback = callback_data.CallbackData("primer", "age", "sex")  # пример

text_and_data = [
        ('Имя (никнейм)', 'name_or_nickname'),
        ('ACTIVISION', 'activision_account'),
        ('PSN', 'psn_account'),
        ('Аккаунт Blizzard', 'blizzard_account'),
        ('Аккаунт Xbox', 'xbox_account'),
        ('Платформу', 'platform_name'),
        ('Устройство ввода', 'input_device_name'),
        ('Инфу о себе', 'about_yourself'),
        ('НАЗАД', 'go_back')

]

inline_kb_edit_data = types.InlineKeyboardMarkup(row_width=1)  # создаём экземпляр клавиатуры
for text, data in text_and_data:  # добавляем в клавиатуру кномпи из списка выше
    button = types.InlineKeyboardButton(text=text, callback_data=data)
    inline_kb_edit_data.add(button)

# inline_kb1.add(types.InlineKeyboardButton('отмена', callback_data='cancel'))  # добавляем кнопку отмена
