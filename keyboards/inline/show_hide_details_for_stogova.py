from aiogram import types

text_and_data_show = [
        ('Скрыть детали', 'hide_details'),
]
text_and_data_hide = [
        ('Показать детали', 'show_details'),
]

inline_kb_show_details = types.InlineKeyboardMarkup(row_width=1)  # создаём экземпляр клавиатуры
for text, data in text_and_data_show:  # добавляем в клавиатуру кномпи из списка выше
    button = types.InlineKeyboardButton(text=text, callback_data=data)
    inline_kb_show_details.add(button)

inline_kb_hide_details = types.InlineKeyboardMarkup(row_width=1)  # создаём экземпляр клавиатуры
for text, data in text_and_data_hide:  # добавляем в клавиатуру кномпи из списка выше
    button = types.InlineKeyboardButton(text=text, callback_data=data)
    inline_kb_hide_details.add(button)

