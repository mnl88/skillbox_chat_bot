import asyncio
# from datetime import datetime
# import math

from aiogram import types
from aiogram.dispatcher.filters.builtin import CommandStart, Command

from filters import IsPrivate
# from re import compile
# from aiogram.utils.deep_linking import get_start_link
from data.config import admins, COD_CHAT_ID
# from handlers.private_chat.cod_statistics import stat_update
# from handlers.private_chat.handler_0_middleware import update_tg_account, mentioned_user_list, full_profile_info, \
#     profile_info
from loader import dp, bot
# from utils.db_api.alchemy import Person, DB
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
# from .handler_3_cod_stats import show_profile
import logging
# from handlers.cod_old_handlers.handler_0_middleware import update_tg_account, mentioned_user_list, profile_info
# from keyboards.inline import inline_kb1_shoe_profile_or_stats, inline_kb_to_reg, inline_kb_edit_data, inline_kb_edit_or_not
# from keyboards import inline
from keyboards.inline import inline_kb_start_is_reg, inline_kb_start_is_not_reg, inline_kb_editing_profile

from emoji import emojize

from utils.db_api.db_instanse import TG_Account, Badminton_player, B4U_Account
from utils.db_api.db_instanse import start_db
from aiogram.dispatcher import FSMContext
from states import RegPlayerState

logger = logging.getLogger(__name__)


# создание учётки, присим ввести имя
@dp.callback_query_handler(text="profile_create", state=RegPlayerState.intro_player_out_db)
async def bot_start_without_deeplink(call: types.CallbackQuery, state: FSMContext):
    # my_bot = await bot.get_me()
    await bot.answer_callback_query(callback_query_id=call.id)
    await call.message.answer('Подскажите, как мне к тебе обращаться, друг, чтобы и тебе было приятно, и мне?! =)')
    await RegPlayerState.username_entered.set()


# имя введено, предлагаем нажать кнопку РЕДАКТИРОВАТЬ ПРОФИЛЬ
@dp.message_handler(state=RegPlayerState.username_entered)
async def username_input(message: types.Message, state: FSMContext):

    # await message.delete()
    # text = message.text
    # data = await state.get_data()
    # msg = await message.answer(f'{text} + {data}')
    db = await start_db()
    tg_account = TG_Account(**message.from_user.values)
    if await tg_account.is_exists_by_id(db):
        tg_account = await tg_account.update(db)
    else:
        await tg_account.create(db)
    tg_account = await tg_account.read_by_id(db)
    tg_account: TG_Account
    player = Badminton_player(tg_id=tg_account.id, nickname=message.text)
    if await player.is_already_exists(db):
        logger.error(f'Бадминтонист {player} уже был зарегистрирован ранее в БД')
        # await RegPlayerState.
    else:
        await player.create(db)
        logger.info('Бадминтонист зарегистрирован в БД')

        main_message = await message.answer(
            text=f'Приятно познакомиться, {player.nickname}!\n\n'
                 f'Советую не откладывать в долгий ящик, а сразу в разделе редактирования профиля указать дополнительную информацию, необходимую '
                 f'для получения полного доступа ко всем моим функциям!',
            reply_markup=inline_kb_start_is_reg)
        await RegPlayerState.intro_player_in_db.set()

    await db.dispose()


# показываем инфу о профиле и предлагаем отредактировать другие параметры
@dp.callback_query_handler(text="profile_edit", state=RegPlayerState.intro_player_in_db)
async def show_profile_and_choose_what_to_edit(call: types.CallbackQuery):

    db = await start_db()
    tg_account = await TG_Account(**call.from_user.values).read_by_id(db)
    player = Badminton_player(tg_id=tg_account.id)
    if await player.is_already_exists(db):
        player = await player.read_by_tg_id(db)
        player: Badminton_player
        text = [
            f'Указанное имя: {player.nickname}\n',
        ]
        if player.b4u_id:
            b4u_account = await B4U_Account(id=player.b4u_id).smart_get(db)
            url = f'http://badminton4u.ru/players/{b4u_account.id}'
            player_b4u_acc_string = f'<a href="{url}">{b4u_account.username}</a>'
            text.append(
                f'Привязанный профиль LAB: {player.b4u_id}\n({player_b4u_acc_string})\n'
            )
        if player.vk_id:
            url = f'http:/vc.com/{player.vk_id}'
            player_vk_acc_string = f'<a href="{url}">{player.vk_id}</a>'
            text.append(
                f'Привязанный профиль ВК: {player_vk_acc_string}\n'
            )
        await bot.send_message(
            chat_id=call.message.chat.id,
            text='\n'.join(text),
            reply_markup=inline_kb_editing_profile
        )
        await RegPlayerState.profile_correctly_save.set()
        await bot.answer_callback_query(callback_query_id=call.id)
    else:
        logger.info('Бадминтонист не зарегистрирован ранее в БД')

    await db.dispose()


    # message = await call.message.answer(tg_account)

    # text = [
    #     f'<b>Вы не зарегистрированы. \nНа данный момент САМОСТОЯТЕЛЬНАЯ регистрация не возможна!</b>',
    #     f'\n<b>Приносим свои извинения!</b>'
    # ]
    # if await tg_account.is_exists_by_id(db):
    #     tg_account = await tg_account.update(db)
    #     player = Badminton_player(tg_id=tg_account.id)
    #     if await player.is_already_exists(db):
    #         player = await player.fetch_by_tg_id(db)
    #         logger.info(f'Бадминтонист {player} уже был зарегистрирован ранее в БД')
    #         url = f'http://badminton4u.ru/players/{player.b4u_id}'
    #         player_b4u_acc_string = f'<a href="{url}">{player.b4u_id}</a>'
    #         text = [
    #             f'Привет, {message.from_user.full_name}, '
    #             f'а я тебя помню!!!',
    #             f'\nУказанное имя при регистрации: {player.nickname}',
    #         ]
    #         if player.b4u_id:
    #             text.append(
    #                 f'Привязанный профиль LAB при регистрации: {player_b4u_acc_string}\n\n'
    #                 f'Нажмите /b4u , чтобы увидеть свой рейтинг LAB')
    #         await StateAddMe.profile_exists.set()
    #     else:
    #         logger.info('Бадминтонист не зарегистрирован ранее в БД')
    # else:
    #     logger.info('Телеграмм-аккаунт не зарегистрирован ранее в БД')
    # message2 = await message.answer(text='\n'.join(text), parse_mode=types.ParseMode.HTML)
    # await hello_message.delete()
    # await asyncio.sleep(30)
    # await message2.delete()

    # for AsyncEngine created in function scope, close and
    # clean-up pooled connections
    # await db.dispose()


# выбрано ПЕРЕИМЕНОВАНИЕ, предлагаем ввести имя
@dp.callback_query_handler(text="renaming", state=RegPlayerState.profile_correctly_save)
async def bot_start_without_deeplink(call: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query_id=call.id)
    await call.message.answer(
        'По поводу смены пола - это я пошутил! А вот имя, по которому я смогу к тебе обращаться, ты всегда можешь '
        'выбрать другое! =) Напиши, как мне теперь тебя величать?')
    await RegPlayerState.profile_renaming.set()


# имя введено, обновляем в БД, показываем инфу о профиле и предлагаем отредактировать другие параметры
@dp.message_handler(state=RegPlayerState.profile_renaming)
async def username_input(message: types.Message, state: FSMContext):
    db = await start_db()
    player = await Badminton_player(tg_id=message.from_user.id).read_by_tg_id(db)
    await player.update(db, nickname=message.text)
    await RegPlayerState.profile_correctly_renamed.set()

    player = await player.read_by_tg_id(db)

    new_message = await message.answer(f'Теперь я буду именовать тебя ни как иначе, как {message.text}!\n')

    player: Badminton_player
    text = [
        f'Указанное имя: {player.nickname}',
    ]
    if player.b4u_id:
        b4u_account = await B4U_Account(id=player.b4u_id).smart_get(db)
        url = f'http://badminton4u.ru/players/{b4u_account.id}'
        player_b4u_acc_string = f'<a href="{url}">{b4u_account.username}</a>'
        text.append(
            f'Привязанный профиль LAB: {player.b4u_id}\n({player_b4u_acc_string})\n'
        )
    if player.vk_id:
        url = f'http://badminton4u.ru/players/{player.vk_id}'
        player_b4u_acc_string = f'<a href="{url}">{player.vk_id}</a>'
        text.append(
            f'Привязанный профиль ВК: {player_b4u_acc_string}\n\n'
        )
    await message.answer(
        text='\n'.join(text),
        reply_markup=inline_kb_editing_profile
    )
    await RegPlayerState.profile_correctly_save.set()
    await db.dispose()
    await asyncio.sleep(10)
    await message.delete()
    await asyncio.sleep(30)
    await new_message.delete()


    # player = await tg_account.read_by_tg_id()
    # player = Badminton_player(tg_id=tg_account.id, nickname=message.text)
    # if await player.is_already_exists(db):
    #     logger.error(f'Бадминтонист {player} уже был зарегистрирован ранее в БД')
    #     # await RegPlayerState.
    # else:
    #     await player.create(db)
    #     logger.info('Бадминтонист зарегистрирован в БД')
    #
    #     main_message = await message.answer(
    #         text=f'Приятно познакомиться, {player.nickname}!\n\n'
    #              f'Советую не откладывать долгий ящик, а сразу в разделе редактирования профиля указать дополнительную информацию, необходимую '
    #              f'для получения полного доступа ко всем моим функциям',
    #         reply_markup=inline_kb_start_is_reg)
    #     await RegPlayerState.edit_profile.set()

    await db.dispose()


# выбрано Указать профиль LAB, предлагаем ввести LAB ID
@dp.callback_query_handler(text="lab_entering", state=RegPlayerState.profile_correctly_save)
async def bot_start_without_deeplink(call: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query_id=call.id)
    url = 'http://badminton4u.ru/players/'
    await call.message.answer(
        f'Укажи свой ID (цифрами) на сайте <a href="{url}">"Любительской Ассоциации Бадминтона"</a>,'
        f' чтобы я смог показывать тебе твой рейтинг прямо в Телеграме!',
        parse_mode=types.ParseMode.HTML,
        disable_web_page_preview=False
    )
    await RegPlayerState.profile_b4u_input.set()


# LAB ID введено, обновляем в БД, показываем инфу о профиле и предлагаем отредактировать другие параметры
@dp.message_handler(state=RegPlayerState.profile_b4u_input)
async def lab_id_input(message: types.Message, state: FSMContext):
    temprory_msg = await message.answer(
        'Когда-нибудь тут будет валидация, что пользователь ввёл число верно, а не абы что! =)')
    db = await start_db()

    player = await Badminton_player(tg_id=message.from_user.id).read_by_tg_id(db)
    # todo: добавить валидацию, если пользователь введёт не то
    try:
        # b4u_id = int(message.text)
        b4u_account = await B4U_Account(id=int(message.text)).smart_get(db)
        # if not await B4U_Account(id=b4u_id).is_exists_by_id(db):
        #     await B4U_Account(id=b4u_id).create(db)
        if b4u_account:
            await player.update(db, b4u_id=b4u_account.id)

        await RegPlayerState.profile_correctly_b4u_input.set()
    except:
        await message.answer(
            'Судя по всему ты не справился с заданием с первого раза. Походу зря говорят, что бадминтон - интеллектуальная игра!!!')

    player = await player.read_by_tg_id(db)

    new_message = await message.answer(f'Указанный тобой LAB ID: {message.text}!\n')

    player: Badminton_player
    text = [
        f'Указанное имя: {player.nickname}\n',
    ]
    if player.b4u_id:
        b4u_account = await B4U_Account(id=player.b4u_id).smart_get(db)
        url = f'http://badminton4u.ru/players/{b4u_account.id}'
        player_b4u_acc_string = f'<a href="{url}">{b4u_account.username}</a>'
        text.append(
            f'Привязанный профиль LAB: {player.b4u_id}\n({player_b4u_acc_string})\n'
        )
    if player.vk_id:
        url = f'http:/vc.com/{player.vk_id}'
        player_vk_acc_string = f'<a href="{url}">{player.vk_id}</a>'
        text.append(
            f'Привязанный профиль ВК: {player_vk_acc_string}\n'
        )
    await message.answer(
        text='\n'.join(text),
        reply_markup=inline_kb_editing_profile
    )
    await RegPlayerState.profile_correctly_save.set()
    await db.dispose()
    await asyncio.sleep(10)
    await message.delete()
    await asyncio.sleep(30)
    await new_message.delete()


# выбрано Указать профиль ВК, предлагаем ввести ВК ID
@dp.callback_query_handler(text="vk_entering", state=RegPlayerState.profile_correctly_save)
async def bot_start_without_deeplink(call: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query_id=call.id)
    url = 'https://vk.com/linkapp'
    await call.message.answer(
        f'Если укажешь свой ID (цифрами) на сайте <a href="{url}">"ВКонтакте"</a>,'
        f' то в дальнейшем сможешь пользоваться дополнительным функционалом.',
        parse_mode=types.ParseMode.HTML,
        disable_web_page_preview=False
    )
    await RegPlayerState.profile_vk_input.set()


# VK ID введено, обновляем в БД, показываем инфу о профиле и предлагаем отредактировать другие параметры
@dp.message_handler(state=RegPlayerState.profile_vk_input)
async def vk_id_input(message: types.Message, state: FSMContext):
    temprory_msg = await message.answer(
        'Когда-нибудь тут будет валидация, что пользователь ввёл число верно, а не абы что! =)')
    db = await start_db()

    player = await Badminton_player(tg_id=message.from_user.id).read_by_tg_id(db)
    # todo: добавить валидацию, если пользователь введёт не то
    try:
        vk_id = int(message.text)
        await player.update(db, vk_id=vk_id)

        await RegPlayerState.profile_correctly_vk_input.set()
    except:
        await message.answer(
            'Судя по всему ты не справился с заданием с первого раза. Походу зря говорят, что бадминтон - интеллектуальная игра!!!')

    player = await player.read_by_tg_id(db)

    new_message = await message.answer(f'Указанный тобой VK ID: {message.text}!\n')

    player: Badminton_player
    text = [
        f'Указанное имя: {player.nickname}\n',
    ]
    if player.b4u_id:
        b4u_account = await B4U_Account(id=player.b4u_id).smart_get(db)
        url = f'http://badminton4u.ru/players/{b4u_account.id}'
        player_b4u_acc_string = f'<a href="{url}">{b4u_account.username}</a>'
        text.append(
            f'Привязанный профиль LAB: {player.b4u_id}\n({player_b4u_acc_string})\n'
        )
    if player.vk_id:
        url = f'http:/vc.com/{player.vk_id}'
        player_vk_acc_string = f'<a href="{url}">{player.vk_id}</a>'
        text.append(
            f'Привязанный профиль ВК: {player_vk_acc_string}\n'
        )
    await message.answer(
        text='\n'.join(text),
        reply_markup=inline_kb_editing_profile
    )
    await RegPlayerState.profile_correctly_save.set()
    await db.dispose()
    await asyncio.sleep(10)
    await message.delete()
    await asyncio.sleep(30)
    await new_message.delete()


    # player = await tg_account.read_by_tg_id()
    # player = Badminton_player(tg_id=tg_account.id, nickname=message.text)
    # if await player.is_already_exists(db):
    #     logger.error(f'Бадминтонист {player} уже был зарегистрирован ранее в БД')
    #     # await RegPlayerState.
    # else:
    #     await player.create(db)
    #     logger.info('Бадминтонист зарегистрирован в БД')
    #
    #     main_message = await message.answer(
    #         text=f'Приятно познакомиться, {player.nickname}!\n\n'
    #              f'Советую не откладывать долгий ящик, а сразу в разделе редактирования профиля указать дополнительную информацию, необходимую '
    #              f'для получения полного доступа ко всем моим функциям',
    #         reply_markup=inline_kb_start_is_reg)
    #     await RegPlayerState.edit_profile.set()

    await db.dispose()





# message2 = await message.answer(text='\n'.join(text), parse_mode=types.ParseMode.HTML)
    # await hello_message.delete()
    # await asyncio.sleep(30)
    # await message2.delete()


    # message2 = await message.answer(text='Мы тебя типо записали, спасибо!', parse_mode=types.ParseMode.HTML)

#     my_bot = await bot.get_me()
#     await message.delete()
#     logger.info(f'Пользователь {message.from_user.full_name} (ID: {message.from_user.id}) нажал команду СТАРТ')
#
#     # cod_chat = await dp.bot.get_chat(chat_id=COD_CHAT_ID)
#     url = 'http://badminton4u.ru/'
#
#     text = [
#         'Данный бот создан как подспорье для бадминтонистов-любителей Санкт-Петербурга. '
#         'В данный момент бот находится в процессе активной разработки, '
#         'поэтому возможны ошибки и неточности в его работе.',
#         '',
#         'На текущий момент основной функцией бота является отображение своего рейтинга LAB, '
#         'согласно сайту ',
#         f'<a href="{url}">"Любительской Ассоциации Бадминтона"</a>'
#         '\n',
#         '<b>Для доступа к основным возможностям бота требуется пройти быструю регистрацию</b>'
#         # ' (/add_me)</b>'
#         '\n',
#         # 'Справка по основным командам: /help',
#         # '',
#         'автор: @MaN1Le'
#     ]
#     joined_text = '\n'.join(text)
#     intro_message = await message.answer(
#         text=joined_text,
#         parse_mode=types.ParseMode.HTML,
#         disable_web_page_preview=True
#     )
#     # await intro_message.pin()
#
#     await types.ChatActions.typing()
#     while_waiting_message = await message.answer(
#         text='Привет, друг! Подожди буквально пару секунд, я проверю, зарегистрирован ли ты в базе данных...')
#     db = await start_db()
#     tg_account = TG_Account(**message.from_user.values)
#     # text = [
#     #     f'<b>Вы не зарегистрированы. \nНа данный момент САМОСТОЯТЕЛЬНАЯ регистрация не возможна!</b>',
#     #     f'\n<b>Приносим свои извинения!</b>'
#     # ]
#     # await StateAddMe.profile_not_exists.set()
#     if await tg_account.is_exists_by_id(db):
#         tg_account = await tg_account.update(db)
#         player = Badminton_player(tg_id=tg_account.id)
#         if await player.is_already_exists(db):
#             player = await player.fetch_by_tg_id(db)
#             player: Badminton_player
#             logger.info(f'Бадминтонист {player} уже был зарегистрирован ранее в БД')
#             main_message = await message.answer(
#                 text=f'Привет, {player.nickname}, рад нашей встрече!\nЧем могу быть полезным?',
#                 reply_markup=inline_kb_start_is_reg)
#             # intro_message = await message.answer(
#             #     text=joined_text,
#             #     parse_mode=types.ParseMode.HTML,
#             #     reply_markup=inline_kb_start
#             # )
#
#
#
#             # url = f'http://badminton4u.ru/players/{player.b4u_id}'
#             # player_b4u_acc_string = f'<a href="{url}">{player.b4u_id}</a>'
#             # text = [
#             #     f'Привет, {message.from_user.full_name}, '
#             #     f'а я тебя помню!!!',
#             #     f'\nУказанное имя при регистрации: {player.nickname}',
#             # ]
#             # if player.b4u_id:
#             #     text.append(
#             #         f'Привязанный профиль LAB при регистрации: {player_b4u_acc_string}\n\n'
#             #         f'Нажмите /b4u , чтобы увидеть свой рейтинг LAB')
#             # await StateAddMe.profile_exists.set()
#         else:
#             logger.info('Бадминтонист не зарегистрирован ранее в БД')
#             main_message = await message.answer(
#                 text=f'Всегда рад новым знакомствам!\nМеня зовут {my_bot.full_name}, а тебя?',
#                 reply_markup=inline_kb_start_is_not_reg)
#     else:
#         logger.info('Телеграмм-аккаунт не зарегистрирован ранее в БД')
#
#     # message2 = await message.answer(text='\n'.join(text), parse_mode=types.ParseMode.HTML)
#     # await while_waiting_message.delete()
#     await asyncio.sleep(30)
#     await while_waiting_message.delete()
#
#     # for AsyncEngine created in function scope, close and
#     # clean-up pooled connections
#     # await db.dispose()
#
#     # chat = await bot.get_chat(chat_id=message.chat.id)
#
#     # await bot.delete_message(
#     #     chat_id=message.from_user.id,
#     #     message_id=hello_message.message_id
#     # )
#
# # """
# # Хэндлеры, обращающиеся к БД, позволяющие CRUD
# # """
# #
# # available_chose_edition = [
# #     "activision id",
# #     "psn id",
# #     "имя или прозвище"]
# #
# # cancel_inline_button = types.InlineKeyboardButton(text='Отмена!', callback_data='отмена')
# #
# #
# # class OrderAddUser(StatesGroup):
# #     waiting_for_enter_activision_id = State()
# #
# #
# # class OrderEditUser(StatesGroup):
# #     step_0 = State()
# #     step_1 = State()
# #     step_2 = State()
# #     step_3 = State()
# #

# text_and_data = [
#     ('Имя (никнейм)', 'name_or_nickname'),
#     ('ACTIVISION', 'activision_account'),
#     ('PSN', 'psn_account'),
#     ('Аккаунт Blizzard', 'blizzard_account'),
#     ('Аккаунт Xbox', 'xbox_account'),
#     ('Платформу', 'platform_name'),
#     ('Устройство ввода', 'input_device_name'),
#     ('Инфу о себе', 'about_yourself')
# ]
#
#
# # Редактирование пользователя. ШАГ 0.
# @dp.message_handler(chat_type=['private'], commands=['edit_me'], state="*")
# @dp.message_handler(user_id=admins, commands=['edit_me'], state="*")
# async def edit_me_in_bd(message: types.Message, state: FSMContext):
#     logger.info(
#         f'Хэндлер edit_me запущен пользователем с id {message.from_user.id} '
#         f'({message.from_user.full_name}, {message.from_user.username})')
#     await types.ChatActions.typing()
#     await OrderEditUser.step_0.set()  # Устанавливаем состояние step_0
#
#     db = DB()
#     update_tg_account(message.from_user)
#     if db.is_tg_account_exists(message.from_user.id) is False:
#         await message.answer(
#             str(message.from_user.first_name) + ", для выполнения данной команды вы должны зарегистрироваться." +
#             "\nДля регистрации перейдите в ПРИВАТНЫЙ ЧАТ с ботом",
#         )
#         await state.finish()
#         return
#     else:
#         tg_account = db.get_tg_account(tg_id=message.from_user.id)
#         person = db.get_person_by_tg_account(tg_account=tg_account)
#         await OrderEditUser.step_1.set()  # Устанавливаем состояние step_1
#         await edit_person_in_bd(db, person, message, state)

#
# # Редактирование пользователя. ШАГ 0. Случай, если кого-то упомянули
# @dp.message_handler(chat_type=['private'], user_id=admins, commands=['edit_person'], state="*")
# async def edit_mentioned_person_in_bd(message: types.Message, state: FSMContext):
#     logger.info(
#         f'Хэндлер edit_person запущен пользователем с id {message.from_user.id} '
#         f'({message.from_user.full_name}, {message.from_user.username})')
#     await types.ChatActions.typing()
#     await OrderEditUser.step_0.set()  # Устанавливаем состояние step_0
#     cod_user: Person
#     # находим кол-во упомянутых пользователей
#     persons = mentioned_user_list(message)
#     print('Кол-во идентифицированных упомянутых пользователей: ', len(persons))
#     # если 0, то или cod_user - это вы, или прерываем хендлер
#     db = DB()
#     if len(persons) == 0:
#         update_tg_account(message.from_user)
#         if db.is_tg_account_exists(message.from_user.id) is False:
#             await message.answer(
#                 str(message.from_user.first_name) + ", для выполнения данной команды вы должны зарегистрироваться." +
#                 "\nДля регистрации напишите боту в ПРИВАТНОМ ЧАТЕ команду: /add_me"
#             )
#             return
#         else:
#             tg_account = db.get_tg_account(tg_id=message.from_user.id)
#             cod_user = db.get_person_by_tg_account(tg_account=tg_account)
#         logger.info(f'В тексте сообщения не найдено упоминаний людей, ранее зарегистрированных в базе данных.')
#         await message.reply('В тексте сообщения не найдено упоминаний людей, ранее зарегистрированных в базе данных.')
#         await message.answer('Вывожу информацию о тебе...')  # tckb ytn
#     # если 1, то он и есть cod_user
#     elif len(persons) == 1:
#         cod_user = persons[0]
#         logger.info(f'В тексте сообщения найдено упоминание пользователя, ранее зарегистрированного в базе данных')
#         await message.reply(
#             'В тексте сообщения найдено упоминание пользователя, ранее зарегистрированного в базе данных')
#         await message.answer('Вывожу информацию об этом пользователе...')
#     # если несколько - то первый из упомянутых - cod_user
#     else:
#         cod_user = persons[0]
#         logger.info(
#             f'В тексте найдено сообщения упоминание нескольких пользователей, ранее зарегистрированных в базе данных, начато редактирование пользователя {cod_user.tg_account}')
#         await message.reply(
#             f'В тексте найдено сообщения упоминание нескольких пользователей, ранее зарегистрированных в базе данных')
#         await message.answer(f'Вывожу информацию об этом пользователе...{cod_user.tg_account}')
#     await OrderEditUser.step_1.set()  # Устанавливаем состояние step_1
#     await edit_person_in_bd(db, cod_user, message, state)
#
#
# # Редактирование пользователя. ШАГ 1.
# async def edit_person_in_bd(db: DB, person: Person, message: types.Message, state: FSMContext):
#     keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
#     full_text = profile_info(person)
#     print('Будем редактировать - ', person)
#     await message.answer(full_text, reply_markup=keyboard)
#
#     text_and_data = [('Редактировать!', 'yes'), ('Отмена!', 'отмена')]
#     row_btns = (types.InlineKeyboardButton(text, callback_data=data) for text, data in text_and_data)
#     inline_kb1 = types.InlineKeyboardMarkup().add(*row_btns)
#     await message.answer(f'Хотите начать редактирование данного пользователя?', reply_markup=inline_kb1)
#
#     # state = await state.get_data()
#     # print(state)
#     # state = await state.update_data(db=db)
#     await state.update_data(person=person)
#     await OrderEditUser.step_2.set()  # Устанавливаем состояние step_2
#
#
# # Редактирование пользователя. ШАГ 2. Заглушка
# @dp.callback_query_handler(text='отмена', state='*')
# async def paused_and_canceled(query: types.CallbackQuery, state: FSMContext):  # обратите внимание, есть второй аргумент
#     text = query.data
#     await state.finish()
#     # высылает текст юзеру
#     await bot.send_message(
#         query.message.chat.id,
#         f'Редактирование отменено пользователем', reply_markup=types.ReplyKeyboardRemove())
#     logger.info(f'Редактирование отменено пользователем {query.from_user.username} - ID: {query.from_user.username}')
#
#
# # Редактирование пользователя. ШАГ 2. Заглушка
# @dp.callback_query_handler(text='yes', state=OrderEditUser.step_2)
# async def edit_person_step_2_yes(query: types.CallbackQuery,
#                                  state: FSMContext):  # обратите внимание, есть второй аргумент
#     person = await state.get_data('person')
#     print(f'{person=}')
#
#     text = query.data
#     await types.ChatActions.typing()
#
#     buttons = (types.InlineKeyboardButton(text, callback_data=data) for text, data in text_and_data)
#     inline_kb = types.InlineKeyboardMarkup()
#     # for button in buttons:
#     #     inline_kb.add(*button)
#     inline_kb.add(*buttons)
#     inline_kb.add(cancel_inline_button)
#
#     await bot.send_message(
#         chat_id=query.message.chat.id,
#         text=f'Что именно вы хотите изменить?',
#         reply_markup=inline_kb)
#
#     await OrderEditUser.step_3.set()  # Устанавливаем состояние step_3
#     # высылает текст юзеру
#     # await bot.send_message(query.message.chat.id, f'Вы нажали {text}')
#
#
# @dp.callback_query_handler(state=OrderEditUser.step_3)
# async def edit_person_step_3(query: types.CallbackQuery, state: FSMContext):
#     await types.ChatActions.typing()
#     db = DB()
#     # tg_account = db.get_tg_account(tg_id=query.from_user.id)
#     # cod_user = db.get_person_by_tg_account(tg_account=tg_account)
#     #
#     # # callback_data = query.data
#
#     # if data == 'отмена':
#     #     await paused_and_canceled(query, state)
#     # elif data == 'name_or_nickname':
#     #
#     for text, data in text_and_data:
#         if data == query.data:
#
#             if query.data == 'platform_name':
#                 inline_kb_platform = types.InlineKeyboardMarkup(row_width=2)
#                 platforms = db.get_all_platforms()
#                 for platform in platforms:
#                     print(platform)
#                     inline_platform_button = types.InlineKeyboardButton(text=platform.name, callback_data=platform.id)
#                     inline_kb_platform.insert(inline_platform_button)
#                 inline_kb_platform.add(cancel_inline_button)
#                 await bot.send_message(
#                     chat_id=query.message.chat.id,
#                     text=f'Какую платформу указать как основную?',
#                     reply_markup=inline_kb_platform
#                 )
#
#             elif query.data == 'input_device_name':
#                 inline_kb_device = types.InlineKeyboardMarkup()
#                 devices = db.get_all_platforms()
#                 for device in devices:
#                     inline_device_button = types.InlineKeyboardButton(text=device.name, callback_data=device)
#                     inline_kb_device.add(inline_device_button)
#                 inline_kb_device.add(cancel_inline_button)
#                 await bot.send_message(
#                     chat_id=query.message.chat.id,
#                     text=f'Какое устройство ввода указать как основное?',
#                     reply_markup=types.inline_kb_device
#                 )
#
#             else:
#                 await bot.send_message(
#                     chat_id=query.message.chat.id,
#                     text=f'Введите {text}',
#                     reply_markup=types.ReplyKeyboardRemove()

                # )
    # elif query.data == 'отмена':
    #     await paused_and_canceled(query, state)

    # неожиданно всплывающее сообщение
    # await query.answer(text='АААААААААААААААААА', show_alert=True)

    # async with state.proxy() as data:
    #     print(data['person'])
    #
    # person2 = await state.get_data('person')
    # print(f'{person2=}')
#     if message.text.lower() == 'нет':
#         print('Вы сказали НЭТ')
#         await cancel_handler(message, state)
#     elif message.text.lower() == 'да':
#         print('Вы сказали ДАА')
#         await cancel_handler(message, state)
#         keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
#         buttons = []
#         # text_and_data = (
#         #     ("Имя(прозвище)", person.name_or_nickname),
#         #     ("Аккаунт ACTIVISION", person.activision_account),
#         #     ("Аккаунт PSN", person.psn_account),
#         #     ("Аккаунт Blizzard", person.psn_account),
#         #     ("Аккаунт Xbox", person.xbox_account),
#         #     ("Предпочитаемая платформа", person.platform),
#         #     ("Предпочитаемое устройство ввода", person.input_device),
#         #     ("Информация о себе", person.about_yourself)
#         # )
#         # for text, data in text_and_data:
#         #     button = types.InlineKeyboardButton(text, callback_data=data)
#         #     buttons.append(button)
#         # keyboard.add(buttons)
#         # await message.answer(f'Какие данные вы хотите указать/отредактировать?', reply_markup=keyboard)
#         # await OrderEditUser.step_2.set()
#     else:
#         await message.answer(f'Напишите или ДА, или НЕТ!!!')
#         return
#
#
# # Редактирование пользователя. ШАГ 3.
# # @dp.message_handler(state=OrderEditUser.step_3, content_types=types.ContentTypes.TEXT)
# # async def edit_person_step_3(message: types.Message, state: FSMContext):  # обратите внимание, есть второй аргумент
# #     await types.ChatActions.typing()
# #     person: Person = await state.get_data()
# #     if message.text.lower() == 'нет':
# #         print('Вы сказали НЭТ')
# #         await cancel_handler(message, state)
# #     elif message.text.lower() == 'да':
# #         print('Вы сказали ДАА')
# #         await cancel_handler(message, state)
# #         keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
# #
# #         for chose in text_and_data:
# #             keyboard.add(chose)
# #         await message.answer(f'Какие данные вы хотите указать/отредактировать?', reply_markup=keyboard)
# #         await OrderEditUser.step_2.set()
# #     else:
# #         await message.answer(f'Напишите или ДА, или НЕТ!!!')
#         return
#
#     # print('Выводим заглушку')
#     # await message.answer(zaglushka())
#     # await state.finish()
#
#     # db = DB()
#     #
#     # db.get_tg_account(tg_id=message.from_user.id)
#     # member = Person()
#     #
#     # if (message.from_user.id) is not False:
#     #     member = get_member_old(message.from_user.id)
#     # else:
#     #     member.tg_account.id = message.from_user.id
#     # await state.update_data(Activision_ID=message.text)
#     # user_data = await state.get_data()
#     # print(f'{user_data=}')
#     #
#     # pattern = compile('.+#+\d{0,20}')
#     # is_valid = pattern.match(user_data['Activision_ID'])
#     # if is_valid:
#     #     member.activision_id = user_data['Activision_ID']
#     #     session.add(member)
#     #     session.commit()
#     #     print(member)
#     #     print('Данные прошли валидацию')
#     #     await message.reply(
#     #         message.from_user.first_name + ", благодарим за регистрацию!\n" +
#     #         "для внесения дополнительной информации о себе советуем воспользоваться командой /edit_me",
#     #         reply_markup=types.ReplyKeyboardRemove()
#     #         )
#     # else:
#     #     print('Данные не прошли валидацию')
#     #     await message.reply(message.from_user.first_name +
#     #                         ", указанный вами Activision ID (" + user_data['Activision_ID'] +
#     #                         ") НЕ ПРОШЁЛ ВАЛИДАЦИЮ И НЕ БЫЛ СОХРАНЁН!\n\n" +
#     #                         "ещё одна попытка?! /add_me", reply_markup=types.ReplyKeyboardRemove()
#     #                         )
#     # await state.finish()


# # Команда редактирования пользователя. ШАГ 1. Выбор, какой параметр редактировать
# @dp.message_handler(chat_type=['private'], commands=['edit_me'], state="*")
# async def edit_user_profile_step_1(message: types.Message):
#     if is_row_exists_old(message.from_user.id) is False:
#         await message.answer(
#             str(message.from_user.first_name) + ", вы не зарегистрированы." +
#             "\nДля регистрации воспользуйтесь командой: /add_me"
#             )
#     else:
#         await show_profile(message, False)
#         keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
#         for chose in available_chose_edition:
#             keyboard.add(chose.upper())
#         keyboard.add("отмена")
#         await message.answer(
#             "Вы можете указать/отредактировать следующие данные:\n\n" +
#             "ACTIVISION_ID - необьходим для работы БОТА \nпример: Ivan#123456789\n\n" +
#             "PSN_ID - для добавления в ТУСОВКУ, \nпример: Ivan_Ivanov_1999\n\n" +
#             "ИМЯ или ПРОЗВИЩЕ - для того, чтобы к вам могли обращаться по имени, \nпример: Просто Иван\n\n\n" +
#             "указание другого параметра приведёт к отмене редактирования"
#             , reply_markup=keyboard)
#         await OrderEditUser.waiting_for_choose_parameter.set()
#
#
# # Команда редактирования пользователя. ШАГ 2. Уточняем значение того параметра, что указали ранее...
# @dp.message_handler(state=OrderEditUser.waiting_for_choose_parameter, content_types=types.ContentTypes.TEXT)
# async def edit_user_profile_step_2(message: types.Message, state: FSMContext):
#     await message.reply("введите", reply_markup=types.ReplyKeyboardRemove())
#     selected_choose = message.text.lower()
#
#     if selected_choose in available_chose_edition:
#         await state.update_data(user_choose=message.text.lower())
#         user_data = await state.get_data()
#         print(f'{user_data=}')
#         await OrderEditUser.waiting_for_choose_data.set()
#     else:
#         await cancel_handler(message, state)
#         # await state.finish()
#         # await message.reply("отмена", reply_markup=types.ReplyKeyboardRemove())
#         # return
#
#
# # Команда редактирования пользователя. ШАГ 3. Сохраняем введенное значение...
# @dp.message_handler(state=OrderEditUser.waiting_for_choose_data, content_types=types.ContentTypes.TEXT)
# async def edit_user_profile_step_3(message: types.Message, state: FSMContext):
#     member = COD_User_old(tg_id=message.from_user.id)
#     if get_member_old(message.from_user.id) is not False:
#         member = get_member_old(message.from_user.id)
#     pattern = compile('')
#     user_data = await state.get_data()
#     if user_data['user_choose'] == 'activision_id':
#         pattern = compile('.+#+\d{0,20}')
#     if user_data['user_choose'] == 'psn id':
#         pattern = compile('\w')
#     if user_data['user_choose'] == 'имя или прозвище':
#         pattern = compile('\w')
#     is_valid = pattern.match(user_data['user_choose'])
#     await state.update_data(value=message.text)
#     user_data = await state.get_data()
#     print(f'{user_data=}')
#     if is_valid:
#         if user_data['user_choose'] == 'activision id':
#             member.activision_id = user_data['value']
#         if user_data['user_choose'] == 'psn id':
#             member.psn_id = user_data['value']
#         if user_data['user_choose'] == 'имя или прозвище':
#             member.name = user_data['value']
#         session.add(member)
#         session.commit()
#         await message.reply(
#             message.from_user.first_name + ", вы выбрали обновить " + user_data['user_choose'] +
#             " и указали значение " + user_data['value'], reply_markup=types.ReplyKeyboardRemove()
#             )
#     else:
#         await message.reply(
#             message.from_user.first_name + ", вы выбрали обновить " + user_data['user_choose'] +
#             " и указали значение " + user_data['value'] + "\n\n"
#             "УКАЗАННЫЕ ВАМИ ДАНЫЕ НЕ ПРОШЛИ ВАЛИДАЦИЮ И НЕ БЫЛИ СОХРАНЕНЫ!", reply_markup=types.ReplyKeyboardRemove()
#             )
#     await OrderEditUser.waiting_for_continue_editing.set()
#     keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
#     keyboard.add("Продолжить редактирование")
#     keyboard.add("Завершить редактирование")
#     await message.answer(
#         "Продолжить редактирование профиля?\n\n", reply_markup=keyboard)
#
#
# # Команда редактирования пользователя. ШАГ 4. Продолжить или прервать редактирование?
# @dp.message_handler(state=OrderEditUser.waiting_for_continue_editing, content_types=types.ContentTypes.TEXT)
# async def edit_user_profile_step_4(message: types.Message, state: FSMContext):
#     if message.text == "Продолжить редактирование":
#         await edit_user_profile_step_1(message)
#     else:
#         await state.finish()
#         await message.reply("Редактирование профиля завершено", reply=True, reply_markup=types.ReplyKeyboardRemove())
#         return
#
#

# @dp.message_handler(CommandStart(deep_link=compile(r'.+'), encoded=False), IsPrivate())
# async def bot_start_with_deeplink(message: types.Message):
#     deep_link_args = message.get_args()
#     text = [
#         f'Привет, {message.from_user.full_name}!',
#         f'Вы находитесь в личной переписке',
#         f'В вашей команде ЕСТЬ deep_link',
#         f'Вы передали аргумент {deep_link_args}',
#     ]
#     joined_text = '\n'.join(text)
#     await message.answer(text=joined_text)
#
#     cod_chat = await dp.bot.get_chat(chat_id=COD_CHAT_ID)
#     text = [
#         'Данный бот написан для предоставления пользователям информации по своей статистике в игре '
#         f'CALL OF DUTY MW 2019/CW/Warzone и упрощения коммуникации участников тематической группы'
#         f'<a href="{cod_chat.invite_link}">{cod_chat.full_name}</a>',
#         '',
#         'Справка по основным командам: /help',
#         '',
#         'автор: @MaN1Le'
#     ]
#     joined_text = '\n'.join(text)
#     await message.answer(text=joined_text, parse_mode=types.ParseMode.HTML)
#
#     # await is_exist_in_bd(message):

#
# @dp.message_handler(CommandStart(), IsPrivate())
# async def bot_start_without_deeplink(message: types.Message):
#     deep_link = await get_start_link(payload='123', encode=False)
#     text = [
#         f'Привет, {message.from_user.full_name}!',
#         f'Вы находитесь в личной переписке',
#         f'В вашей команде НЕТ deep_link',
#         f'Вы передали аргумент {deep_link}',
#     ]
#     joined_text = '\n'.join(text)
#     await message.answer(text=joined_text)
#
#     # await is_exist_in_bd(message):

 # deep_link = await get_start_link(payload='123', encode=False)
    # text = [
    #     f'Привет, {message.from_user.full_name}!',
    #     f'Вы находитесь в личной переписке',
    #     f'В вашей команде НЕТ deep_link',
    #     f'Вы передали аргумент {deep_link}',
    # ]
    # joined_text = '\n'.join(text)
    # await message.answer(text=joined_text)

    # await is_exist_in_bd(message):