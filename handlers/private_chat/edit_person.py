"""
Хэндлеры, обращающиеся к БД, позволяющие CRUD
"""
from loader import dp, bot
from utils.db_api.alchemy import Person, DB
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
# from .handler_3_cod_stats import show_profile
import logging
from handlers.private_chat.handler_0_middleware import update_tg_account, mentioned_user_list, profile_info
from data.config import admins
from aiogram import types

logger = logging.getLogger(__name__)

available_chose_edition = [
    "activision id",
    "psn id",
    "имя или прозвище"]


cancel_inline_button = types.InlineKeyboardButton(text='Отмена!', callback_data='отмена')


class OrderAddUser(StatesGroup):
    waiting_for_enter_activision_id = State()


class OrderEditUser(StatesGroup):
    step_0 = State()
    step_1 = State()
    step_2 = State()
    step_3 = State()


text_and_data = [
        ('Имя (никнейм)', 'name_or_nickname'),
        ('ACTIVISION', 'activision_account'),
        ('PSN', 'psn_account'),
        ('Аккаунт Blizzard', 'blizzard_account'),
        ('Аккаунт Xbox', 'xbox_account'),
        ('Платформу', 'platform_name'),
        ('Устройство ввода', 'input_device_name'),
        ('Инфу о себе', 'about_yourself')
]

# Редактирование пользователя. ШАГ 0.
@dp.message_handler(chat_type=['private'], commands=['edit_me'], state="*")
@dp.message_handler(user_id=admins, commands=['edit_me'], state="*")
async def edit_me_in_bd(message: types.Message, state: FSMContext):
    logger.info(
        f'Хэндлер edit_me запущен пользователем с id {message.from_user.id} '
        f'({message.from_user.full_name}, {message.from_user.username})')
    await types.ChatActions.typing()
    await OrderEditUser.step_0.set()  # Устанавливаем состояние step_0

    db = DB()
    update_tg_account(message.from_user)
    if db.is_tg_account_exists(message.from_user.id) is False:
        await message.answer(
            str(message.from_user.first_name) + ", для выполнения данной команды вы должны зарегистрироваться." +
            "\nДля регистрации перейдите в ПРИВАТНЫЙ ЧАТ с ботом",
            )
        await state.finish()
        return
    else:
        tg_account = db.get_tg_account(tg_id=message.from_user.id)
        person = db.get_person_by_tg_account(tg_account=tg_account)
        await OrderEditUser.step_1.set()  # Устанавливаем состояние step_1
        await edit_person_in_bd(db, person, message, state)


# Редактирование пользователя. ШАГ 0. Случай, если кого-то упомянули
@dp.message_handler(chat_type=['private'], user_id=admins, commands=['edit_person'], state="*")
async def edit_mentioned_person_in_bd(message: types.Message, state: FSMContext):
    logger.info(
        f'Хэндлер edit_person запущен пользователем с id {message.from_user.id} '
        f'({message.from_user.full_name}, {message.from_user.username})')
    await types.ChatActions.typing()
    await OrderEditUser.step_0.set()  # Устанавливаем состояние step_0
    cod_user: Person
    # находим кол-во упомянутых пользователей
    persons = mentioned_user_list(message)
    print('Кол-во идентифицированных упомянутых пользователей: ', len(persons))
    # если 0, то или cod_user - это вы, или прерываем хендлер
    db = DB()
    if len(persons) == 0:
        update_tg_account(message.from_user)
        if db.is_tg_account_exists(message.from_user.id) is False:
            await message.answer(
                str(message.from_user.first_name) + ", для выполнения данной команды вы должны зарегистрироваться." +
                "\nДля регистрации напишите боту в ПРИВАТНОМ ЧАТЕ команду: /add_me"
            )
            return
        else:
            tg_account = db.get_tg_account(tg_id=message.from_user.id)
            cod_user = db.get_person_by_tg_account(tg_account=tg_account)
        logger.info(f'В тексте сообщения не найдено упоминаний людей, ранее зарегистрированных в базе данных.')
        await message.reply('В тексте сообщения не найдено упоминаний людей, ранее зарегистрированных в базе данных.')
        await message.answer('Вывожу информацию о тебе...')  # tckb ytn
    # если 1, то он и есть cod_user
    elif len(persons) == 1:
        cod_user = persons[0]
        logger.info(f'В тексте сообщения найдено упоминание пользователя, ранее зарегистрированного в базе данных')
        await message.reply('В тексте сообщения найдено упоминание пользователя, ранее зарегистрированного в базе данных')
        await message.answer('Вывожу информацию об этом пользователе...')
    # если несколько - то первый из упомянутых - cod_user
    else:
        cod_user = persons[0]
        logger.info(f'В тексте найдено сообщения упоминание нескольких пользователей, ранее зарегистрированных в базе данных, начато редактирование пользователя {cod_user.tg_account}')
        await message.reply(f'В тексте найдено сообщения упоминание нескольких пользователей, ранее зарегистрированных в базе данных')
        await message.answer(f'Вывожу информацию об этом пользователе...{cod_user.tg_account}')
    await OrderEditUser.step_1.set()  # Устанавливаем состояние step_1
    await edit_person_in_bd(db, cod_user, message, state)


# Редактирование пользователя. ШАГ 1.
async def edit_person_in_bd(db: DB, person: Person, message: types.Message, state: FSMContext):

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    full_text = profile_info(person)
    print('Будем редактировать - ', person)
    await message.answer(full_text, reply_markup=keyboard)

    text_and_data = [('Редактировать!', 'yes'), ('Отмена!', 'отмена')]
    row_btns = (types.InlineKeyboardButton(text, callback_data=data) for text, data in text_and_data)
    inline_kb1 = types.InlineKeyboardMarkup().add(*row_btns)
    await message.answer(f'Хотите начать редактирование данного пользователя?', reply_markup=inline_kb1)

    # state = await state.get_data()
    # print(state)
    # state = await state.update_data(db=db)
    await state.update_data(person=person)
    await OrderEditUser.step_2.set()  # Устанавливаем состояние step_2


# Редактирование пользователя. ШАГ 2. Заглушка
@dp.callback_query_handler(text='отмена', state='*')
async def paused_and_canceled(query: types.CallbackQuery, state: FSMContext):  # обратите внимание, есть второй аргумент
    text = query.data
    await state.finish()
    # высылает текст юзеру
    await bot.send_message(
        query.message.chat.id,
        f'Редактирование отменено пользователем', reply_markup=types.ReplyKeyboardRemove())
    logger.info(f'Редактирование отменено пользователем {query.from_user.username} - ID: {query.from_user.username}')


# Редактирование пользователя. ШАГ 2. Заглушка
@dp.callback_query_handler(text='yes', state=OrderEditUser.step_2)
async def edit_person_step_2_yes(query: types.CallbackQuery, state: FSMContext):  # обратите внимание, есть второй аргумент
    person = await state.get_data('person')
    print(f'{person=}')

    text = query.data
    await types.ChatActions.typing()


    buttons = (types.InlineKeyboardButton(text, callback_data=data) for text, data in text_and_data)
    inline_kb = types.InlineKeyboardMarkup()
    # for button in buttons:
    #     inline_kb.add(*button)
    inline_kb.add(*buttons)
    inline_kb.add(cancel_inline_button)

    await bot.send_message(
        chat_id=query.message.chat.id,
        text=f'Что именно вы хотите изменить?',
        reply_markup=inline_kb)

    await OrderEditUser.step_3.set()  # Устанавливаем состояние step_3
    # высылает текст юзеру
    # await bot.send_message(query.message.chat.id, f'Вы нажали {text}')


@dp.callback_query_handler(state=OrderEditUser.step_3)
async def edit_person_step_3(query: types.CallbackQuery, state: FSMContext):
    await types.ChatActions.typing()
    db = DB()
    # tg_account = db.get_tg_account(tg_id=query.from_user.id)
    # cod_user = db.get_person_by_tg_account(tg_account=tg_account)
    #
    # # callback_data = query.data

    # if data == 'отмена':
    #     await paused_and_canceled(query, state)
    # elif data == 'name_or_nickname':
    #
    for text, data in text_and_data:
        if data == query.data:

            if query.data == 'platform_name':
                inline_kb_platform = types.InlineKeyboardMarkup(row_width=2)
                platforms = db.get_all_platforms()
                for platform in platforms:
                    print(platform)
                    inline_platform_button = types.InlineKeyboardButton(text=platform.name, callback_data=platform.id)
                    inline_kb_platform.insert(inline_platform_button)
                inline_kb_platform.add(cancel_inline_button)
                await bot.send_message(
                    chat_id=query.message.chat.id,
                    text=f'Какую платформу указать как основную?',
                    reply_markup=inline_kb_platform
                )

            elif query.data == 'input_device_name':
                inline_kb_device = types.InlineKeyboardMarkup()
                devices = db.get_all_platforms()
                for device in devices:
                    inline_device_button = types.InlineKeyboardButton(text=device.name, callback_data=device)
                    inline_kb_device.add(inline_device_button)
                inline_kb_device.add(cancel_inline_button)
                await bot.send_message(
                    chat_id=query.message.chat.id,
                    text=f'Какое устройство ввода указать как основное?',
                    reply_markup=types.inline_kb_device
                )

            else:
                await bot.send_message(
                    chat_id=query.message.chat.id,
                    text=f'Введите {text}',
                    reply_markup=types.ReplyKeyboardRemove()

                )
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
