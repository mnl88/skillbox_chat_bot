import asyncio
import json
import logging
import os
import time

from dotenv import load_dotenv
from vkbottle.api import API

load_dotenv()

# bot = Bot(token=bot_token)
api = API(os.getenv("api_token"))
# group_id = 116868448

# bot = Bot(os.getenv("bot_token"))

logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')

logger = logging.getLogger(__name__)


async def get_all_comment(group_id: int):
    good_data = []
    topics = await api.board.get_topics(group_id=group_id)
    for topic in topics.items:
        await asyncio.sleep(0.5)
        comments = await api.board.get_comments(group_id=group_id, topic_id=topic.id)
        print('.', end='')
        comment_list = []
        for comment in comments.items:
            await asyncio.sleep(0.5)
            likes = await api.likes.get_list(
                type='topic_comment',
                owner_id=-group_id,
                item_id=comment.id,
                extended=True
            )
            like_list = []
            for like in likes.items:
                like_list.append({
                    'id': like.id,
                    'first_name': like.first_name,
                    'last_name': like.last_name,
                    'url': f'https://vk.com/id{like.id}',
                })

            comment_inst = {
                'id': comment.id,
                'from_id': comment.from_id,
                'date': comment.date,
                'text': comment.text
            }

            # if like_list:
            #     comment_inst.update({'likes': like_list})
            # comment_inst['likes'] = like_list

            if len(like_list) > 0:
                comment_inst['likes'] = like_list

            comment_list.append(comment_inst)

        good_data.append({
            'id': topic.id,
            'title': topic.title,
            'updated': topic.updated,
            'created': topic.created,
            'comments': comment_list})

    user_ids = []
    for topics in good_data:
        for comment in topics['comments']:
            if str(comment['from_id']) not in user_ids:
                user_ids.append(str(comment['from_id']))

    await asyncio.sleep(0.5)
    users = await api.users.get(user_ids=user_ids)

    user_list = []
    for user in users:
        user_list.append({
            'id': user.id,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'url': f'https://vk.com/id{user.id}'
        })

    for topics in good_data:
        for comment in topics['comments']:
            for user in user_list:
                if comment['from_id'] == user['id']:
                    comment['from_whom'] = user


    with open('good_data.json', 'w') as fp:
        json.dump(good_data, fp)

    return good_data

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
    all_comments = await get_all_comment(group_id=group_id)
    user_comments = []
    for topic in all_comments:
        for comment in topic['comments']:
            if comment['from_id'] == user_vk_id:
                user_comments.append({
                    'topic_id': topic['id'],
                    'topic_title': topic['title'],
                    'topic_updated': topic['updated'],
                    'topic_created': topic['created'],
                    'comment': comment,
                })
    return user_comments


async def main_async():
    # await get_all_comment(group_id=group_id)
    a = await get_comments_by_user_id(user_vk_id=2680992)
    print(a)
    await api.http.session.close()


if __name__ == '__main__':
    start_time = time.time()
    loop = asyncio.new_event_loop()
    loop.run_until_complete(main_async())
    loop.run_until_complete(asyncio.sleep(1))
    logger.info(f"Execution time: {time.time() - start_time} seconds")
    # bot.run_forever()

# from vkwave.bots import
# import requests
# import time
#
# from auth_data import access_token
#
# client_id = 7969360
# count = 5
# domain = 'spbbadm'
#
#
# def get_token(client_id):
#     scope = [
#         'friends',
#         'wall',
#         'video',
#         'offline'
#     ]
#     scope_str = ','.join(scope)
#     access_token_url = f"https://oauth.vk.com/authorize?client_id={client_id}" \
#                        f"&display=page&redirect_uri=https://oauth.vk.com/blank.html&scope={scope_str}" \
#                        f"&response_type=token&v=5.5"
#     print(access_token_url)
#     return access_token_url
#
#
# def make_url(method, params_dict):
#     params_str = []
#
#     for key, value in params_dict.items():
#         param_str = str(key) + '=' + str(value)
#         params_str.append(param_str)
#
#     params = '&'.join(params_str)
#
#     url = f'https://api.vk.com/method/{method}?{params}'
#     return url
#
#
# def get_topics_id():
#
#     params_dict = {
#         'group_id': 116868448,
#         'access_token': access_token,
#         'v': '5.81'
#     }
#     url = make_url('board.getTopics', params_dict)
#     resp = requests.get(url)
#     # print(resp.text)
#     src = resp.json()
#     items = src['response']['items']
#
#     messages_id = []
#     for item in items[3:4]:
#         print(item)
#         messages_id.append(item['id'])
#     print(messages_id)
#     print()
#     return messages_id
# #
#
# def get_wall_posts():
#     params_dict = {
#         'domain': domain,
#         'count': count,
#         'access_token': access_token,
#         'v': '5.131'
#     }
#     url = make_url('wall.get', params_dict)
#     # print(url)
#     resp = requests.get(url)
#     src = resp.json()
#     # print(src)
#     posts = src['response']['items']
#     print(len(posts))
#     # for post in posts:
#     #     print(post)
# #
#
# def get_messages(topic_id):
#
#     params_dict = {
#         'group_id': 116868448,
#         'topic_id': topic_id,
#         'need_likes': 1,
#         'access_token': access_token,
#         'v': '5.81'
#     }
#     url = make_url('board.getComments', params_dict)
#     resp = requests.get(url)
#     print(resp.text)
#     # src = resp.json()
#     # items = src['response']['items']
#     #
#     # messages_id = []
#     # for item in items:
#     #     messages_id.append(item['id'])
#     # print(messages_id)
#     # return messages_id


# def main():
#     topics_id = get_topics_id()
#     for topic in topics_id:
#         messages = get_messages(topic)
#         time.sleep(1)
#         print()
#
#     likes.getList
#
#
# if __name__ == '__main__':
#     main()
