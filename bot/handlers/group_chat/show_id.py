import logging
import asyncio

from aiogram import Router, types, html, F
from aiogram.filters import Command

logger = logging.getLogger(__name__)
router = Router()


@router.message(F.text == "show_id")
@router.message(Command("show_id"))
async def new_user_joined(message: types.Message):
    print(message.chat.id)
    await message.delete()
