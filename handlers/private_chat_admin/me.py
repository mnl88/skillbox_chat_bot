import asyncio

from aiogram import types
from aiogram.dispatcher.filters.builtin import Command

from filters import IsPrivate
from handlers.private_chat.handler_0_middleware import update_tg_account, profile_info, update_statistics_if_needs
from loader import dp, bot
from utils.db_api.alchemy import Person, DB, TG_Account
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
# from .handler_3_cod_stats import show_profile
import logging
# from handlers.cod_old_handlers.handler_0_middleware import update_tg_account, mentioned_user_list, profile_info
from keyboards.inline import inline_kb1_shoe_profile_or_stats, inline_kb_edit_data, \
    inline_kb_edit_or_not
from keyboards import inline

logger = logging.getLogger(__name__)


class CommandMeState(StatesGroup):
    intro = State()
    no_person_in_db = State()
    show_profile_or_stats = State()
    showing_person_data = State()
    showing_statistics = State()
    edit_profile = State()
    choose_what_to_edit = State()
    edit_value_selected_before = State()
    input_device_is_selected = State()
    platform_is_selected = State()
    account_is_selected = State()
    account_is_entered = State()


# при нажатии /me
@dp.message_handler(Command('me'), IsPrivate())
async def command_me(message: types.Message, state: FSMContext):
    logger.info(f'Пользователь {message.from_user.full_name} (ID: {message.from_user.id}) нажал команду ME')
    text = 'Привет, друг! Подожди буквально пару секунд, я проверю, зарегистрирован ли ты в базе данных...'
    main_message = await message.answer(text=text)
    async with state.proxy() as data:
        data['main_message_id'] = main_message.message_id
    await types.ChatActions.typing()
    await asyncio.sleep(1)
    db = DB()
    tg_account = db.get_tg_account(tg_id=message.from_user.id)
    if db.is_person_exists(tg_account):  # если пользователь уже есть в БД
        logger.info('Пользователь уже был зарегистрирован ранее в БД')
        text = [
            f'Привет, {message.from_user.full_name}, '
            f'а я тебя помню!!!',
            f'Что я могу для тебя сделать?',
        ]
        inline_kb = inline_kb1_shoe_profile_or_stats
        await CommandMeState.show_profile_or_stats.set()
    else:
        logger.info('Пользователя нет в БД')
        text = [
            f'Привет, {message.from_user.full_name}, как я понял, мы с тобой ещё не знакомы?!',
            '',
            f'Для корректной работы БОТА прошу тебя зарегистрироваться '
            f'и указать любой из перечисленных аккаунтов, привязанных к Call of Duty...'
        ]
        inline_kb = inline.kb_account
        await CommandMeState.account_is_selected.set()
    joined_text = '\n'.join(text)
    await bot.edit_message_text(
        chat_id=message.from_user.id,
        message_id=main_message.message_id,
        text=joined_text,
        reply_markup=inline_kb
    )
    db.close()


# при указании аккаунта нажата кнопка НАЗАД
@dp.callback_query_handler(text='go_back', state=CommandMeState.account_is_entered)
async def command_me(query: types.CallbackQuery, state: FSMContext):
    logger.info(f'Пользователь {query.from_user.full_name} (ID: {query.from_user.id}) нажал кнопку НАЗАД')

    data = await state.get_data()

    text = [
        f'{query.from_user.full_name}, для корректной работы БОТА прошу тебя зарегистрироваться '
        f'и указать любой из перечисленных аккаунтов, привязанных к Call of Duty...'
    ]
    inline_kb = inline.kb_account
    await CommandMeState.account_is_selected.set()

    joined_text = '\n'.join(text)
    await bot.edit_message_text(
        chat_id=query.from_user.id,
        message_id=data['main_message_id'],
        text=joined_text,
        reply_markup=inline_kb
    )


# при указании аккаунта
@dp.callback_query_handler(state=CommandMeState.account_is_selected)
async def command_me(query: types.CallbackQuery, state: FSMContext):
    await types.ChatActions.typing()

    data = await state.get_data()
    logger.info(f'Пользователь {query.from_user.full_name} '
                f'(ID: {query.from_user.id}) нажал кнопку {query.data}')

    await bot.answer_callback_query(callback_query_id=query.id)

    message_text = f"Введите {query.data}. \nЕсли передумали, нажмите кнопку НАЗАД"

    await bot.edit_message_text(
        chat_id=query.from_user.id,
        message_id=data['main_message_id'],
        text=message_text,
        reply_markup=inline.inline_kb_go_back,
        parse_mode=types.ParseMode.HTML
    )
    async with state.proxy() as data:
        data['selected_account'] = query.data
    await CommandMeState.account_is_entered.set()


# при указании аккаунта
@dp.message_handler(state=CommandMeState.account_is_entered)
async def command_me(message: types.Message, state: FSMContext):
    message_id = message.message_id

    await types.ChatActions.typing()
    data = await state.get_data()
    logger.info(f'Пользователь {message.from_user.full_name} '
                f'(ID: {message.from_user.id}) указал значение {message.text}')

    # message_text = f"Введите {query.data}. \nЕсли передумали, нажмите кнопку НАЗАД"

    db = DB()
    # tg_account = TG_Account(id=message.from_user.id)
    person = Person(tg_account=TG_Account(id=message.from_user.id))
    if data['selected_account'] == 'psn_account':
        person.psn_account = message.text
    if data['selected_account'] == 'blizzard_account':
        person.blizzard_account = message.text
    if data['selected_account'] == 'activision_account':
        person.psn_account = message.text
    if data['selected_account'] == 'xbox_account':
        person.psn_account = message.text
    db.session.add(person)
    db.session.commit()
    update_tg_account(from_tg_user=message.from_user)

    db.session.commit()
    text = [
        f'{message.from_user.full_name}, спасибо за регистрацию.',
        '',
        f'Что я могу для тебя сделать?',
    ]

    inline_kb = inline_kb1_shoe_profile_or_stats
    await CommandMeState.show_profile_or_stats.set()
    joined_text = '\n'.join(text)
    await bot.edit_message_text(
        chat_id=message.from_user.id,
        message_id=data['main_message_id'],
        text=joined_text,
        reply_markup=inline_kb
    )
    await bot.delete_message(
        chat_id=message.from_user.id,
        message_id=message_id
            )
    db.close()


# если нажата кнопка show_profile
@dp.callback_query_handler(text='show_profile', state=CommandMeState.show_profile_or_stats)
async def callback_show_profile(query: types.CallbackQuery, state: FSMContext):
    await types.ChatActions.typing()
    data = await state.get_data()
    main_message_id = data['main_message_id']
    print(f'{main_message_id=}')
    logger.info(f'Пользователь {query.from_user.full_name} '
                f'(ID: {query.from_user.id}) нажал инлайн кнопку ПОКАЗАТЬ ПРОФИЛЬ')
    await bot.answer_callback_query(callback_query_id=query.id)
    db = DB()
    tg_account = db.get_tg_account(tg_id=query.from_user.id)
    person = db.get_person_by_tg_account(tg_account=tg_account)
    full_text = profile_info(person) + '\n\n<b>Хотите изменить профиль?</b>'
    # await asyncio.sleep(1)

    await bot.edit_message_text(
        chat_id=query.from_user.id,
        message_id=main_message_id,
        text=full_text,
        parse_mode=types.ParseMode.HTML,
        reply_markup=inline_kb_edit_or_not
    )
    await CommandMeState.edit_profile.set()
    db.close()


# если нажата кнопка edit_profile
# TODO: 1) сделать кнопку назад, а потом уже вариант заполнения...
#
#
@dp.callback_query_handler(text='edit_profile', state=CommandMeState.edit_profile)
async def callback_show_profile(query: types.CallbackQuery, state: FSMContext):
    logger.info(f'Пользователь {query.from_user.full_name} '
                f'(ID: {query.from_user.id}) нажал инлайн кнопку РЕДАКТИРОВАТЬ ПРОФИЛЬ')
    await types.ChatActions.typing()
    data = await state.get_data()
    main_message_id = data['main_message_id']

    await bot.answer_callback_query(callback_query_id=query.id)
    db = DB()
    tg_account = db.get_tg_account(tg_id=query.from_user.id)
    person = db.get_person_by_tg_account(tg_account=tg_account)
    full_text = '<b>Выберите, что вы хотите изменить?</b>'
    # await asyncio.sleep(1)

    await bot.edit_message_text(
        chat_id=query.from_user.id,
        message_id=main_message_id,
        text=(profile_info(person) + '\n\n' + full_text),
        parse_mode=types.ParseMode.HTML,
        reply_markup=inline_kb_edit_data
    )
    await CommandMeState.choose_what_to_edit.set()
    db.close()


# если нажата кнопка show_statistics
@dp.callback_query_handler(text='show_statistics', state=CommandMeState.show_profile_or_stats)
async def callback_show_statistics(query: types.CallbackQuery, state: FSMContext):
    await types.ChatActions.typing()
    data = await state.get_data()
    main_message_id = data['main_message_id']
    logger.info(f'Пользователь {query.from_user.full_name} '
                f'(ID: {query.from_user.id}) нажал инлайн кнопку ПОКАЗАТЬ СТАТИСТИКУ')

    db = DB()
    await bot.answer_callback_query(callback_query_id=query.id)
    tg_account = db.get_tg_account(tg_id=query.from_user.id)
    update_tg_account(query.from_user)

    person = db.get_person_by_tg_account(tg_account=tg_account)
    update_statistics_if_needs(db, person)

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
        f'Имя/ник: <b>{name_or_nickname}</b>',
        f'Имя в Телеге: <b>{username}</b>',
        f'Аккаунт ACTIVISION: <b>{activision_account}</b>',
        f'Аккаунт PSN: <b>{psn_account}</b>',
        f'К/Д WarZone: <b>{kd_warzone}</b>',
        f'К/Д в мультиплеере(MW19): <b>{kd_multiplayer}</b>',
        f'К/Д в Cold War: <b>{kd_cold_war_multiplayer}</b>',
        '',
        f'Last update: ',
        f'<b>{modified_kd_at}</b>'
    ]
    full_text = '\n'.join(text_by_strings)
    await bot.edit_message_text(
        chat_id=query.from_user.id,
        message_id=main_message_id,
        text=full_text,
        parse_mode=types.ParseMode.HTML,
        reply_markup=inline.inline_kb_go_back
    )
    db.close()
    await CommandMeState.show_profile_or_stats.set()


# при нажатии НАЗАД из СТАТИСТИКИ
@dp.callback_query_handler(
    text='go_back',
    state=[
        CommandMeState.show_profile_or_stats,
        CommandMeState.edit_profile,
        CommandMeState.choose_what_to_edit,
        CommandMeState.input_device_is_selected,
        CommandMeState.platform_is_selected
    ]
)
async def command_me(query: types.CallbackQuery, state: FSMContext):
    await types.ChatActions.typing()
    data = await state.get_data()
    main_message_id = data['main_message_id']
    print(f'{main_message_id=}')
    logger.info(f'Пользователь {query.from_user.full_name} '
                f'(ID: {query.from_user.id}) нажал инлайн кнопку НАЗАД')
    text = [
        f'Привет, {query.from_user.full_name},',
        f'Что я могу для тебя сделать?'
    ]
    inline_kb = inline_kb1_shoe_profile_or_stats
    await CommandMeState.show_profile_or_stats.set()
    joined_text = '\n'.join(text)
    await bot.edit_message_text(
        chat_id=query.from_user.id,
        message_id=main_message_id,
        text=joined_text,
        reply_markup=inline_kb
    )
    await bot.answer_callback_query(callback_query_id=query.id)


# при ВЫБОРЕ что именнор редактировать...
@dp.callback_query_handler(
    state=CommandMeState.choose_what_to_edit,
    text=[
        'name_or_nickname',
        'activision_account',
        'psn_account',
        'blizzard_account',
        'xbox_account',
        'about_yourself',
    ]
)
async def command_me(query: types.CallbackQuery, state: FSMContext):
    await types.ChatActions.typing()
    data = await state.get_data()
    main_message_id = data['main_message_id']
    logger.info(f'Пользователь {query.from_user.full_name} '
                f'(ID: {query.from_user.id}) нажал кнопку {query.data}')

    db = DB()
    tg_account = db.get_tg_account(tg_id=query.from_user.id)
    person = db.get_person_by_tg_account(tg_account=tg_account)

    chose_text = ''
    previous_value = 'НЕ УКАЗАН'
    if query.data == 'name_or_nickname':
        chose_text = 'ИМЯ или НИКНЕЙМ'
        previous_value = person.name_or_nickname
    elif query.data == 'activision_account':
        chose_text = 'Аккаунт ACTIVISION'
        previous_value = person.activision_account
    elif query.data == 'psn_account':
        chose_text = 'Аккаунт PlayStationNetwork'
        previous_value = person.psn_account
    elif query.data == 'blizzard_account':
        chose_text = 'Аккаунт BLIZZARD (BATTLENET)'
        previous_value = person.blizzard_account
    elif query.data == 'xbox_account':
        chose_text = 'Аккаунт XBOX'
        previous_value = person.xbox_account
    elif query.data == 'platform_name':
        chose_text = 'Платформа (PC/PS/XBOX/...)'
        if person.platform is not None:
            previous_value = person.platform.name
    elif query.data == 'input_device_name':
        chose_text = 'Устройство ввода (клавомышь/геймпад)'
        if person.input_device is not None:
            previous_value = person.input_device.name
    elif query.data == 'about_yourself':
        chose_text = 'О себе'
        previous_value = person.about_yourself
    elif query.data == 'go_back':
        logger.error(f'ОШИБКА, кол бэк го бэк должен был поймать другой хендлер!!!!')
    else:
        logger.error(f'НЕОПОЗНАННЫЙ ВЫБОР!!!!{query.data}')
    async with state.proxy() as data:
        data['selected_key'] = query.data

    text = [
        profile_info(person),
        f'{query.from_user.full_name}, '
        f'ты выбрал редактирование <b>{chose_text}</b>.',
        f'Предыдущее значение - <b>{previous_value}</b>',
        f'Напиши ниже новое значение...'
    ]

    # inline_kb = inline_kb1_shoe_profile_or_stats
    # await CommandMeState.show_profile_or_stats.set()
    joined_text = '\n'.join(text)
    await bot.edit_message_text(
        chat_id=query.from_user.id,
        message_id=main_message_id,
        text=joined_text,
        parse_mode=types.ParseMode.HTML
    )
    db.close()
    await CommandMeState.edit_value_selected_before.set()


# при ВЫБОРЕ редактирования platform_name или input_device_name...
@dp.callback_query_handler(state=CommandMeState.choose_what_to_edit,
                           text=['platform_name', 'input_device_name'])
async def command_me(query: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    logger.info(f'Пользователь {query.from_user.full_name} '
                f'(ID: {query.from_user.id}) нажал кнопку {query.data}')

    if query.data == 'platform_name':
        keyboard = inline.kb_platform
        message_text = "Укажите основную платформу, которую вы используете для игры в Call of Duty"
        await CommandMeState.platform_is_selected.set()
    else:  # elif query.data == 'input_device_name'
        keyboard = inline.kb_input_device
        message_text = "Укажите основное устройство ввода, которое вы используете для игры в Call of Duty"
        await CommandMeState.input_device_is_selected.set()

    await bot.edit_message_text(
        chat_id=query.from_user.id,
        message_id=data['main_message_id'],
        text=message_text,
        reply_markup=keyboard,
        parse_mode=types.ParseMode.HTML
    )


# при указании платформы
@dp.callback_query_handler(state=CommandMeState.platform_is_selected)
async def command_me(query: types.CallbackQuery, state: FSMContext):
    await types.ChatActions.typing()
    data = await state.get_data()
    logger.info(f'Пользователь {query.from_user.full_name} '
                f'(ID: {query.from_user.id}) нажал кнопку {query.data}')
    db = DB()
    tg_account = db.get_tg_account(tg_id=query.from_user.id)
    person = db.get_person_by_tg_account(tg_account=tg_account)

    platform = db.get_all_platforms(id=query.data)[0]
    person.platform = platform.id
    db.update_person(person)

    await bot.answer_callback_query(callback_query_id=query.id)

    message_text = "Данные о платформе, на которой вы играете в Call of Duty, успешно обновлены!"

    await bot.edit_message_text(
        chat_id=query.from_user.id,
        message_id=data['main_message_id'],
        text=message_text,
        reply_markup=inline.inline_kb_go_back,
        parse_mode=types.ParseMode.HTML
    )

    db.close()


# при указании устройства ввода
@dp.callback_query_handler(state=CommandMeState.input_device_is_selected)
async def command_me(query: types.CallbackQuery, state: FSMContext):
    await types.ChatActions.typing()
    data = await state.get_data()
    logger.info(f'Пользователь {query.from_user.full_name} '
                f'(ID: {query.from_user.id}) нажал кнопку {query.data}')
    db = DB()
    tg_account = db.get_tg_account(tg_id=query.from_user.id)
    person = db.get_person_by_tg_account(tg_account=tg_account)

    input_device = db.get_all_input_devices(id=query.data)[0]
    person.input_device = input_device.id
    db.update_person(person)

    await bot.answer_callback_query(callback_query_id=query.id)

    message_text = "Данные об устройстве ввода, которое вы используете для игры в Call of Duty, успешно обновлены!"

    await bot.edit_message_text(
        chat_id=query.from_user.id,
        message_id=data['main_message_id'],
        text=message_text,
        reply_markup=inline.inline_kb_go_back,
        parse_mode=types.ParseMode.HTML
    )

    db.close()


@dp.message_handler(IsPrivate(), state=CommandMeState.edit_value_selected_before)
async def command_me(message: types.Message, state: FSMContext):
    data = await state.get_data()
    main_message_id = data['main_message_id']
    selected_key = data['selected_key']
    logger.info(f'Пользователь {message.from_user.full_name} (ID: {message.from_user.id})'
                f' решил отредактировать {selected_key} и указал значение {message.text}')
    async with state.proxy() as data:
        data['selected_value'] = message.text
    await types.ChatActions.typing()
    db = DB()
    tg_account = db.get_tg_account(tg_id=message.from_user.id)
    person = db.get_person_by_tg_account(tg_account=tg_account)
    if selected_key == 'name_or_nickname':
        person.name_or_nickname = message.text
    elif selected_key == 'activision_account':
        person.activision_account = message.text
    elif selected_key == 'blizzard_account':
        person.blizzard_account = message.text
    elif selected_key == 'psn_account':
        person.psn_account = message.text
    elif selected_key == 'xbox_account':
        person.xbox_account = message.text
    elif selected_key == 'about_yourself':
        person.about_yourself = message.text
    elif selected_key == 'platform_name':
        pass
    elif selected_key == 'input_device_name':
        pass
    else:
        logger.error(f'НЕОПОЗНАННЫЙ ВЫБОР!!!! {selected_key}')
    db.update_person(person)  # сохраним внесённые изменения
    full_text = f'<b>{selected_key}</b> удачно изменён на <b>{message.text}</b>\n\n' + \
                profile_info(person) + '\n\n<b>Хотите изменить что-то ещё?</b>'
    await asyncio.sleep(2)
    await bot.delete_message(
        chat_id=message.from_user.id,
        message_id=message.message_id)
    await bot.edit_message_text(
        chat_id=message.from_user.id,
        message_id=main_message_id,
        text=full_text,
        parse_mode=types.ParseMode.HTML,
        reply_markup=inline_kb_edit_or_not
    )
    await CommandMeState.edit_profile.set()
    db.close()
