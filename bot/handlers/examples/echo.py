import logging
import asyncio

from aiogram import Router, types, html, F


logger = logging.getLogger(__name__)
router = Router()


# @router.message(content_types=[types.ContentType.NEW_CHAT_MEMBERS])
@router.message()
async def new_user_joined(message: types.Message):
    if message.from_user:
        first_name = message.from_user.first_name  # Не может быть пустым
        last_name = message.from_user.last_name  # Может быть пустым
        username = message.from_user.username  # Может быть пустым
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