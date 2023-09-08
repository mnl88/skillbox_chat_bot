import asyncio
import errno
import json
import logging
import os
import time
from datetime import datetime
import shutil

from urllib.parse import urlparse
from bs4 import BeautifulSoup

import httpx

from dotenv import load_dotenv
from sqlalchemy import Table, Column, Integer, String, DateTime, MetaData, Float
from sqlalchemy import create_engine

# import pandas as pd
# from openpyxl import Workbook
# from openpyxl.styles import Font
# from openpyxl.utils.dataframe import dataframe_to_rows
# from openpyxl.styles import numbers
#
# from parser_uts import parse_uts
# from send_xlsx_to_email import send_price_email

# from utils.db_api.db_instanse import B4U_Account

logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')

logger = logging.getLogger(__name__)

URL = urlparse('http://badminton4u.ru/players')


def get_info(html):
    soup = BeautifulSoup(html, 'html.parser')
    stat = {'name': soup.find('div', class_='breadcrumbs').find('li', class_='active').text}
    trs = soup.find('div', class_="profile-info").find('table', class_="user-rating-table bordered-table").find_all(
        'tr')
    for tr in trs[1:]:
        tds = tr.find_all('td')
        category = None
        rating = None
        date_of_calc = None
        for i, td in enumerate(tds):
            match i:
                case 1:
                    category = td.text
                case 2:
                    rating = int(td.text)
                case 3:
                    date_of_calc = td.text
        stat[category] = {'rating': rating, 'date_of_calc': date_of_calc}
    # print(stat)
    b4u_dict = {'username': stat['name']}
    if '[s] Одиночки' in stat:
        b4u_dict.update({
            'single_rating': stat['[s] Одиночки']['rating'],
            'single_rating_date_of_calc': stat['[s] Одиночки']['date_of_calc'],
        })
    if '[d] Пары' in stat:
        b4u_dict.update({
            'double_rating': stat['[d] Пары']['rating'],
            'double_rating_date_of_calc': stat['[d] Пары']['date_of_calc'],
        })
    return b4u_dict


async def get_html(player_id: int) -> str:
    async with httpx.AsyncClient() as client:
        url = URL.geturl()+'/'+str(player_id)
        response = await client.get(url=url)
        if response.status_code == 200:
            html = response.text
            return html


async def stat_parser(player_id: int) -> dict:
    html = await get_html(player_id=player_id)
    if html:
        info = await asyncio.to_thread(get_info, html)
        info.update({'id': player_id})
        return info


async def main_async():
    # stat = await stat_parser(player_id=17284)
    # print(stat)
    # получаем текущую дату
    # current_date_str = datetime.strftime(datetime.now(), "%Y%m%d")

    b4u_players = [
        17264,
        17284,
        17287,
        17392
    ]

    tasks = []
    for player in b4u_players:
        tasks.append(stat_parser(player_id=player))

    stats = await asyncio.gather(*tasks)

    for stat in stats:
        print(stat)
    #     stat: B4U_Account
    #     print(stat)
    #     print(stat.single_rating)
    #     print(stat.double_rating)

    # stat = await stat_parser(player_id=17264)
    # stat2 = await stat_parser(player_id=17284)
    # print(stat)
    # print(stat2)


if __name__ == '__main__':
    start_time = time.time()
    loop = asyncio.new_event_loop()
    loop.run_until_complete(main_async())
    loop.run_until_complete(asyncio.sleep(1))
    logger.info(f"Execution time: {time.time() - start_time} seconds")