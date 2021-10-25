from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as exp_cond
from selenium.webdriver.support.ui import WebDriverWait
from typing import List

from data.config import PSN_USERNAME, PSN_PASSWORD, PSN_EMAIL
import time
import random
from selenium.common.exceptions import NoSuchElementException
from bs4 import BeautifulSoup
import re
import logging

logger = logging.getLogger(__name__)
# TODO: сделать асинхронной
# TODO: научиться запускать SELENIUM на сервере

class PSN_Bot:

    def __init__(self, username, email, password):

        self.username = username
        self.email = email
        self.password = password
        self.browser = webdriver.Chrome('E:/Documents/Python3/aiogram-bot-template/utils/selenium_psn/chromedriver_win32/chromedriver.exe')
        self.time_start = time.time()  # время, во сколько был инициирован браузер
        self.browser.maximize_window()

    # закрываем страницу, закрываем браузер
    def close_browser(self):

        self.browser.close()
        self.browser.quit()

    # логинимся в учётке PSN
    def login(self):

        browser = self.browser
        browser.get(
            'https://my.account.sony.com/central/signin/?response_type=token&scope=capone%3Areport_submission%2Ckamaji%3Agame_list%2Ckamaji%3Aget_account_hash%2Cuser%3Aaccount.get%2Cuser%3Aaccount.profile.get%2Ckamaji%3Asocial_get_graph%2Ckamaji%3Augc%3Adistributor%2Cuser%3Aaccount.identityMapper%2Ckamaji%3Amusic_views%2Ckamaji%3Aactivity_feed_get_feed_privacy%2Ckamaji%3Aactivity_feed_get_news_feed%2Ckamaji%3Aactivity_feed_submit_feed_story%2Ckamaji%3Aactivity_feed_internal_feed_submit_story%2Ckamaji%3Aaccount_link_token_web%2Ckamaji%3Augc%3Adistributor_web%2Ckamaji%3Aurl_preview&client_id=656ace0b-d627-47e6-915c-13b259cd06b2&redirect_uri=https%3A%2F%2Fmy.playstation.com%2Fauth%2Fresponse.html%3FrequestID%3Dexternal_request_8fd55d10-4c4f-4650-9df3-813be5e7ce41%26baseUrl%3D%2F%26returnRoute%3D%2F%26targetOrigin%3Dhttps%3A%2F%2Fmy.playstation.com%26excludeQueryParams%3Dtrue&tp_console=true&ui=pr&cid=ee755996-3570-4767-9681-0ba09aa86503&error=login_required&error_code=4165&no_captcha=true#/signin/ca?entry=ca')

        username_input_xpath = '/html/body/div[3]/div/div/div[3]/div/div/div/div/div[4]/div/div[1]/main/div/div/div[5]/div/form/div[1]/div/div/div/div/input'
        password_input_xpath = '/html/body/div[3]/div/div/div[3]/div/div/div/div/div[4]/div/div[1]/main/div/div/div[5]/div/form/div[1]/div[2]/div/div/div/input'
        username_xpath = '/html/body/div[6]/div/main/div[1]/div/div[2]/a/span[2]/span[2]/span'

        logger.info('Поиск элемента USERNAME_FIELD')
        if self.xpath_exists(username_input_xpath, 500):
            username_input = browser.find_element_by_xpath(username_input_xpath)
            username_input.clear()
            username_input.send_keys(self.email)
            username_input.send_keys(Keys.ENTER)
            time.sleep(random.randrange(0, 1))
            logger.info('Поиск элемента PASSWORD_FIELD')
            if self.xpath_exists(password_input_xpath, 10):
                password_input = browser.find_element_by_xpath(password_input_xpath)
                password_input.clear()
                password_input.send_keys(self.password)
                password_input.send_keys(Keys.ENTER)
                time.sleep(random.randrange(0, 1))
                logger.info('Поиск элемента USERNAME')
                if self.xpath_is_equal(self.username, username_xpath, 500):
                    logger.info('Мы залогинились на сайте SONY')
        else:
            logger.critical('Залогиниться на сайте SONY не получилось')

    # возвращает состояние (залогинены или нет)
    def is_logged_in_func(self):
        logger.info('Начинаем проверку, залогинены мы на сайте www.playstation.com или нет')
        is_logged_in = False
        browser = self.browser
        browser.execute_script("window.open('https://my.playstation.com/profile/me/friends')")  # создаём новую вкладку
        tabs = browser.window_handles  # получаем список вкладок
        browser.switch_to.window(tabs[1])  # переключаемся на вторую вкладку
        time.sleep(1)  # на всякий случай ждём 1 секунду
        my_ps_link_xpath = '/html/body/div[3]/div/header/div/div/div/a'
        logger.info('Начинаем проверку, отрисовалась ли на странице значок playstation')

        if self.xpath_is_equal('My PlayStation', my_ps_link_xpath):  # проверяем, отрисовалась ли ссылка на странице
            logger.info('Cсылка My PlayStation корректно отрисована на web-странице')
            time.sleep(1)  # на всякий случай ждём 1 секунду
            psn_xpath = '/html/body/div[6]/div/main/div[1]/div/div[2]/a/span[2]/span[2]/span'
            login_button_xpath = '/html/body/div[6]/div/main/div/div[1]/div/div[3]/button[1]'

            try:
                print('gsdgjklsd ')
                if self.xpath_is_equal('Войти в сеть', login_button_xpath):
                    logger.info('Мы не залогинены')
                    is_logged_in = False
                elif self.xpath_is_equal('Sign In', login_button_xpath):
                    logger.info('Мы не залогинены')
                    is_logged_in = False
                elif self.xpath_is_equal(self.username, psn_xpath):
                    logger.info('Мы залогинены по Username = ', self.username)
                    is_logged_in = True
            except Exception as ex:
                logger.info('Exception: ', ex)
        self.browser.close()  # закрывам текущую вкладку
        browser.switch_to.window(tabs[0])  # переключаемся на первую вкладку
        return is_logged_in

    # проверяем, друг ли тебе указанный пользователь
    def psn_status(self, psn):

        browser = self.browser
        browser.get('https://my.playstation.com/profile/' + str(psn))
        time.sleep(random.randrange(0, 1))
        friend_or_not_button_xpath = '/html/body/div[6]/div/main/div[2]/div/div[2]/div[1]/div/div[1]/button'
        status = 'Неизвестно'
        if self.xpath_exists(friend_or_not_button_xpath, 60):
            a = browser.find_element_by_xpath(friend_or_not_button_xpath).text
            # print(a)

            time.sleep(random.randrange(0, 1))
            add_to_friend_button_xpath = '/html/body/div[6]/div/main/div[2]/div/div[2]/div[1]/div/div[1]/button'
            if self.xpath_exists(add_to_friend_button_xpath, 60):
                status = browser.find_element_by_xpath(add_to_friend_button_xpath).text

        print(f'{psn} - {status}')
        """
          Paha_Babaha - Добавить Друга
          Manile_88 - Подписаться
          New_Renegades - Вы подписаны
          """
        return status

    # получаем список друзей в виде словаря {psn, name, now_playing, status, ps_plus}
    def friends_list(self, psn) -> List[dict]:

        url = 'https://my.playstation.com/profile/me/friends'
        if psn != self.username:
            url = 'https://my.playstation.com/profile/'+str(psn)+'/friends'

        browser = self.browser
        browser.get(url)

        psn_xpath = '/html/body/div[6]/div/main/div[1]/div/div[2]/a/span[2]/span[2]/span'
        players = []
        if self.xpath_is_equal(self.username, psn_xpath):  # проверяем видимость username
            print('Проверка логирования на сайт под psn = ', self.username, ' пройдена успешно!')

            time.sleep(random.randrange(1, 2))
            html_page = str(browser.page_source)

        # для тренировки на макете html
        # with open("psn_html.html", "rb") as file:
        #     html = file.read()

            soup = BeautifulSoup(html_page, 'lxml').find('section', class_='friends-list__content')  # превращаем HTML в суп

            try:
                items = soup.find_all('div', class_='friends-list__user-tile-container')  # разбиваем построчно

                for item in items:

                    psn = item.find(dir="ltr").get_text().strip()
                    if item.find(class_="user-tile-card__online-id online-id") is not None:
                        psn = item.find(class_="user-tile-card__online-id online-id").get_text().strip()

                    full_name = None
                    if item.find('span', class_=re.compile(
                            'user-tile-card__primary-name user-tile-card__primary-name--*')) is not None:
                        full_name = item.find('span', class_=re.compile(
                            'user-tile-card__primary-name user-tile-card__primary-name--*')).get_text().strip()

                    now_playing = None
                    if item.find(class_="user-tile-card__now-playing--title") is not None:
                        now_playing = item.find(class_="user-tile-card__now-playing--title").get_text().strip()

                    status = None
                    if item.find('span', class_=re.compile('user-tile-card__online-status*')) is not None:
                        status = item.find(class_=re.compile('user-tile-card__online-status*')).get('aria-label')

                    ps_plus = None
                    if item.find('span', class_=re.compile('user-tile-card__status*')) is not None:
                        ps_plus = item.find(class_=re.compile('user-tile-card__status*')).get('aria-label')

                    player = {
                        'psn': psn,
                        'name': full_name,
                        'now_playing': now_playing,
                        'status': status,
                        'ps_plus': ps_plus
                    }
                    players.append(player)

            except Exception as ex:
                print(ex)
        return players

    # добавляем в друзья, пишем сообщение
    def add_to_friend(self, psn: str, message=None):

        browser = self.browser
        browser.get('https://my.playstation.com/profile/' + str(psn))
        time.sleep(random.randrange(0, 1))
        friend_or_not_button_xpath = '/html/body/div[6]/div/main/div[2]/div/div[2]/div[1]/div/div[1]/button'
        if self.xpath_exists(friend_or_not_button_xpath, 60):
            a = browser.find_element_by_xpath(friend_or_not_button_xpath).text
            print(a)

            time.sleep(random.randrange(0, 1))
            add_to_friend_button_xpath = '/html/body/div[6]/div/main/div[2]/div/div[2]/div[1]/div/div[1]/button'
            if self.xpath_exists(add_to_friend_button_xpath, 60):
                browser.find_element_by_xpath(add_to_friend_button_xpath).click()

                time.sleep(random.randrange(0, 1))
                add_to_friend_button_xpath2 = '/html/body/div[3]/div/header/div/div/div/div[2]/div/div/div/div/div[3]/button[1]'
                if self.xpath_exists(add_to_friend_button_xpath2, 60):
                    browser.find_element_by_xpath(add_to_friend_button_xpath2).click()
                    print(f'запрос пользователю {psn} о добавлении в друзья отправлен')

    # возвращает кол-во друзей
    def friends_count_func(self, psn):
        browser = self.browser
        browser.get(f'https://my.playstation.com/profile/{psn}/friends')
        psn_xpath = '/html/body/div[6]/div/main/div[1]/div/div[2]/a/span[2]/span[2]/span'
        friends_count = 0
        if self.xpath_is_equal(psn, psn_xpath):  # проверяем видимость username
            friends_count = int(browser.find_element_by_xpath(
                '/html/body/div[6]/div/main/div[2]/div/section/div/div[2]/div/div/header/header/span').text)
        return friends_count

    # проверка нахождения элемента на странице по xpath
    def xpath_exists(self, xpath, waiting_time=600.0):

        browser = self.browser
        start = time.time()
        while True:
            try:
                if time.time() >= start+waiting_time:
                    print(f'Прошло более {waiting_time}сек, элемент так и не найден(')
                    exist = False
                    break
                time.sleep(random.randrange(0, 1))
                browser.find_element_by_xpath(xpath)
                logger.info(f'Элемент найден за {time.time()-start} секунд')
                exist = True
                break
            except NoSuchElementException:
                exist = False
        return exist

    # проверка соответствия значения текста внутри элемента на странице по xpath
    def xpath_is_equal(self, value, xpath, waiting_time=600.0):

        is_equal = False
        browser = self.browser
        if self.xpath_exists(xpath):
            start = time.time()
            while True:
                try:
                    if time.time() >= start + waiting_time:
                        logger.info(f'Прошло более {waiting_time}сек, значение {value} так и не было найдено(')

                        break
                    time.sleep(random.randrange(0, 1))
                    if browser.find_element_by_xpath(xpath).text == value:
                        logger.info(f'Значение {value} было найдено за {time.time()-start} сек')
                        is_equal = True
                        break
                except Exception:
                    is_equal = False
        return is_equal


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(message)s',
        datefmt='%d.%m.%y %H:%M:%S')
    my_bot = PSN_Bot(PSN_USERNAME, PSN_EMAIL, PSN_PASSWORD)  # создаем экземпляр браузера
    # print(my_bot.is_logged_in_func())  # проверяем, залогинены ли мы - False
    my_bot.login()  # логинимся
    # print(my_bot.is_logged_in_func())  # проверяем, залогинены ли мы - True
    psn = 'manile_88'  # активная PSN
    print(my_bot.friends_count_func(my_bot.username))  # выводим кол-во друзей
    players = my_bot.friends_list(my_bot.username)  # получаем список друзей и выводим их
    for player in players:
        print(player)
    # psn1 = 'Paha_Babaha'
    # psn2 = 'Manile_88'
    # psn3 = 'New_Renegades'

    my_bot.add_to_friend(psn)
    # my_bot.psn_status(psn1)
    # my_bot.psn_status(psn2)
    # my_bot.psn_status(psn3)

    #
    # #

