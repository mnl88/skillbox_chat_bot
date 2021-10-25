from config import ADMIN_ID
from misc import dp
from alchemy import Person, TG_Account, DB
from aiogram import types
import asyncio


@dp.message_handler(user_id=ADMIN_ID, commands="add_manile")
async def add_me_for_test(message: types.Message):
    """проверяет, есть ли пользователь НИКИТА, если нет, то добавляет его в БД"""
    tg_id = 202181776
    manile = get_member_old(tg_id)
    if manile is False:
        print('нету Manile')
        manile = COD_User_old(tg_id=tg_id)
        manile.tg_name = 'MaNiLe88'
        manile.name = 'Никита'
        manile.activision_id = 'Imago#1393409'
        session.add(manile)
        session.commit()
        await message.answer("выполнено")
    print(type(manile))
    print(manile)


@dp.message_handler(user_id=ADMIN_ID, commands="spam")
async def status_set(message: types.Message):
    i = 0
    while True:
        await asyncio.sleep(4)
        await message.answer(str(datetime.now()))
        i += 1
        if i == 10:
            break


