from aiogram import types
from misc import dp
from config import ADMIN_ID


# тут будет код
@dp.message_handler()
async def replied_from(message: types.Message):
    # print(message.reply_to_message.from_user.id)
    # print(message.reply_to_message.from_user.id)
    # if message.reply_to_message.forward_from.id is not None:
    print(message.forward_from)

    # chat_id = message.chat.id
    # chat_id = 202181776  # ID личного чата между мной и ботом
    # await dp.bot.send_message(chat_id, message)  # бот пересылает мне сообщения из любого чата в личку

    print(message.text)

@dp.message_handler(commands=['1'])
async def statistic(message: types.Message):
    await message.reply(text='test', reply=True)
    # тут будет код
    chat_id = message.chat.id
    chat_id = 202181776  # ID личного чата между мной и ботом
    await dp.bot.send_message(chat_id, message)  # бот пересылает мне сообщения из любого чата в личку


@dp.message_handler(commands=['2'])
async def statistic(message: types.Message):
    text = [
        '1-ая строка',
        '2-ая строка',
        '3-яя строка'
        ]
    full_text = '\n'.join(text)  # красивый способ объеденить строки с пререносами
    await message.answer(full_text)


@dp.message_handler(commands=['3'])
async def statistic(message: types.Message):
    asd = dp.bot.get_me
    print(asd)



@dp.message_handler(user_id=ADMIN_ID, commands="chat_info")
async def chat_info(message: types.Message):
    """вывести в Телеграм ID чата"""

    text = f"Заголовок: {str(message.chat.title)}\nID этого чата: {str(message.chat.id)}"
    await message.answer(text=text, reply=False)

# @dp.message_handler(commands=['test'])
# async def status_set(message: types.Message):
#     while True:
#         await asyncio.sleep(1)
#         await message.reply(text='test')
