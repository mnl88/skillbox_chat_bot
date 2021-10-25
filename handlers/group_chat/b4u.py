import asyncio

from aiogram import types
from loader import dp, bot
from data.config import admins
from utils.b4u_parser.b4u_script import stat_parser
from utils.db_api.db_instanse import TG_Account, Badminton_player, B4U_Account
from utils.db_api.db_instanse import start_db


@dp.message_handler(commands="b4u", chat_type=['group', 'supergroup'])
@dp.message_handler(commands="b4u")
@dp.message_handler(commands="b4u", state='*')
async def b4u_command(message: types.Message):

    await types.ChatActions.typing()
    db = await start_db()

    try:
        tg_account = await TG_Account(**message.from_user.values).read_by_id(db)
        player = await Badminton_player(tg_id=tg_account.id).read_by_tg_id(db)
        b4u_account = await B4U_Account(id=player.b4u_id).smart_get(db)

        url = f'http://badminton4u.ru/players/{b4u_account.id}'
        b4u_acc_string = f'<a href="{url}">{b4u_account.username}</a>'

        text = [
            f'Привет, {player.nickname}!\n',
            f'Твой профиль LAB: \n{b4u_acc_string}.'
        ]
        if b4u_account.single_rating:
            text.append(f'Одиночный рейтинг: {b4u_account.single_rating}')
        if b4u_account.single_rating_date_of_calc:
            text.append(f'дата расчёта: {b4u_account.single_rating_date_of_calc}.')
        if b4u_account.double_rating:
            text.append(f'Парный рейтинг: {b4u_account.double_rating}')
        if b4u_account.double_rating_date_of_calc:
            text.append(f'дата расчёта: {b4u_account.double_rating_date_of_calc}.')

        msg = await message.answer('\n'.join(text), parse_mode=types.ParseMode.HTML)

    except:
        my_bot = await bot.get_me()
        msg = await message.answer(
            f'Скорее всего ты не зарегистрирован @{my_bot.username}',
            parse_mode=types.ParseMode.HTML)

    await asyncio.sleep(20)
    await message.delete()
    await asyncio.sleep(1000)
    await msg.delete()

    # if await tg_account.fetch_by_tg_id(db):
    #     tg_account = await tg_account.update(db)
    #     player = Badminton_player(tg_id=tg_account.id)
    #     if await player.is_already_exists(db):
    #         player = await player.fetch_by_tg_id(db)
    #         player: Badminton_player
    #         print('player Exist!!!!', player)
    #         logger.info('Бадминтонист уже был зарегистрирован ранее в БД')
    #         if player.b4u_id:
    #             print("САКСЕС!")
    #         url = f'http://badminton4u.ru/players/{player.b4u_id}'
    #         player_b4u_acc_string = f'<a href="{url}">{player.b4u_id}</a>'
    #         text = [
    #             f'Привет, {message.from_user.full_name}, '
    #             f'а я тебя помню!!!',
    #             f'\nУказанное имя при регистрации: {player.nickname}',
    #         ]
    #         if player.b4u_id:
    #             text.append(f'Привязанный профиль LAB при регистрации: {player_b4u_acc_string}')
    #     else:
    #         logger.info('Бадминтонист не зарегистрирован ранее в БД')
    # else:
    #     logger.info('Телеграмм-аккаунт не зарегистрирован ранее в БД')
    # joined_text = '\n'.join(text)
    # message2 = await message.answer(text=joined_text, parse_mode=types.ParseMode.HTML)
    # await hello_message.delete()
    # await asyncio.sleep(30)
    # await message2.delete()



    # player_id = 17284
    # b4u_players = [
    #     17264,
    #     17284,
    #     17287,
    #     17392,
    #     17392213
    # ]
    #
    # for player_id in b4u_players:
    #     stat = await stat_parser(player_id=player_id)
    #     print(stat)


    # player_id = 17284

    # stat = await stat_parser(player_id=player_id)
    # print(stat)
    # name = stat['name']
    # s_rating = stat['[s] Одиночки']['rating']
    # s_rating_date_of_calc = stat['[s] Одиночки']['date_of_calc']
    # d_rating = stat['[d] Пары']['rating']
    # d_rating_date_of_calc = stat['[d] Пары']['date_of_calc']
    # text = [
    #     f'Бадминтонист',
    #     f'{name},',
    #     f'одиночный рейтинг: {s_rating},',
    #     f'дата расчёта: {s_rating_date_of_calc};',
    #     f'парный рейтинг: {d_rating},',
    #     f'дата расчёта: {d_rating_date_of_calc}.',
    # ]
    # message_text = '\n'.join(text)
    #
    # await message.answer(message_text)

