import requests
from bs4 import BeautifulSoup as BS
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from browsermobproxy import Server
from selenium.common.exceptions import TimeoutException
import time
import traceback
import sqlite3
import json


class Parser:
    def __init__(self, label_info=None, label_info2=None, label_info3=None):
        self.label_info = label_info
        self.label_info2 = label_info2
        self.label_info3 = label_info3
        self.counter_bet = 0
        self.counter_game = 0
        self.db = 'oddsportal.db'
        self.main_page = 'https://www.oddsportal.com'
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:71.0) Gecko/20100101 Firefox/71.0'
        }
        self.bookmakersData = self.get_bookmakersdata()
        self.server = None
        self.browser = None

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
        self.server = Server(path=r"browsermob-proxy-2.1.4\bin\browsermob-proxy.bat",
                             options={'existing_proxy_port_to_use': 8090})
        self.server.start()
        try:
            proxy = self.server.create_proxy()
        except Exception:
            print('[WARNING] Сервер уже запущен')
            proxy = self.server.create_proxy()
        profile = webdriver.FirefoxProfile()
        profile.set_proxy(proxy.selenium_proxy())
        self.browser = webdriver.Firefox(firefox_profile=profile, options=options)

    def start(self, sport):
        """
        Получение тегов чемпионата
        Запуск парсера
        self.pars
        """
        if not self.browser:
            self.browser_start()
        soccer_url = 'https://www.oddsportal.com/results/#soccer'
        r = requests.get(soccer_url, headers=self.headers)
        html = BS(r.content, 'html.parser')
        championships = html.select('table.table-main.sport')[0].select('td')
        # список с ссылками на все чемпионаты
        href_championships = [championship.select('a')[0]['href'] for championship in championships
                              if len(championship.select('a')) > 0]
        for href_championship in href_championships:
            self.pars(href_championship, sport)
        if self.browser:
            self.server.stop()
            self.browser.quit()

    def pars(self, href_champ, sport):
        """
        Парсинг
        :param championship:
        список тегов чемпионатов
        :return:
        """
        with open('savepoint', 'w', encoding='utf8') as savepointfile:  # сохранение чемпионата
            savepointfile.write(str(href_champ))
        years_menu = None
        if sport == 'soccer':
            if href_champ.split('/')[1] == sport:
                champ_request_allyears = requests.get(self.main_page + href_champ, headers=self.headers)
                html_championship = BS(champ_request_allyears.content, 'html.parser')
                years_menu = html_championship.select('.main-menu2.main-menu-gray')
        year_page_reversed = []
        string_sport = None
        country = None
        string_champ = None
        if years_menu:
            years_pages = years_menu[0].select('a')
            first_page = years_pages[0]['href']
            self.browser.get(self.main_page + first_page)
            content_first_page = self.browser.page_source
            soup_champ = BS(content_first_page, 'html.parser')
            string_sport = soup_champ.select('#breadcrumb')[0].select('a')[1].text
            country = soup_champ.select('#breadcrumb')[0].select('a')[2].text
            string_champ = soup_champ.select('#breadcrumb')[0].select('a')[3].text
            print('[INFO] Страна ' + country)
            print('[INFO] Чемпионат ' + string_champ)
            if self.check_champ_in_db(self.main_page + first_page):
                print('[INFO] Чемпионат полностью в базе')
                return
            print('[INFO] Чемпионат не полностью в базе')
            year_page_reversed = years_pages
            year_page_reversed.reverse()
        if year_page_reversed:
            for page in year_page_reversed:
                year_page = self.main_page + page['href']
                print('[INFO] Страница с годом ' + page.text + ' ' + year_page)
                if self.check_champ_in_db(year_page):
                    print('[INFO] Год полностью есть в базе')
                    continue
                print('[INFO] Год не полностью в базе')
                if year_page != self.browser.current_url:
                    self.browser.get(year_page)
                soup_pagination = BS(self.browser.page_source, 'html.parser')
                pagination = soup_pagination.select('#pagination')
                if not pagination:
                    self.get_champ_data_in_year(year_page)
                else:
                    max_page = pagination[0].select('a')[-1]['x-page']
                    p = int(max_page)
                    while p != 1:
                        print('[INFO]Страница ' + str(p))
                        year_page_add = self.main_page + page['href'] +\
                                        '#/page/%s/' % str(p)
                        if self.check_champ_in_db(year_page_add):
                            p -= 1
                            continue
                        self.get_champ_data_in_year(year_page_add, p)
                        p -= 1
                    self.get_champ_data_in_year(year_page)

    def check_champ_in_db(self, champ_url):
        """
        Проверка: закончен ли парсинг чемпионата
        :return:
        bool
        """
        if not self.browser:
            self.browser_start()
        if champ_url != self.browser.current_url:
            self.browser.get(champ_url)
        content_browser = self.browser.page_source
        soup_champ = BS(content_browser, 'html.parser')
        trs = soup_champ.select('#tournamentTable')[0].select('tr')
        if trs[0].select('.cms'):
            print('[INFO] No data available')
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
        query = 'SELECT url FROM game'
        cur.execute(query)
        data_game = [game[0] for game in cur.fetchall()]
        for game in data_game:
            if url == game:
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
        :param url:
            адрес страницы
        :param args:
            если страница имеет много подстраниц,
             args[0] - номер этой страницы
        :return:
        """
        print(url)
        if not self.browser:
            self.browser_start()
        if url != self.browser.current_url:
            self.browser.get(self.main_page)
            self.browser.get(url)
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
            while active_page != args[0]:
                print('[INFO] проверка правильности страницы')
                content_browser = self.browser.page_source
                soup_champ = BS(content_browser, 'html.parser')
                active_page = int(soup_champ.select('#pagination')[0].select('span.active-page')[0].text)
            print('[INFO] Страница верная')
        matches = []
        for tr in trs:
            if 'deactivate' in tr['class']:
                if len(tr.select('span.live-odds-ico-prev')) == 0:
                    timematch = tr.select('td.table-time')[0].text
                    match_url = self.main_page + tr.select('a')[0]['href']
                    game_name = tr.select('a')[0].text
                    command1 = game_name.split(' - ')[0]
                    command2 = game_name.split(' - ')[1]
                    result, odds, time = self.get_match_data(match_url)

        # for tr in trs:
        #     try:
        #         if tr['class'] == ['center', 'nob-border']:
        #             date = tr.select('span')[0].text
        #         elif 'deactivate' in tr['class']:
        #             if len(tr.select('span.live-odds-ico-prev')) == 0:
        #                 timematch = tr.select('td.table-time')[0].text
        #                 match_url = 'https://www.oddsportal.com' + tr.select('a')[0]['href']
        #                 game_name = tr.select('a')[0].text
        #                 command1 = game_name.split(' - ')[0]
        #                 command2 = game_name.split(' - ')[1]
        #                 # check_list = [command1, command2, match_url, date, timematch, sport, country, liga]
        #                 if self.check_game_in_db(match_url):
        #                     continue
        #                 else:
        #                     try:
        #                         match_data = self.get_match_data(match_url)
        #                     except Exception:
        #                         print(traceback.format_exc())
        #                     out_match = [command1,
        #                                  command2,
        #                                  match_url,
        #                                  date,
        #                                  timematch,
        #                                  match_data[0],
        #                                  sport,
        #                                  country,
        #                                  liga]
        #                     if 'Canceled' != match_data[0] and 'awarded' not in match_data[0]:
        #                         self.add_game_in_db(out_match)
        #                         self.add_bet_in_db(match_data[1], out_match)
        #     except KeyError:
        #         print('[WARNING] Not odds')

    def continue_parsing(self):
        if not self.browser:
            self.browser_start()
        savepointfile = open('savepoint', 'r', encoding='utf8')
        liga_str = savepointfile.read()
        savepointfile.close()
        soccer_url = 'https://www.oddsportal.com/results/#soccer'
        r = requests.get(soccer_url, headers=self.headers)
        html = BS(r.content, 'html.parser')
        body = html.select('table.table-main.sport')
        ligs = body[0].select('td')
        ligs_str = [str(liga) for liga in ligs]
        if liga_str in ligs_str:
            liga_index = ligs_str.index(liga_str)
            for lig in ligs[liga_index:]:
                self.pars(lig)
        else:
            print('[INFO] Сохранение не найдено')
        if self.browser:
            self.server.stop()
            self.browser.quit()

    def last_year_pars(self):
        if not self.browser:
            self.browser_start()
        soccer_url = 'https://www.oddsportal.com/results/#soccer'
        r = requests.get(soccer_url, headers=self.headers)
        html = BS(r.content, 'html.parser')
        body = html.select('table.table-main.sport')
        ligs = body[0].select('td')
        for lig in ligs:
            self.pars_last_year(lig)
        self.server.stop()
        self.browser.quit()

    def pars_last_year(self, lig):
        if len(lig.select('a')) > 0:
            href_liga = lig.select('a')[0]['href']
            if href_liga.split('/')[1] == 'soccer':
                liga_request_allyears = requests.get('https://www.oddsportal.com' + href_liga, headers=self.headers)
                soup_liga = BS(liga_request_allyears.content, 'html.parser')
                years_menu = soup_liga.select('.main-menu2.main-menu-gray')
                if years_menu:
                    years_pages = years_menu[0].select('a')
                    self.browser.get('https://www.oddsportal.com' + years_pages[0]['href'])
                    content_browser = self.browser.page_source
                    soup_liga = BS(content_browser, 'html.parser')
                    breadcrump = soup_liga.select('#breadcrumb')
                    breadcrump_a = breadcrump[0].select('a')
                    sport = breadcrump_a[1].text
                    country = breadcrump_a[2].text
                    liga = breadcrump_a[3].text
                    print('[INFO] Страна ' + country)
                    print('[INFO] Чемпионат ' + liga)
                    first_year_page = 'https://www.oddsportal.com' + years_pages[0]['href']
                    if self.check_champ_in_db(first_year_page):
                        print('[INFO] Чемпионат есть в базе')
                        return
                    print('[INFO] Страница с годом ' + first_year_page)
                    page_pagination = BS(self.browser.page_source, 'html.parser')
                    pagination = page_pagination.select('#pagination')
                    try:
                        if len(pagination) == 0:
                            self.get_liga_data_in_year(first_year_page, sport, country, liga)
                        else:
                            max_page = pagination[0].select('a')[-1]['x-page']
                            p = int(max_page)
                            while p != 1:
                                print('[INFO]Страница ' + str(p))
                                year_page_add = 'https://www.oddsportal.com' + years_pages[0][
                                    'href'] + '#/page/%s/' % str(p)
                                self.get_liga_data_in_year(year_page_add, sport, country, liga)
                                p -= 1
                            self.get_liga_data_in_year(first_year_page, sport, country, liga)
                    except TimeoutException:
                        print('[EROR] TimeoutException')

    def restart_browser(self):
        print('[INFO] Перезапуск драйвера')
        self.browser.close()
        self.proxy.close()
        self.options = Options()
        self.options.headless = False
        self.proxy = self.server.create_proxy()
        self.profile = webdriver.FirefoxProfile()
        self.profile.set_proxy(self.proxy.selenium_proxy())
        self.browser = webdriver.Firefox(firefox_profile=self.profile, options=self.options)

    def get_odds_response(self, url):
        request_odds_url = None
        if self.counter_game % 100 == 0:
            self.restart_browser()
        while not request_odds_url:
            print('[INFO] Получение API запроса для %s' % url)
            print('поиск ошибки0')
            try:
                self.proxy.new_har("oddsportal")
                print('поиск ошибки1')
                self.browser.get(url)
            except Exception:
                print('ОШИИИИИИИИИИИИИИИИИИИИИИИИББББББКААААААААААА 222222222222222222222222222222')
                print(traceback.format_exc())
            print('поиск ошибки2')
            out = self.proxy.har
            print('поиск ошибки3')
            for el in out['log']['entries']:
                if 'https://fb.oddsportal.com/feed/match/' in el['request']['url']:
                    print(el['request']['url'])
                    request_odds_url = el['request']['url'][:-13]
                    return request_odds_url



    def add_game_in_db(self, data_parsing: list):
        con = sqlite3.connect(self.db)
        cur = con.cursor()
        cur.execute('INSERT INTO game (command1,command2,url,date,timematch,'
                    'result,sport,country,liga) '
                    'VALUES(?,?,?,?,?,?,?,?,?)', data_parsing)
        con.commit()
        print('[INFO] игра %s добавлена в базу' % str(data_parsing[0:2]))
        self.counter_game += 1
        self.label_info2.setText('Добавлено игр: ' + str(self.counter_game))
        self.update_label3()
        cur.close()
        con.close()

    def update_label3(self):
        con = sqlite3.connect(self.db)
        cur = con.cursor()
        query = 'SELECT * FROM game'
        cur.execute(query)
        all_game_count = len(cur.fetchall())
        self.label_info3.setText('Всего игр в базе: ' + str(all_game_count))
        cur.close()
        con.close()

    def add_bet_in_db(self, bets_dict: dict, data_parsing: list):
        print('[INFO] add bets in db.....')
        start = time.time()
        con = sqlite3.connect(self.db)
        cur = con.cursor()
        query = 'SELECT id,command1,command2,url,date,timematch,result,sport,country,liga FROM game'
        cur.execute(query)
        data_game_dict = {}
        for game in cur.fetchall():
            data_game_dict[game[0]] = [el for el in game[1:]]
        key_game = None
        for key, item in data_game_dict.items():
            if item == data_parsing:
                key_game = key
                break
        for key, item in bets_dict.items():
            self.add_bookmaker_in_db(key, cur, con)
            key_bookmaker = None
            query = 'SELECT * FROM bookmaker'
            cur.execute(query)
            data_bookmakers = [[el for el in bookmaker] for bookmaker in cur.fetchall()]
            for bookmaker in data_bookmakers:
                if bookmaker[1] == key:
                    key_bookmaker = bookmaker[0]
                    break
            data_out = []
            if len(item) == 3:
                data_out = [key_bookmaker, item[0], item[1], item[2], key_game]
            elif len(item) == 2:
                data_out = [key_bookmaker, item[0], 0, item[1], key_game]
            cur.execute('INSERT INTO bet (bookmaker_id,p1,x,p2,game_id) VALUES(?,?,?,?,?)', data_out)
            self.counter_bet += 1
        self.label_info.setText('Добавлено коэф.: ' + str(self.counter_bet))
        # print('[INFO] Ставка добавлена в базу')
        con.commit()
        end = time.time()
        time_compl = end - start
        print('[INFO]Время добавления ставок в базу %s' % str(time_compl))
        cur.close()
        con.close()

    def add_bookmaker_in_db(self, name: str, cur, con):
        query = 'SELECT * FROM bookmaker'
        cur.execute(query)
        data_name = [name[1] for name in cur.fetchall()]
        if name in data_name:
            # print('[INFO] %s букмекер уже есть в базе' % name)
            return
        else:
            cur.execute('INSERT INTO bookmaker (name) VALUES(?)', [name])
            con.commit()
            print('[INFO] Букмекер %s добавлен в базу' % name)


parser = Parser()
#parser.get_champ_data_in_year('https://www.oddsportal.com/soccer/argentina/superliga/results/#/page/4/', 4)
parser.start('soccer')