#!/usr/bin/python3
# -*- coding: utf-8 -*-
import traceback
import sys
from PyQt5 import QtGui, QtWidgets
from PyQt5.QtCore import QThread, Qt
from browsermobproxy import Server
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
        self.pushButton_2.clicked.connect(self.start_multi_parsing)

    def update_counter_game(self):
        print('[INFO] Подключение к базе')
        con = sqlite3.connect(self.db)
        cur = con.cursor()
        query = 'SELECT COUNT(*) FROM game'
        cur.execute(query)
        all_game_count = cur.fetchone()
        self.label_41.setText('Количество игр в базе: ' + str(all_game_count[0]))
        cur.close()
        con.close()
        print('[INFO] Подключение к базе успешно')

    def start_multi_parsing(self):
        self.managepars = ManagerPars()
        self.managepars.start()


class ManagerPars(QThread):
    def __init__(self):
        super().__init__()
        self.hrefs_pars = []
        #self.parser_statuses = [False for i in range(0, 10)]
        self.soccer_url = 'https://www.oddsportal.com/results/#soccer'
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:71.0) Gecko/20100101 Firefox/71.0'
        }
        self.parsers = [ParserThread() for _ in range(0, 10)]

    def pars(self):
        soccer_url = 'https://www.oddsportal.com/results/#soccer'
        r = requests.get(soccer_url, headers=self.headers)
        html = BS(r.content, 'html.parser')
        championships = html.select('table.table-main.sport')[0].select('td')
        # список с ссылками на все чемпионаты
        href_championships = [championship.select('a')[0]['href'] for championship in championships
                              if len(championship.select('a')) > 0]
        href_championships_soccer = [href for href in href_championships if href.split('/')[1] == 'soccer']
        for href in href_championships_soccer:
            if href not in self.hrefs_pars:
                self.hrefs_pars.append(href)
            while not False in [self.parsers[i].status for i in range(0, 10)]:
                time.sleep(.2)
                print('.......')
            for i in range(0, 10):
                if not self.parsers[i].status:
                    time.sleep(.2)
                    self.parsers[i].href = href
                    self.parsers[i].start()
                    break

    def run(self):
        self.pars()


class ParserThread(QThread):
    def __init__(self):
        super().__init__()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:71.0) Gecko/20100101 Firefox/71.0'
        }
        self.status = False
        self.main_page = 'https://www.oddsportal.com'
        self.href = ''
        self.browser = None

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
        self.proxy = self.server.create_proxy()
        profile = webdriver.FirefoxProfile()
        profile.set_proxy(self.proxy.selenium_proxy())
        self.browser = webdriver.Firefox(firefox_profile=profile, options=options)

    def pars(self):
        if not self.browser:
            self.browser_start()
        # self.status = True
        # print(self.href)
        # print('Парсинг')
        # champ_request_allyears = requests.get(self.main_page + self.href, headers=self.headers)
        # html_championship = BS(champ_request_allyears.content, 'html.parser')
        # years_menu = html_championship.select('.main-menu2.main-menu-gray')
        # if years_menu:
        #     years_pages = years_menu[0].select('a')
        #     first_page = years_pages[0]['href']



    def run(self):
        try:
            self.pars()
        except Exception as ex:
            print(ex)


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



