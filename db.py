import sqlite3

DB = 'soccer.db'


def add_game_in_db(data):
    con = sqlite3.connect(DB)
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
    cur.executemany('INSERT INTO game (command1,command2,url,date,timematch,'
                        'result,sport,country,liga,url_api) '
                        'VALUES(?,?,?,?,?,?,?,?,?,?)', input_data)
    con.commit()
    print('[INFO] Игры добавлены в базу')
    cur.close()
    con.close()


def add_bookmaker_in_db(name: str, cur, con):
    query = 'SELECT * FROM bookmaker'
    cur.execute(query)
    data_name = [name[1] for name in cur.fetchall()]
    if name in data_name:
        return
    else:
        cur.execute('INSERT INTO bookmaker (name) VALUES(?)', [name])
        con.commit()


def add_bet_in_db(data):
    print('[INFO] add bets in db.....')
    con = sqlite3.connect(DB)
    cur = con.cursor()
    query = 'SELECT id,url FROM game'
    cur.execute(query)
    data_game_dict = {}
    for game in cur.fetchall():
        data_game_dict[game[1]] = game[0]
    for d in data:
        for key, item in d['odds'].items():
            add_bookmaker_in_db(key, cur, con)
    key_bookmakers = []
    p1 = []
    x = []
    p2 = []
    t = []
    keys_game = []
    for d in data:
        key_game = data_game_dict[d['url']]
        for key, item in d['odds'].items():
            query = 'SELECT * FROM bookmaker'
            cur.execute(query)
            data_bookmakers = [[el for el in bookmaker] for bookmaker in cur.fetchall()]
            for bookmaker in data_bookmakers:
                if bookmaker[1] == key:
                    key_bookmakers.append(bookmaker[0])
                    break
            p1.append(item[0])
            x.append(item[1])
            p2.append(item[2])
            t.append(item[3])
            keys_game.append(key_game)
    data_out = [[key_bookmakers[i],
                 p1[i],
                 x[i],
                 p2[i],
                 keys_game[i],
                 t[i]] for i in range(0, len(keys_game))]
    cur.executemany('INSERT INTO bet (bookmaker_id,p1,x,p2,game_id,open_time) VALUES(?,?,?,?,?,?)', data_out)
    con.commit()
    cur.close()
    con.close()


def check_game_in_db(url):
    con = sqlite3.connect(DB)
    cur = con.cursor()
    query = 'SELECT EXISTS(SELECT * FROM game WHERE url = ? LIMIT 1)'
    cur.execute(query, [url])
    game_bool = [game[0] for game in cur.fetchall()][0]
    if game_bool:
        cur.close()
        con.close()
        return True
    else:
        cur.close()
        con.close()
        return False


def get_bookmakers_from_bet():
    con = sqlite3.connect(DB)
    cur = con.cursor()
    query = \
        '''SELECT book.name AS book_name
            FROM bet b
            INNER JOIN bookmaker book ON b.bookmaker_id = book.id
        '''
    cur.execute(query)
    data = [bookmaker[0] for bookmaker in cur.fetchall()]
    cur.close()
    con.close()
    return data

def get_count_games():
    con = sqlite3.connect(DB)
    cur = con.cursor()
    query = 'SELECT COUNT(*) FROM game'
    cur.execute(query)
    games_count = cur.fetchone()[0]
    return games_count
