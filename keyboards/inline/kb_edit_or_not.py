from aiogram import types
from aiogram.utils import callback_data
from keyboards.inline import cancel_button

callback = callback_data.CallbackData("primer", "age", "sex")  # пример

text_and_data = [
        ('Редактировать профиль', 'edit_profile'),
        ('НАЗАД', 'go_back')
]

inline_kb_edit_or_not = types.InlineKeyboardMarkup(row_width=1)  # создаём экземпляр клавиатуры
for text, data in text_and_data:  # добавляем в клавиатуру кномпи из списка выше
    button = types.InlineKeyboardButton(text=text, callback_data=data)
    inline_kb_edit_or_not.add(button)

# inline_kb1.add(types.InlineKeyboardButton('отмена', callback_data='cancel'))  # добавляем кнопку отмена
