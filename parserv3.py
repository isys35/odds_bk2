import requests
from bs4 import BeautifulSoup as BS
import re
import sys
import json
from urllib.parse import unquote
import time



def get_hrefs_champs_soccer():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:71.0) Gecko/20100101 Firefox/71.0'
    }
    soccer_url = 'https://www.oddsportal.com/results/#soccer'
    r = requests.get(soccer_url, headers=headers)
    html = BS(r.content, 'html.parser')
    championships = html.select('table.table-main.sport')[0].select('td')
    # список с ссылками на все чемпионаты
    href_championships = [championship.select('a')[0]['href'] for championship in championships
                          if len(championship.select('a')) > 0]
    href_championships_soccer = [href for href in href_championships if href.split('/')[1] == 'soccer']
    return href_championships_soccer

def get_matchs(href):
    count = 0
    url = 'https://www.oddsportal.com' + href
    print(url)
    years_hrefs = get_years_champ(url)
    if not years_hrefs:
        return
    print(years_hrefs)
    for year_href in years_hrefs:
        id_champ = get_ajax_year_id(year_href)
        print(id_champ)
        pages = get_year_pages(id_champ, year_href)
        print(pages)
        games_hrefs = []
        for p in range(0, pages):
            games_href_page = get_games_page(id_champ, year_href, int(p+1))
            games_hrefs.extend(games_href_page)
        print(games_hrefs)
        for game_href in games_hrefs:
            req_odds = get_request_url(game_href, year_href)
            print(req_odds)
            full_data = get_full_data(game_href,req_odds)
            print(full_data)
            count += 1
            print(count)

def get_games_page(id,href,p):
    url_req = f'https://fb.oddsportal.com/ajax-sport-country-tournament-archive/1/{id}/X0/1/2/{p}/?_={int(time.time() * 1000)}'
    url_referer = 'https://www.oddsportal.com' + href
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:71.0) Gecko/20100101 Firefox/71.0',
        'Referer': url_referer
    }
    resp = requests.get(url_req, headers=headers)
    resp_json_text = \
    resp.text.replace(f"globals.jsonpCallback('/ajax-sport-country-tournament-archive/1/{id}/X0/1/2/{p}/', ", '').rsplit(
        ');', maxsplit=1)[0]
    json_resp = json.loads(resp_json_text)
    soup = BS(str(json_resp['d']['html']), 'lxml')
    names = soup.select('.name.table-participant')
    hrefs = [name.select_one('a')['href'] for name in names]
    return hrefs

def get_year_pages(id, href):
    url_req = f'https://fb.oddsportal.com/ajax-sport-country-tournament-archive/1/{id}/X0/1/2/1/?_={int(time.time()*1000)}'
    url_referer = 'https://www.oddsportal.com' + href
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:71.0) Gecko/20100101 Firefox/71.0',
        'Referer': url_referer
    }
    resp = requests.get(url_req, headers=headers)
    resp_json_text = resp.text.replace(f"globals.jsonpCallback('/ajax-sport-country-tournament-archive/1/{id}/X0/1/2/1/', ", '').rsplit(');', maxsplit=1)[0]
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




def get_years_champ(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:71.0) Gecko/20100101 Firefox/71.0',
        'Referer': url
    }
    page = requests.get(url, headers=headers)
    soup = BS(page.text, 'html.parser')
    main_menu = soup.select_one('.main-menu2.main-menu-gray')
    try:
        years_href = [a['href']for a in main_menu.select('a')]
    except AttributeError:
        print('page not found')
        return
    return years_href
    # with open('page.html', 'w', encoding='utf8') as html_file:
    #      html_file.write(str(main_menu))

def get_ajax_year_id(href):
    url = 'https://www.oddsportal.com' + href
    print(url)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:71.0) Gecko/20100101 Firefox/71.0',
        'Referer': url
    }
    page = requests.get(url, headers=headers)
    soup = BS(page.text, 'html.parser')
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

def get_request_url(href_game, href_year):
    url_referer = 'https://www.oddsportal.com' + href_year
    url_game = 'https://www.oddsportal.com' + href_game
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:71.0) Gecko/20100101 Firefox/71.0',
        'Referer': url_referer
    }
    page = requests.get(url_game, headers=headers)
    soup = BS(page.text, 'html.parser')
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
    url_out = 'https://fb.oddsportal.com/feed/match/1-1-{}-1-2-{}.dat?_={}'.format(id1,id2,int(time.time()*1000))
    return url_out

def get_full_data(href_game, req_url):
    url_game = 'https://www.oddsportal.com' + href_game
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:71.0) Gecko/20100101 Firefox/71.0',
        'referer': url_game
    }
    r = requests.get(req_url, headers=headers)
    odds_response = r.text
    return odds_response

if __name__ == '__main__':
    hrefs_champs_soccer = get_hrefs_champs_soccer()
    for href in hrefs_champs_soccer:
        get_matchs(href)

