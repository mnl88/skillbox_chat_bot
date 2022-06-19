import logging
import asyncio

from aiogram import Router, types, html, F

from middlewares.message_counter import CounterMiddleware

logger = logging.getLogger(__name__)
router = Router()
router.message.filter(F.chat.type.in_({"group", "supergroup"}))


# @router.message(F.chat.type.in_({"group", "supergroup"}), commands="id")
@router.message(content_types=[types.ContentType.NEW_CHAT_MEMBERS])
async def new_user_joined(message: types.Message):
    for new_member in message.new_chat_members:
        first_name = new_member.first_name  # Не может быть пустым
        last_name = new_member.last_name  # Может быть пустым
        username = new_member.username  # Может быть пустым
        mention = ''
        if username:
            mention = ' @' + username
        text = [
            f'Привет, {first_name} {mention}',
            'Рады приветствовать тебя в нашем локальном Санкт-Петербургском '
            'чате студентов Skillbox отделения frontend-разработки =)\n',
            'Расскажи немного о себе, и, в идеале, отметь свой рассказ хэштегом #вкратце_о_себе',
            'Также по этому хэштегу ты сможешь найти краткую информацию о других участниках данного чата!',
            'Зачастую мы оставляем в закреплённых комментариях важную и нужную информацию и/или опросы\n',
            'По возможности, ознакомься с несколькими последними =)',
        ]
        welcome_message = await message.answer('\n'.join(text))


# @router.message()
# async def aaa(update, **kwargs):
#     for items in kwargs.items():
#         print(f"{items}")