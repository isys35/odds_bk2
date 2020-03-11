import requests
from bs4 import BeautifulSoup as BS
import async_request
import re
import sys
import json
from urllib.parse import unquote
import time
from aiohttp.client_exceptions import ClientConnectorError
from requests.exceptions import ConnectionError


class Parser:
    def __init__(self):
        self.db = 'soccer.db'
        self.soccer_url = 'https://www.oddsportal.com/results/#soccer'
        self.main_url = 'https://www.oddsportal.com'
        self.async_count = 20
        self.main_header = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:71.0) Gecko/20100101 Firefox/71.0'
        }
        self.out_match_data = {}
        self.bookmakersData = self.get_bookmakersdata()
        self.start_time = time.time()
        self.count_match = 0

    @staticmethod
    def get_bookmakersdata():
        with open("bookmakersData.json", "r") as read_file:
            return json.load(read_file)

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
        time.sleep(1)
        headers = self.get_headers(urls_ref)
        urls = [url + (str(int(time.time()*1000))) for url in urls]
        try:
            responses = async_request.input_reuqests(urls, headers)
        except Exception:
            return []
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
        return games_urls, command1_list, command2_list, timematch_list, date_list

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
        col_content = soup.select('#col-content')
        try:
            result = col_content[0].select('p.result')[0].text
        except IndexError:
            result = 'Canceled'
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
        return url_out, result

    def update_first_data(self, response):
        soup_champ = BS(response, 'lxml')
        string_sport = soup_champ.select('#breadcrumb')[0].select('a')[1].text
        self.out_match_data['sport'] = string_sport
        country = soup_champ.select('#breadcrumb')[0].select('a')[2].text
        self.out_match_data['country'] = country
        string_champ = soup_champ.select('#breadcrumb')[0].select('a')[3].text
        self.out_match_data['champ'] = string_champ


    def clear_response_odds(self, odds_response):
        print(odds_response)
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
        print(full_data[1]['d'])
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

            else:
                for pos, item in odds.items():
                    if not item:
                        dict_openodds[bk_id][pos] = dict_odds[bk_id][pos]
        for bk_id, odd in dict_openodds.items():
            if type(odd) is list:
                odds = odd
                if bk_id in self.bookmakersData:
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
        return out_dict_odds

    def start(self):
        urls = parser.get_hrefs_champs_soccer()
        self.start_time = time.time()
        self.count_match = 0
        self.parsing(urls)

    def parsing(self, urls):
        prepared_urls = self.prepare_url(urls)

        for urls in prepared_urls:
            responses_champ = self.get_responses(urls)
            self.out_match_data = {}
            for response in responses_champ:
                self.update_first_data(response)

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
                        games_url, command1_list, command2_list, timematch_list, date_list = self.get_games(
                            response_match,
                            years_ids[responses_pages.index(response_page)],
                            responses_matchs.index(response_match) + 1)
                        prepared_games_url = self.prepare_url(games_url)
                        prepared_timematch_list = self.prepare_url(timematch_list)
                        prepared_command1_list = self.prepare_url(command1_list)
                        prepared_command2_list = self.prepare_url(command2_list)
                        prepared_date_list = self.prepare_url(date_list)
                        for i in range(0,len(prepared_games_url)):
                            responses_for_odds_request = self.get_response_for_odds_request(prepared_games_url[i],
                                                                                            years_urls[
                                                                                                responses_pages.index(
                                                                                                    response_page)])
                            odds_requests_url, result_list = self.odds_requests_url_and_result(responses_for_odds_request)
                            responses_odds = []
                            while not responses_odds:
                                responses_odds = self.get_response_odds(odds_requests_url, games_url)
                                if not responses_odds:
                                    odds_requests_url, result_list = self.odds_requests_url_and_result(
                                        responses_for_odds_request)
                                    continue
                                for recsonse_o in responses_odds:
                                    if "'E': 'notAllowed'" in recsonse_o:
                                        odds_requests_url, result_list = self.odds_requests_url_and_result(
                                            responses_for_odds_request)
                                        responses_odds = []
                                        continue
                            for game_resp in responses_odds:
                                self.out_match_data['time'] = prepared_timematch_list[i][responses_odds.index(game_resp)]
                                self.out_match_data['url'] = prepared_games_url[i][responses_odds.index(game_resp)]
                                self.out_match_data['command1'] = prepared_command1_list[i][responses_odds.index(game_resp)]
                                self.out_match_data['command2'] = prepared_command2_list[i][responses_odds.index(game_resp)]
                                self.out_match_data['result'] = result_list[responses_odds.index(game_resp)]
                                self.out_match_data['odds'] = self.clear_response_odds(game_resp)
                                self.out_match_data['date'] = prepared_date_list[i][responses_odds.index(game_resp)]
                                self.out_match_data['req_api'] = None
                                print(f"[INFO] {self.out_match_data['country']}  {self.out_match_data['champ']} "
                                    f" {self.out_match_data['command1']} {self.out_match_data['command2']} " )
                                print(self.out_match_data['url'])
                                self.count_match += 1
                            print(f'[INFO] Прошло {time.time() - self.start_time} секунд')
                            print(f'[INFO] Добавлено {self.count_match} матчей')

    def odds_requests_url_and_result(self, responses_for_odds_request):
        odds_requests_url = []
        result_list = []
        for response_for_odds_request in responses_for_odds_request:
            request_url, result = self.get_request_url_odds(response_for_odds_request)
            odds_requests_url.append(request_url)
            result_list.append(result)
        return odds_requests_url,result_list




if __name__ == '__main__':
    parser = Parser()
    try:
        parser.start()
    except ClientConnectorError:
        print('[WARNING] Проблема с соединением')
        parser.start()
    except ConnectionError:
        print('[WARNING] Проблема с соединением')
        parser.start()


