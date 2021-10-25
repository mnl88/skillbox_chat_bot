import asyncio
import datetime
import config
from aiogram import types
from misc import dp
from alchemy import *
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from cod_stats_parser import *

user_commands_list = ''
admin_commands_list = '/spam - spam'


# available_choose = (
#     ('CTAPT', 'on'),
#     ('CТОП', 'off'),
# )

available_choose = [
    "старт",
    "стоп",
    "отмена"]


class Spam_status(StatesGroup):
    spam_unsigned = State()
    spam_on = State()
    spam_off = State()


@dp.message_handler(user_id=config.ADMIN_ID, commands="spam")
async def spam(message: types.Message):
    print('spam')
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for choose in available_choose:
        keyboard.add(choose.lower())
    await message.answer(
        "Старт, стоп или отмена?", reply_markup=keyboard)
    await Spam_status.spam_unsigned.set()


@dp.message_handler(state=Spam_status.spam_unsigned, content_types=types.ContentTypes.TEXT)
@dp.async_task
async def status_set(message: types.Message, state: FSMContext):
    print('status_set')
    text = f'не выбрано'
    if message.text.lower() == 'старт':
        await Spam_status.spam_on.set()
        text = f'ВКЛЮЧЕНО'
    if message.text.lower() == 'стоп':
        await Spam_status.spam_off.set()
        text = f'ВЫКЛЮЧЕНО'
    print(text)
    markup = types.ReplyKeyboardRemove()
    await message.answer(text=text, reply_markup=markup)
    while True:
        await asyncio.sleep(4)
        current_state = await state.get_state()
        print(datetime.now(), current_state)


# @dp.message_handler(content_types=types.ContentTypes.TEXT)
# async def echo(message: types.Message):
#     await message.answer(message.text)
