from aiogram import types
from loader import dp, bot
from data.config import admins
from utils.ps_vk_group_parser.vk_group_parser import get_comments_by_user_id
from utils.db_api.db_instanse import Badminton_player, B4U_Account, TG_Account
from utils.db_api.db_instanse import start_db
import asyncio

@dp.message_handler(user_id=admins, commands="gravity_of_sport")
@dp.message_handler(user_id=admins, commands="gravity_of_sport", state='*')
async def set_commands_to_bf(message: types.Message):
    await types.ChatActions.typing()
    msg = await message.answer('Ваш запрос обрабатывается, подождите...')
    try:
        db = await start_db()
        player = await Badminton_player(tg_id=message.from_user.id).read_by_tg_id(db)
        player: Badminton_player
        group_id = 116868448
        comments = await get_comments_by_user_id(group_id=group_id, user_vk_id=player.vk_id)
        text = ['Мои записи:']
        print(comments)

        for comment in comments:
            topic_title = comment['topic_title']
            comment_text = comment['comment']['text']
            url = 'https://vk.com/topic-'+str(group_id)+'_'+str(comment['topic_id'])
            text.append(
                f'<a href="{url}">"{topic_title}"</a>\n({comment_text})\n'
                # f'\n({comment_text}\n'
            )
        await msg.delete()
        await message.answer(
            text='\n'.join(text),
            parse_mode=types.ParseMode.HTML,
            disable_web_page_preview=True
        )
    except:
        msg2 = await message.answer('что-то пошло не так, возможно, у вас не правильно указан ВК ID')
        await asyncio.sleep(20)
        await message.delete()
        await msg2.delete()
    'https://vk.com/topic-116868448_48219608'
