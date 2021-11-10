import asyncio
import datetime
import json
import logging
import os
import re
import time
from urllib.parse import urlparse

import httpx
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')

logger = logging.getLogger(__name__)


async def parse_board_with_all_topics_comments_and_likes(group_id: int):
    URL = urlparse('https://api.vk.com/')

    async def smart_sleep_for_vk_api():
        await asyncio.sleep(0.4)
        # print(time.time()-start_time, 'seconds')

    def cut_list_by_size(lst: list, size=25) -> list:
        """

        :param lst:
        :param size:
        :return:
        """

        list_of_lists = []
        sub_list = []
        for i, item in enumerate(lst):
            sub_list.append(item)
            if (i + 1) % size == 0:
                list_of_lists.append(sub_list)
                sub_list = []
            if i + 1 == len(lst):
                list_of_lists.append(sub_list)
        return list_of_lists

    async def get_topics(group_id: int) -> dict:
        async with httpx.AsyncClient() as client:
            params = {
                'group_id': group_id,
                'count': 100,
                'extended': 1,
                'preview': 1,
                'preview_length': 0,
                'v': 5.81,
                'access_token': os.getenv('api_token')
            }
            await smart_sleep_for_vk_api()
            response = await client.get(url=URL.geturl() + f'/method/board.getTopics', params=params)
            if response.status_code == 200:
                r_json = response.json()
                if 'error' in r_json:
                    logger.error(r_json)
                if 'response' in r_json:
                    if r_json['response']['count'] == len(r_json['response']['items']):
                        r_json['response'].update({'group_id': group_id})
                        return r_json['response']
                    else:
                        logger.error('topics count is not equal to items!!')

    async def add_comments_to_topics(topics: dict) -> dict:

        # ограничение vk api, нельзя получить более 100 сообщений из одной темы за раз!!!
        max_count_of_comments = 100

        blocks = cut_list_by_size(topics['items'])
        list_of_comments = []
        for block in blocks:
            vk_script = 'return ['
            for topic in block:
                vk_script += 'API.board.getComments(' \
                             '{"group_id": ' + str(topics['group_id']) \
                             + ', "topic_id": ' + str(topic['id']) \
                             + ', "count": ' + str(max_count_of_comments) \
                             + ', "need_likes": 1}),'
            vk_script += '];'
            # print(vk_script)
            async with httpx.AsyncClient() as client:
                params = {
                    'code': vk_script,
                    'v': 5.81,
                    'access_token': os.getenv('api_token')
                }
                await smart_sleep_for_vk_api()
                response = await client.get(url=URL.geturl() + f'/method/execute', params=params)
                if response.status_code == 200:
                    r_json = response.json()
                    if 'error' in r_json:
                        logger.error(r_json)
                    if 'response' in r_json:
                        # print(len(r_json['response']))
                        for item in r_json['response']:
                            if item['count'] == max_count_of_comments:
                                logger.error(f'ограничение vk api, нельзя получить более 100 сообщений из одной темы за раз!!!')
                            # print(item['count'], end='\n'*3)
                            list_of_comments.append(item)

        for i, topic in enumerate(topics['items']):
            for j, comments in enumerate(list_of_comments):
                if i == j:
                    # print(comments, end='\n\n')
                    topic.update({'comments': comments})

        return topics

        # for topic in list_of_comments:
        #     all_results.append(topic)
        #
        # for topic in topics['items']:
        #     for result in all_results:
        #         if topic['id'] == result['topic_id']:
        #             print('!')
        #             # topic: dict
        #             # topic.update({'comments': result})

        # return topics

        # for r in list_of_comments:
        #     print(r, end='\n\n\n')

        # print(list_of_comments)
        # all_results.append({
        #     'topic_id': topic_id,
        #     'comments': list_of_comments[]
        # })

        # for r in all_results:
        #     print(r, end='\n\n\n')
        # print(len(all_results))

        # print(all_results)
        # for x in all_results:
        #     print(x)
        #     print()
        #         for r in r_json['response']:
        #             print(r)
        #             print()
        # #     #     if r_json['response']['count'] == len(r_json['response']['items']):
        # #     #         r_json['response'].update({'group_id': group_id})
        # #     #         return r_json['response']
        #     #     else:
        #     #         logger.error('topics count is not equal to items!!')
        # print(vk_script)
        # params = {
        #     'group_id': topics['group_id'],
        #     'topic_id': topics['items'][0]['id'],
        #     'need_likes': 1,
        #     'count': 100,
        #     'extended': 1,
        #     'v': 5.81,
        #     'access_token': os.getenv('api_token')
        # }
        #
        # group_id = topics['group_id']
        # topic_id = topics['items'][0]['id']
        #
        # vk_script = 'return API.board.getComments({"group_id": ' + str(group_id) + ', "topic_id": ' + str(topic_id) + '});'
        # print(vk_script)
        #
        # params_2 = {
        #     'code': vk_script,
        #     'v': 5.81,
        #     'access_token': os.getenv('api_token')
        # }
        #
        # response = await client.get(url=URL.geturl() + f'/method/execute', params=params_2)
        # if response.status_code == 200:
        #     r_json = response.json()
        #     print(r_json)
        #     if 'error' in r_json:
        #         logger.error(r_json)
        #     if 'response' in r_json:
        #         print(len(r_json['response']))
        #         for r in r_json['response']:
        #             print(r)
        #             print()
        # #     #     if r_json['response']['count'] == len(r_json['response']['items']):
        # #     #         r_json['response'].update({'group_id': group_id})
        # #     #         return r_json['response']
        #     #     else:
        #     #         logger.error('topics count is not equal to items!!')

    async def add_likes_to_comments(topics_with_comments: dict):
        list_of_liked_comments_ids = []
        for topic in topics_with_comments['items']:
            if topic['comments']['count'] > 0:
                for comment in topic['comments']['items']:
                    if comment['likes']['count'] != 0:
                        list_of_liked_comments_ids.append(comment['id'])
        blocks = cut_list_by_size(list_of_liked_comments_ids)
        list_of_likes = []
        for block in blocks:
            await smart_sleep_for_vk_api()
            vk_script = 'return ['
            for likes_id in block:
                vk_script += 'API.likes.getList({"type": "topic_comment", "owner_id": -' + str(
                    topics['group_id']) + ', "item_id": ' + str(likes_id) + ', "extended": 1, "count": 1000}),'
            vk_script += '];'
            # print(vk_script)
            async with httpx.AsyncClient() as client:
                params = {
                    'code': vk_script,
                    'v': 5.81,
                    'access_token': os.getenv('api_token')
                }
                await asyncio.sleep(0.4)
                response = await client.get(url=URL.geturl() + f'/method/execute', params=params)
                if response.status_code == 200:
                    r_json = response.json()
                    if 'error' in r_json:
                        logger.error(r_json)
                    if 'response' in r_json:
                        for item in r_json['response']:
                            list_of_likes.append(item)
        list_of_comment_ids_and_likes = []
        for i, likes in enumerate(list_of_likes):
            for j, comment_id in enumerate(list_of_liked_comments_ids):
                if i == j:
                    list_of_comment_ids_and_likes.append({
                        'comment_id': comment_id,
                        'likes': likes,
                    })

        for topic in topics_with_comments['items']:
            for comment in topic['comments']['items']:
                for item in list_of_comment_ids_and_likes:
                    if comment['id'] == item['comment_id']:
                        comment['likes'].update({'items': item['likes']['items']})

        return topics_with_comments

    async def correct_users_info(board):

        users_ids = []
        users_list = []

        for topic in board['items']:
            for comment in topic['comments']['items']:
                if comment['from_id'] not in users_ids and comment['from_id'] > 0:
                    users_ids.append(comment['from_id'])
                if comment["likes"]['count'] !=0:
                    for user_who_liked in comment["likes"]['items']:
                        if user_who_liked['id'] not in users_ids:
                            if comment['from_id'] > 0:
                                users_ids.append(comment['from_id'])

        # print(users_ids)
        users_ids_str = ''
        for user_id in users_ids:
            users_ids_str += f'{user_id}, '
        # print(users_ids_str)

        async with httpx.AsyncClient() as client:
            params = {
                'user_ids': users_ids_str,
                'fields': 'domain',
                # 'fields': 'photo_id, verified, sex, bdate, city, country, home_town, has_photo, photo_50, photo_100, '
                #           'photo_200_orig, photo_200, photo_400_orig, photo_max, photo_max_orig, online, domain, '
                #           'has_mobile, contacts, site, education, universities, schools, status, last_seen, '
                #           'followers_count, common_count, occupation, nickname, relatives, relation, personal, '
                #           'connections, exports, activities, interests, music, movies, tv, books, games, about, '
                #           'quotes, can_post, can_see_all_posts, can_see_audio, can_write_private_message, '
                #           'can_send_friend_request, is_favorite, is_hidden_from_feed, timezone, screen_name, '
                #           'maiden_name, crop_photo, is_friend, friend_status, career, blacklisted, '
                #           'blacklisted_by_me, can_be_invited_group',
                'v': 5.81,
                'access_token': os.getenv('api_token')
            }
            await smart_sleep_for_vk_api()
            response = await client.get(url=URL.geturl() + f'/method/users.get', params=params)
            if response.status_code == 200:
                r_json = response.json()
                if 'error' in r_json:
                    logger.error(r_json)
                if 'response' in r_json:
                    # if r_json['response']['count'] == len(r_json['response']['items']):
                    users_list = r_json['response']
                        # r_json['response'].update({'group_id': group_id})
                        # return r_json['response']
                    # else:
                    #     logger.error('topics count is not equal to items!!')


                # if comment['from_id'] >= 0:  # отсеиваем комментарии от лица группы
                #     comment = {
                #         'from_id': comment['from_id'],
                #
                #     }
                #     print(comment)

        for topic in board['items']:
            for comment in topic['comments']['items']:
                for user in users_list:
                    if user['id'] == comment['from_id']:
                        comment.update({'author': user})
                # if comment['from_id'] not in users_ids and comment['from_id'] > 0:
                #     users_ids.append(comment['from_id'])
                # if comment["likes"]['count'] !=0:
                #     for user_who_liked in comment["likes"]['items']:
                #         if user_who_liked['id'] not in users_ids:
                #             if comment['from_id'] > 0:
                #                 users_ids.append(comment['from_id'])

        return board


        #         if comment['from_id'] == user_vk_id:
        #             user_comments.append({
        #                 'topic_id': topic['id'],
        #                 'topic_title': topic['title'],
        #                 'topic_updated': topic['updated'],
        #                 'topic_created': topic['created'],
        #                 'comment': comment,
        #             })
        # # print(user_comments)
        # return user_comments

    async def sort_board_by_supposed_datatime(board):
        year = datetime.date.today().year
        for topic in board['items']:
            supposed_datatime = ''
            try:
                pattern = '\d{1,2}\.\d{1,2}'
                date_and_month = re.match(pattern, topic['title'])
                if date_and_month:
                    day = int(date_and_month[0].split('.')[0])
                    month = int(date_and_month[0].split('.')[1])
                    # supposed_datatime = datetime.datetime(year, month, day)
                    supposed_datatime = datetime.datetime(year, month, day).strftime("%Y%m%d")

            except Exception as e:
                logger.info('Не удалось распознать дату. Ошибка:', e)
            # print(supposed_datatime)
            topic.update({'supposed_datatime': supposed_datatime})

        # сортируем список словарей по ключу словаря 'supposed_datatime'
        sorted_topics = sorted(board['items'], key=lambda k: k['supposed_datatime'])
        # for topic in sorted_topics:
        #     print(topic['supposed_datatime'])

        board['items'] = sorted_topics

        return board

    # получаем список всех обсуждений
    topics = await get_topics(group_id=group_id)

    # получаем список всех обсуждений и комментариев
    topics_with_comments = await add_comments_to_topics(topics=topics)

    # with open('good_data.json', 'w') as fp:
    #     json.dump(topics_with_comments, fp)

    # получаем список всех обсуждений, комментариев и лайков
    topics_with_comments_and_likes = await add_likes_to_comments(topics_with_comments=topics_with_comments)

    # with open('good_data.json', 'w') as fp:
    #     json.dump(topics_with_comments_and_likes, fp)

    topics = await correct_users_info(topics_with_comments_and_likes)

    topics = await sort_board_by_supposed_datatime(topics)

    # with open('good_data.json', 'w') as fp:
    #     json.dump(topics, fp)

    return topics

    # topic_ids = get_topic_ids(topics)  # получаем ID каждого обсуждения
    # print(topic_ids)
    # board = await get_board(group_id, topic_ids)  # получаем список тем группы
    # for topic in board:
    #     print(topic)
    # comment_ids_with_likes = get_comment_ids_with_likes(board)  # получаем список id сообщений, где есть лайки
    # likes = await get_likes(group_id, comment_ids_with_likes)
    # topics = append_likes_to_board(board, likes)
    # return {'group_id': group_id, 'topics': topics}

    # for block in list_of_comments:
    #     # await asyncio.sleep(1.1)
    #     for comment in block:
    #         for key, value in comment.items():
    #             print(key, value)
    #             print()
    #         print()
    #     print()

    # comments_with_likes = []
    # for comment_block in comment_blocks:
    #     print(comment_block)
    # await asyncio.sleep(1.1)
    # for comment in comment_block:
    # comment_id = comment['comment'].items[0].id
    # likes = await api.likes.get_list(
    #                 type='topic_comment',
    #                 owner_id=-group_id,
    #                 item_id=comment['id'],
    #                 extended=True
    #             )
    # print(likes)

    # like_list = []

    # for like in likes.items:
    #     like_list.append({
    #         'id': like.id,
    #         'first_name': like.first_name,
    #         'last_name': like.last_name,
    #         'url': f'https://vk.com/id{like.id}',
    #     })

    #
    #         await asyncio.sleep(0.5)
    #         likes = await api.likes.get_list(
    #             type='topic_comment',
    #             owner_id=-group_id,
    #             item_id=comment.id,
    #             extended=True
    #         )
    #         like_list = []
    #         for like in likes.items:
    #             like_list.append({
    #                 'id': like.id,
    #                 'first_name': like.first_name,
    #                 'last_name': like.last_name,
    #                 'url': f'https://vk.com/id{like.id}',
    #             })
    #
    #         comment_inst = {
    #             'id': comment.id,
    #             'from_id': comment.from_id,
    #             'date': comment.date,
    #             'text': comment.text
    #         }
    #
    #         # if like_list:
    #         #     comment_inst.update({'likes': like_list})
    #         # comment_inst['likes'] = like_list
    #
    #         if len(like_list) > 0:
    #             comment_inst['likes'] = like_list
    #
    #         comment_list.append(comment_inst)
    #
    #     good_data.append({
    #         'id': topic.id,
    #         'title': topic.title,
    #         'updated': topic.updated,
    #         'created': topic.created,
    #         'comments': comment_list})
    #
    # user_ids = []
    # for topics in good_data:
    #     for comment in topics['comments']:
    #         if str(comment['from_id']) not in user_ids:
    #             user_ids.append(str(comment['from_id']))
    #
    # await asyncio.sleep(0.5)
    # users = await api.users.get(user_ids=user_ids)
    #
    # user_list = []
    # for user in users:
    #     user_list.append({
    #         'id': user.id,
    #         'first_name': user.first_name,
    #         'last_name': user.last_name,
    #         'url': f'https://vk.com/id{user.id}'
    #     })
    #
    # for topics in good_data:
    #     for comment in topics['comments']:
    #         for user in user_list:
    #             if comment['from_id'] == user['id']:
    #                 comment['from_whom'] = user
    #
    #
    # with open('good_data.json', 'w') as fp:
    #     json.dump(good_data, fp)
    #
    # return good_data

    # print(json.dumps(all_comments, indent=4, sort_keys=True))

    # print(topics)
    # for topic in topics.items:
    # #     pass
    #     # print(topic.dict())
    #     # # print(topic.title)
    #     await asyncio.sleep(0.5)
    #     # # Получаю все сообщения в обсуждении
    #     comments = await api.board.get_comments(
    #         group_id=group_id,
    #         topic_id=topic.id,
    #     )
    #     with open('comments.json', 'w') as fp:
    #         json.dump(comments.dict(), fp)
    # text = []
    # for item in comments.items:
    #     await asyncio.sleep(0.5)

    #     user = await api.users.get(user_ids=[str(item.from_id)])
    #     text.append(
    #         f'{item.text},\nавтор: {user[0].first_name} {user[0].last_name}\n(https://vk.com/id{user[0].id})')
    #     await asyncio.sleep(0.5)
    #
    # return text


async def get_comments_by_user_id(group_id=116868448, user_vk_id=2680992):
    """
    Возвращает список записей заданного пользователя ВК

    :param group_id: ID группы ВК (int, без минуса)
    :param user_vk_id: ID пользователя ВК (int)
    :return:
    """
    board = await parse_board_with_all_topics_comments_and_likes(group_id)
    user_comments = []
    for topic in board['items']:
        for comment in topic['comments']['items']:
            if comment['from_id'] == user_vk_id:
                user_comments.append({
                    'topic_id': topic['id'],
                    'topic_title': topic['title'],
                    'topic_updated': topic['updated'],
                    'topic_created': topic['created'],
                    'comment': comment,
                })
    # with open('yes.json', 'w') as fp:
    #     json.dump(user_comments, fp)
    # print(user_comments)
    return user_comments


async def get_topics_and_calculate_messages_and_likes(liker_users_ids: list, group_id=116868448):
    """
    Возвращает список обсуждений, сообщений и учёт лайков

    :param group_id: ID группы ВК (int, без минуса)
    :param user_vk_id: ID пользователя ВК (int)
    :param liker_users_ids: список ID пользователей ВК, чьи лайки учитывать (int)

    :return: список обсуждений, сообщений и учёт лайков (list)
    """
    board = await parse_board_with_all_topics_comments_and_likes(group_id)
    topics_list = []
    for topic in board['items']:
        messages = []
        for comment in topic['comments']['items']:
            if 'author' in comment:  # отсеиваем комментарии от лица группы
                message = {
                    'text': comment['text'],
                    'author_domain': comment['author']['domain'],
                    'author_name': comment['author']['first_name'] + ' ' + comment['author']['last_name'],
                    'is_training_payed': False
                }
                if 'items' in comment['likes']:
                    for like in comment['likes']['items']:
                        if like['id'] in liker_users_ids:
                            message.update({'is_training_payed': True})
                if message:
                    messages.append(message)
        if messages:

            topic_dict = {
                'title': topic['title'],
                'id': topic['id'],
                'messages': messages
            }

            topics_list.append(topic_dict)



    with open('yes.json', 'w') as fp:
        json.dump(topics_list, fp)

    return topics_list


async def main_async():
    board = await parse_board_with_all_topics_comments_and_likes(group_id=116868448)

    # await get_topics_and_calculate_messages_and_likes(liker_users_ids=[14496783, ], group_id=116868448)
    # await get_comments_by_user_id(group_id=116868448, user_vk_id=2680992)


if __name__ == '__main__':
    start_time = time.time()
    loop = asyncio.new_event_loop()
    loop.run_until_complete(main_async())
    loop.run_until_complete(asyncio.sleep(1))
    logger.info(f"Execution time: {time.time() - start_time} seconds")
    # bot.run_forever()
