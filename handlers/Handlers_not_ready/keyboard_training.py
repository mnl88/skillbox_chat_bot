import asyncio
import datetime
import config
from aiogram import types
from misc import dp, bot
from alchemy import *
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from cod_stats_parser import *

"""
This bot is created for the demonstration of a usage of inline keyboards.
"""

user_commands_list = '/str - str,\n'
admin_commands_list = ''


@dp.message_handler(commands='str')
async def start_cmd_handler(message: types.Message):
    keyboard_markup = types.InlineKeyboardMarkup(row_width=3)
    # default row_width is 3, so here we can omit it actually
    # kept for clearness

    text_and_data = (
        ('Yes!', 'yes'),
        ('No!', 'no'),
    )
    # in real life for the callback_data the callback data factory should be used
    # here the raw string is used for the simplicity
    row_btns = (types.InlineKeyboardButton(text, callback_data=data) for text, data in text_and_data)

    # keyboard_markup.add(button1)

    keyboard_markup.row(*row_btns)
    keyboard_markup.add(
        # url buttons have no callback data
        types.InlineKeyboardButton(text='aiogram source', callback_data='aiogram'),
        types.InlineKeyboardButton('aiogram source', url='https://github.com/aiogram/aiogram'),
        types.InlineKeyboardButton('aiogram source', url='https://github.com/aiogram/aiogram'),
        types.InlineKeyboardButton('aiogram source', url='https://github.com/aiogram/aiogram'),
        types.InlineKeyboardButton('aiogram source', url='https://github.com/aiogram/aiogram'),
        types.InlineKeyboardButton('aiogram source', url='https://github.com/aiogram/aiogram'),
    )

    await message.reply("Hi!\nDo you love aiogram?", reply_markup=keyboard_markup)


# Use multiple registrators. Handler will execute when one of the filters is OK
@dp.callback_query_handler(text='no')  # if cb.data == 'no'
@dp.callback_query_handler(text='yes')  # if cb.data == 'yes'
async def inline_kb_answer_callback_handler(query: types.CallbackQuery):
    answer_data = query.data
    # always answer callback queries, even if you have nothing to say
    await query.answer(f'You answered with {answer_data!r}')

    if answer_data == 'yes':
        text = 'Great, me too!'
    elif answer_data == 'no':
        text = 'Oh no...Why so?'
    else:
        text = f'Unexpected callback data {answer_data!r}!'

    await bot.send_message(query.from_user.id, text)


@dp.callback_query_handler(text='aiogram')  # if cb.data == 'aiogram'
async def start_cmd_handler(message: types.Message):
    print(f'Вы нажали третью кнопку')
