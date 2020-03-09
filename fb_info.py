import sqlite3
import time
from collections import Counter
import requests
from threading import Thread

def main():
    con = sqlite3.connect('soccer.db')
    cur = con.cursor()
    query = 'SELECT url_api,url FROM game'
    cur.execute(query)
    urls = [[url[0], url[1]] for url in cur.fetchall()]
    keys = []
    for url in urls:
        print(url[0], url[0].split('-')[-1].replace('yj','').replace('.dat?_=',''))
        keys.append(url[0].split('-')[-1].replace('yj','').replace('.dat?_=',''))
    counter = Counter(keys)
    counter = dict(counter)
    print(counter)
    print(len(counter))
    for key, item in counter.items():
        if item < 5:
            print(key)
    check_key = counter['ed8']
    for url in urls:
        if url[0].split('-')[-1].replace('yj', '').replace('.dat?_=','') == 'ed8':
            print(url[0])
            print(url[1])
    cur.close()
    con.close()
    return counter


def get_response(key):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:71.0) Gecko/20100101 Firefox/71.0',
        'Referer': 'https://www.oddsportal.com/soccer/argentina/primera-b-nacional-2010-2011/rosario-central-c-a-i-8MdODRJ9/'
    }
    timer_reg = str(time.time()).split('.')[0] + str(time.time()).split('.')[1][0:3]
    url = f'https://fb.oddsportal.com/feed/match/1-1-8MdODRJ9-1-2-yj{key}.dat?_={timer_reg}'
    #print(url)
    r = requests.get(url, headers=headers)
    print(r.text)
    return r.text


class KeyChecker(Thread):
    def __init__(self):
        super().__init__()
        self.response_key = None
        self.out_request = None

    def run(self):
        while True:
            if self.response_key:
                responce = get_response(self.response_key)
                if not '"E":"notAllowed"' in responce:
                    print(responce)
                    self.out_request = responce
                else:
                    self.response_key = None
def get_key():
    counter = main()
    listing = list(counter.items())
    listing.sort(key=lambda x: x[1], reverse=True)
    list_key = [key[0] for key in listing]
    # count_key = len(listing)
    # for key in counter:
    #     print(count_key)
    #     responce = get_response(key)
    #     if not '"E":"notAllowed"' in responce:
    #         print(responce)
    #     else:
    #         print('...........')
    #     count_key -= 1
    checkers = [KeyChecker() for i in range(0, 100)]
    for checker in checkers:
        checker.start()
    while True:
        for checker in checkers:
            if not checker.response_key:
                checker.response_key = list_key.pop(0)
                if checker.out_request:
                    return checker.out_request
            print(len(list_key))

if __name__ == '__main__':
    key = get_key()
    print(key)







