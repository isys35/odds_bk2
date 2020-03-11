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
        self.async_count = 10
        self.main_header = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:71.0) Gecko/20100101 Firefox/71.0'
        }

    def get_hrefs_champs_soccer(self):
        r = requests.get(self.soccer_url, headers=self.main_header)
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

    def prepare_url(self, urls):
        prepared_urls = []
        while urls:
            if len(urls) > self.async_count:
                interact_list = []
                for i in range(self.async_count):
                    interact_list.append(urls.pop(0))
                prepared_urls.append(interact_list)
            else:
                prepared_urls.append(urls)
                urls = []
        return prepared_urls

    def get_headers(self, urls):
        headers = []
        for url in urls:
            header = self.main_header
            header['Referer'] = url
            headers.append(header)
        return headers

    def get_years_responses(self, urls):
        headers = self.get_headers(urls)
        responses = async_request.input_reuqests(urls, headers)
        return responses

    def get_years_urls(self, response):
        soup = BS(response, 'lxml')
        main_menu = soup.select_one('.main-menu2.main-menu-gray')
        try:
            years_href = [a['href'] for a in main_menu.select('a')]
        except AttributeError:
            print('page not found')
            return
        years_urls = self.href_to_url(years_href)
        print(years_urls)
        return years_urls



if __name__ == '__main__':
    parser = Parser()
    urls = parser.get_hrefs_champs_soccer()
    prepared_urls = parser.prepare_url(urls)
    print(len(prepared_urls))
    for urls in prepared_urls:
        responses = parser.get_years_responses(urls)
        for response in responses:
            years_urls = parser.get_years_urls(response)