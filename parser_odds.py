import requests
from bs4 import BeautifulSoup
import re
import sys
import json
from urllib.parse import unquote
import time


def save_file(txt: str, file_name: str):
    with open(file_name, 'w', encoding='utf8') as file:
        file.write(txt)


def load_file(file_name: str):
    with open(file_name, 'r', encoding='utf8') as file:
        return file.read()


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
        self.champs_id_file = 'champs_id'

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

    @staticmethod
    def get_data_ajax(resp: str):
        json_text = re.search(r'globals\.jsonpCallback\(.*, (\{.*\})\);', resp)
        json_text = json_text.group(1)
        json_text = re.sub('null', 'None', json_text)
        json_text = re.sub('true', 'True', json_text)
        json_text = re.sub('false', 'False', json_text)
        return json_text

    def load_bookmakers(self):
        with open("bookmakersData.json", "r") as read_file:
            bookmakers_data = json.load(read_file)
            for bookmaker in bookmakers_data:
                self.bookmakers[bookmaker] = bookmakers_data[bookmaker]['WebName']

    def get_event_data(self, url: str):
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
        breadcrumb = soup.select_one('#breadcrumb')
        champ_name = breadcrumb.select('a')[-1].text
        country = breadcrumb.select('a')[-2].text
        date_block = soup.select_one('.date.datet')['class'][2]
        date = int(re.search(r'(\d*)-', date_block).group(1))
        json_data = self.get_data_script(resp.text, 'Event')
        command1 = json_data['home']
        command2 = json_data['away']
        # champ_id = json_data['tournamentId']
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
        print(url)
        resp = requests.get(url, headers=headers_fb)
        json_data = eval(self.get_data_ajax(resp.text))
        print(json_data)
        openodds = json_data['d']['oddsdata']['back'][f'E-{e1}-{e2}-0-0-0']['opening_odds']
        opening_change_time = json_data['d']['oddsdata']['back'][f'E-{e1}-{e2}-0-0-0']['opening_change_time']
        openodds_filter = {}
        for bookmaker_id in openodds:
            if bookmaker_id in self.bookmakers:
                if type(openodds[bookmaker_id]) is dict:
                    list_keys_and_koef = list(openodds[bookmaker_id].items())
                    list_keys_and_koef.sort()
                    list_koef = [el[1] for el in list_keys_and_koef]
                    openodds_filter[self.bookmakers[bookmaker_id]] = {'coef': list_koef}
                else:
                    openodds_filter[self.bookmakers[bookmaker_id]] = {'coef': openodds[bookmaker_id]}
                if type(opening_change_time[bookmaker_id]) is dict:
                    list_keys_and_time = list(opening_change_time[bookmaker_id].items())
                    list_keys_and_time.sort()
                    list_time = [el[1] for el in list_keys_and_time]
                    openodds_filter[self.bookmakers[bookmaker_id]]['change_time'] = list_time[0]
                else:
                    openodds_filter[self.bookmakers[bookmaker_id]]['change_time'] = opening_change_time[bookmaker_id][0]
        return {'e1': e1,
                'result': result,
                'command1': command1,
                'command2': command2,
                'champ_name': champ_name,
                'date': date,
                'country': country,
                'sport': self.SPORTS_ID[sport_id],
                'open_odds': openodds_filter}


if __name__ == '__main__':
    grabber = Grabber()
    #grabber.update_champs_id()
    data = grabber.get_event_data('https://www.oddsportal.com/soccer/africa/cecafa-clubs-cup/as-maniema-green-eagles-OYTGqXsb/')
    print(data)
    # grabber.get_match_data('https://www.oddsportal.com/basketball/asia/asia-championship-u16/china-australia-bVGTfJ0e/')


