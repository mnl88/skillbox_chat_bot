import json
import asyncio
import logging
import datetime

from aiogram import types
from aiogram.dispatcher import FSMContext

from data.config import admins
from keyboards.inline import inline_kb_hide_details, inline_kb_show_details
from loader import dp, bot
from states.bot_states import StogovaScheduleState
from utils.db_api.db_instanse import Badminton_player
from utils.db_api.db_instanse import start_db
from utils.ps_vk_group_parser.vk_group_parser import get_comments_by_user_id, \
    get_comments_in_several_topics_by_vk_user_id
from utils.ps_vk_group_parser.vk_group_parser import get_topics_and_calculate_messages_and_likes
import emoji

import re

logger = logging.getLogger(__name__)

stogova_id = 525157051
varlamova_id = 818059455
sviridenko_id = 1057050334  # Свириденко
natasha_vk_id = 14496783
ps_staff_ids = [stogova_id, varlamova_id, sviridenko_id]

from emoji import emojize


@dp.message_handler(user_id=admins, commands="gravity_of_sport")
@dp.message_handler(user_id=admins, commands="gravity_of_sport", state='*')
async def set_commands_to_bf(message: types.Message):
    await types.ChatActions.typing()
    msg = await message.answer('Ваш запрос обрабатывается, подождите...')

    # TODO: разобраться с caption_entities, чтобы он выводил инфу по упомянутым людям

    try:
        db = await start_db()
        player = await Badminton_player(tg_id=message.from_user.id).read_by_tg_id(db)
        player: Badminton_player
        group_id = 116868448
        comments = await get_comments_by_user_id(group_id=group_id, user_vk_id=player.vk_id)
        if comments:
            text = ['Мои записи:']

            for comment in comments:
                topic_title = comment['topic_title']
                comment_text = comment['comment']['text']
                url = 'https://vk.com/topic-' + str(group_id) + '_' + str(comment['topic_id'])
                text.append(
                    f'<a href="{url}">"{topic_title}"</a>'
                    f'\n({comment_text}\n'
                )
            await message.answer(
                text='\n'.join(text),
                parse_mode=types.ParseMode.HTML,
                disable_web_page_preview=True
            )
    except Exception as e:
        print(e)
        msg2 = await message.answer('что-то пошло не так, возможно, у вас не правильно указан ВК ID')
        await asyncio.sleep(20)
        await message.delete()
        await msg2.delete()
    finally:
        await msg.delete()


@dp.message_handler(user_id=[*admins, *ps_staff_ids], commands="ps_all", state=(['*', None]))
async def show_info_about_record(message: types.Message, state: FSMContext):
    await types.ChatActions.typing()
    msg = await message.answer('Ваш запрос обрабатывается, подождите...')
    try:
        # db = await start_db()
        # player = await Badminton_player(tg_id=message.from_user.id).read_by_tg_id(db)
        # player: Badminton_player
        group_id = 116868448
        board = await get_topics_and_calculate_messages_and_likes(liker_users_ids=[14496783, ], group_id=group_id)
        if board:

            datetime_now_str = datetime.datetime.now().strftime("%X")
            # datetime_now_str = datetime.datetime.now().strftime("%d.%m.%Y %X")
            # print(datetime_now_str)
            part_of_text_with_details = ['Список записей на ' + datetime_now_str + ':']
            part_of_text_without_details = ['Список записей на ' + datetime_now_str + ':']

            for topic in board:
                topic_title = topic['title']
                url = 'https://vk.com/topic-' + str(group_id) + '_' + str(topic['id'])
                part_of_text_with_details.append(f'<a href="{url}">{topic_title}</a>')
                part_of_text_without_details.append(f'<a href="{url}">{topic_title}</a>')

                msg_count = 0
                payed_count = 0
                for comment in topic['messages']:
                    if comment['is_training_payed'] is True:
                        payed_count += 1
                    msg_count += 1

                part_of_text_with_details.append(f'<b>записей в теме: {msg_count}</b>,')
                part_of_text_with_details.append(f'<b>из них с отметкой об оплате: {payed_count}</b>\n')

                part_of_text_without_details.append(f'<b>записей в теме: {msg_count}</b>,')
                part_of_text_without_details.append(f'<b>из них с отметкой об оплате: {payed_count}</b>\n')

                for comment in topic['messages']:
                    url = "https://vk.com/" + comment['author_domain']
                    author = comment['author_name']
                    comment_text = comment['text']
                    pay = emojize(':cross_mark:') + ' не оплачено'
                    if comment['is_training_payed']:
                        pay = emojize(':check_mark:') + ' оплачено'

                    part_of_text_with_details.append(
                        f'<b>{comment_text}</b>, \nавтор: <a href="{url}">{author}</a>\n({pay})\n')
                    # f'\n({comment_text}\n'
                part_of_text_with_details.append('\n')

            async with state.proxy() as data:
                data['text_with_details'] = '\n'.join(part_of_text_with_details)
                data['text_without_details'] = '\n'.join(part_of_text_without_details)
                data['message_id'] = message.message_id

            await message.answer(
                text='\n'.join(part_of_text_without_details),
                parse_mode=types.ParseMode.HTML,
                disable_web_page_preview=True,
                reply_markup=inline_kb_hide_details
            )

    except Exception as e:
        logger.error(e)
        msg2 = await message.answer('что-то пошло не так, возможно, у вас не правильно указан ВК ID')
        await asyncio.sleep(20)
        await message.delete()
        await msg2.delete()
    finally:
        await msg.delete()


@dp.message_handler(user_id=[*admins, stogova_id], commands=['ps', 'nastya', 'stogova'], state=(['*', None]))
async def show_info_about_record(message: types.Message, state: FSMContext):
    await types.ChatActions.typing()
    msg = await message.answer('Ваш запрос обрабатывается, подождите...')
    try:
        # player: Badminton_player
        group_id = 116868448
        board = await get_topics_and_calculate_messages_and_likes(liker_users_ids=[natasha_vk_id, ], group_id=group_id)

        is_records_exist = False

        if board:

            datetime_now_str = datetime.datetime.now().strftime("%X")
            # datetime_now_str = datetime.datetime.now().strftime("%d.%m.%Y %X")
            # print(datetime_now_str)
            part_of_text_with_details = ['Список записей на ' + datetime_now_str + ':']
            part_of_text_without_details = ['Список записей на ' + datetime_now_str + ':']

            for topic in board:
                if 'СТОГОВ' in topic['title'].upper():

                    is_records_exist = True
                    topic_title = topic['title']
                    url = 'https://vk.com/topic-' + str(group_id) + '_' + str(topic['id'])
                    part_of_text_with_details.append(f'<a href="{url}">{topic_title}</a>')
                    part_of_text_without_details.append(f'<a href="{url}">{topic_title}</a>')

                    msg_count = 0
                    payed_count = 0
                    for comment in topic['messages']:
                        if comment['is_training_payed'] is True:
                            payed_count += 1
                        msg_count += 1

                    part_of_text_with_details.append(f'<b>записей в теме: {msg_count}</b>,')
                    part_of_text_with_details.append(f'<b>из них с отметкой об оплате: {payed_count}</b>\n')

                    part_of_text_without_details.append(f'<b>записей в теме: {msg_count}</b>,')
                    part_of_text_without_details.append(f'<b>из них с отметкой об оплате: {payed_count}</b>\n')

                    for comment in topic['messages']:
                        url = "https://vk.com/" + comment['author_domain']
                        author = comment['author_name']
                        comment_text = comment['text']
                        pay = emojize(':cross_mark:') + ' не оплачено'
                        if comment['is_training_payed']:
                            pay = emojize(':check_mark:') + ' оплачено'

                        part_of_text_with_details.append(
                            f'<b>{comment_text}</b>, \nавтор: <a href="{url}">{author}</a>\n({pay})\n')
                    part_of_text_with_details.append('\n')

            async with state.proxy() as data:
                data['text_with_details'] = '\n'.join(part_of_text_with_details)
                data['text_without_details'] = '\n'.join(part_of_text_without_details)
                data['message_id'] = message.message_id

            if is_records_exist:
                await message.answer_sticker(sticker='CAACAgEAAxkBAAEMis9hi5BxR6L-Tx8S9kU1mQIYbf6KigACaQgAAr-MkASxL4G2gv6QQSIE')
                await message.answer(
                    text='\n'.join(part_of_text_without_details),
                    parse_mode=types.ParseMode.HTML,
                    disable_web_page_preview=True,
                    reply_markup=inline_kb_hide_details
                )
            else:
                await message.answer_sticker(
                    sticker='CAACAgIAAxkBAAEMirFhi4xnQ3PJAhJHsGeRQZkp_0_7EgACoAEAAooSqg4K2hVuYPTufiIE')
                await message.answer(
                    text=f'Настя, на {datetime_now_str} '
                         f'записи на тренировки с тобой в качестве основного тренера отсутствуют!'
                    # parse_mode=types.ParseMode.HTML,
                    # disable_web_page_preview=True,
                    # reply_markup=inline_kb_hide_details
                )

    except Exception as e:
        logger.error(f'Ошибка - {e}')
        msg2 = await message.answer('что-то пошло не так, возможно, у вас не правильно указан ВК ID')
        await asyncio.sleep(20)
        await message.delete()
        await msg2.delete()
    finally:
        await msg.delete()


@dp.callback_query_handler(text=["hide_details", "show_details"], state=(['*', None]))
async def ys_boss(call: types.CallbackQuery, state: FSMContext):

    state_data = await state.get_data()
    await bot.delete_message(chat_id=call.message.chat.id,
                             message_id=call.message.message_id)

    if call.data == 'show_details':
        text = state_data['text_with_details']
        keyboard = inline_kb_show_details
    else:
        text = state_data['text_without_details']
        keyboard = inline_kb_hide_details

    await call.message.answer(
        text,
        parse_mode=types.ParseMode.HTML,
        disable_web_page_preview=True,
        reply_markup=keyboard
    )


# при нажатии /me
@dp.message_handler(commands=['me'], state=['*', None])
# @dp.message_handler(commands="me", state='*')
async def command_me(message: types.Message, state: FSMContext):
    logger.info(f'Пользователь {message.from_user.full_name} (ID: {message.from_user.id}) нажал команду ME')
    await types.ChatActions.typing()
    msg = await message.answer('Ваш запрос обрабатывается, подождите...')
    vk_group_id_volley = 64612773  # ID группы Волейбол на Ваське
    vk_group_id_pritjazhenie = 116868448  # ID группы Притяжение
    vk_group_id_craft = 190120334  # ID группы Крафт
    vk_group_ids = [vk_group_id_volley, vk_group_id_pritjazhenie, vk_group_id_craft]

    try:
        db = await start_db()
        player = await Badminton_player(tg_id=message.from_user.id).read_by_tg_id(db)
        player: Badminton_player
        board = await get_comments_in_several_topics_by_vk_user_id(topic_ids=vk_group_ids, user_vk_id=player.vk_id)
        # with open('my_board.json', 'w') as fp:
        #     json.dump(board, fp)
        if board:
            text = [f'Список записей на {datetime.datetime.now().strftime("%X")}:']
            for group in board:
                group_url = 'https://vk.com/' + str(group['group']['screen_name'])
                group_title = group['group']['name'].upper()
                text.append(
                    f'<a href="{group_url}">{group_title}</a>'
                )
                for topic in group['topics']:
                    topic_url = 'https://vk.com/topic-' + str(group['group']['id']) + '_' + str(topic['topic_id'])
                    topic_title = topic['topic_title'].strip()[:50]
                    text.append(
                        f'<a href="{topic_url}">{topic_title}</a>'
                    )

                    for i, comment in enumerate(topic['comments']):
                        comment_text = comment['text']
                        text.append(
                            # f'<a href="{url}">"{topic_title}"</a>'
                            f'{i + 1}) {comment_text}'
                        )
                text.append('')
            full_text = '\n'.join(text)
            await message.answer(
                text=full_text,
                parse_mode=types.ParseMode.HTML,
                disable_web_page_preview=True
            )
    except Exception as e:
        print(e)
        # msg2 = await message.answer('что-то пошло не так, возможно, у вас не правильно указан ВК ID')
        # await asyncio.sleep(20)
        # await message.delete()
        # await msg2.delete()
    finally:
        await msg.delete()

