"""
Хэндлеры, обращающиеся к БД, только с правами чтения
"""

from handlers.private_chat.handler_0_middleware import update_tg_account, full_profile_info, mentioned_user_list
from loader import dp
from utils.db_api.alchemy import Person, DB
from aiogram import types
from utils.parser_cod_tracker_gg.cod_stats_parser import get_kd, parse_stat
from data.config import admins, COD_CHAT_ID
from aiogram.utils.markdown import text
import logging
from datetime import datetime
import math

logger = logging.getLogger(__name__)


# Обновляем статистику по КД
async def stat_update(db: DB, person: Person):
    try:
        parsed_stats = parse_stat(activision_account=person.activision_account)
        kd_ratio = get_kd(parsed_stats)
        if kd_ratio['warzone'] is None and kd_ratio['modern-warfare'] is None and kd_ratio['cold-war'] is None:
            logger.info('Т.к. значения всех КД не определены, то перезаписи КД не будет')
            result = False
        else:
            logger.info(f'Парсинг КД прошёл успешно. {kd_ratio=}')
            person.kd_warzone = kd_ratio['warzone']
            person.kd_multiplayer = kd_ratio['modern-warfare']
            person.kd_cold_war_multiplayer = kd_ratio['cold-war']
            person.modified_kd_at = datetime.now()
            db.session.add(person)
            db.session.commit()
            logger.info(f'Статистика КД обновлена. {person}')
            logger.info(f'{person.kd_warzone=}, {person.kd_multiplayer=}, {person.kd_cold_war_multiplayer=}')
            result = True
    except Exception as ex:
        db.session.rollback()
        logger.info(f'Ошибка. {ex}')
        result = False
    return result


# Показывает полные данные о пользователе
@dp.message_handler(chat_type='private', commands=['show_full_profile_info'])  # любой, но только в личке
@dp.message_handler(user_id=admins, commands=['show_full_profile_info'])  # админ - в любом чате
async def show_full_profile_info(message: types.Message, is_reply=True):
    """показывает данные пользователя"""
    logger.info(
        f'Хэндлер show_full_profile_info запущен пользователем с id {message.from_user.id} '
        f'({message.from_user.full_name}, {message.from_user.username})')
    await types.ChatActions.typing()
    update_tg_account(message.from_user)
    db = DB()
    if not db.get_person_by_tg_account(db.get_tg_account(message.from_user.id)):
        await message.answer(
            'Для отображения статистики необходимо сообщить мне свой ACTIVISION ID: /add_me', reply=True)
    else:
        tg_acc = db.get_tg_account(message.from_user.id)
        print(tg_acc)
        cod_user = db.get_person_by_tg_account(tg_acc)
        print(cod_user)
        full_text = full_profile_info(cod_user)
        await message.answer(full_text, reply=is_reply, parse_mode=text())
        # print(full_text)


# Показывает статистику по КД
# TODO: Проверить, работает ли на сервере парсер с новыми ЗАГОЛОВКАМИ
@dp.message_handler(commands=['stat'])
async def show_stat(message: types.Message):
    logger.info(
        f'Хэндлер STAT запущен пользователем с id {message.from_user.id} '
        f'({message.from_user.full_name}, {message.from_user.username})')
    """показывает статистику игрока"""
    await types.ChatActions.typing()
    db = DB()
    update_tg_account(message.from_user)

    members = mentioned_user_list(message)

    # если упоминаний нет, то добавляем в список себя
    if len(members) == 0:
        logger.info(f'Не найдено ни каких упоминаний, выводим статистику по себе...')
        tg_account = db.get_tg_account(tg_id=message.from_user.id)
        logger.info(f'{tg_account=}')
        try:
            me = db.get_person_by_tg_account(tg_account)
            if me is not None:  # проверяем, смогли ли мы загрузить свою учётку в БД
                if me.modified_kd_at is None:
                    logger.info(f'КД ранее ни разу удачно не обновлялось')
                    need_to_update_kd = True
                else:
                    logger.info(f'Последнее удачное обновление КД произошло {me.modified_kd_at}')
                    # сколько прошло секунд с последнего обновления
                    timestamp_delta = datetime.now().timestamp() - me.modified_kd_at.timestamp()
                    # переводим секунды в часы, с округлением вниз
                    hours_delta_int = math.floor(timestamp_delta/(60*60))
                    logger.info(f'Последнее удачное обновление КД было {hours_delta_int} часов назад')
                    hours = 10  # как часто обновлять КД
                    if hours_delta_int > hours:
                        need_to_update_kd = True
                    else:
                        need_to_update_kd = False
                        logger.info(f'КД обновляется на чаще раза в {hours} часов. Еще не пришло время обновлять КД')
                if need_to_update_kd:
                    logger.info(f'Обновляем КД')
                    await stat_update(db=db, person=me)
                members.append(me)
        except Exception as ex:
            print(ex)
            await message.answer(
                'Ошибка: пользователь не найден в базе данных.\nДля работы БОТА необходимо открыть ПРИВАТНЫЙ чат с ним и зарегистрироваться.', reply=True)

    for person in members:
        await types.ChatActions.typing(2)
        name_or_nickname = 'empty'
        if person.name_or_nickname is not None:
            name_or_nickname = str(person.name_or_nickname)
        username = 'empty'
        if person.tg_account.username is not None:
            username = str(person.tg_account.username)
        activision_account = 'empty'
        if person.activision_account is not None:
            activision_account = str(person.activision_account)
        psn_account = 'empty'
        if person.psn_account is not None:
            psn_account = str(person.psn_account)
        kd_warzone = 'empty'
        if person.kd_warzone is not None:
            kd_warzone = str(float(person.kd_warzone))
        kd_multiplayer = 'empty'
        if person.kd_multiplayer is not None:
            kd_multiplayer = str(float(person.kd_multiplayer))
        kd_cold_war_multiplayer = 'empty'
        if person.kd_cold_war_multiplayer is not None:
            kd_cold_war_multiplayer = str(float(person.kd_cold_war_multiplayer))
        modified_kd_at = 'empty'
        if person.modified_kd_at is not None:
            modified_kd_at = str(person.modified_kd_at.strftime("%d.%m.%Y")) + \
                             '\n' + str(person.modified_kd_at.strftime("%H:%M:%S"))
        text_by_strings = [
            'Имя/ник: ' + name_or_nickname,
            'Имя в Телеге: ' + username,
            'Аккаунт ACTIVISION: ' + activision_account,
            'Аккаунт PSN: ' + psn_account,
            'К/Д WarZone: ' + kd_warzone,
            'К/Д в мультиплеере(MW19): ' + kd_multiplayer,
            'К/Д в Cold War: ' + kd_cold_war_multiplayer,
            '',
            'Last update: ',
            modified_kd_at
        ]
        full_text = '\n'.join(text_by_strings)  # красивый способ объеденить строки с пререносами
        await message.answer(text=full_text, reply=True)


# Показывает статистику по КД всех зарегистрированных пользователей
@dp.message_handler(chat_type=['group', 'supergroup'], is_chat_admin=True,
                    chat_id=COD_CHAT_ID, commands=['stats_all'])
@dp.message_handler(user_id=admins, commands=['stats_all'])
async def show_stats_all(message: types.Message, is_reply=True):
    """показывает статистику всех игроков в базе данных"""
    logger.info(
        f'Хэндлер STATS_ALL запущен пользователем с id {message.from_user.id} '
        f'({message.from_user.full_name}, {message.from_user.username})')
    await types.ChatActions.typing()
    db = DB()
    members = db.get_all_persons()
    logger.info(f'Из БД загружено {len(members)} записей')
    await message.answer(text=f'Кол-во записей в БД: {len(members)}', reply=True)
    for person in members:
        await types.ChatActions.typing()
        name_or_nickname = 'empty'
        if person.name_or_nickname is not None:
            name_or_nickname = str(person.name_or_nickname)
        username = 'empty'
        if person.tg_account.username is not None:
            username = str(person.tg_account.username)
        activision_account = 'empty'
        if person.activision_account is not None:
            activision_account = str(person.activision_account)
        psn_account = 'empty'
        if person.psn_account is not None:
            psn_account = str(person.psn_account)
        kd_warzone = 'empty'
        if person.kd_warzone is not None:
            kd_warzone = str(float(person.kd_warzone))
        kd_multiplayer = 'empty'
        if person.kd_multiplayer is not None:
            kd_multiplayer = str(float(person.kd_multiplayer))
        kd_cold_war_multiplayer = 'empty'
        if person.kd_cold_war_multiplayer is not None:
            kd_cold_war_multiplayer = str(float(person.kd_cold_war_multiplayer))
        modified_kd_at = 'empty'
        if person.modified_kd_at is not None:
            modified_kd_at = str(person.modified_kd_at.strftime("%d.%m.%Y")) + \
                             '\n' + str(person.modified_kd_at.strftime("%H:%M:%S"))
        text_by_strings = [
            'Имя/ник: ' + name_or_nickname,
            'Имя в Телеге: ' + username,
            'Аккаунт ACTIVISION: ' + activision_account,
            'Аккаунт PSN: ' + psn_account,
            'К/Д WarZone: ' + kd_warzone,
            'К/Д в мультиплеере(MW19): ' + kd_multiplayer,
            'К/Д в Cold War: ' + kd_cold_war_multiplayer,
            '',
            'Last update: ',
            modified_kd_at
        ]
        full_text = '\n'.join(text_by_strings)  # красивый способ объеденить строки с пререносами
        await message.answer(text=full_text, reply=False)


# Обновляет статистику по КД
@dp.message_handler(chat_type='private', commands=['stat_update'])
@dp.message_handler(user_id=admins, commands=['stat_update'])
async def stat_update_handler(message: types.Message):
    await types.ChatActions.typing()
    db = DB()
    tg_account = db.get_tg_account(tg_id=message.from_user.id)
    if tg_account is not None:
        member = db.get_person_by_tg_account(tg_account=tg_account)
        print(member)
        if await stat_update(person=member, db=db):
            await message.answer(message.from_user.first_name + ", статистика обновлена")
        else:
            await message.answer(message.from_user.first_name +
                                 ", вам необходимо уточнить свой ACTIVISION_ID, для этого воспользуйтесь командой /add_me")


# Обновляет статистику по КД всем зарегистрированным пользователей
@dp.message_handler(chat_type=['group', 'supergroup', 'private'], is_chat_admin=True,
                    chat_id=COD_CHAT_ID, commands=['stats_update_all'])
@dp.message_handler(user_id=admins, commands=['stats_update_all'])
async def stats_update_all(message: types.Message):
    logger.info(
        f'Хэндлер stats_update_all запущен пользователем с id {message.from_user.id} '
        f'({message.from_user.full_name}, {message.from_user.username})')
    await types.ChatActions.typing()
    db = DB()
    players = db.get_all_persons()
    for player in players:
        await types.ChatActions.typing()
        if player is not None:  # проверяем, смогли ли мы загрузить свою учётку в БД
            if player.modified_kd_at is None:
                logger.info(f'КД ранее ни разу удачно не обновлялось')
                need_to_update_kd = True
            else:
                logger.info(f'Последнее удачное обновление КД произошло {player.modified_kd_at}')
                # сколько прошло секунд с последнего обновления
                timestamp_delta = datetime.now().timestamp() - player.modified_kd_at.timestamp()
                # переводим секунды в часы, с округлением вниз
                hours_delta_int = math.floor(timestamp_delta / (60 * 60))
                logger.info(f'Последнее удачное обновление КД было {hours_delta_int} часов назад')
                hours = 10  # как часто обновлять КД
                if hours_delta_int > hours:
                    need_to_update_kd = True
                else:
                    need_to_update_kd = False
                    logger.info(f'КД обновляется на чаще раза в {hours} часов. Еще не пришло время обновлять КД')
            if need_to_update_kd:
                logger.info(f'Обновляем КД')
                await stat_update(db=db, person=player)
                await message.answer(f'статистика игрока с аккаунтом ACTIVISION {player.activision_account} обновлена')
            else:
                await message.answer(
                    f'Обновление статистики для игрока с аккаунтом ACTIVISION {player.activision_account} не требуется')
    await message.answer(message.from_user.first_name + ", обновление статистики по всем пользователям закончена!")


@dp.message_handler(chat_type=['group', 'supergroup'], commands=['stats_update_all', 'stats_all'])
async def show_stats_all(message: types.Message, is_reply=True):
    """показывает статистику всех игроков в базе данных"""
    await types.ChatActions.typing()
    await message.answer(
        'Данную команду может выполнить только пользователь с правами админимтратора', reply=is_reply)


