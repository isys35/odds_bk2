import time
import sqlite3
from collections import Counter
import statistics

db = 'oddsportal.db'


def clear_duplicate_game():
    con = sqlite3.connect(db)
    cur = con.cursor()
    query = 'SELECT url FROM game'
    print('[INFO] Подсчёт дубликатов игр')
    cur.execute(query)
    urls = [url[0] for url in cur.fetchall()]
    counter_urls = Counter(urls)
    url_duplicate_list = []
    for key, item in counter_urls.items():
        if item > 1:
            url_duplicate_list.append(key)
    duplicates = len(url_duplicate_list)
    print('[INFO] Количество дубликатов игр: ' + str(duplicates))
    if duplicates:
        print('[INFO ]Удаляеем дубликаты игр')
        query = 'DELETE FROM bet WHERE game_id NOT IN (SELECT min(id) FROM game GROUP BY url)'
        cur.execute(query)
        query = 'DELETE FROM game_info WHERE game_id NOT IN (SELECT min(id) FROM game GROUP BY url)'
        cur.execute(query)
        query = 'DELETE FROM game WHERE rowid NOT IN (SELECT min(rowid) FROM game GROUP BY url)'
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
        con.commit()
    cur.close()
    con.close()


def clear_duplicate_bet():
    con = sqlite3.connect(db)
    cur = con.cursor()
    print('[INFO] Подсчёт дубликатов ставок')
    query = 'SELECT bookmaker_id,game_id FROM bet'
    cur.execute(query)
    bets = [(bet[0], bet[1]) for bet in cur.fetchall()]
    counter_bets = Counter(bets)
    bets_duplicate_list = []
    for key, item in counter_bets.items():
        if item > 1:
            bets_duplicate_list.append(key)
    duplicates = len(bets_duplicate_list)
    print('[INFO] Количество дубликатов коэф: ' + str(duplicates))
    if duplicates:
        print('Удаляеем дубликаты ставок')
        query = 'DELETE FROM bet WHERE rowid NOT IN (SELECT min(rowid) FROM bet GROUP BY bookmaker_id, game_id)'
        cur.execute(query)
        con.commit()
        con.execute("VACUUM")
        con.commit()
    cur.close()
    con.close()



if __name__ == "__main__":
    clear_duplicate_game()
    clear_duplicate_bet()
    print('[INFO] Завершено.')