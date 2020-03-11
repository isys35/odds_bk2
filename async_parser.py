import requests
from bs4 import BeautifulSoup as BS
import async_request
import re
import sys
import json
from urllib.parse import unquote
import time


class Parser:
    def __init__(self):
        self.db = 'soccer.db'
        self.soccer_url = 'https://www.oddsportal.com/results/#soccer'
        self.main_url = 'https://www.oddsportal.com'

    def get_hrefs_champs_soccer(self):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:71.0) Gecko/20100101 Firefox/71.0'
        }
        r = requests.get(self.soccer_url, headers=headers)
        html = BS(r.content, 'html.parser')
        championships = html.select('table.table-main.sport')[0].select('td')
        # список с ссылками на все чемпионаты
        href_championships = [championship.select('a')[0]['href'] for championship in championships
                              if len(championship.select('a')) > 0]
        href_championships_soccer = [href for href in href_championships if href.split('/')[1] == 'soccer']
        urls_soccer = self.href_to_url(href_championships_soccer)
        return urls_soccer

    def href_to_url(self, hrefs):
        urls = [self.main_url + href for href in hrefs]
        return urls




if __name__ == '__main__':
    parser = Parser()
    hrefs = parser.get_hrefs_champs_soccer()
    print(hrefs)