import logging

from aiogram import types
from loader import dp, bot

from aiogram.dispatcher.filters import Text
from data.config import admins
from utils.ps_vk_group_parser.vk_group_parser import get_comments_by_user_id

from utils.db_api.db_instanse import TG_Account
from utils.db_api.db_instanse import start_db
from utils.db_api.db_instanse import add_member_using_tg_id
# from utils.db_api.db_instanse import is_tg_acc_exists_in_db
# from utils.db_api.db_instanse import add_td_acc_if_not_exist


logger = logging.getLogger(__name__)


# @dp.message_handler(chat_type=['group', 'supergroup'], is_chat_admin=True)
# @dp.message_handler(Text(contains='add_me'), chat_type=['group', 'supergroup'], is_chat_admin=True)
# @dp.message_handler(commands=['add_me'], chat_type=['group', 'supergroup'], is_chat_admin=True)
# @dp.message_handler(commands=['add_me'], chat_type=['group', 'supergroup'])
# @dp.message_handler(chat_type=['group', 'supergroup'])
async def set_commands_to_bf(message: types.Message):

    # print(f'{message.text}')
    logger.info(f'Группа: {message.chat.title} (id = {message.chat.id})')
    db = await start_db()
    tg_account = TG_Account(**message.from_user.values)
    logger.info(f'Текст: {message.text} (автор = {tg_account})')

    is_alreade_exist = await add_td_acc_if_not_exist(db, tg_account)
    if is_alreade_exist:
        logger.info(f'Этот пользователь уже был ранее добавлен в БД')
    else:
        logger.info(f'Пользователь добавлен в БД!!!')

    # if await is_tg_acc_exists_in_db(db, user):
    #     await message.answer('Бро, я и так давно за тобой слежу!!!')
    # else:
    #     await add_member_using_tg_id(db, user)
    #     await message.answer('Спасибо, Бро! Буду приглядывать за тобой')





    # user_vk_id = 2680992
    # comments = await get_comments_by_user_id(user_vk_id=user_vk_id)
    # text = ['Мои записи:']
    # print(comments)
    # for comment in comments:
    #     topic_title = comment['topic_title']
    #     comment_text = comment['comment']['text']
    #     text.append(
    #         f'Текст сообщения: {comment_text} \n ({topic_title})'
    #     )
    # message_text = '\n'.join(text)
    # await message.answer(message_text)

