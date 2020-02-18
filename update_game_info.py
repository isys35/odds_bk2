import time
import sqlite3
from parser_odds import Parser
import xlwt
import os


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
        check_clear_table = 'n'
        if not table_info:
            print('[INFO] Таблицы game_info нету в базе данных')
            self.greate_game_info_table()
        else:
            check_clear_table = input('Очистить старую таблицу game_info (y/n) ')
        if check_clear_table == 'y':
            con = sqlite3.connect(self.db)
            cur = con.cursor()
            query = 'DELETE FROM game_info'
            cur.execute(query)
            con.commit()
            cur.close()
            con.close()
            folder = 'game_info'
            for the_file in os.listdir(folder):
                file_path = os.path.join(folder, the_file)
                os.unlink(file_path)
            print('[INFO] Таблица очищена')
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
        print(data)
        game_info_folder = 'game_info/'
        file_name =game_info_folder + url.replace('/', '').split('-')[-1] + '.xls'
        wb = xlwt.Workbook()
        ws = wb.add_sheet('sheet')
        aligment = xlwt.Alignment()
        aligment.horz = xlwt.Alignment.HORZ_CENTER
        style_centr_aligment = xlwt.XFStyle()
        style_centr_aligment.alignment = aligment
        #ws.col(2).width = 6000
        ws.col(0).width = 4000
        ws.col(4).width = 6000
        #ws.col(6).width = 6000
        ws.write(0, 0, str(data[3]))
        ws.write(1, 0, str(data[2]))
        ws.write(2, 0, str(data[0]))
        ws.write(4, 0, 'Букмекер')
        ws.write(4, 1, 'П1', style_centr_aligment)
        ws.write(4, 2, 'X', style_centr_aligment)
        ws.write(4, 3, 'П2', style_centr_aligment)
        ws.write(4, 4, 'Время', style_centr_aligment)
        ws.write(4, 5, 'Маржа', style_centr_aligment)
        target_row = 5
        list_for_excel = []
        for bookmaker in data[1]:
            list_for_excel.append([bookmaker,
                                   data[1][bookmaker]['open_odds'][0],
                                   data[1][bookmaker]['open_odds'][1],
                                   data[1][bookmaker]['open_odds'][2],
                                   data[1][bookmaker]['openning_change_times'][0]])
        list_for_excel.sort(key=lambda i: i[4])
        for el in list_for_excel:
            ws.write(target_row, 0, el[0])
            ws.write(target_row, 1, el[1], style_centr_aligment)
            ws.write(target_row, 4, str(time.ctime(el[4])).split(' ', 1)[1])
            ws.write(target_row, 2, el[2], style_centr_aligment)
            ws.write(target_row, 3, el[3], style_centr_aligment)
            major = ((1 / el[1] * 100)
                     + (1 / el[2] * 100)
                     + (1 / el[3] * 100)) - 100
            ws.write(target_row, 5, round(major, 2), style_centr_aligment)
            target_row += 1
            p1_real = el[1] * (1+major/100)
            x_real = el[2] * (1 + major / 100)
            p2_real = el[3] * (1 + major / 100)
            ws.write(target_row, 1, round(p1_real, 2), style_centr_aligment)
            ws.write(target_row, 2, round(x_real, 2), style_centr_aligment)
            ws.write(target_row, 3, round(p2_real, 2), style_centr_aligment)
            target_row += 1
            p1delta = p1_real-el[1]
            if p1_real > el[1]:
                p1delta = '+' + str(round(p1delta, 2))
            else:
                p1delta = '-' + str(round(p1delta, 2))
            xdelta = x_real - el[2]
            if x_real > el[2]:
                xdelta = '+' + str(round(xdelta, 2))
            else:
                xdelta = '-' + str(round(xdelta, 2))
            p2delta = p2_real - el[3]
            if p2_real > el[3]:
                p2delta = '+' + str(round(p2delta, 2))
            else:
                p2delta = '-' + str(round(p2delta, 2))
            ws.write(target_row, 1, p1delta, style_centr_aligment)
            ws.write(target_row, 2, xdelta, style_centr_aligment)
            ws.write(target_row, 3, p2delta, style_centr_aligment)
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
