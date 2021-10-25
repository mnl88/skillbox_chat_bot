from aiogram import types
from loader import dp, bot
import asyncio
from filters import IsPrivate


@dp.message_handler(IsPrivate())
async def bot_echo(message: types.Message):

    message_1_id = message.message_id

    text = [
        f'Прости, друг, я не знаю команды: <b>{message.text}</b>',
        '',
        'Данные сообщения будут автоматически удалено через несколько секунд'
    ]

    joined_text = '\n'.join(text)

    message_2 = await message.reply(
        text=joined_text,
        parse_mode=types.ParseMode.HTML
    )

    await asyncio.sleep(5)

    await bot.delete_message(
        chat_id=message.from_user.id,
        message_id=message_2.message_id,
    )
    await bot.delete_message(
        chat_id=message.from_user.id,
        message_id=message_1_id,
    )
