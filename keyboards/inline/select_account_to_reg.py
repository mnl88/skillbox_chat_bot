from random import shuffle
# from aiogram.utils import callback_data
from aiogram import types

accounts = [  # data, name, example
        ('psn_account', 'Аккаунт PSN', 'Nickname_1234567'),
        ('blizzard_account', 'Аккаунт Blizzard', 'Nickname#12345'),
        ('activision_account', 'Аккаунт Activision', 'Nickname#12345678'),
        ('xbox_account', 'Аккаунт Xbox',  'Nickname#1234567')
]

kb_account = types.InlineKeyboardMarkup(row_width=1)  # создаём экземпляр клавиатуры
# callback = callback_data.CallbackData('account', 'data', 'name', 'example')

shuffle(accounts)

for data, name, example in accounts:
    button = types.InlineKeyboardButton(
        text=name,
        callback_data=data
        )
    kb_account.add(button)
