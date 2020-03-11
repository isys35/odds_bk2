import requests
import time

def req(urls, headers):
    data = []
    for url in urls:
        r = requests.get(url,headers=headers)
        data.append(r.text)
    return data

def main():
    t0 = time.time()
    urls = ['https://1xstavka.ru/live/Basketball/1939157-Space-League/228926957-Cavs-Bulls/',
            'https://1xstavka.ru/live/Basketball/2055229-Premier-League-3h3/228928178-Khimik-Orange-Tigers-Blue/',
            'https://1xstavka.ru/live/Basketball/2055636-Buzzer-League/228927943-Asian-Tigers-Australian-Spiders/']
    headers = {
        'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:73.0) Gecko/20100101 Firefox/73.0'
    }
    data = req(urls, headers)
    t = time.time() - t0
    print(t)
    return t

if __name__ == '__main__':
    i = 0
    t = []
    while i!=10:
        i += 1
        t.append(main())
    print('Среднее время ' + str(sum(t)/len(t)))