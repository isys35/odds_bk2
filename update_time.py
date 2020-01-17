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
    load_game = data_list[0]
    try:
        with open('save_date', 'r', encoding='utf8') as load_file:
            load_game = eval(load_file.read())
        print('[INFO] Файл загрузки получен')
    except FileNotFoundError:
        print('[WARNING] Файл загрузки не найден')
    index_load_game = data_list.index(load_game)
    total_games = len(game_list[index_load_game:])
    time_list = []
    con = sqlite3.connect(parser.db)
    cur = con.cursor()
    for game in game_list[index_load_game:]:
        start = time.time()
        print('[INFO] Получаем дату {}'.format(game['url']))
        date = parser.get_date(game['url'])
        print('[INFO] Дата в базе {}'.format(game['date']))
        print('[INFO] Сравниваем дату из сайта с датой из бд')
        if game['date'] == date:
            print('[INFO] Даты совпадают')
        else:
            print('[INFO] Даты не совпадают')
            print('[INFO] Меняем значения в базе')
            query = 'UPDATE game SET date = ? WHERE url = ?'
            cur.execute(query, [date, game['url']])
            print('[INFO] Значение измененно')
        end = time.time()
        time_compl = end - start
        time_list.append(time_compl)
        total_games -= 1
        print('[INFO] Осталось проверить {} игр'.format(total_games))
        if total_games % 10 == 0:
            print('[INFO] Сохранение изменений')
            con.commit()
            with open('save_date', 'w', encoding='utf8') as savefile:  # сохранение
                savefile.write(str((date, game['url'])))
            print('[INFO] Сохраненно')
        time_to_compl = statistics.mean(time_list) * total_games
        hour = int(time_to_compl // 3600)
        minute = int((time_to_compl % 3600) // 60)
        second = (time_to_compl % 3600) % 60
        print('[INFO] Осталось примерно {} часов {} минут {} секунд'.format(hour, minute, second))
    cur.close()
    con.close()


if __name__ == "__main__":
    update_time()