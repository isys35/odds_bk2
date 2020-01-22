import time
import sqlite3
from parser_odds import Parser

db = 'oddsportal.db'


def update_game_info():
    con = sqlite3.connect(db)
    cur = con.cursor()
    query = 'SELECT count(*) FROM sqlite_master WHERE type=? AND name=?'
    cur.execute(query, ['table', 'game_info'])
    table_info = cur.fetchone()[0]
    cur.close()
    con.close()
    if not table_info:
        print('[INFO] Таблицы game_info нету в базе данных')
        greate_game_info_table()
    con = sqlite3.connect(db)
    cur = con.cursor()
    query = 'SELECT id, url FROM  game'
    cur.execute(query)
    games = [[game[0], game[1]] for game in cur.fetchall()]
    query = 'SELECT game_id FROM  game_info'
    cur.execute(query)
    game_info_ids = [game_id[0] for game_id in cur.fetchall()]
    print(games)
    print(game_info_ids)
    cur.close()
    con.close()
    parser = Parser()
    for game in games:
        if game[0] in game_info_ids:
            print('[INFO] Игра уже есть в game_info')
            continue
        else:
            data = parser.get_match_data(game[1])
            print(data)


def greate_game_info_table():
    print('[INFO] Создание таблицы game_info')
    con = sqlite3.connect(db)
    cur = con.cursor()
    query = """CREATE TABLE `game_info` 
    (`id`	INTEGER PRIMARY KEY AUTOINCREMENT,
    `game_id`	INTEGER,
    `file_path`	TEXT,
    FOREIGN KEY(`game_id`) REFERENCES `game`(`id`))"""
    cur.execute(query)
    cur.close()
    con.close()

update_game_info()
