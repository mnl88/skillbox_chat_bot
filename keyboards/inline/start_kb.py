from aiogram import types
# from aiogram.utils import callback_data
from keyboards.inline import cancel_button

from emoji import emojize

# callback = callback_data.CallbackData("profile", "age", "sex")  # пример

text_and_data_is_reg = [
        # (emojize(':glasses:') + ' Показать профиль', 'profile_show'),
        (emojize(':pencil:') + ' Редактировать профиль', 'profile_edit'),
        (emojize(':red_exclamation_mark:') + ' Удалить профиль', 'profile_delete'),
        (emojize(':laptop:') + ' Информация о БадминтонБоте', 'bot_info')
]

text_and_data_is_not_reg = [
        (emojize(':pen:') + ' Зарегистрировать профиль', 'profile_create'),
        (emojize(':laptop:') + ' Информация о БадминтонБоте', 'bot_info')
]

inline_kb_start_is_reg = types.InlineKeyboardMarkup(row_width=1)  # создаём экземпляр клавиатуры
for text, data in text_and_data_is_reg:  # добавляем в клавиатуру кномпи из списка выше
    button = types.InlineKeyboardButton(text=text, callback_data=data)
    inline_kb_start_is_reg.add(button)

inline_kb_start_is_not_reg = types.InlineKeyboardMarkup(row_width=1)  # создаём экземпляр клавиатуры
for text, data in text_and_data_is_not_reg:  # добавляем в клавиатуру кномпи из списка выше
    button = types.InlineKeyboardButton(text=text, callback_data=data)
    inline_kb_start_is_not_reg.add(button)


text_and_data_is_not_reg2 = [
        (emojize(':OK_hand:') + ' Изменить имя и пол', 'renaming'),
        (emojize(':1st_place_medal:') + ' Указать профиль LAB', 'lab_entering'),
        (emojize(':2nd_place_medal:') + ' Указать профиль ВК', 'vk_entering'),
        (emojize(':END_arrow:') + '<< ОТМЕНА', 'cancel_callback')
]

inline_kb_editing_profile = types.InlineKeyboardMarkup(row_width=1)  # создаём экземпляр клавиатуры
for text, data in text_and_data_is_not_reg2:  # добавляем в клавиатуру кномпи из списка выше
    button = types.InlineKeyboardButton(text=text, callback_data=data)
    inline_kb_editing_profile.add(button)

# inline_kb1.add(types.InlineKeyboardButton('отмена', callback_data='cancel'))  # добавляем кнопку отмена
