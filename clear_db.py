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
    ids_list = []
    for url in url_duplicate_list:
        start = time.time()
        query = 'SELECT id FROM game WHERE url = ?'
        cur.execute(query, [url])
        ids = [index[0] for index in cur.fetchall()]
        ids_list += ids[1:]
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
    print('[INFO] Удаляем дубликаты...')
    if len(ids_list) == 1:
        query_list = '(%i)' % ids_list[0]
    else:
        query_list = tuple(ids_list)
    query = 'DELETE FROM game WHERE id IN {}'.format(query_list)
    cur.execute(query)
    query = 'DELETE FROM bet WHERE game_id IN {}'.format(query_list)
    cur.execute(query)
    query = 'DELETE FROM game_info WHERE game_id IN {}'.format(query_list)
    cur.execute(query)
    con.commit()
    print('[INFO] Дубликаты удалены.')
    print('[INFO] Создаём новую таблицу')
    query = """CREATE TABLE `game_new` (`id`	INTEGER PRIMARY KEY AUTOINCREMENT,`command1` TEXT, `command2` TEXT, 
    `url` TEXT UNIQUE, `date`	TEXT, `timematch`	TEXT, `result`	TEXT, `sport`	TEXT, `country`	TEXT, 
    `liga`	TEXT) """
    cur.execute(query)
    print('[INFO] Копируем данные из старой таблицы')
    query = """INSERT INTO `game_new` SELECT * FROM `game`"""
    cur.execute(query)
    print('[INFO] Удаляем старую таблицу')
    query = """DROP TABLE `game`"""
    cur.execute(query)
    print('[INFO] Переименовываем новую таблицу')
    query = """ALTER TABLE `game_new` RENAME TO game;"""
    cur.execute(query)
    con.commit()
    con.execute("VACUUM")
    cur.close()
    con.close()
    print('[INFO] Завершено.')

clear_duplicate()
