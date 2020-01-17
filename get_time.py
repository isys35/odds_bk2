import requests
from bs4 import BeautifulSoup as BS


def get_time(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:71.0) Gecko/20100101 Firefox/71.0',
        'referer': url.rsplit('/', 2)[0]+'/results/'}
    r = requests.get(url, headers=headers)
    html = BS(r.content, 'html.parser')
    print(html)

get_time('https://www.oddsportal.com/soccer/africa/africa-cup-of-nations-u20/nigeria-south-africa-rHJ74HD5/')