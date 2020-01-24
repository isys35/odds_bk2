import time
import sqlite3
from parser_odds import Parser
import xlwt


class GameInfo:
    def __init__(self):
        self.db = 'oddsportal.db'
        self.parser = Parser()

    def update_game_info(self):
        con = sqlite3.connect(self.db)
        cur = con.cursor()
        query = 'SELECT count(*) FROM sqlite_master WHERE type=? AND name=?'
        cur.execute(query, ['table', 'game_info'])
        table_info = cur.fetchone()[0]
        cur.close()
        con.close()
        if not table_info:
            print('[INFO] Таблицы game_info нету в базе данных')
            self.greate_game_info_table()
        con = sqlite3.connect(self.db)
        cur = con.cursor()
        query = 'SELECT id, url FROM  game'
        cur.execute(query)
        games = [[game[0], game[1]] for game in cur.fetchall()]
        query = 'SELECT game_id FROM  game_info'
        cur.execute(query)
        game_info_ids = [game_id[0] for game_id in cur.fetchall()]
        cur.close()
        con.close()
        for game in games:
            if game[0] in game_info_ids:
                print('[INFO] Игра уже есть в game_info')
                continue
            else:
                data = self.parser.get_match_fulldata(game[1])
                self.save_data_in_file(data, game[1])
                self.add_game_info_in_db(game[0], game[1])

    def get_game_info(self, url):
        con = sqlite3.connect(self.db)
        cur = con.cursor()
        query = 'SELECT id FROM game WHERE url=?'
        cur.execute(query, [url])
        game_id = [game_id[0] for game_id in cur.fetchone()][0]
        data = self.parser.get_match_fulldata(url)
        self.save_data_in_file(data, url)
        self.add_game_info_in_db(game_id, url)
        cur.close()
        con.close()

    def add_game_info_in_db(self, game_id, url):
        print('[INFO] Добавление файла информации в базу')
        game_info_folder = 'game_info/'
        file_name = game_info_folder + url.replace('/', '').split('-')[-1] + '.xls'
        con = sqlite3.connect(self.db)
        cur = con.cursor()
        query = 'INSERT INTO game_info (game_id,file_path) VALUES(?,?)'
        cur.execute(query, [game_id, file_name])
        con.commit()
        cur.close()
        con.close()

    def save_data_in_file(self, data, url):
        game_info_folder = 'game_info/'
        file_name =game_info_folder + url.replace('/', '').split('-')[-1] + '.xls'
        wb = xlwt.Workbook()
        ws = wb.add_sheet('sheet')
        ws.col(2).width = 6000
        ws.col(4).width = 6000
        ws.col(6).width = 6000
        ws.write(0, 0, str(data[3]))
        ws.write(1, 0, str(data[2]))
        ws.write(2, 0, str(data[0]))
        ws.write(4, 0, 'Букмекер')
        ws.write(4, 1, 'П1')
        ws.write(4, 2, 'Время')
        ws.write(4, 3, 'X')
        ws.write(4, 4, 'Время')
        ws.write(4, 5, 'П2')
        ws.write(4, 6, 'Время')
        ws.write(4, 7, 'Маржа')
        target_row = 5
        for bookmaker in data[1]:
            ws.write(target_row, 0, bookmaker)
            ws.write(target_row, 1, data[1][bookmaker]['open_odds'][0])
            ws.write(target_row, 2, time.ctime(data[1][bookmaker]['openning_change_times'][0]))
            ws.write(target_row, 3, data[1][bookmaker]['open_odds'][1])
            ws.write(target_row, 4, time.ctime(data[1][bookmaker]['openning_change_times'][1]))
            ws.write(target_row, 5, data[1][bookmaker]['open_odds'][2])
            ws.write(target_row, 6, time.ctime(data[1][bookmaker]['openning_change_times'][2]))
            major = ((1 / data[1][bookmaker]['open_odds'][0] * 100)
                     + (1 / data[1][bookmaker]['open_odds'][1] * 100)
                     + (1 / data[1][bookmaker]['open_odds'][2] * 100)) - 100
            ws.write(target_row, 7, major)
            target_row += 1
            if '0' in data[1][bookmaker] or '1' in data[1][bookmaker] or '2' in data[1][bookmaker]:
                check_max = []
                for key, item in data[1][bookmaker].items():
                    if key in ['0', '1', '2']:
                        check_max.append(len(item))
                max_len_history = max(check_max)
                for key, item in data[1][bookmaker].items():
                    if key in ['0', '1', '2']:
                        item.sort(key=lambda i: i[2])
                        if len(item) != max_len_history:
                            while len(item) != max_len_history:
                                item.append(item[-1])
                for i in range(1, max_len_history):
                    p1 = 0
                    p2 = 0
                    x = 0
                    out_keys = []
                    if '0' in data[1][bookmaker]:
                        ws.write(target_row, 1, float(data[1][bookmaker]['0'][i][0]))
                        ws.write(target_row, 2, time.ctime(data[1][bookmaker]['0'][i][2]))
                        p1 = float(data[1][bookmaker]['0'][i][0])
                    else:
                        ws.write(target_row, 1, float(data[1][bookmaker]['open_odds'][0]))
                        ws.write(target_row, 2, time.ctime(data[1][bookmaker]['openning_change_times'][0]))
                        out_keys.append('0')
                    if '1' in data[1][bookmaker]:
                        ws.write(target_row, 3, float(data[1][bookmaker]['1'][i][0]))
                        ws.write(target_row, 4, time.ctime(data[1][bookmaker]['1'][i][2]))
                        x = float(data[1][bookmaker]['1'][i][0])
                    else:
                        ws.write(target_row, 3, float(data[1][bookmaker]['open_odds'][1]))
                        ws.write(target_row, 4, time.ctime(data[1][bookmaker]['openning_change_times'][1]))
                        out_keys.append('1')
                    if '2' in data[1][bookmaker]:
                        ws.write(target_row, 5, float(data[1][bookmaker]['2'][i][0]))
                        ws.write(target_row, 6, time.ctime(data[1][bookmaker]['2'][i][2]))
                        p2 = float(data[1][bookmaker]['2'][i][0])
                    else:
                        ws.write(target_row, 5, float(data[1][bookmaker]['open_odds'][2]))
                        ws.write(target_row, 6, time.ctime(data[1][bookmaker]['openning_change_times'][2]))
                        out_keys.append('2')
                    for key in out_keys:
                        if key == '0':
                            p1 = float(data[1][bookmaker]['open_odds'][0])
                        elif key == '2':
                            p2 = float(data[1][bookmaker]['open_odds'][2])
                        elif key == '1':
                            x = float(data[1][bookmaker]['open_odds'][1])
                    if p1 and p2 and x:
                        major = ((1/p1*100) + (1/x*100) + (1/p2*100)) - 100
                        ws.write(target_row, 7, major)
                        target_row += 1
        wb.save(file_name)

    def greate_game_info_table(self):
        print('[INFO] Создание таблицы game_info')
        con = sqlite3.connect(self.db)
        cur = con.cursor()
        query = """CREATE TABLE `game_info` 
        (`id`	INTEGER PRIMARY KEY AUTOINCREMENT,
        `game_id`	INTEGER,
        `file_path`	TEXT,
        FOREIGN KEY(`game_id`) REFERENCES `game`(`id`))"""
        cur.execute(query)
        cur.close()
        con.close()


if __name__ == "__main__":
    GameInfo().update_game_info()
