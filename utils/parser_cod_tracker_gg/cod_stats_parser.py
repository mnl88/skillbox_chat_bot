"""
Парсер с сайта https://cod.tracker.gg/

platform_type 1 - PC
platform_type 2 - PS
platform_type 3 - Xbox

"""

# TODO: сделать асинхронной

# import requests
from bs4 import BeautifulSoup
import logging
import re
from typing import List, Dict, Optional, Any

logger = logging.getLogger(__name__)

HOST = 'https://cod.tracker.gg/'
URL_MP_START = 'modern-warfare/profile/atvi/'
URL_MP_FINISH = '/mp'
URL_WZ_START = 'warzone/profile/atvi/'
URL_WZ_FINISH = '/overview'
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36',
    'DNT': '1',
    'sec-ch-ua': '"Google Chrome";v="87", " Not;A Brand";v="99", "Chromium";v="87"',
    'sec-ch-ua-mobile': '?0',
    'Upgrade-Insecure-Requests': '1'
}


def get_html(host, url_start, url_finish, activision_id: str):
    """распарчим страничку"""
    url_middle = activision_id.replace('#', '%23')
    url = host + url_start + url_middle + url_finish
    logger.info(f'url: {url}')
    response = requests.get(url=url, headers=HEADERS)
    return response


def get_content(html, game_type='WZ'):
    """Вернем список труб"""
    if game_type == 'WZ':
        kd_ratio_column = 2
    else:
        kd_ratio_column = 0

    soup = BeautifulSoup(html.text, 'html.parser')  # превращаем HTML в суп
    kd_ratio = 'unknown'
    try:
        mini_soup = soup.find('div', class_='giant-stats')  # уменьшаем суп до таблицы
        items = mini_soup.find_all('div', class_='stat align-left giant expandable')  # разбиваем построчно
        for i, item in enumerate(items[:3]):  # перебирает только строк в каждом блоке
            if i == kd_ratio_column:
                title = item.find('span', title='K/D Ratio').get_text()
                if title == 'K/D Ratio':
                    kd_ratio = item.find('span', class_='value').get_text()
    except:
        pass
    return kd_ratio


def parser_act_id(activision_id, game_type='WZ'):
    """парсер КД по id activision"""

    if game_type == 'WZ':
        html = get_html(HOST, URL_WZ_START, URL_WZ_FINISH, activision_id)
    else:
        html = get_html(HOST, URL_MP_START, URL_MP_FINISH, activision_id)
    if html.status_code == 200:
        kd_ratio = get_content(html, game_type)
    else:
        logger.error(f'Что-то не так {html}, {html.status_code}')
        kd_ratio = 'unknown'
    return kd_ratio


def get_html_2(url):
    response = requests.get(url=url, headers=HEADERS)
    return response


# парсер. возвращает словарь вида: warzone - plumber - kills - 10
def parse_stat(activision_account=None, psn_account=None,
               blizzard_account=None, xbox_account=None, platform_type=None) -> dict:
    """парсер. возвращает словарь вида: warzone - plumber - kills - 10"""

    url_host = 'https://cod.tracker.gg/'

    if platform_type == 2 and psn_account is not None:
        url_profile_type_part = 'psn/'
        url_account_name_part = psn_account
        # 'https://cod.tracker.gg/warzone/profile/psn/manile_88/overview'

    elif platform_type == 1 and blizzard_account is not None:
        url_profile_type_part = 'battlenet/'
        url_account_name_part = blizzard_account.replace('#', '%23')
        # 'https://cod.tracker.gg/warzone/profile/battlenet/Manile%2321212/overview'

    elif platform_type == 3 and xbox_account is not None:
        url_profile_type_part = 'xbl/'
        url_account_name_part = xbox_account.replace(' ', '%20')
        # 'https://cod.tracker.gg/warzone/profile/xbl/UNKNOWN%206989/overview'

    elif activision_account is not None:
        # 'https://cod.tracker.gg/warzone/profile/atvi/npopok%236351930/overview'
        url_profile_type_part = 'atvi/'
        url_account_name_part = activision_account.replace('#', '%23')

    else:
        logger.error('Account Activision или сочитание платформа + аккаунт к этой платформе не обнаружены')
        return {'warzone': None, 'modern-warfare': None, 'cold-war': None}

    urls = {
        'warzone': url_host + 'warzone/profile/' + url_profile_type_part + url_account_name_part,
        'modern-warfare': url_host + 'modern-warfare/profile/' + url_profile_type_part + url_account_name_part,
        'cold-war': url_host + 'cold-war/profile/' + url_profile_type_part + url_account_name_part
    }
    all_stats_dict = {}
    for game_type, url in urls.items():

        html = get_html_2(urls[game_type])
        # print('html.status_code = ', html.status_code)
        if html.status_code == 200:
            # kd_ratio = get_kd_ratio(html, game_type)
            logger.info(f'{game_type}, url: {url} - доступна для парсинга')
            all_stats_dict[game_type] = get_statistics(html)
        elif html.status_code == 404:
            # kd_ratio = get_kd_ratio(html, game_type)
            logger.info(f'{game_type}, url: {url} - ошибка 404, парсинг невозможен')
            all_stats_dict[game_type] = get_statistics(html)
        else:
            logger.error(f'Что-то не так {urls[game_type]}, {html.status_code}')
            all_stats_dict[game_type] = None
    return all_stats_dict


def get_statistics(html) -> dict:
    """Вернем список труб"""

    soup = BeautifulSoup(html.text, 'html.parser')  # превращаем HTML в суп
    stat_dict = {}
    try:
        items = soup.find('div', class_='trn-grid').find_all('div', class_='segment-stats card bordered responsive')
        for item in items:
            header = item.find('h2').get_text()
            stat_dict[header] = {}
            cells = item.find_all('div', class_='numbers')
            for cell in cells:
                title = cell.find('span', class_="name").get('title')
                if cell.find('span', class_="value") is not None:
                    value = cell.find('span', class_="value").get_text()
                else:
                    value = None
                if stat_dict[header].setdefault(title) is None:
                    stat_dict[header][title] = value
        # print(stat_dict)
    except:
        pass
    return stat_dict


def get_kd(full_statistic: dict):
    kd_ratio = {}
    try:
        kd_ratio['warzone'] = full_statistic.setdefault('warzone').setdefault('Battle Royale').setdefault('K/D Ratio')
    except Exception as ex:
        print('ERROR: ', ex)
        kd_ratio['warzone'] = None
    try:
        kd_ratio['modern-warfare'] = full_statistic.setdefault('modern-warfare').setdefault('Lifetime Overview').setdefault('K/D Ratio')
    except Exception as ex:
        print('ERROR: ', ex)
        kd_ratio['modern-warfare'] = None
    try:
        kd_ratio['cold-war'] = full_statistic.setdefault('cold-war').setdefault('Lifetime Overview').setdefault('K/D Ratio')
    except Exception as ex:
        print('ERROR: ', ex)
        kd_ratio['cold-war'] = None
    return kd_ratio


def show_statistics(full_statistic: dict):
    for game, game_type in full_statistic.items():
        print('\n', game)
        for stat, value in game_type.items():
            print('\n', stat)
            for s, v in value.items():
                print(s, ': ', v)


def main():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(message)s',
        datefmt='%d.%m.%y %H:%M:%S')

    full_statistic = parse_stat(activision_account='DRONORD#9501196')
    show_statistics(full_statistic)

    # kd_ratio_wz = parse_stat(activision_account='npopok#6351930')['warzone']['Battle Royale']['K/D Ratio']
    # kd_ratio_mw = parse_stat(psn_account='manile_88', platform_type=2)['modern-warfare']['Lifetime Overview']['K/D Ratio']
    # # kd_ratio_cd = parse_stat(blizzard_account='Manile#21212', platform_type=1)['cold-war']['Warzone Overview']['K/D Ratio']
    # # kd_ratio_wz_2 = parse_stat(xbox_account='unknown 7878', platform_type=3)['cold-war']['Warzone Overview']['K/D Ratio']
    # # kd_ratio_cd_2 = parse_stat()['cold-war']['Warzone Overview']['K/D Ratio']
    # statistic = parse_stat(activision_account='npopok#6351930')

    # kd_wz_example = get_kd(parse_stat(activision_account='npopok#6351930'), 'WZ')
    # print(f'{kd_wz_example=}')
    # kd_mp_example = get_kd(parse_stat(psn_account='manile_88', platform_type=2), 'MP')
    # print(f'{kd_mp_example=}')
    # kd_cw_example = get_kd(parse_stat(blizzard_account='Manile#21212', platform_type=1), 'CD')
    # print(f'{kd_cw_example=}')


if __name__ == '__main__':
    main()
