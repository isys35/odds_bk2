import time
import sqlite3
from collections import Counter
import statistics


def clear_duplicate():
    db = 'oddsportal.db'
    con = sqlite3.connect(db)
    cur = con.cursor()
    query = 'SELECT url FROM game'
    cur.execute(query)
    urls = [url[0] for url in cur.fetchall()]
    counter_urls = Counter(urls)
    url_duplicate_list = []
    for key, item in counter_urls.items():
        if item > 1:
            url_duplicate_list.append(key)
    duplicates = len(url_duplicate_list)
    print('[INFO] Количество дубликатов: ' + str(duplicates))
    time_list = []
    for url in url_duplicate_list:
        query = 'SELECT id FROM game WHERE url = ?'
        cur.execute(query, [url])
        ids = [index[0] for index in cur.fetchall()]
        start = time.time()
        print('[INFO] Удаляем дубликаты...')
        if len(ids) == 2:
            query_list = '(%i)' % ids[1]
        else:
            query_list = tuple(ids[1:])
        query = 'DELETE FROM game WHERE id IN {}'.format(query_list)
        print(query)
        cur.execute(query)
        query = 'DELETE FROM bet WHERE game_id IN {}'.format(query_list)
        print(query)
        cur.execute(query)
        query = 'DELETE FROM game_info WHERE game_id IN {}'.format(query_list)
        print(query)
        cur.execute(query)
        duplicates -= 1
        print('[INFO] Количество дубликатов: ' + str(duplicates))
        end = time.time()
        final_time = end - start
        time_list.append(final_time)
        time_to_compl = statistics.mean(time_list) * duplicates
        hour = int(time_to_compl // 3600)
        minute = int((time_to_compl % 3600) // 60)
        second = (time_to_compl % 3600) % 60
        print('[INFO] Осталось примерно {} часов {} минут {} секунд'.format(hour, minute, second))
        con.commit()
    cur.close()
    con.close()


clear_duplicate()
