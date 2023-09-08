import logging

from aiogram import Router, html, F
from aiogram.filters import ChatMemberUpdatedFilter, IS_MEMBER, IS_NOT_MEMBER
from aiogram.types import ChatMemberUpdated

logger = logging.getLogger(__name__)
router = Router()


@router.chat_member(ChatMemberUpdatedFilter(IS_NOT_MEMBER >> IS_MEMBER))
async def on_user_leave(event: ChatMemberUpdated):
    await event.answer('Привет, дорогой друг')
    user = event.from_user
    if user:
        first_name = user.first_name  # Не может быть пустым
        last_name = user.last_name  # Может быть пустым
        username = user.username  # Может быть пустым
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
        welcome_message = await event.answer('\n'.join(text))

