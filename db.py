import sqlite3
import time

def add_game_in_db(db, data):
    """
    Добавление игры в базу
    :param args:
    :arg[0] - Словарь для ручного добавления в базу
    :return:
    """
    con = sqlite3.connect(db)
    cur = con.cursor()
    input_data = [[el['command1'],
                  el['command2'],
                  el['url'],
                  el['date'],
                  el['time'],
                  el['result'],
                  el['sport'],
                  el['country'],
                  el['champ'],
                  el['req_api']]
                  for el in data]
    executing = False
    while not executing:
        try:
            cur.executemany('INSERT INTO game (command1,command2,url,date,timematch,'
                        'result,sport,country,liga,url_api) '
                        'VALUES(?,?,?,?,?,?,?,?,?,?)', input_data)
            executing = True
        except sqlite3.OperationalError:
            print('[WARNING] База данных используется...')
            print('[WARNING] Ожидание...')
            time.sleep(0.1)
    commited = False
    while not commited:
        try:
            con.commit()
            commited = True
        except sqlite3.OperationalError:
            print('[WARNING] База данных используется...')
            print('[WARNING] Ожидание...')
            time.sleep(0.1)
    print('[INFO] Множество игр добавлено в базу')
    cur.close()
    con.close()


def add_bookmaker_in_db(name: str, cur, con):
    query = 'SELECT * FROM bookmaker'
    executing = False
    while not executing:
        try:
            cur.execute(query)
            executing = True
        except sqlite3.OperationalError:
            print('[WARNING] База данных используется...')
            print('[WARNING] Ожидание...')
            time.sleep(0.1)

    data_name = [name[1] for name in cur.fetchall()]
    if name in data_name:
        return
    else:
        executing = False
        while not executing:
            try:
                cur.execute('INSERT INTO bookmaker (name) VALUES(?)', [name])
                executing = True
            except sqlite3.OperationalError:
                print('[WARNING] База данных используется...')
                print('[WARNING] Ожидание...')
                time.sleep(0.1)
        commited = False
        while not commited:
            try:
                con.commit()
                commited = True
            except sqlite3.OperationalError:
                print('[WARNING] База данных используется...')
                print('[WARNING] Ожидание...')
                time.sleep(0.2)
        print('[INFO] Букмекер %s добавлен в базу' % name)

def add_bet_in_db(db, data):
    print(data)
    print('[INFO] add bets in db.....')
    con = sqlite3.connect(db)
    cur = con.cursor()
    query = 'SELECT id,url FROM game'
    executing = False
    while not executing:
        try:
            cur.execute(query)
            executing = True
        except sqlite3.OperationalError:
            print('[WARNING] База данных используется...')
            print('[WARNING] Ожидание...')
            time.sleep(0.1)
    data_game_dict = {}
    for game in cur.fetchall():
        data_game_dict[game[0]] = game[1]
    keys_game = []
    for key, item in data_game_dict.items():
        for d in data:
            if item == d['url']:
                print(key)
                keys_game.append(key)
                break
    for d in data:
        for key, item in d['odds'].items():
            add_bookmaker_in_db(key, cur, con)
    key_bookmakers = []
    p1 = []
    x = []
    p2 = []
    t = []
    for d in data:
        for key, item in d['odds'].items():
            query = 'SELECT * FROM bookmaker'
            executing = False
            while not executing:
                try:
                    cur.execute(query)
                    executing = True
                except sqlite3.OperationalError:
                    print('[WARNING] База данных используется...')
                    print('[WARNING] Ожидание...')
                    time.sleep(0.1)
            data_bookmakers = [[el for el in bookmaker] for bookmaker in cur.fetchall()]
            for bookmaker in data_bookmakers:
                if bookmaker[1] == key:
                    key_bookmakers.append(bookmaker[0])
                    break
            p1.append(item[0])
            x.append(item[1])
            p2.append(item[2])
            t.append(item[3])
    data_out = [[key_bookmakers[i],
                 p1[i],
                 x[i],
                 p2[i],
                 keys_game[i],
                 t[i]] for i in range(0, len(keys_game))]
    print(data_out)
    cur.executemany('INSERT INTO bet (bookmaker_id,p1,x,p2,game_id,open_time) VALUES(?,?,?,?,?,?)', data_out)
    con.commit()
    cur.close()
    con.close()

def check_game_in_db(db, url):
    print('[INFO] Проверка игры ' + url)
    con = sqlite3.connect(db)
    cur = con.cursor()
    query = 'SELECT EXISTS(SELECT * FROM game WHERE url = ? LIMIT 1)'
    cur.execute(query, [url])
    game_bool = [game[0] for game in cur.fetchall()][0]
    if game_bool:
        print('[INFO] %s игра уже есть в базе ' % str(url))
        cur.close()
        con.close()
        return True
    else:
        print('[INFO] %s игры нету в базе ' % str(url))
        cur.close()
        con.close()
        return False