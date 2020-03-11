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

    def get_responses(self, urls):
        headers = self.get_headers(urls)
        responses = async_request.input_reuqests(urls, headers)
        return responses

    def get_year_response(self, ids, urls_ref, p):
        urls = [f'https://fb.oddsportal.com/ajax-sport-country-tournament-archive/1/{id}/X0/1/2/{p}/?_={int(time.time() * 1000)}' for id in ids]
        headers = self.get_headers(urls_ref)
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

    def get_ajax_year_id(self, response):
        soup = BS(response, 'html.parser')
        try:
            script = soup.select_one('script:contains("new OpHandler")').text
        except AttributeError:
            print('Page not found')
            return
        json_text = re.search('PageTournament\((.*?)\);', script)
        if not json_text:
            print('script not found')
            sys.exit()
        try:
            json_data = json.loads(json_text.group(1))
        except ValueError:
            print('json not parsed')
            sys.exit()
        id = json_data.get('id')
        return id

    def get_pages(self, response, id):
        resp_json_text = \
        response.replace(f"globals.jsonpCallback('/ajax-sport-country-tournament-archive/1/{id}/X0/1/2/1/', ",
                          '').rsplit(');', maxsplit=1)[0]
        json_resp = json.loads(resp_json_text)
        soup = BS(str(json_resp['d']['html']), 'lxml')
        # with open('page.html', 'w', encoding='utf8') as html_file:
        #     html_file.write(str(soup))
        pagination = soup.select_one('#pagination')
        if not pagination:
            return 1
        else:
            page = int(pagination.select('a')[-1]['x-page'])
            return page


if __name__ == '__main__':
    parser = Parser()
    urls = parser.get_hrefs_champs_soccer()
    prepared_urls = parser.prepare_url(urls)
    print(len(prepared_urls))
    for urls in prepared_urls:
        responses_champ = parser.get_responses(urls)
        for response in responses_champ:
            years_urls = parser.get_years_urls(response)
            responses_years = parser.get_responses(years_urls)
            years_ids = []
            for response_year in responses_years:
                year_id = parser.get_ajax_year_id(response_year)
                years_ids.append(year_id)
            responses_pages = parser.get_year_response(years_ids, years_urls, 1)
            # тут можно ускорить
            for response_page in responses_pages:
                pages = parser.get_pages(response_page,years_ids[responses_pages.index(response_page)])
                print(pages)


