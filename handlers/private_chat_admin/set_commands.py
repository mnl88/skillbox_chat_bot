from aiogram import types
from loader import dp, bot
from data.config import admins


@dp.message_handler(user_id=admins, commands="set_commands")
async def set_commands_to_bf(message: types.Message):
    """УСТАНОВИТЬ КОМАНДЫ вместо BotFather"""

    commands = [
        types.BotCommand(command="/about", description="О боте")
                ]
    await bot.set_my_commands(commands)
    await message.answer("Команды настроены. Перезапустите Telegram")


@dp.message_handler(user_id=admins, commands="clear_commands")
async def set_commands_to_bf(message: types.Message):
    """удалить КОМАНДЫ вместо BotFather"""
    await bot.set_my_commands([])
    await message.answer("Команды очищены. Перезапустите Telegram")

