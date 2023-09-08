import asyncio
import logging

from aiogram import Bot, Dispatcher, Router, types, F
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.types.chat_member_updated import ChatMemberUpdated
from aiogram.utils.markdown import hbold

from aiogram.filters import IS_MEMBER, IS_NOT_MEMBER

from aiogram import Router

from data.config import bot_config

from handlers.group_chat import (chat_member_added, chat_member_left)
from handlers.examples import echo


async def main():
    bot = Bot(
        token=bot_config.token,
        parse_mode=ParseMode.HTML
    )

    # All handlers should be attached to the Router (or Dispatcher)
    dp = Dispatcher(
        # forum_chat_id=bot_config.chat_id,
    )

    # @dp.message(CommandStart())
    # async def command_start_handler(message: Message) -> None:
    #     """
    #     This handler receives messages with `/start` command
    #     """
    #     # Most event objects have aliases for API methods that can be called in events' context
    #     # For example if you want to answer to incoming message you can use `message.answer(...)` alias
    #     # and the target chat will be passed to :ref:`aiogram.methods.send_message.SendMessage`
    #     # method automatically or call API method directly via
    #     # Bot instance: `bot.send_message(chat_id=message.chat.id, ...)`
    #     await message.answer(f"Hello, {hbold(message.from_user.full_name)}!")

    # @router.message(F.chat.func(lambda chat: chat.id == bot_config.chat_id))
    # @router.message()
    # async def echo_handler(message: types.Message) -> None:
    #     """
    #     Handler will forward receive a message back to the sender
    #
    #     By default, message handler will handle all message types (like a text, photo, sticker etc.)
    #     """
    #     try:
    #         await message.answer('ID этого чата = ' + str(message.chat.id))
    #         # Send a copy of the received message
    #         await message.send_copy(chat_id=message.chat.id)
    #     except TypeError:
    #         # But not all the types is supported to be copied so need to handle it
    #         await message.answer("Nice try!")

    # dp.include_router(router)

    # Ensure that we always have PostgreSQL connection in middlewares
    # dp.message.outer_middleware(DbSessionMiddleware(sessionmaker))
    # dp.edited_message.outer_middleware(DbSessionMiddleware(sessionmaker))

    # talk_router = get_shared_router(config.bot)
    # talk_router.message.outer_middleware(TopicsManagementMiddleware())
    # talk_router.message.middleware(RepliesMiddleware())
    # talk_router.edited_message.middleware(EditedMessagesMiddleware())

    dp.include_router(chat_member_added.router)
    dp.include_router(chat_member_left.router)
    # dp.include_router(echo.router)

    # await logger.ainfo("Starting Bot")
    await dp.start_polling(
        bot,
        # allowed_updates=dp.resolve_used_update_types()
    )


logging.basicConfig(level=logging.INFO)
asyncio.run(main())
