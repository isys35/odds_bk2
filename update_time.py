from parser_odds import Parser
import sqlite3
import time

def update_time():
    parser = Parser()
    print('[INFO] Подключение к базе данных')
    con = sqlite3.connect(parser.db)
    cur = con.cursor()
    query = 'SELECT date,url FROM game'
    print('[INFO] Получаем ссылки на игры и их дату')
    cur.execute(query)
    data_list = cur.fetchall()
    game_list = []
    for game in data_list:
        dict_game = {'date': game[0],
                     'url': game[1]}
        game_list.append(dict_game)
    cur.close()
    con.close()
    for game in game_list:
        start = time.time()
        print('[INFO] Получаем дату {}'.format(game['url']))
        date = parser.get_date(game['url'])
        print('[INFO] Сравниваем дату из сайта с датой из бд')
        if game['date'] == date:
            print('[INFO] Даты совпадают')
            continue
        else:
            print('[INFO] Даты не совпадают')
            print('[INFO] Меняем значения в базе')
            con = sqlite3.connect(parser.db)
            cur = con.cursor()
            query = 'UPDATE game SET date = ? WHERE url = ?'
            cur.execute(query, [game['date'], game['url']])
            con.commit()
            print('[INFO] Значение измененно')
        end = time.time()
        time_compl = end - start
        print(str(time_compl))
    cur.close()
    con.close()

if __name__ == "__main__":
    update_time()