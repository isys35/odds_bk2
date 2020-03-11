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
        self.out_match_data = {}

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

    def get_year_response_for_page(self, id, url_ref, p):
        urls = [f'https://fb.oddsportal.com/ajax-sport-country-tournament-archive/1/{id}/X0/1/2/{pi+1}/?_=' \
                    f'{int(time.time() * 1000)}' for pi in range(p)]
        urls_ref = [url_ref for _ in range(p)]
        headers = self.get_headers(urls_ref)
        responses = async_request.input_reuqests(urls, headers)
        return responses

    def get_response_for_odds_request(self, urls, url_ref):
        urls_ref = [url_ref for _ in range(len(urls))]
        headers = self.get_headers(urls_ref)
        responses = async_request.input_reuqests(urls, headers)
        return responses

    def get_response_odds(self, urls, urls_ref):
        headers = self.get_headers(urls_ref)
        urls = [url + (str(int(time.time()*1000))) for url in urls]
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

    def get_games(self, response, id, p):
        resp_json_text = \
            response.replace(f"globals.jsonpCallback('/ajax-sport-country-tournament-archive/1/{id}/X0/1/2/{p}/', ",
                              '').rsplit(
                ');', maxsplit=1)[0]
        json_resp = json.loads(resp_json_text)
        soup = BS(str(json_resp['d']['html']), 'lxml')
        names = soup.select('.name.table-participant')
        command1_list = [c1.text.split(' - ')[0] for c1 in names]
        command2_list = [c2.text.split(' - ')[1] for c2 in names]
        timematch_list =[t['class'][-1].split('-')[0].replace('t','') for t in soup.select('.table-time')]
        timematch_list, date_list = self.reformat_timelist(timematch_list)
        hrefs = [name.select_one('a')['href'] for name in names]
        games_urls = self.href_to_url(hrefs)
        return games_urls, timematch_list, command1_list, command2_list, timematch_list, date_list

    def reformat_timelist(self, timelist):
        timematch_list = []
        date_list = []
        for t in timelist:
            timematch = time.strftime("%H:%M", time.localtime(float(t)))
            timematch_list.append(timematch)
            date = time.strftime("%d %b %Y", time.localtime(float(t)))
            date_list.append(date)
        return timematch_list,date_list

    def get_request_url_odds(self, response):
        soup = BS(response, 'html.parser')
        script = soup.select_one('script:contains("new OpHandler")').text
        json_text = re.search('PageEvent\((.*?)\);', script)
        if not json_text:
            print('script not found')
            sys.exit()
        try:
            json_data = json.loads(json_text.group(1))
        except ValueError:
            print('json not parsed')
            sys.exit()
        id1 = json_data.get('id')
        id2 = unquote(json_data.get('xhash'))
        url_out = 'https://fb.oddsportal.com/feed/match/1-1-{}-1-2-{}.dat?_='.format(id1, id2)
        return url_out

    def update_first_data(self, response):
        soup_champ = BS(response, 'lxml')
        string_sport = soup_champ.select('#breadcrumb')[0].select('a')[1].text
        self.out_match_data['sport'] = string_sport
        country = soup_champ.select('#breadcrumb')[0].select('a')[2].text
        self.out_match_data['country'] = country
        string_champ = soup_champ.select('#breadcrumb')[0].select('a')[3].text
        self.out_match_data['champ'] = string_champ
        print('[INFO] Страна ' + country)
        print('[INFO] Чемпионат ' + string_champ)

    def start(self):
        urls = parser.get_hrefs_champs_soccer()
        self.parsing(urls)

    def parsing(self, urls):
        prepared_urls = self.prepare_url(urls)
        print(len(prepared_urls))
        for urls in prepared_urls:
            responses_champ = self.get_responses(urls)
            self.out_match_data = {}
            for response in responses_champ:
                self.update_first_data(response)
                print(self.out_match_data)
                years_urls = self.get_years_urls(response)
                responses_years = self.get_responses(years_urls)
                years_ids = []
                for response_year in responses_years:
                    year_id = self.get_ajax_year_id(response_year)
                    years_ids.append(year_id)
                responses_pages = self.get_year_response(years_ids, years_urls, 1)
                # тут можно ускорить
                for response_page in responses_pages:
                    pages = self.get_pages(response_page, years_ids[responses_pages.index(response_page)])
                    responses_matchs = self.get_year_response_for_page(
                        years_ids[responses_pages.index(response_page)],
                        years_urls[responses_pages.index(response_page)],
                        pages)
                    for response_match in responses_matchs:
                        games_url, timematch_list, command1_list, command2_list, timematch_list, date_list = self.get_games(
                            response_match,
                            years_ids[responses_pages.index(response_page)],
                            responses_matchs.index(response_match) + 1)
                        print(len(games_url))
                        responses_for_odds_request = self.get_response_for_odds_request(games_url,
                                                                                          years_urls[
                                                                                              responses_pages.index(
                                                                                                  response_page)])
                        odds_requests_url = []
                        for response_for_odds_request in responses_for_odds_request:
                            request_url = self.get_request_url_odds(response_for_odds_request)
                            odds_requests_url.append(request_url)
                        responses_odds = self.get_response_odds(odds_requests_url, games_url)
                        print(len(responses_odds))

if __name__ == '__main__':
    parser = Parser()
    parser.start()



