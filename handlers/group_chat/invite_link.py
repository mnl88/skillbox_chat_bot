import logging

from aiogram import types
from loader import dp, bot

logger = logging.getLogger(__name__)


@dp.message_handler(text='invite_link')
async def bot_echo_group(message: types.Message):
    logger.info(f'был запущен обработчик bot_echo_group')
    # инвайт генерируется только если бот добавлен в чат в качестве админа
    invite_link = await bot.export_chat_invite_link(chat_id=-341478688)
    await message.answer(text=f'Эхо - {message.text}, invite_link - {invite_link}')