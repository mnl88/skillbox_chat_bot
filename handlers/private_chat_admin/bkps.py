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
from utils.ps_vk_group_parser.vk_group_parser import get_comments_by_user_id
from utils.ps_vk_group_parser.vk_group_parser import get_topics_and_calculate_messages_and_likes


import re

logger = logging.getLogger(__name__)

stogova_id = 525157051
varlamova_id = 818059455
sviridenko_id = 1057050334  # Свириденко
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


@dp.message_handler(user_id=[*admins, stogova_id], commands="ps", state=(['*', None]))
async def show_info_about_record(message: types.Message, state: FSMContext):
    await types.ChatActions.typing()
    msg = await message.answer('Ваш запрос обрабатывается, подождите...')
    try:
        # db = await start_db()
        # player = await Badminton_player(tg_id=message.from_user.id).read_by_tg_id(db)
        # player: Badminton_player
        group_id = 116868448
        board = await get_topics_and_calculate_messages_and_likes(liker_users_ids=[14496783, ], group_id=group_id)

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
                await message.answer(
                    text='\n'.join(part_of_text_without_details),
                    parse_mode=types.ParseMode.HTML,
                    disable_web_page_preview=True,
                    reply_markup=inline_kb_hide_details
                )
            else:
                await message.answer(
                    text=f'На {datetime_now_str} записей на тренировки с трениром Стоговая Анастасия не найдено'
                    # parse_mode=types.ParseMode.HTML,
                    # disable_web_page_preview=True,
                    # reply_markup=inline_kb_hide_details
                )

    except Exception as e:
        logger.error(e)
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

