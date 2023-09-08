import logging

from aiogram import Router, html, F
from aiogram.filters import ChatMemberUpdatedFilter, IS_MEMBER, IS_NOT_MEMBER
from aiogram.types import ChatMemberUpdated

logger = logging.getLogger(__name__)
router = Router()


@router.chat_member(ChatMemberUpdatedFilter(IS_MEMBER >> IS_NOT_MEMBER))
async def on_user_leave(event: ChatMemberUpdated):
    name = event.from_user.first_name
    await event.answer(f'Прощай, {name}, ты был хорошим другом!')
