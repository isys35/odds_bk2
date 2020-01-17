from parser_odds import Parser
import sqlite3
import time
import statistics


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
    total_games = len(game_list)
    time_list = []
    for game in game_list:
        start = time.time()
        print('[INFO] Получаем дату {}'.format(game['url']))
        date = parser.get_date(game['url'])
        print('[INFO] Дата в базе {}'.format(game['date']))
        print('[INFO] Сравниваем дату из сайта с датой из бд')
        if game['date'] == date:
            print('[INFO] Даты совпадают')
            end = time.time()
            time_compl = end - start
            time_list.append(time_compl)
            total_games -= 1
            print(str(time_compl))
            print('[INFO] Осталось проверить {} игр'.format(total_games))
            time_to_compl = statistics.mean(time_list) * total_games
            hour = int(time_to_compl // 3600)
            minute = int((time_to_compl % 3600) // 60)
            second = (time_to_compl % 3600) % 60
            print('[INFO] Осталось примерно {} часов {} минут {} секунд'.format(hour, minute, second))
            continue
        else:
            print('[INFO] Даты не совпадают')
            print('[INFO] Меняем значения в базе')
            con = sqlite3.connect(parser.db)
            cur = con.cursor()
            query = 'UPDATE game SET date = ? WHERE url = ?'
            cur.execute(query, [date, game['url']])
            con.commit()
            print('[INFO] Значение измененно')
            total_games -= 1
            print('[INFO] Осталось проверить {} игр'.format(total_games))
        end = time.time()
        time_compl = end - start
        time_list.append(time_compl)
        print(str(time_compl))
        time_to_compl = statistics.mean(time_list) * total_games
        hour = int(time_to_compl // 3600)
        minute = int((time_to_compl % 3600) // 60)
        second = (time_to_compl % 3600) % 60
        print('[INFO] Осталось примерно {} часов {} минут {} секунд'.format(hour, minute, second))
        cur.close()
        con.close()


if __name__ == "__main__":
    update_time()