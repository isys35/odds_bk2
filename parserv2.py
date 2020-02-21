#!/usr/bin/python3
# -*- coding: utf-8 -*-
import traceback
import sys
from PyQt5 import QtGui, QtWidgets
from PyQt5.QtCore import QThread, Qt
import sqlite3
import mainwindow
from bs4 import BeautifulSoup as BS
import multiparser
import requests
from parser_odds import Parser
import webbrowser
import json
import time
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.common import exceptions
from browsermobproxy import Server
from collections import Counter


class MultiParsing(QtWidgets.QDialog, multiparser.Ui_Dialog):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.counter_game = 0
        self.db = 'soccer.db'
        self.main_page = 'https://www.oddsportal.com'
        self.update_counter_game()
        self.pushButton.clicked.connect(self.update_counter_game)
        self.comboBox.addItems([str(i) for i in range(1, 11)])
        self.pushButton_2.clicked.connect(self.start_multi_parsing)

    def update_counter_game(self):
        print('[INFO] Подключение к базе')
        con = sqlite3.connect(self.db)
        cur = con.cursor()
        query = 'SELECT COUNT(*) FROM game'
        executing = False
        while not executing:
            try:
                cur.execute(query)
                executing = True
            except sqlite3.OperationalError:
                print('[WARNING] База данных используется...')
                print('[WARNING] Ожидание...')
                time.sleep(0.1)
        all_game_count = cur.fetchone()
        self.label_41.setText('Количество игр в базе: ' + str(all_game_count[0]))
        cur.close()
        con.close()
        print('[INFO] Подключение к базе успешно')

    def start_multi_parsing(self):
        self.managepars = ManagerPars(int(self.comboBox.currentText()),self)
        self.managepars.start()


class ManagerPars(QThread):
    def __init__(self, n_pars, window):
        super().__init__()
        self.n_pars = n_pars
        self.window = window
        self.hrefs_pars = []
        #self.parser_statuses = [False for i in range(0, 10)]
        self.soccer_url = 'https://www.oddsportal.com/results/#soccer'
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:71.0) Gecko/20100101 Firefox/71.0'
        }
        self.start_time = time.time()
        self.labels = [
            {
                'status': self.window.label_3,
                'country': self.window.label_2,
                'champ': self.window.label_4,
                'count': self.window.label_31
            },
            {
                'status': self.window.label_16,
                'country': self.window.label_17,
                'champ': self.window.label_18,
                'count': self.window.label_36
            },
            {
                'status': self.window.label_6,
                'country': self.window.label_7,
                'champ': self.window.label_5,
                'count': self.window.label_32
            },
            {
                'status': self.window.label_19,
                'country': self.window.label_21,
                'champ': self.window.label_20,
                'count': self.window.label_37
            },
            {
                'status': self.window.label_8,
                'country': self.window.label_10,
                'champ': self.window.label_9,
                'count': self.window.label_33
            },
            {
                'status': self.window.label_22,
                'country': self.window.label_23,
                'champ': self.window.label_24,
                'count': self.window.label_38
            },
            {
                'status': self.window.label_11,
                'country': self.window.label_12,
                'champ': self.window.label,
                'count': self.window.label_34
            },
            {
                'status': self.window.label_25,
                'country': self.window.label_27,
                'champ': self.window.label_26,
                'count': self.window.label_39
            },
            {
                'status': self.window.label_13,
                'country': self.window.label_15,
                'champ': self.window.label_14,
                'count': self.window.label_35
            },
            {
                'status': self.window.label_30,
                'country': self.window.label_29,
                'champ': self.window.label_28,
                'count': self.window.label_40
            },


        ]
        self.parsers = [ParserThread(self.labels[i]) for i in range(0, self.n_pars)]

    def update_label_info(self):
        count = sum([pars.counter_game for pars in self.parsers])
        self.window.label_42.setText(f'Количество добавленных игр: {count}')
        delta_time = time.time() - self.start_time
        game_per_sec = count/delta_time
        game_per_hour = round(game_per_sec*60)
        self.window.label_43.setText(f'Скорость : {game_per_hour} игр/минуту')


    def pars(self):
        soccer_url = 'https://www.oddsportal.com/results/#soccer'
        r = requests.get(soccer_url, headers=self.headers)
        html = BS(r.content, 'html.parser')
        championships = html.select('table.table-main.sport')[0].select('td')
        # список с ссылками на все чемпионаты
        href_championships = [championship.select('a')[0]['href'] for championship in championships
                              if len(championship.select('a')) > 0]
        href_championships_soccer = [href for href in href_championships if href.split('/')[1] == 'soccer']
        print(href_championships_soccer)
        self.start_time = time.time()
        for href in href_championships_soccer:
            if href not in self.hrefs_pars:
                self.hrefs_pars.append(href)
            while not False in [self.parsers[i].status for i in range(0, self.n_pars)]:
                time.sleep(1)
                self.update_label_info()
                print('.......')
            for i in range(0, self.n_pars):
                if not self.parsers[i].status:
                    self.parsers[i].status = True
                    time.sleep(.2)
                    self.parsers[i].href = href
                    self.parsers[i].start()
                    break

    def run(self):
        self.pars()


class ParserThread(QThread):
    def __init__(self, labels):
        super().__init__()
        self.labels = labels
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:71.0) Gecko/20100101 Firefox/71.0'
        }
        self.counter_game = 0
        self.counter_bet = 0
        self.status = False
        self.main_page = 'https://www.oddsportal.com'
        self.db = 'soccer.db'
        self.href = ''
        self.browser_start()
        self.out_match_data = {}
        self.bookmakersData = self.get_bookmakersdata()

    def update_label(self):
        if self.status:
            self.labels['status'].setText('Состояние: in progress')
        if 'country' in self.out_match_data:
            self.labels['country'].setText('Страна: {}'.format(self.out_match_data['country']))
        if 'champ' in self.out_match_data:
            self.labels['champ'].setText('Чемпионат: {}'.format(self.out_match_data['champ']))
        self.labels['count'].setText('Количество добавленных игр: {}'.format(self.counter_game))


    @staticmethod
    def get_bookmakersdata():
        with open("bookmakersData.json", "r") as read_file:
            return json.load(read_file)

    def browser_start(self):
        """
        Запуск браузера
        self.browser
        """
        print('[INFO] Запуск браузера')
        options = Options()
        options.headless = False  # False - не отображает браузер; True - отображает
        self.server = Server(path=r"browsermob-proxy-2.1.4\bin\browsermob-proxy.bat")
        self.server.start()
        self.proxy = self.server.create_proxy()
        profile = webdriver.FirefoxProfile()
        profile.set_proxy(self.proxy.selenium_proxy())
        self.browser = webdriver.Firefox(firefox_profile=profile, options=options)
        print('[INFO] Браузер запущен')

    def pars(self):
        print('parsing ' + self.href)
        self.out_match_data = {}
        self.status = True
        champ_request_allyears = requests.get(self.main_page + self.href, headers=self.headers)
        html_championship = BS(champ_request_allyears.content, 'html.parser')
        years_menu = html_championship.select('.main-menu2.main-menu-gray')
        year_page_reversed = []
        if years_menu:
            years_pages = years_menu[0].select('a')
            first_page = years_pages[0]['href']
            print(first_page)
            browse = False
            while not browse:
                try:
                    self.browser.get(self.main_page + self.href)
                    browse = True
                except exceptions.WebDriverException:
                    print('[INFO] Не удалось подключиться')
                    time.sleep(5)
            content_first_page = self.browser.page_source
            soup_champ = BS(content_first_page, 'html.parser')
            string_sport = soup_champ.select('#breadcrumb')[0].select('a')[1].text
            self.out_match_data['sport'] = string_sport
            country = soup_champ.select('#breadcrumb')[0].select('a')[2].text
            self.out_match_data['country'] = country
            string_champ = soup_champ.select('#breadcrumb')[0].select('a')[3].text
            self.out_match_data['champ'] = string_champ
            self.update_label()
            print('[INFO] Страна ' + country)
            print('[INFO] Чемпионат ' + string_champ)
            if self.check_champ_in_db(self.main_page + first_page):
                print('[INFO] Чемпионат полностью в базе')
                self.status = False
                return
            print('[INFO] Чемпионат не полностью в базе')
            year_page_reversed = years_pages
            year_page_reversed.reverse()
        if year_page_reversed:
            for page in year_page_reversed:
                year_page = self.main_page + page['href']
                if year_page == 'https://www.oddsportal.com//results/':
                    continue
                print('[INFO] Страница с годом ' + page.text + ' ' + year_page)
                if self.check_champ_in_db(year_page):
                    print('[INFO] Год полностью есть в базе')
                    continue
                print('[INFO] Год не полностью в базе')
                if year_page != self.browser.current_url:
                    browse = False
                    while not browse:
                        try:
                            self.browser.get(year_page)
                            browse = True
                        except exceptions.WebDriverException:
                            print('[INFO] Не удалось подключиться')
                            time.sleep(5)
                soup_pagination = BS(self.browser.page_source, 'html.parser')
                pagination = soup_pagination.select('#pagination')
                if not pagination:
                    self.get_champ_data_in_year(year_page)
                else:
                    max_page = pagination[0].select('a')[-1]['x-page']
                    p = int(max_page)
                    while p != 1:
                        print('[INFO]Страница ' + str(p))
                        year_page_add = self.main_page + page['href'] + '#/page/%s/' % str(p)
                        if self.check_champ_in_db(year_page_add):
                            p -= 1
                            continue
                        self.get_champ_data_in_year(year_page_add, p)
                        p -= 1
                    self.get_champ_data_in_year(year_page)
        self.status = False

    def check_champ_in_db(self, champ_url):
        """
        Проверка: закончен ли парсинг чемпионата
        :return:
        bool
        """
        if champ_url != self.browser.current_url:
            browse = False
            while not browse:
                try:
                    self.browser.get(champ_url)
                    browse = True
                except exceptions.WebDriverException:
                    print('[INFO] Не удалось подключиться')
                    time.sleep(5)
        content_browser = self.browser.page_source
        soup_champ = BS(content_browser, 'html.parser')
        trs = soup_champ.select('#tournamentTable')[0].select('tr')
        if trs[0].select('.cms'):
            print('[INFO] No data available')
            return True
        try:
            for tr in trs:
                check = tr['class']
        except KeyError:
            print('[WARNING] Not odds')
            return True
        for tr in trs:
            if 'deactivate' in tr['class']:
                if len(tr.select('span.live-odds-ico-prev')) == 0:
                    match_url = self.main_page + tr.select('a')[0]['href']
                    if self.check_game_in_db(match_url):
                        return True
                    else:
                        return False

    def check_game_in_db(self, url):
        """
        Проверка есть ли игра в базе
        :param url:
        Ссылка на игру
        :return:
        bool
        """
        print('[INFO] Проверка игры ' + url)
        con = sqlite3.connect(self.db)
        cur = con.cursor()
        query = 'SELECT EXISTS(SELECT * FROM game WHERE url = ? LIMIT 1)'
        executing = False
        while not executing:
            try:
                cur.execute(query, [url])
                executing = True
            except sqlite3.OperationalError:
                print('[WARNING] База данных используется...')
                print('[WARNING] Ожидание...')
                time.sleep(0.1)
        game_bool = [game[0] for game in cur.fetchall()][0]
        if game_bool:
            print('[INFO] %s игра уже есть в базе ' % str(url))
            cur.close()
            con.close()
            return True
        print('[INFO] %s игры нету в базе ' % str(url))
        cur.close()
        con.close()
        return False

    def get_champ_data_in_year(self, url, *args):
        """
        Получение данных из страницы со списком матчей
        и добавление игр в бд
        :param url:
            адрес страницы
        :param args:
            если страница имеет много подстраниц,
             args[0] - номер этой страницы
        :return:
        """
        print(url)
        if url != self.browser.current_url:
            browse = False
            while not browse:
                try:
                    self.browser.get(self.main_page)
                    browse = True
                except exceptions.WebDriverException:
                    print('[INFO] Не удалось подключиться')
                    time.sleep(5)
            browse = False
            while not browse:
                try:
                    self.browser.get(url)
                    browse = True
                except exceptions.WebDriverException:
                    print('[INFO] Не удалось подключиться')
                    time.sleep(5)
        content_browser = self.browser.page_source
        soup_champ = BS(content_browser, 'html.parser')
        trs = soup_champ.select('#tournamentTable')[0].select('tr')
        trs.reverse()
        try:
            for tr in trs:
                check = tr['class']
        except KeyError:
            print('[WARNING] Not odds')
            return []
        if args:
            active_page = 0
            count_check_page = 0
            while active_page != args[0]:
                print('[INFO] проверка правильности страницы')
                content_browser = self.browser.page_source
                soup_champ = BS(content_browser, 'html.parser')
                active_page = int(soup_champ.select('#pagination')[0].select('span.active-page')[0].text)
                count_check_page += 1
                if count_check_page == 50:
                    count_check_page = 0
                    browse = False
                    while not browse:
                        try:
                            self.browser.get(self.main_page)
                            browse = True
                        except exceptions.WebDriverException:
                            print('[INFO] Не удалось подключиться')
                            time.sleep(5)
                    browse = False
                    while not browse:
                        try:
                            self.browser.get(url)
                            browse = True
                        except exceptions.WebDriverException:
                            print('[INFO] Не удалось подключиться')
                            time.sleep(5)
            print('[INFO] Страница верная')
        for tr in trs:
            if 'deactivate' in tr['class']:
                if len(tr.select('span.live-odds-ico-prev')) == 0:
                    timematch = tr.select('td.table-time')[0].text
                    match_url = self.main_page + tr.select('a')[0]['href']
                    if self.check_game_in_db(match_url):
                        continue
                    game_name = tr.select('a')[0].text
                    command1 = game_name.split(' - ')[0]
                    command2 = game_name.split(' - ')[1]
                    result, odds, date, req_api = self.get_match_data(match_url)
                    self.out_match_data['time'] = timematch
                    self.out_match_data['url'] = match_url
                    self.out_match_data['command1'] = command1
                    self.out_match_data['command2'] = command2
                    self.out_match_data['result'] = result
                    self.out_match_data['odds'] = odds
                    self.out_match_data['date'] = date
                    self.out_match_data['req_api'] = req_api
                    print(self.out_match_data)
                    if 'Canceled' != result and 'awarded' not in result:
                        self.add_game_in_db()
                        self.add_bet_in_db()

    def add_game_in_db(self):
        """
        Добавление игры в базу
        :param args:
        :arg[0] - Словарь для ручного добавления в базу
        :return:
        """
        con = sqlite3.connect(self.db)
        cur = con.cursor()
        input_data = [self.out_match_data['command1'],
                          self.out_match_data['command2'],
                          self.out_match_data['url'],
                          self.out_match_data['date'],
                          self.out_match_data['time'],
                          self.out_match_data['result'],
                          self.out_match_data['sport'],
                          self.out_match_data['country'],
                          self.out_match_data['champ'],
                          self.out_match_data['req_api']
                          ]
        executing = False
        while not executing:
            try:
                cur.execute('INSERT INTO game (command1,command2,url,date,timematch,'
                            'result,sport,country,liga,url_api) '
                            'VALUES(?,?,?,?,?,?,?,?,?,?)', input_data)
                executing = True
            except sqlite3.OperationalError:
                print('[WARNING] База данных используется...')
                print('[WARNING] Ожидание...')
                time.sleep(0.1)
        commited = False
        while not commited:
            try:
                con.commit()
                commited = True
            except sqlite3.OperationalError:
                print('[WARNING] База данных используется...')
                print('[WARNING] Ожидание...')
                time.sleep(0.1)
        print('[INFO] игра %s добавлена в базу' % str(input_data[0:2]))
        self.counter_game += 1
        self.update_label()
        print('[INFO] Добавлено игр ' + str(self.counter_game))
        cur.close()
        con.close()

    def add_bet_in_db(self):
        """
                Добавление коэф-тов в бд
                :return:
                """
        print('[INFO] add bets in db.....')
        start = time.time()
        con = sqlite3.connect(self.db)
        cur = con.cursor()
        query = 'SELECT id,url FROM game'
        executing = False
        while not executing:
            try:
                cur.execute(query)
                executing = True
            except sqlite3.OperationalError:
                print('[WARNING] База данных используется...')
                print('[WARNING] Ожидание...')
                time.sleep(0.1)
        data_game_dict = {}
        for game in cur.fetchall():
            data_game_dict[game[0]] = game[1]
        key_game = None
        for key, item in data_game_dict.items():
            if item == self.out_match_data['url']:
                key_game = key
                break
        for key, item in self.out_match_data['odds'].items():
            self.add_bookmaker_in_db(key, cur, con)
            key_bookmaker = None
            query = 'SELECT * FROM bookmaker'
            executing = False
            while not executing:
                try:
                    cur.execute(query)
                    executing = True
                except sqlite3.OperationalError:
                    print('[WARNING] База данных используется...')
                    print('[WARNING] Ожидание...')
                    time.sleep(0.1)
            data_bookmakers = [[el for el in bookmaker] for bookmaker in cur.fetchall()]
            for bookmaker in data_bookmakers:
                if bookmaker[1] == key:
                    key_bookmaker = bookmaker[0]
                    break
            data_out = []
            if len(item) == 4:
                data_out = [key_bookmaker, item[0], item[1], item[2], key_game, item[3]]
            elif len(item) == 3:
                data_out = [key_bookmaker, item[0], 0, item[1], key_game, item[2]]
            executing = False
            while not executing:
                try:
                    cur.execute('INSERT INTO bet (bookmaker_id,p1,x,p2,game_id,open_time) VALUES(?,?,?,?,?,?)', data_out)
                    executing = True
                except sqlite3.OperationalError:
                    print('[WARNING] База данных используется...')
                    print('[WARNING] Ожидание...')
                    time.sleep(0.1)
            self.counter_bet += 1
        print('[INFO] Кол-во добавленных ставок ' + str(self.counter_bet))
        commited = False
        while not commited:
            try:
                con.commit()
                commited = True
            except sqlite3.OperationalError:
                print('[WARNING] База данных используется...')
                print('[WARNING] Ожидание...')
                time.sleep(0.2)
        end = time.time()
        time_compl = end - start
        print('[INFO]Время добавления ставок в базу %s' % str(time_compl))
        cur.close()
        con.close()

    @staticmethod
    def add_bookmaker_in_db(name: str, cur, con):
        """
        Добавление букмекера в базу данных
        :param name:
        название бк
        :param cur:
        cursor бд
        :param con:
        connect бд
        :return:
        """
        query = 'SELECT * FROM bookmaker'
        executing = False
        while not executing:
            try:
                cur.execute(query)
                executing = True
            except sqlite3.OperationalError:
                print('[WARNING] База данных используется...')
                print('[WARNING] Ожидание...')
                time.sleep(0.1)
        data_name = [name[1] for name in cur.fetchall()]
        if name in data_name:
            return
        else:
            executing = False
            while not executing:
                try:
                    cur.execute('INSERT INTO bookmaker (name) VALUES(?)', [name])
                    executing = True
                except sqlite3.OperationalError:
                    print('[WARNING] База данных используется...')
                    print('[WARNING] Ожидание...')
                    time.sleep(0.1)
            commited = False
            while not commited:
                try:
                    con.commit()
                    commited = True
                except sqlite3.OperationalError:
                    print('[WARNING] База данных используется...')
                    print('[WARNING] Ожидание...')
                    time.sleep(0.2)
            print('[INFO] Букмекер %s добавлен в базу' % name)

    def get_match_data(self, url: str):
        """
        Получения данных с игры
        :param url:
        Ссылка на игру
        :return:
        """
        print(url)
        start = time.time()
        request_odds_url = self.get_odds_response(url)
        result = self.get_result(url)
        date = self.get_date(url)
        headers = {
             'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:71.0) Gecko/20100101 Firefox/71.0',
             'referer': url
         }
        # время запроса для подключения к API
        timer_reg = str(time.time()).split('.')[0] + str(time.time()).split('.')[1][0:3]
        # итоговый запрос
        req_for_time = request_odds_url + timer_reg
        odds_response = '"E":"notAllowed"'
        print(req_for_time)
        while '"E":"notAllowed"' in odds_response:
            print(req_for_time)
            r = requests.get(req_for_time, headers=headers)
            odds_response = r.text
            if '"E":"notAllowed"' in odds_response:
                print('notAllowed')
                request_odds_url = self.get_odds_response(url)
                timer_reg = str(time.time()).split('.')[0] + str(time.time()).split('.')[1][0:3]
                req_for_time = request_odds_url + timer_reg
        if '"odds":' in odds_response:
            out_odds = self.clear_response_odds(odds_response)
            end = time.time()
            time_compl = end - start
            print('[INFO]Время получения данных из игры %s' % str(time_compl))
            return [result, out_odds, date, request_odds_url]
        return [result, {}, date, request_odds_url]

    def get_odds_response(self, url):
        """
        получение url запроса к API
        :param url:
        адрес страницы с игрой
        :return:
        """
        request_odds_url = None
        while not request_odds_url:
            print('[INFO] Получение API запроса для %s' % url)
            self.proxy.new_har('oddsportal')
            browse = False
            while not browse:
                try:
                    self.browser.get(url)
                    browse = True
                except exceptions.WebDriverException:
                    print('[INFO] Не удалось подключиться')
                    time.sleep(5)
            out = self.proxy.har
            for el in out['log']['entries']:
                if 'https://fb.oddsportal.com/feed/match/' in el['request']['url']:
                    print(el['request']['url'])
                    request_odds_url = el['request']['url'][:-13]
                    return request_odds_url

    def get_result(self, url):
        """
        Получение результата матча
        :param url:
        адрес страницы с игрой
        :return:
        """
        if url != self.browser.current_url:
            browse = False
            while not browse:
                try:
                    self.browser.get(url)
                    browse = True
                except exceptions.WebDriverException:
                    print('[INFO] Не удалось подключиться')
                    time.sleep(5)
        content_match = self.browser.page_source
        soup_liga = BS(content_match, 'html.parser')
        col_content = soup_liga.select('#col-content')
        try:
            result = col_content[0].select('p.result')[0].text
        except IndexError:
            result = 'Canceled'
        print('[INFO] ' + result)
        return result

    def get_date(self, url, full=False):
        """
        Получение даты матча
        :param status:
        :param url:
        адрес страницы с игрой
        :return:
        """
        if url != self.browser.current_url:
            browse = False
            while not browse:
                try:
                    self.browser.get(url)
                    browse = True
                except exceptions.WebDriverException:
                    print('[INFO] Не удалось подключиться')
                    time.sleep(5)
        content_match = self.browser.page_source
        soup_liga = BS(content_match, 'html.parser')
        col_content = soup_liga.select('#col-content')
        try:
            if full:
                date = col_content[0].select('p.date')[0].text
            else:
                date = col_content[0].select('p.date')[0].text.split(', ')[1]
        except IndexError:
            date = 'None'
        print('[INFO] ' + date)
        return date

    def clear_response_odds(self, odds_response, full=False):
        """
        Очистка ответа от API от ненужных данных
        :param full:
        :param odds_response:
        :return:
        """
        null = None
        true = True
        false = False
        left_cut1 = odds_response.split('globals.jsonpCallback', 1)
        right_cut1 = left_cut1[-1].rsplit(';', 1)
        full_data = [el for el in eval(right_cut1[0])]
        dict_openodds = full_data[1]['d']['oddsdata']['back']['E-1-2-0-0-0']['opening_odds']
        dict_odds = full_data[1]['d']['oddsdata']['back']['E-1-2-0-0-0']['odds']
        dict_opening_change_time = full_data[1]['d']['oddsdata']['back']['E-1-2-0-0-0']['opening_change_time']
        dict_change_time = full_data[1]['d']['oddsdata']['back']['E-1-2-0-0-0']['change_time']
        outcome_id = full_data[1]['d']['oddsdata']['back']['E-1-2-0-0-0']['OutcomeID']
        out_dict_odds = {}
        for bk_id, odds in dict_openodds.items():
            if type(odds) is list:
                for i in range(0, len(odds)):
                    if not odds[i]:
                        dict_openodds[bk_id][i] = dict_odds[bk_id][i]
                    if full:
                        if odds[i]:
                            if not self.bookmakersData[bk_id]['WebName'] in out_dict_odds:
                                out_dict_odds[self.bookmakersData[bk_id]['WebName']] = {str(i): []}
                            else:
                                out_dict_odds[self.bookmakersData[bk_id]['WebName']][str(i)] = []
                            out_dict_odds[self.bookmakersData[bk_id]['WebName']][str(i)].append([dict_odds[bk_id][i],
                                                                                                 None,
                                                                                                 dict_change_time[bk_id][i]])
            else:
                for pos, item in odds.items():
                    if not item:
                        dict_openodds[bk_id][pos] = dict_odds[bk_id][pos]
                    if full:
                        if item:
                            if not self.bookmakersData[bk_id]['WebName'] in out_dict_odds:
                                out_dict_odds[self.bookmakersData[bk_id]['WebName']] = {pos: []}
                            else:
                                out_dict_odds[self.bookmakersData[bk_id]['WebName']][pos] = []
                            out_dict_odds[self.bookmakersData[bk_id]['WebName']][pos].append([dict_odds[bk_id][pos],
                                                                                              None,
                                                                                              dict_change_time[bk_id][
                                                                                                  pos]])
        for bk_id, odd in dict_openodds.items():
            if type(odd) is list:
                odds = odd
                if bk_id in self.bookmakersData:
                    if full:
                        if not self.bookmakersData[bk_id]['WebName'] in out_dict_odds:
                            out_dict_odds[self.bookmakersData[bk_id]['WebName']] = {'open_odds': odds}
                        else:
                            out_dict_odds[self.bookmakersData[bk_id]['WebName']]['open_odds'] = odds
                    else:
                        out_dict_odds[self.bookmakersData[bk_id]['WebName']] = odds
            else:
                odds = [None, None, None]
                if bk_id in self.bookmakersData:
                    for pos, item in odd.items():
                        if pos == '0':
                            odds[0] = item
                        elif pos == '1':
                            odds[1] = item
                        elif pos == '2':
                            odds[2] = item
                    if full:
                        if not self.bookmakersData[bk_id]['WebName'] in out_dict_odds:
                            out_dict_odds[self.bookmakersData[bk_id]['WebName']] = {'open_odds': odds}
                        else:
                            out_dict_odds[self.bookmakersData[bk_id]['WebName']]['open_odds'] = odds
                    else:
                        out_dict_odds[self.bookmakersData[bk_id]['WebName']] = odds
        for bk_id, change_time in dict_opening_change_time.items():
            if type(change_time) is list:
                openning_change_times = change_time
                if bk_id in self.bookmakersData:
                    if openning_change_times[0]:
                        out_dict_odds[self.bookmakersData[bk_id]['WebName']].append(openning_change_times[0])
                    else:
                        out_dict_odds[self.bookmakersData[bk_id]['WebName']].append(dict_change_time[bk_id][0])
            else:
                openning_change_times = [None, None, None]
                if bk_id in self.bookmakersData:
                    for pos, item in change_time.items():
                        if pos == '0':
                            if item:
                                openning_change_times[0] = item
                            else:
                                openning_change_times[0] = dict_change_time[bk_id]['0']
                        elif pos == '1':
                            if item:
                                openning_change_times[1] = item
                            else:
                                openning_change_times[1] = dict_change_time[bk_id]['1']
                        elif pos == '2':
                            if item:
                                openning_change_times[2] = item
                            else:
                                openning_change_times[2] = dict_change_time[bk_id]['2']
                    if not openning_change_times[0]:
                        print('проверка времени', change_time)
                    out_dict_odds[self.bookmakersData[bk_id]['WebName']].append(openning_change_times[0])
        if not full:
            print('[INFO] Кол-во букмеккеров в игре ' + str(len(out_dict_odds)))
            print('[INFO] Коэ-ты:')
            print(out_dict_odds)
        else:
            print(out_dict_odds)
        return out_dict_odds

    def run(self):
        try:
            self.pars()
        except Exception as ex:
            print(ex)
            print(traceback.format_exc())


def main():
    try:
        app = QtWidgets.QApplication(sys.argv)
        window = MultiParsing()
        window.show()
        app.exec_()
    except Exception as ex:
        print(ex)


if __name__ == '__main__':
    try:
        main()
    except Exception as ex:
        print(ex)



