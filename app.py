import logging
import asyncio

from aiogram import Bot, Dispatcher

from handlers.group_chat import new_members_adding
from handlers.errors import errors
from middlewares.message_counter import CounterMiddleware
from ui_commands import set_bot_commands


from data import config

logger = logging.getLogger(__name__)


async def main() -> None:
    logging.basicConfig(
        level="DEBUG",
        format='%(asctime)s | %(levelname)s | %(name)s |  %(lineno)d | %(message)s',
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    # Initialize Bot instance with a default parse mode which will be passed to all API calls
    bot = Bot(config.BOT_TOKEN, parse_mode="HTML")

    # Setup dispatcher and bind routers to it
    dp = Dispatcher()

    # Allow interaction in private chats (not groups or channels) only
    # dp.message.filter(F.chat.type == "private")

    # Register middlewares
    # dp.message.middleware(CounterMiddleware())
    dp.message.middleware(CounterMiddleware())
    # dp.message.middleware(DbSessionMiddleware(db_pool))
    # dp.callback_query.middleware(CheckActiveGameMiddleware())
    # dp.callback_query.middleware(DbSessionMiddleware(db_pool))

    # Register handlers
    dp.include_router(new_members_adding.router)
    dp.include_router(errors.router)
    # dp.include_router(forwarded_messages.router)

    # Set bot commands in UI
    # await set_bot_commands(bot)

    # Run bot
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())

if __name__ == "__main__":
    asyncio.run(main())
