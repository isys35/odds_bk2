import sqlite3

db = 'soccer.db'

def main():
    con = sqlite3.connect(db)
    cur = con.cursor()
    query = 'SELECT id,result FROM game'
    cur.execute(query)
    games = cur.fetchall()
    id_for_del = [game[0] for game in games if game[1] == 'Canceled' or 'awarded' in game[1]]
    print(id_for_del)
    print(len(id_for_del))
    for id in id_for_del:
        print('delete')
        cur.execute('DELETE FROM bet WHERE game_id = ?', [id])
        cur.execute('DELETE FROM game WHERE id = ?', [id])
        con.commit()
    cur.close()

if __name__ == '__main__':
    main()