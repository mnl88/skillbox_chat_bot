from aiogram import types
from aiogram.dispatcher.filters import BaseFilter


class IsPrivate(BaseFilter):

    async def check(self, message: types.Message) -> bool:
        # return isinstance(message.chat.type, types.ChatType.PRIVATE)
        return message.chat.type == types.ChatType.PRIVATE
