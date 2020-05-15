import requests
from bs4 import BeautifulSoup
import re
import sys
import json
from urllib.parse import unquote
import time


def save_file(page: str, file_name: str):
    with open(file_name, 'w', encoding='utf8') as file:
        file.write(page)


class Grabber:
    MAIN_URL = 'https://www.oddsportal.com'
    HEADERS = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:76.0) Gecko/20100101 Firefox/76.0'
        }
    SPORTS_ID = {
        1: 'Soccer',
        2: 'Tennis',
        3: 'Basketball',
        4: 'Hockey',
        5: 'American Football',
        6: 'Baseball',
        7: 'Handball',
        8: 'Rugby Union',
        9: 'Floorball',
        10: 'Bandy',
        11: 'Futsal',
        12: 'Volleyball',
        13: 'Cricket',
        14: 'Darts',
        15: 'Snooker',
        16: 'Boxing',
        17: 'Beach Volleyball',
        18: 'Aussie Rules',
        19: 'Rugby League',
        21: 'Badminton',
        22: 'Water polo',
        26: 'Beach Soccer',
        28: 'MMA',
        30: 'Pesäpallo',
        36: 'eSports',
    }
    E = {
        1: [1, 2],
        2: [3, 2],
        3: [3, 1],
        4: [1, 2],
        5: [3, 1],
        6: [3, 1],
        7: [1, 2],
        8: [1, 2],
        9: [1, 2],
        10: [1, 2],
        11: [1, 2],
        12: [3, 2],
        13: [3, 1],
        14: [3, 2],
        15: [3, 2],
        16: [1, 2],
        17: [3, 2],
        18: [3, 1],
        19: [1, 2],
        21: [3, 2],
        22: [1, 2],
        26: [1, 2],
        28: [3, 2],
        30: [1, 2],
        36: [3, 2],
    }

    def __init__(self):
        self.bookmakers = {}
        self.load_bookmakers()

    def update_champs_id(self):
        url = self.MAIN_URL + '/results/'
        resp = requests.get(url, headers=self.HEADERS)
        soup = BeautifulSoup(resp.text, 'lxml')
        trs = soup.select('tr')
        trs = [tr for tr in trs if 'xsid' in tr.attrs]
        country = None
        for tr in trs:
            if 'class' in tr.attrs:
                if tr['class'] == ['center']:
                    country = tr.text.strip()
            tds = tr.select('td')
            for td in tds:
                a = td.select_one('a')
                if a:
                    if a['href'][:2] != '//':
                        url_champ = self.MAIN_URL + a['href']
                        resp_champ = requests.get(url_champ, headers=self.HEADERS)
                        if 'Page not found' in resp_champ.text:
                            continue
                        sport_id = int(tr['xsid'])
                        data_champ = self.get_data_script(resp_champ.text, 'Tournament')
                        champ_text_id = data_champ['id']
                        request_time = int(time.time() * 1000)
                        url_champ_ajax = f"https://fb.oddsportal.com/ajax-sport-country-tournament-archive/{sport_id}/{champ_text_id}/X0/1/0/1/?_={request_time}"
                        print(url_champ_ajax)
                        # print(data_champ)
                        # print(tr['xsid'])
                        # print(country)
                        # print(td.text)


    @staticmethod
    def get_data_script(page: str, key: str):
        soup = BeautifulSoup(page, 'lxml')
        script = soup.select_one('script:contains("new OpHandler")').text
        json_text = re.search(f'Page{key}\((.*?)\);', script)
        if not json_text:
            print('script not found')
            sys.exit()
        try:
            json_data = json.loads(json_text.group(1))
        except ValueError:
            print('json not parsed')
            sys.exit()
        return json_data

    def get_data_ajax(self, resp: str):
        json_text = re.search('globals\.jsonpCallback\(.*, (.*)\);', resp)
        json_text = json_text.group(1)
        json_text = re.sub('null', 'None', json_text)
        json_text = re.sub('true', 'True', json_text)
        json_text = re.sub('false', 'False', json_text)
        return eval(json_text)

    def load_bookmakers(self):
        with open("bookmakersData.json", "r") as read_file:
            bookmakers_data = json.load(read_file)
            for bookmaker in bookmakers_data:
                self.bookmakers[bookmaker] = bookmakers_data[bookmaker]['WebName']

    def get_match_data(self, url: str):
        resp = requests.get(url, headers=self.HEADERS)
        soup = BeautifulSoup(resp.text, 'lxml')
        game_info_soup = soup.select_one('#col-content')
        result = game_info_soup.select_one('p.result')
        result_live = game_info_soup.select_one('p.result-live')
        if result:
            result = result.text
        elif result_live:
            result = result_live.text
        else:
            result = None
        json_data = self.get_data_script(resp.text, 'Event')
        command1 = json_data['home']
        command2 = json_data['away']
        version_id = json_data['versionId']
        sport_id = json_data['sportId']
        id = json_data['id']
        xhash = unquote(json_data['xhash'])
        e1 = self.E[sport_id][0]
        e2 = self.E[sport_id][1]
        time_request = int(time.time() * 1000)
        url = f'https://fb.oddsportal.com/feed/match/{version_id}-{sport_id}-{id}-{e1}-{e2}-{xhash}.dat?_={time_request}'
        headers_fb = self.HEADERS
        headers_fb['Referer'] = url
        resp = requests.get(url, headers=headers_fb)
        json_data = self.get_data_ajax(resp.text)
        openodds = json_data['d']['oddsdata']['back'][f'E-{e1}-{e2}-0-0-0']['opening_odds']
        openodds_filter = {}
        print(json_data)
        for bookmaker_id in openodds:
            if bookmaker_id in self.bookmakers:
                if type(openodds[bookmaker_id]) is dict:
                    list_keys_and_koef = list(openodds[bookmaker_id].items())
                    list_keys_and_koef.sort()
                    list_koef = [el[1] for el in list_keys_and_koef]
                    openodds_filter[self.bookmakers[bookmaker_id]] = list_koef
                else:
                    openodds_filter[self.bookmakers[bookmaker_id]] = openodds[bookmaker_id]
        print(openodds_filter)


if __name__ == '__main__':
    grabber = Grabber()
    grabber.update_champs_id()
    #grabber.get_match_data('https://www.oddsportal.com/soccer/africa/africa-cup-of-nations/equatorial-guinea-tunisia-MujIJeiH/')
    # grabber.get_match_data('https://www.oddsportal.com/basketball/asia/asia-championship-u16/china-australia-bVGTfJ0e/')


