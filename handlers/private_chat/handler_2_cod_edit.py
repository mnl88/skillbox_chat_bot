"""
Хэндлеры, обращающиеся к БД, позволяющие CRUD
"""

from loader import dp
from utils.db_api.alchemy import Person, TG_Account, DB
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
# from .handler_3_cod_stats import show_profile
from re import compile
import logging
from datetime import datetime


logger = logging.getLogger(__name__)

available_chose_edition = [
    "activision id",
    "psn id",
    "имя или прозвище"]


class OrderAddUser(StatesGroup):
    waiting_for_enter_activision_id = State()


class OrderEditUser(StatesGroup):
    waiting_for_choose_parameter = State()
    waiting_for_choose_data = State()
    waiting_for_continue_editing = State()





# Команда добавления пользователя. ШАГ 1
@dp.message_handler(chat_type=['private'], commands=['add_me'], state="*")
async def add_user_to_bd_step_1(message: types.Message):
    logger.info(
        f'Хэндлер add_me запущен пользователем с id {message.from_user.id} '
        f'({message.from_user.full_name}, {message.from_user.username})')
    await types.ChatActions.typing()
    db = DB()
    if db.is_tg_account_exists(message.from_user.id):
        await message.answer(
            str(message.from_user.first_name) + ", вы уже были зарегистрированы ранее." +
            "\nДля внесения изменений воспользуйтесь командой: /edit_me"
            )
    else:
        tg_account = TG_Account(
            id=message.from_user.id,
            username=message.from_user.username,
            first_name=message.from_user.first_name,
            is_bot=message.from_user.is_bot,
            language_code=message.from_user.language_code,
            modified_at=datetime.now()
        )
        person = Person(tg_account=tg_account)
        try:
            db.session.add(person)
            db.session.commit()
            await message.answer(
                str(message.from_user.first_name) + ", спасибо за регистрацию." +
                "\nДля внесения изменений воспользуйтесь командой: /edit_me"
            )
        except Exception as ex:
            db.session.rollback()
            logger.error(ex)
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add("отмена")
        await message.answer(
            "Для правильной работы сообщите мне ACTIVISION_ID:\n" +
            "\nпример: Ivan_Ivanov#123456789"
            , reply_markup=keyboard)
        await OrderAddUser.waiting_for_enter_activision_id.set()


