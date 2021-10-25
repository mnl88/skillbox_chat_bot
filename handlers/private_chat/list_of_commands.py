from aiogram import types
from aiogram.dispatcher.filters.builtin import Command, ChatTypeFilter, IDFilter
from loader import dp
from data.config import admins


@dp.message_handler(
    Command(commands=['commands', 'list', 'help']),
    ChatTypeFilter(types.ChatType.PRIVATE),
    IDFilter(user_id=admins)
)
async def list_of_commands(message: types.Message):
    """Список всех команд"""
    text = [
        'Список команд: ',
        '',
        '/about_cod_bot - о боте,',
        '/commands - список основных команд,',
        '/add_me - добавить свой профиль (работает только при отправке запроса в личные сообщения БОТу),',
        '/edit_me - редактировать свой профиль (работает только при отправке запроса в личные сообщения БОТу),',
        '/stat - показывает информацию о КД всех упомянутых в сообщении людей (при их отсутствии показывает Ваш КД),',
        '/stat_update - обновить информацию о своём КД (работает только при отправке запроса в личные сообщения БОТу).',
        '/show_full_profile_info - показать ПОЛНУЮ инфу о профиле (только при отправке запроса в личные сооб-ия БОТу).',
        '',
        'Список команд для администраторов:',
        '/set_commands - установить команды вместо BotFather,',
        '/clear_commands - удалить команды вместо BotFather,',
        '/chat_info - вывести ID чата,',
        '/stats_update_all - обновляет статистику по КД всем зарегистрированным пользователей.\n',
        '/add_all_psn_to_friends - добавить всех в друзья по psn,',
        '/stats_all - показать информацию о всех пользователях и их КД'
    ]
    joined_text = '\n'.join(text)
    await message.answer(text=joined_text, reply=False)
