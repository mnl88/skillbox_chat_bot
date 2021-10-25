from loader import dp
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from filters import IsPrivate
import logging
import asyncio

from handlers.private_chat.start import bot_start_without_deeplink

logger = logging.getLogger(__name__)


# Прервать любой их хэндлеров
@dp.message_handler(IsPrivate(), state='*', commands=['cancel', 'отмена'])
@dp.message_handler(IsPrivate(), Text(equals=['cancel', 'отмена'], ignore_case=True), state='*')
@dp.callback_query_handler(text="cancel_callback", state='*')
async def cancel_handler(call: types.CallbackQuery, state: FSMContext):
    """
    Прерывание любого их хэндлеров
    """
    logger.info(f'Пользователь {call.message.from_user.full_name} (ID: {call.message.from_user.id}) нажал команду ОТМЕНА')
    await state.finish()
    msg = await call.message.reply('Работа бота остановлена. Чтобы заново запустить бота нажмите /start', reply_markup=types.ReplyKeyboardRemove())
    await asyncio.sleep(60)
    await msg.delete()

