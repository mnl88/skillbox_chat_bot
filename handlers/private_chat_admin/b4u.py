from aiogram import types
from loader import dp, bot
from data.config import admins
from utils.b4u_parser.b4u_script import stat_parser


@dp.message_handler(user_id=admins, commands="b4u")
async def set_commands_to_bf(message: types.Message):
    # player_id = 17284
    player_id = 17287
    stat = await stat_parser(player_id=player_id)
    name = stat['name']
    s_rating = stat['[s] Одиночки']['rating']
    s_rating_date_of_calc = stat['[s] Одиночки']['date_of_calc']
    d_rating = stat['[d] Пары']['rating']
    d_rating_date_of_calc = stat['[d] Пары']['date_of_calc']
    text = [
        f'Бадминтонист',
        f'{name},',
        f'одиночный рейтинг: {s_rating},',
        f'дата расчёта: {s_rating_date_of_calc};',
        f'парный рейтинг: {d_rating},',
        f'дата расчёта: {d_rating_date_of_calc}.',
    ]
    message_text = '\n'.join(text)

    await message.answer(message_text)

