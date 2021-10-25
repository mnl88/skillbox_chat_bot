from aiogram import types
from aiogram.dispatcher.filters import CommandStart
from re import compile

from aiogram.types import ParseMode
from aiogram.types.message_entity import MessageEntity
from aiogram.utils.markdown import text, bold, italic, code, pre, hlink

from loader import dp
from data.config import admins, COD_CHAT_ID, PSN_EMAIL, PSN_PASSWORD, PSN_USERNAME
from utils.db_api.alchemy import Person, TG_Account, DB
from utils.selenium_psn.psn_selenium_parser import PSN_Bot
import asyncio
import random
import time


# Запускаем бот из группы
@dp.message_handler(user_id=admins, chat_type='private', commands=['psn_friend_list'])
async def online_123(message: types.Message):
    ps_pars = PSN_Bot(PSN_USERNAME, PSN_EMAIL, PSN_PASSWORD)  # создаем экземпляр браузера
    if not ps_pars.is_logged_in_func():
        ps_pars.login()  # логинимся
    print(f'Кол-во друзей - {ps_pars.friends_count_func(ps_pars.username)}')  # выводим кол-во друзей
    friends = ps_pars.friends_list(ps_pars.username)
    for user in friends:
        print('PSN: ', user['psn'])
        print('имя: ', user['name'])
        print('статус: ', user['now_playing'])
        print('во что играет: ', user['status'])
        print('подписка: ', user['ps_plus'], '\n')
    print(f'Кол-во друзей - {len(friends)}')  # выводим кол-во друзей другим способом
    print(f'С момента инициализации прошло {round(time.time()-ps_pars.time_start, 2)} секунд')  # выводим время работы модуля


@dp.message_handler(user_id=admins, chat_type='private', commands=['mension'])
async def online_123(message: types.Message):
    text1 = message.from_user.get_mention() + ', ты лучше всех!!!'
    await message.answer(text1, parse_mode=ParseMode.MARKDOWN)
    text2 = bold('Я могу ответить на следующие команды:') + italic(' но отвечать на них я не буду')
    await message.answer(text2, parse_mode=ParseMode.MARKDOWN, disable_notification=True)
    # text3 = message.from_user.id
    # me = await dp.bot.get_chat_member(chat_id=COD_CHAT_ID, user_id=ADMIN_ID)
    text5 = await message.chat.get_member(user_id=ADMIN_ID)
    print(text5['user'])
    # await message.answer(text4, parse_mode=ParseMode.MARKDOWN)


@dp.message_handler(user_id=admins, chat_type='group', commands=['test'])
async def online_123(message: types.Message):
    # khorev_id = 531857857
    # mension = hlink(title='Cанёк', url=f"tg://user?id={khorev_id}")
    # await message.answer(mension, parse_mode='html')
    # f = message.entities
    # print(f)
    for entity in message.entities:
        print(f'В данном сообщении были упомянуты пользователи со следующими id:')
        if entity.type == 'text_mention':
            print(entity.user.id)
        # a = item.user.get_mention
        # print(a)


    #
    # text1 = message.from_user.get_mention() + ', ты лучше всех!!!'
    # await message.answer(text1, parse_mode=ParseMode.MARKDOWN)
    # text2 = bold('Я могу ответить на следующие команды:') + italic(' но отвечать на них я не буду')
    # await message.answer(text2, parse_mode=ParseMode.MARKDOWN, disable_notification=True)
    # # text3 = message.from_user.id
    # # me = await dp.bot.get_chat_member(chat_id=COD_CHAT_ID, user_id=ADMIN_ID)
    # text5 = await message.chat.get_member(user_id=ADMIN_ID)
    # print(text5['user'])
    # # await message.answer(text4, parse_mode=ParseMode.MARKDOWN)
    #
    #
