import math

from utils.db_api.alchemy import Person, TG_Account, DB
from aiogram import types
import logging
from datetime import datetime
import re

from utils.parser_cod_tracker_gg.cod_stats_parser import parse_stat, get_kd

logger = logging.getLogger(__name__)


def update_statistics_if_needs(db: DB, person: Person, hours=10):
    logger.info(f'Не найдено ни каких упоминаний, выводим статистику по себе...')
    if person is not None:  # проверяем, смогли ли мы загрузить свою учётку в БД
        if person.modified_kd_at is None:
            logger.info(f'КД ранее ни разу удачно не обновлялось')
            need_to_update_kd = True
        else:
            logger.info(f'Последнее удачное обновление КД произошло {person.modified_kd_at}')
            # сколько прошло секунд с последнего обновления
            timestamp_delta = datetime.now().timestamp() - person.modified_kd_at.timestamp()
            # переводим секунды в часы, с округлением вниз
            hours_delta_int = math.floor(timestamp_delta / (60 * 60))
            logger.info(f'Последнее удачное обновление КД было {hours_delta_int} часов назад')
            if hours_delta_int > hours:
                need_to_update_kd = True
            else:
                need_to_update_kd = False
                logger.info(f'КД обновляется на чаще раза в {hours} часов. Еще не пришло время обновлять КД')
        if need_to_update_kd:
            logger.info(f'Обновляем КД')
            stat_update(db=db, person=person)


def stat_update(db: DB, person: Person):
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


def load_profile(member: Person):
    """показывает профиль пользователя"""

    result = ''
    text0 = "Имя/ник: " + str(member.name) + "\n"
    if member.tg_name != 'unknown':
        text0 += "Имя в Телеге: @" + str(member.tg_name) + "\n"
    text1 = "ACTIVISION ID: " + str(member.activision_id) + "\n"
    text2 = "PSN ID: " + str(member.psn_id) + "\n"
    result += text0 + text1 + text2
    return result


def load_kd(member: Person):
    """показывает профиль пользователя"""

    result = ''
    text1 = "К/Д в Варзоне: " + str(member.kd_warzone) + "\n"
    text2 = "К/Д в мультиплеере: " + str(member.kd_multiplayer) + "\n\n"
    text3 = "Last update: " \
            + "\n" + str(member.update_kd.strftime("%d.%m.%Y")) \
            + "\n" + str(member.update_kd.strftime("%H:%M:%S"))
    result += text1 + text2 + text3
    return result


# Обновляем аккаунт телеграм в БД
def update_tg_account(from_tg_user) -> bool:
    """Обновляем аккаунт телеграм в БД"""
    db = DB()
    try:
        tg_account = db.get_tg_account(tg_id=from_tg_user.id)
        tg_account.username = from_tg_user.username
        tg_account.first_name = from_tg_user.first_name
        tg_account.is_bot = from_tg_user.is_bot
        tg_account.language_code = from_tg_user.language_code
        tg_account.modified_at = datetime.now()
        db.session.add(tg_account)
        db.session.commit()
        logger.info(f'{tg_account} - успешное обновление в БД')
        return True
    except Exception as ex:
        logger.info(f'Обновление в БД с ОШИБКОЙ {ex}')
        db.session.rollback()
        return False


# Возвращает информацию о Пользователе в виде текста
def profile_info(cod_user: Person) -> str:
    """Возвращает информацию о Пользователе в виде текста"""
    db = DB()
    if cod_user.platform is not None:
        platform = db.get_all_platforms(id=cod_user.platform)[0]
        platform_name = platform.name
    else:
        platform_name = None

    if cod_user.input_device is not None:
        input_device = db.get_all_input_devices(id=cod_user.input_device)[0]
        input_device_name = input_device.name
    else:
        input_device_name = None

    if cod_user.modified_at is not None:
        modified_at = str(cod_user.modified_at.strftime("%d.%m.%Y %H:%M"))
    else:
        modified_at = None
    db.close()
    text_by_strings = [
        f'Информация о пользователе:',
        '',
        f'Порядковый номер в базе данных: {cod_user.id}',
        f'Имя или ник: <b>{cod_user.name_or_nickname}</b>',
        f'Аккаунт ACTIVISION: <b>{cod_user.activision_account}</b>',
        f'Аккаунт PSN: <b>{cod_user.psn_account}</b>',
        f'Аккаунт Blizzard: <b>{cod_user.blizzard_account}</b>',
        f'Аккаунт Xbox: <b>{cod_user.xbox_account}</b>',
        f'Предпочитаемая платформа: <b>{platform_name}</b>',
        f'Предпочитаемое устройство ввода: <b>{input_device_name}</b>',
        f'О себе: <b>{cod_user.about_yourself}</b>',
        f'',
        f'Last update: {modified_at}'
    ]
    full_text = '\n'.join(text_by_strings)  # красивый способ объеденить строки с пререносами
    return full_text


# Возвращает информацию о Пользователе в виде текста
def full_profile_info(cod_user: Person) -> str:
    """Возвращает информацию о Пользователе в виде текста"""

    platform_name = 'empty'
    if cod_user.platform is not None:
        platform_name = cod_user.platform.name
    input_device = 'empty'
    if cod_user.input_device is not None:
        input_device = cod_user.input_device.name
    name_or_nickname = 'empty'
    if cod_user.name_or_nickname is not None:
        name_or_nickname = str(cod_user.name_or_nickname)
    username = 'empty'
    if cod_user.tg_account.username is not None:
        username = str(cod_user.tg_account.username)
    activision_account = 'empty'
    if cod_user.activision_account is not None:
        activision_account = str(cod_user.activision_account)
    psn_account = 'empty'
    if cod_user.psn_account is not None:
        psn_account = str(cod_user.psn_account)
    kd_warzone = 'empty'
    if cod_user.kd_warzone is not None:
        kd_warzone = str(float(cod_user.kd_warzone))

    kd_multiplayer = 'empty'
    if cod_user.kd_multiplayer is not None:
        kd_multiplayer = str(float(cod_user.kd_multiplayer))

    kd_cold_war_multiplayer = 'empty'
    if cod_user.kd_cold_war_multiplayer is not None:
        kd_cold_war_multiplayer = str(float(cod_user.kd_cold_war_multiplayer))

    created_at = 'empty'
    if cod_user.created_at is not None:
        created_at = str(cod_user.created_at.strftime("%d.%m.%Y %H:%M"))

    modified_at = 'empty'
    if cod_user.modified_at is not None:
        modified_at = str(cod_user.modified_at.strftime("%d.%m.%Y %H:%M"))

    modified_kd_at = 'empty'
    if cod_user.modified_kd_at is not None:
        modified_kd_at = str(cod_user.modified_kd_at.strftime("%d.%m.%Y %H:%M"))

    tg_acc_created_at = 'empty'
    if cod_user.tg_account.created_at is not None:
        tg_acc_created_at = str(cod_user.tg_account.created_at.strftime("%d.%m.%Y %H:%M"))

    tg_acc_modified_at = 'empty'
    if cod_user.tg_account.modified_at is not None:
        tg_acc_modified_at = str(cod_user.tg_account.modified_at.strftime("%d.%m.%Y %H:%M"))

    text_by_strings = [
        f'Информация о пользователе:',
        '',
        f'Порядковый номер в базе данных: {cod_user.id}',
        f'Имя или ник: {name_or_nickname}',
        f'Аккаунт ACTIVISION: {activision_account}',
        f'Аккаунт PSN: {psn_account}',
        f'Аккаунт Blizzard: {cod_user.blizzard_account}',
        f'Аккаунт Xbox: {cod_user.xbox_account}',
        f'Предпочитаемая платформа: {platform_name}',
        f'Предпочитаемое устройство ввода: {input_device}',
        f'О себе: {cod_user.about_yourself}',
        f'КД Варзон: {kd_warzone}',
        f'КД мультиплеер: {kd_multiplayer}',
        f'КД Колдвар: {kd_cold_war_multiplayer}',
        f'дата создания аккаунта: {created_at}',
        f'дата изменения аккаунта: {modified_at}',
        f'дата обновления статистики: {modified_kd_at}',
        '',
        f'Информация о телеграм-аккаунте:',
        '',
        f'ID: {cod_user.tg_account.id}',
        f'Username: {username}',
        f'First_name: {cod_user.tg_account.first_name}',
        f'Is_bot: {cod_user.tg_account.is_bot}',
        f'Language_code: {cod_user.tg_account.language_code}',
        f'дата создания аккаунта в БД: {tg_acc_created_at}',
        f'дата изменения аккаунта в БД: {tg_acc_modified_at}'
    ]
    full_text = '\n'.join(text_by_strings)  # красивый способ объеденить строки с пререносами
    return full_text


# Возвращает списком всех упомянутых пользователей
def mentioned_user_list(message: types.Message):
    """Возвращает списком всех упомянутых пользователей"""
    tg_account_list = []
    db = DB()
    members = []

    # часть кода, чтобы узнать есть ли в сообщении текст, кроме текста команд
    message_text = message.text
    pattern = re.compile('/+\w{0,100}')  # паттерн, для нахождения команд в тексте
    all_commands = re.findall(pattern, message_text)  # список всех команд в тексте
    for item in all_commands:
        message_text = message_text.replace(item, '', 1)
    print('ТЕКСТ БЕЗ КОМАНД: ', message_text)
    if message_text == '':
        print('а текст то пустой =)')
        return []
    # часть кода, для mention
    pattern = re.compile('@+\w{0,100}')  # паттерн, для нахождения упоминаний в тексте
    username_list = re.findall(pattern, message.text)  # Список упоминаний по username в данном сообщении
    logger.info(f'В указанном тексте {len(username_list)} упоминаний по username')
    if len(username_list) > 0:
        for mention in username_list:
            mention = mention.replace('@', '')  # Удалим из списка символ @
            logger.info(f'обнаружено упоминание Username = {mention}')
            tg_account = db.get_tg_account(tg_username=mention)
            if tg_account is not None:
                tg_account_list.append(tg_account)

    # часть кода, для text_mention
    text_mentions = []
    for entity in message.entities:
        if entity.type == 'text_mention':
            text_mentions.append(entity)
    logger.info(f'В указанном тексте {len(text_mentions)} упоминаний по text_mention')
    if len(text_mentions) > 0:
        for entity in text_mentions:  # перебираем сущности, являюзиеся текстовыми упоминаниями
            if entity.type == 'text_mention':  # если находим упоминания
                logger.info('text_mention обнаружен')
                tg_account = db.get_tg_account(tg_id=entity.user.id)
                if tg_account is not None:
                    tg_account_list.append(tg_account)


    if len(tg_account_list) > 0:
        for tg_account in tg_account_list:
            member = db.get_person_by_tg_account(tg_account)
            if member is not None:
                logger.info(f'найден аккаунт, соответствующий данному username: {member}')
                members.append(member)
            else:
                logger.info(f'аккаунт, соответствующий {tg_account} не обнаружен')
    return members


# Актуальный текст о проведении ремонтных работ
def zaglushka():
    """Актуальный текст о проведении ремонтных работ"""
    text_by_strings = [
        'В связи с проведением работ регистрация новых пользователей и изменение данных уже зарегистрированных '
        'пользователей временно не осуществляется!',
        'Благодарю за понимание,',
        '@MaNiLe88'
    ]
    full_text = '\n'.join(text_by_strings)  # красивый способ объеденить строки с пререносами
    return full_text
