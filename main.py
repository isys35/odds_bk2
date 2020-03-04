#!/usr/bin/python3
# -*- coding: utf-8 -*-
import traceback
import sys
from PyQt5 import QtGui, QtWidgets
from PyQt5.QtCore import QThread, Qt
from browsermobproxy import Server
import sqlite3
import mainwindow
import dialog
from parserv2 import ParserThread
import webbrowser
import json
import time
import xlwt
from collections import Counter
import win32com.client
import psutil
import subprocess

def eror_handler(func):
    def wrapper(self):
        try:
            func(self)
        except Exception as ex:
            print(ex)
            print(traceback.format_exc())
    return wrapper


def eror_handler_args(func):
    def wrapper(*args):
        try:
            func(*args)
        except Exception as ex:
            print(ex)
            print(traceback.format_exc())
    return wrapper


def brenchmark(func):
    def wrapper(*args):
        start = time.time()
        func(*args)
        end = time.time()
        print('[INFO] Время ' + str(end - start))
    return wrapper


def save_data_in_file(data, url):
    print(data)
    file_path = 'game_info/'
    file_name = file_path + 'info.xls'
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
    ws.write(0, 0, str(data[0][5]))
    ws.write(0, 1, str(data[0][6]))
    ws.write(0, 4, str(data[0][7]))
    ws.write(0, 2, str(data[0][8]))
    ws.write(0, 3, str(data[0][9]))
    ws.write(1, 0, str(data[0][11]))
    ws.write(1, 1, str(data[0][12]))
    ws.write(2, 0, str(data[0][10]))
    ws.write(4, 0, 'Букмекер')
    ws.write(4, 1, 'П1', style_centr_aligment)
    ws.write(4, 2, 'X', style_centr_aligment)
    ws.write(4, 3, 'П2', style_centr_aligment)
    ws.write(4, 4, 'Время', style_centr_aligment)
    ws.write(4, 5, 'Маржа', style_centr_aligment)
    target_row = 5
    list_for_excel = []
    for bookmaker in data:
        list_for_excel.append([bookmaker[0],
                                bookmaker[1],
                                bookmaker[2],
                                bookmaker[3],
                                bookmaker[4]])
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
    full_path = 'D:/Project/odds_bk2/'
    with subprocess.Popen(["start", "/WAIT", file_name], shell=True) as doc:
        doc.poll()


def get_point_result(result):
    if 'awarded' in result:
        return 0, 0
    if '(' in result:
        time_results = result.split('(')[1].split(')')[0].split(', ')
        if len(time_results) > 1:
            t1_p1 = time_results[0].split(':')[0]
            t1_p2 = time_results[0].split(':')[1]
            t2_p1 = time_results[1].split(':')[0]
            t2_p2 = time_results[1].split(':')[1]
            p1 = float(t1_p1) + float(t2_p1)
            p2 = float(t1_p2) + float(t2_p2)
            return p1, p2
        elif len(time_results) == 1:
            p1 = float(time_results[0].split(':')[0])
            p2 = float(time_results[0].split(':')[1])
            return p1, p2
    if 'Final result ' in result:
        result_out = result.replace('Final result ', '').split(' ')[0]
        p1 = float(result_out.split(':')[0])
        p2 = float(result_out.split(':')[1])
        return p1, p2


class MainApp(QtWidgets.QMainWindow, mainwindow.Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.db = 'soccer.db'
        self.parsing = False
        self.logotypes_path = self.get_logotype_path()
        self.data_bookmaker = []
        self.checkboxlist = []
        self.update_bookmakers()
        self.update_label3()
        self.findedgames_for_url = {}
        self.finded_games = []
        self.counter_bets = 0
        self.counter_games = 0
        self.pushButton_5.clicked.connect(lambda: self.open_dialog(self.finded_games))
        #self.pushButton_3.clicked.connect(lambda: self.start_thread_parsing('start'))
        #self.pushButton.clicked.connect(lambda: self.start_thread_parsing('continue'))
        #self.pushButton_2.clicked.connect(lambda: self.start_thread_parsing('lastyear'))
        self.server = Server(path=r"browsermob-proxy-2.1.4\bin\browsermob-proxy.bat",
                             options={'existing_proxy_port_to_use': 8090})
        self.server.start()
        self.pushButton_6.clicked.connect(self.find_games_href)
        self.tableWidget.cellClicked.connect(lambda row, column: self.open_dialog_from_table(row, column))
        for i in range(0, 5):
            self.tableWidget.resizeColumnToContents(i)

    def open_dialog_from_table(self, row, column):
        if column == 5:
            self.open_dialog(self.findedgames_for_url[self.tableWidget.item(row, 0).text()][0])

    @staticmethod
    def get_logotype_path():
        with open("logotypepath.json", "r") as read_file:
            return json.load(read_file)

    @brenchmark
    def update_bookmakers(self):
        """
        Обновление окна букмекеров
        :return:
        """
        print('[INFO] Берём из базы букмекерские конторы')
        con = sqlite3.connect(self.db)
        cur = con.cursor()
        query = \
            '''SELECT book.name AS book_name
                FROM bet b
                INNER JOIN bookmaker book ON b.bookmaker_id = book.id
            '''
        cur.execute(query)
        out_execute = [bookmaker[0] for bookmaker in cur.fetchall()]
        data_bookmaker_checklist = Counter(out_execute).most_common()
        data_bookmaker_checklist.sort(key=lambda i: i[1], reverse=True)
        cur.close()
        con.close()
        print('[INFO] Строим виджеты CheckBox')
        self.checkboxlist = []
        for bookmaker in data_bookmaker_checklist:
            label = QtWidgets.QLabel(self.scrollAreaWidgetContents)
            if bookmaker[0] in self.logotypes_path:
                label.setPixmap(QtGui.QPixmap(self.logotypes_path[bookmaker[0]]))
                self.formLayout.setWidget(data_bookmaker_checklist.index(bookmaker),
                                            QtWidgets.QFormLayout.LabelRole, label)
            check_box = QtWidgets.QCheckBox(self.scrollAreaWidgetContents)
            check_box.setText('{} ({})'.format(str(bookmaker[0]), str(bookmaker[1])))
            self.checkboxlist.append(check_box)
            self.formLayout.setWidget(data_bookmaker_checklist.index(bookmaker),
                                        QtWidgets.QFormLayout.FieldRole, check_box)
            self.verticalLayout.addLayout(self.formLayout)
        for check_box in self.checkboxlist:
            check_box.clicked.connect(lambda state, chck=check_box: self.unselect_allcheckbox(chck))
        self.pushButton_4.clicked.connect(self.update_finded_games)

    def update_finded_games(self):
        self.finded_games = self.find_match(self.get_select_bk(), self.lineEdit.text(),
                                            self.lineEdit_3.text(),
                                            self.lineEdit_2.text())

    def find_games_href(self):
        href = self.lineEdit_4.text()
        parser = ParserThread()
        data = parser.get_match_data(href)
        breadcump = parser.get_breadcump(href)
        _time = parser.get_date(href, full=True)
        _time =_time.split(',')[-1]
        sport = breadcump.split('»')[1]
        country = breadcump.split('»')[2]
        champ = breadcump.split('»')[3]
        command1 = breadcump.split('»')[-1].split('-')[0]
        command2 = breadcump.split('»')[-1].split('-')[-1]
        parser.browser.quit()
        p1_out = 0
        p2_out = 0
        x_out = 0
        k1_1 = 0  # -0.5к1
        k1_2 = 0  # -1.5к1
        k1_3 = 0  # -2.5к1
        k1_4 = 0  # -3.5к1
        k1_5 = 0  # -4.5к1
        k2_1 = 0  # -0.5к2
        k2_2 = 0  # -1.5к2
        k2_3 = 0  # -2.5к2
        k2_4 = 0  # -3.5к2
        k2_5 = 0  # -4.5к2
        x = 0  # X
        oz = 0  # ОЗ
        tb1 = 0  # ТБ 0.5
        tb2 = 0  # ТБ 1.5
        tb3 = 0  # ТБ 2.5
        tb4 = 0  # ТБ 3.5
        self.findedgames_for_url = {}
        for key in data[1]:
            if key != 'Betfair Exchange':
                game_data = self.find_match(key, data[1][key][0], data[1][key][1], data[1][key][2], mainlabel=False)
                points = [0, 0, 0]
                self.findedgames_for_url[key] = [game_data, points]
                for game in game_data:
                    result = game['result']
                    p1_r, p2_r = get_point_result(result)
                    if float(p1_r) > float(p2_r):
                        self.findedgames_for_url[key][1][0] += 1
                        p1_out += 1
                    elif float(p1_r) < float(p2_r):
                        self.findedgames_for_url[key][1][2] += 1
                        p2_out += 1
                    elif float(p1_r) == float(p2_r):
                        self.findedgames_for_url[key][1][1] += 1
                        x_out += 1
                    if p1_r - p2_r > 0.5:
                        k1_1 += 1
                    if p1_r - p2_r > 1.5:
                        k1_2 += 1
                    if p1_r - p2_r > 2.5:
                        k1_3 += 1
                    if p1_r - p2_r > 3.5:
                        k1_4 += 1
                    if p1_r - p2_r > 4.5:
                        k1_5 += 1
                    if p2_r - p1_r > 0.5:
                        k2_1 += 1
                    if p2_r - p1_r > 1.5:
                        k2_2 += 1
                    if p2_r - p1_r > 2.5:
                        k2_3 += 1
                    if p2_r - p1_r > 3.5:
                        k2_4 += 1
                    if p2_r - p1_r > 4.5:
                        k2_5 += 1
                    if p1_r == p2_r:
                        x += 1
                    if p1_r and p2_r:
                        oz += 1
                    if p1_r + p2_r > 0.5:
                        tb1 += 1
                    if p1_r + p2_r > 1.5:
                        tb2 += 1
                    if p1_r + p2_r > 2.5:
                        tb3 += 1
                    if p1_r + p2_r > 3.5:
                        tb4 += 1
        all_out = p1_out + p2_out + x_out
        self.label_12.setText('Найдено матчей: {}'.format(all_out))
        p1_out_percent = 0
        x_out_percent = 0
        p2_out_percent = 0
        if all_out:
            p1_out_percent = round(100 * p1_out / all_out, 2)
            p2_out_percent = round(100 * p2_out / all_out, 2)
            x_out_percent = round(100 * x_out / all_out, 2)
        if k1_1:
            k1_1_p = round(100*k1_1/all_out, 2)
            k1_1_koef = round(100/k1_1_p, 2)
            self.label_23.setText(f' {k1_1_p}% ({k1_1}) ')
            self.label_24.setText(str(k1_1_koef))
        else:
            self.label_23.setText('')
            self.label_24.setText('')
        if k1_2:
            k1_2_p = round(100*k1_2/all_out, 2)
            k1_2_koef = round(100/k1_2_p, 2)
            self.label_26.setText(f' {k1_2_p}% ({k1_2}) ')
            self.label_27.setText(str(k1_2_koef))
        else:
            self.label_26.setText('')
            self.label_27.setText('')
        if k1_3:
            k1_3_p = round(100*k1_3/all_out, 2)
            k1_3_koef = round(100/k1_3_p, 2)
            self.label_29.setText(f' {k1_3_p}% ({k1_3}) ')
            self.label_30.setText(str(k1_3_koef))
        else:
            self.label_29.setText('')
            self.label_30.setText('')
        if k1_4:
            k1_4_p = round(100*k1_4/all_out, 2)
            k1_4_koef = round(100/k1_4_p, 2)
            self.label_32.setText(f' {k1_4_p}% ({k1_4}) ')
            self.label_33.setText(str(k1_4_koef))
        else:
            self.label_32.setText('')
            self.label_33.setText('')
        if k1_5:
            k1_5_p = round(100*k1_5/all_out, 2)
            k1_5_koef = round(100/k1_5_p, 2)
            self.label_65.setText(f' {k1_5_p}% ({k1_5}) ')
            self.label_66.setText(str(k1_5_koef))
        else:
            self.label_65.setText('')
            self.label_66.setText('')
        if k2_1:
            k2_1_p = round(100*k2_1/all_out, 2)
            k2_1_koef = round(100/k2_1_p, 2)
            self.label_86.setText(f' {k2_1_p}% ({k2_1}) ')
            self.label_87.setText(str(k2_1_koef))
        else:
            self.label_86.setText('')
            self.label_87.setText('')
        if k2_2:
            k2_2_p = round(100*k2_2/all_out, 2)
            k2_2_koef = round(100/k2_2_p, 2)
            self.label_89.setText(f' {k2_2_p}% ({k2_2}) ')
            self.label_90.setText(str(k2_2_koef))
        else:
            self.label_89.setText('')
            self.label_90.setText('')
        if k2_3:
            k2_3_p = round(100*k2_3/all_out, 2)
            k2_3_koef = round(100/k2_3_p, 2)
            self.label_92.setText(f' {k2_3_p}% ({k2_3}) ')
            self.label_93.setText(str(k2_3_koef))
        else:
            self.label_92.setText('')
            self.label_93.setText('')
        if k2_4:
            k2_4_p = round(100*k2_4/all_out, 2)
            k2_4_koef = round(100/k2_4_p, 2)
            self.label_95.setText(f' {k2_4_p}% ({k2_4}) ')
            self.label_96.setText(str(k2_4_koef))
        else:
            self.label_95.setText('')
            self.label_96.setText('')
        if k2_5:
            k2_5_p = round(100*k2_5/all_out, 2)
            k2_5_koef = round(100/k2_5_p, 2)
            self.label_98.setText(f' {k2_5_p}% ({k2_5}) ')
            self.label_99.setText(str(k2_5_koef))
        else:
            self.label_98.setText('')
            self.label_99.setText('')
        if x:
            x_p = round(100*x/all_out, 2)
            x_koef = round(100 / x_p, 2)
            self.label_68.setText(f' {x_p}% ({x}) ')
            self.label_69.setText(str(x_koef))
        else:
            self.label_68.setText('')
            self.label_69.setText('')
        if oz:
            oz_p = round(100 * oz / all_out, 2)
            oz_koef = round(100 / oz_p, 2)
            self.label_71.setText(f' {oz_p}% ({oz}) ')
            self.label_72.setText(str(oz_koef))
        else:
            self.label_71.setText('')
            self.label_72.setText('')
        if tb1:
            tb1_p = round(100 * tb1 / all_out, 2)
            tb1_koef = round(100 / tb1_p, 2)
            self.label_74.setText(f' {tb1_p}% ({tb1}) ')
            self.label_75.setText(str(tb1_koef))
        else:
            self.label_74.setText('')
            self.label_75.setText('')
        if tb2:
            tb2_p = round(100 * tb2 / all_out, 2)
            tb2_koef = round(100 / tb2_p, 2)
            self.label_77.setText(f' {tb2_p}% ({tb2}) ')
            self.label_78.setText(str(tb2_koef))
        else:
            self.label_77.setText('')
            self.label_78.setText('')
        if tb3:
            tb3_p = round(100 * tb3 / all_out, 2)
            tb3_koef = round(100 / tb3_p, 2)
            self.label_80.setText(f' {tb3_p}% ({tb3}) ')
            self.label_81.setText(str(tb3_koef))
        else:
            self.label_80.setText('')
            self.label_81.setText('')
        if tb4:
            tb4_p = round(100 * tb4 / all_out, 2)
            tb4_koef = round(100 / tb4_p, 2)
            self.label_83.setText(f' {tb4_p}% ({tb4}) ')
            self.label_84.setText(str(tb4_koef))
        else:
            self.label_83.setText('')
            self.label_84.setText('')
        self.label_13.setText('П1: ' + str(round(p1_out_percent, 2)) + '% (' + str(round(p1_out)) + ')')
        self.label_14.setText('X: ' + str(round(x_out_percent, 2)) + '% (' + str(round(x_out)) + ')')
        self.label_15.setText('П2: ' + str(round(p2_out_percent, 2)) + '% (' + str(round(p2_out)) + ')')
        data_out = []
        for key in data[1]:
            data_el = [key, data[1][key][0], data[1][key][1], data[1][key][2], data[1][key][3], sport, country,
                        command1, command2, champ, data[0], data[2], _time]
            data_out.append(data_el)
        self.update_table_games()
        self.update_koef_info(data_out)
        save_data_in_file(data_out, href)

    def update_koef_info(self, data):
        print(data)

    def update_table_games(self):
        games_sort = [[key, item] for key, item in self.findedgames_for_url.items()]
        games_sort.sort(key=lambda i: len(i[1][0]), reverse=True)
        self.tableWidget.clearContents()
        games_sort = [game for game in games_sort if len(game[1][0]) > 0]
        self.tableWidget.setRowCount(len(games_sort))
        for game in games_sort:
            item_bookmaker = QtWidgets.QTableWidgetItem()
            item_bookmaker.setText(game[0])
            self.tableWidget.setItem(games_sort.index(game), 0, item_bookmaker)
            item_count_match = QtWidgets.QTableWidgetItem()
            item_count_match.setText(str(len(game[1][0])))
            self.tableWidget.setItem(games_sort.index(game), 1, item_count_match)
            item_open_dialog = QtWidgets.QTableWidgetItem()
            item_open_dialog.setText('open')
            self.tableWidget.setItem(games_sort.index(game), 5, item_open_dialog)
            sum_games = game[1][1][0] + game[1][1][1] + game[1][1][2]
            if sum_games:
                item_p1_proc = round(100*game[1][1][0]/sum_games)
                item_x_proc = round(100 * game[1][1][1] / sum_games)
                item_p2_proc = round(100 * game[1][1][2] / sum_games)
            else:
                item_p1_proc = 0
                item_x_proc = 0
                item_p2_proc = 0
            item_p1_text = '{} % ({})'.format(item_p1_proc, game[1][1][0])
            item_x_text = '{} % ({})'.format(item_x_proc, game[1][1][1])
            item_p2_text = '{} % ({})'.format(item_p2_proc, game[1][1][2])
            item_p1 = QtWidgets.QTableWidgetItem()
            item_p1.setText(item_p1_text)
            self.tableWidget.setItem(games_sort.index(game), 2, item_p1)
            item_x = QtWidgets.QTableWidgetItem()
            item_x.setText(item_x_text)
            self.tableWidget.setItem(games_sort.index(game), 3, item_x)
            item_p2 = QtWidgets.QTableWidgetItem()
            item_p2.setText(item_p2_text)
            self.tableWidget.setItem(games_sort.index(game), 4, item_p2)
        for i in range(0, 5):
            self.tableWidget.resizeColumnToContents(i)

    def get_select_bk(self):
        select_bk = None
        for check_box in self.checkboxlist:
            if check_box.isChecked():
                select_bk = check_box.text().rsplit(' ', maxsplit=1)[0]
                return select_bk
        if not select_bk:
            print('[WARNING] Не выбрана букмекерская контора')
            return select_bk

    def update_label3(self):
        """
        Обновление счётчика " всего игр в базе"
        :return:
        """
        con = sqlite3.connect(self.db)
        cur = con.cursor()
        query = 'SELECT COUNT(*) FROM game'
        cur.execute(query)
        all_game_count = cur.fetchone()
        self.label_3.setText('Всего игр в базе: ' + str(all_game_count[0]))
        cur.close()
        con.close()

    def find_match(self, bookmaker, p1, x, p2, mainlabel=True):
        """
        поиск совпадений
        :return:
        список игр
        """
        if not bookmaker:
            return
        con = sqlite3.connect(self.db)
        cur = con.cursor()
        query = 'SELECT id FROM bookmaker WHERE name = ?'
        cur.execute(query, [bookmaker])
        bookmaker_id_list = cur.fetchone()
        if bookmaker_id_list:
            bookmaker_id = bookmaker_id_list[0]
        else:
            cur.execute('INSERT INTO bookmaker (name) VALUES(?)', [bookmaker])
            con.commit()
            cur.execute(query, [bookmaker])
            bookmaker_id = cur.fetchone()[0]
        # Добавить разные инфо если не введени какие нибудь из значений
        if not p1 or not x or not p2:
            print('[WARNING] Введенны не все коэф-ты')
            return
        print('[INFO] Поиск в базе игры с букмекером {} П1 = {} X = {} П2 = {}'.format(bookmaker, p1, x, p2))
        query = 'SELECT game_id FROM bet WHERE ' \
                'bookmaker_id = {} AND p1 = {} AND x = {} AND p2 = {}'.format(bookmaker_id, p1, x, p2)
        print([bookmaker_id, p1, x, p2])
        cur.execute(query)
        matches_finded = []
        for match_id in cur.fetchall():
            if match_id[0] not in matches_finded:
                matches_finded.append(match_id[0])
        if mainlabel:
            self.label_7.setText('Найдено матчей: ' + str(len(matches_finded)))
        print('[INFO] Найдено матчей: ' + str(len(matches_finded)))
        games = []
        if matches_finded:
            for game_id in matches_finded:

                query = '''
                            SELECT id, command1, command2, url, date, timematch,
                            result, sport, country, liga, url_api FROM game 
                            WHERE id = {}
                        '''.format(game_id)
                cur.execute(query)
                data_list = cur.fetchone()
                data_dict = {'id': data_list[0],
                             'command1': data_list[1],
                             'command2': data_list[2],
                             'url': data_list[3],
                             'date': data_list[4],
                             'time': data_list[5],
                             'result': data_list[6],
                             'sport': data_list[7],
                             'country': data_list[8],
                             'champ': data_list[9],
                             'url_api': data_list[10]}
                games.append(data_dict)
            p1_out = 0
            p2_out = 0
            x_out = 0
            for game in games:
                result = game['result']
                p1_r, p2_r = get_point_result(result)
                if float(p1_r) > float(p2_r):
                    p1_out += 1
                elif float(p1_r) < float(p2_r):
                    p2_out += 1
                elif float(p1_r) == float(p2_r):
                    x_out += 1
            all_out = p1_out + p2_out + x_out
            p1_out_percent = 0
            x_out_percent = 0
            p2_out_percent = 0
            if all_out:
                p1_out_percent = 100 * p1_out / all_out
                p2_out_percent = 100 * p2_out / all_out
                x_out_percent = 100 * x_out / all_out
            if mainlabel:
                self.label_9.setText('П1: ' + str(round(p1_out_percent)) + '% (' + str(round(p1_out)) + ')')
                self.label_10.setText('X: ' + str(round(x_out_percent)) + '% (' + str(round(x_out)) + ')')
                self.label_8.setText('П2: ' + str(round(p2_out_percent)) + '% (' + str(round(p2_out)) + ')')
        else:
            if mainlabel:
                self.label_9.setText('П1:')
                self.label_10.setText('X:')
                self.label_8.setText('П2:')
        cur.close()
        con.close()
        return games

    @staticmethod
    def clear_layout(layout):
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def unselect_allcheckbox(self, check_box):
        """
        снять выеделение со всех check_box
        :param check_box:
        :return:
        """
        for check in self.checkboxlist:
            if check != check_box:
                check.setChecked(False)

    def open_dialog(self, g):
        """
        Открыть диалоговое окно
        :return:
        """
        dial = Dialog()
        dial.games = g
        dial.update_table_games(g)
        dial.update_info(g)
        dial.exec_()


class Dialog(QtWidgets.QDialog, dialog.Ui_Dialog):
    def __init__(self):
        super().__init__()
        self.db = 'soccer.db'
        self.setupUi(self)
        self.games = []
        self.lineEdit.textChanged.connect(self.change_filter)
        self.lineEdit_2.textChanged.connect(self.change_filter)
        self.lineEdit_3.textChanged.connect(self.change_filter)
        self.tableWidget.cellClicked.connect(lambda row, column: self.open_page_in_browser(row, column))
        self.tableWidget.cellClicked.connect(lambda row, column: self.open_excel_file(row, column))

    def update_table_games(self, games):
        """
        Обновить таблицу с играми
        :param games:
        :return:
        """
        self.tableWidget.clearContents()
        self.tableWidget.setRowCount(len(games))
        for game in games:
            item_index = QtWidgets.QTableWidgetItem()
            item_index.setText(str(games.index(game)))
            self.tableWidget.setVerticalHeaderItem(games.index(game), item_index)
            item_command1 = QtWidgets.QTableWidgetItem()
            item_command1.setTextAlignment(Qt.AlignHCenter)
            item_command1.setText(game['command1'])
            self.tableWidget.setItem(games.index(game), 5, item_command1)
            item_command2 = QtWidgets.QTableWidgetItem()
            item_command2.setTextAlignment(Qt.AlignHCenter)
            item_command2.setText(game['command2'])
            self.tableWidget.setItem(games.index(game), 6, item_command2)
            item_url = QtWidgets.QTableWidgetItem()
            item_url.setText(game['url'])
            self.tableWidget.setItem(games.index(game), 8, item_url)
            item_date = QtWidgets.QTableWidgetItem()
            if game['date']:
                item_date.setText(game['date'].rsplit(' ', 1)[0])
                item_date.setTextAlignment(Qt.AlignHCenter)
            self.tableWidget.setItem(games.index(game), 1, item_date)
            self.tableWidget.resizeColumnToContents(1)
            item_year = QtWidgets.QTableWidgetItem()
            if game['date']:
                item_year.setText(game['date'].rsplit(' ', 1)[1])
                item_year.setTextAlignment(Qt.AlignHCenter)
            self.tableWidget.setItem(games.index(game), 0, item_year)
            self.tableWidget.resizeColumnToContents(0)
            item_time = QtWidgets.QTableWidgetItem()
            item_time.setText(game['time'])
            item_time.setTextAlignment(Qt.AlignHCenter)
            self.tableWidget.setItem(games.index(game), 2, item_time)
            self.tableWidget.resizeColumnToContents(2)
            item_result = QtWidgets.QTableWidgetItem()
            item_result.setText(game['result'])
            self.tableWidget.setItem(games.index(game), 7, item_result)
            self.tableWidget.resizeColumnToContents(7)
            item_country = QtWidgets.QTableWidgetItem()
            item_country.setText(game['country'])
            item_country.setTextAlignment(Qt.AlignHCenter)
            self.tableWidget.setItem(games.index(game), 3, item_country)
            self.tableWidget.resizeColumnToContents(3)
            item_liga = QtWidgets.QTableWidgetItem()
            item_liga.setText(game['champ'])
            item_liga.setTextAlignment(Qt.AlignHCenter)
            self.tableWidget.setItem(games.index(game), 4, item_liga)
            item_click = QtWidgets.QTableWidgetItem()
            item_click.setText('Перейти на сайт')
            self.tableWidget.setItem(games.index(game), 9, item_click)
            self.tableWidget.resizeColumnToContents(9)
            item_info = QtWidgets.QTableWidgetItem()
            item_info.setText('Файл информации')
            self.tableWidget.setItem(games.index(game), 10, item_info)
            self.tableWidget.resizeColumnToContents(10)

    def change_filter(self):
        """
        Фильтр
        :return:
        """
        games_filt = []
        for game in self.games:
            year_in_game = game['date'].split(' ')[-1]
            country_in_game = game['country'].lower()
            champ_in_game = game['champ'].lower()
            if self.lineEdit.text() in year_in_game \
                    and self.lineEdit_2.text() in country_in_game \
                    and self.lineEdit_3.text() in champ_in_game:
                games_filt.append(game)
        self.update_table_games(games_filt)
        self.update_info(games_filt)

    def update_info(self, games):
        k1_1 = 0  # -0.5к1
        k1_2 = 0  # -1.5к1
        k1_3 = 0  # -2.5к1
        k1_4 = 0  # -3.5к1
        k1_5 = 0  # -4.5к1
        k2_1 = 0  # -0.5к2
        k2_2 = 0  # -1.5к2
        k2_3 = 0  # -2.5к2
        k2_4 = 0  # -3.5к2
        k2_5 = 0  # -4.5к2
        x = 0  # X
        oz = 0  # ОЗ
        tb1 = 0  # ТБ 0.5
        tb2 = 0  # ТБ 1.5
        tb3 = 0  # ТБ 2.5
        tb4 = 0  # ТБ 3.5
        for game in games:
            p1, p2 = get_point_result(game['result'])
            if p1 - p2 > 0.5:
                k1_1 += 1
            if p1 - p2 > 1.5:
                k1_2 += 1
            if p1 - p2 > 2.5:
                k1_3 += 1
            if p1 - p2 > 3.5:
                k1_4 += 1
            if p1 - p2 > 4.5:
                k1_5 += 1
            if p2 - p1 > 0.5:
                k2_1 += 1
            if p2 - p1 > 1.5:
                k2_2 += 1
            if p2 - p1 > 2.5:
                k2_3 += 1
            if p2 - p1 > 3.5:
                k2_4 += 1
            if p2 - p1 > 4.5:
                k2_5 += 1
            if p1 == p2:
                x += 1
            if p1 and p2:
                oz += 1
            if p1 + p2 > 0.5:
                tb1 += 1
            if p1 + p2 > 1.5:
                tb2 += 1
            if p1 + p2 > 2.5:
                tb3 += 1
            if p1 + p2 > 3.5:
                tb4 += 1
        if k1_1:
            k1_1_p = round(100*k1_1/len(games), 2)
            k1_1_koef = round(100/k1_1_p, 2)
            self.label_6.setText(f' {k1_1_p}% ({k1_1}) ')
            self.label_4.setText(str(k1_1_koef))
        else:
            self.label_6.setText('')
            self.label_4.setText('')
        if k1_2:
            k1_2_p = round(100*k1_2/len(games), 2)
            k1_2_koef = round(100/k1_2_p, 2)
            self.label_11.setText(f' {k1_2_p}% ({k1_2}) ')
            self.label_10.setText(str(k1_2_koef))
        else:
            self.label_11.setText('')
            self.label_10.setText('')
        if k1_3:
            k1_3_p = round(100*k1_3/len(games), 2)
            k1_3_koef = round(100/k1_3_p, 2)
            self.label_14.setText(f' {k1_3_p}% ({k1_3}) ')
            self.label_13.setText(str(k1_3_koef))
        else:
            self.label_14.setText('')
            self.label_13.setText('')
        if k1_4:
            k1_4_p = round(100*k1_4/len(games), 2)
            k1_4_koef = round(100/k1_4_p, 2)
            self.label_17.setText(f' {k1_4_p}% ({k1_4}) ')
            self.label_16.setText(str(k1_4_koef))
        else:
            self.label_17.setText('')
            self.label_16.setText('')
        if k1_5:
            k1_5_p = round(100*k1_5/len(games), 2)
            k1_5_koef = round(100/k1_5_p, 2)
            self.label_7.setText(f' {k1_5_p}% ({k1_5}) ')
            self.label_9.setText(str(k1_5_koef))
        else:
            self.label_7.setText('')
            self.label_9.setText('')
        if k2_1:
            k2_1_p = round(100*k2_1/len(games), 2)
            k2_1_koef = round(100/k2_1_p, 2)
            self.label_44.setText(f' {k2_1_p}% ({k2_1}) ')
            self.label_45.setText(str(k2_1_koef))
        else:
            self.label_44.setText('')
            self.label_45.setText('')
        if k2_2:
            k2_2_p = round(100*k2_2/len(games), 2)
            k2_2_koef = round(100/k2_2_p, 2)
            self.label_38.setText(f' {k2_2_p}% ({k2_2}) ')
            self.label_39.setText(str(k2_2_koef))
        else:
            self.label_38.setText('')
            self.label_39.setText('')
        if k2_3:
            k2_3_p = round(100*k2_3/len(games), 2)
            k2_3_koef = round(100/k2_3_p, 2)
            self.label_35.setText(f' {k2_3_p}% ({k2_3}) ')
            self.label_36.setText(str(k2_3_koef))
        else:
            self.label_35.setText('')
            self.label_36.setText('')
        if k2_4:
            k2_4_p = round(100*k2_4/len(games), 2)
            k2_4_koef = round(100/k2_4_p, 2)
            self.label_41.setText(f' {k2_4_p}% ({k2_4}) ')
            self.label_42.setText(str(k2_4_koef))
        else:
            self.label_41.setText('')
            self.label_42.setText('')
        if k2_5:
            k2_5_p = round(100*k2_5/len(games), 2)
            k2_5_koef = round(100/k2_5_p, 2)
            self.label_47.setText(f' {k2_5_p}% ({k2_5}) ')
            self.label_48.setText(str(k2_5_koef))
        else:
            self.label_47.setText('')
            self.label_48.setText('')
        if x:
            x_p = round(100*x/len(games), 2)
            x_koef = round(100 / x_p, 2)
            self.label_50.setText(f' {x_p}% ({x}) ')
            self.label_51.setText(str(x_koef))
        else:
            self.label_50.setText('')
            self.label_51.setText('')
        if oz:
            oz_p = round(100 * oz / len(games), 2)
            oz_koef = round(100 / oz_p, 2)
            self.label_53.setText(f' {oz_p}% ({oz}) ')
            self.label_54.setText(str(oz_koef))
        else:
            self.label_53.setText('')
            self.label_54.setText('')
        if tb1:
            tb1_p = round(100 * tb1 / len(games), 2)
            tb1_koef = round(100 / tb1_p, 2)
            self.label_56.setText(f' {tb1_p}% ({tb1}) ')
            self.label_57.setText(str(tb1_koef))
        else:
            self.label_56.setText('')
            self.label_57.setText('')
        if tb2:
            tb2_p = round(100 * tb2 / len(games), 2)
            tb2_koef = round(100 / tb2_p, 2)
            self.label_59.setText(f' {tb2_p}% ({tb2}) ')
            self.label_60.setText(str(tb2_koef))
        else:
            self.label_59.setText('')
            self.label_60.setText('')
        if tb3:
            tb3_p = round(100 * tb3 / len(games), 2)
            tb3_koef = round(100 / tb3_p, 2)
            self.label_20.setText(f' {tb3_p}% ({tb3}) ')
            self.label_19.setText(str(tb3_koef))
        else:
            self.label_20.setText('')
            self.label_19.setText('')
        if tb4:
            tb4_p = round(100 * tb4 / len(games), 2)
            tb4_koef = round(100 / tb4_p, 2)
            self.label_62.setText(f' {tb4_p}% ({tb4}) ')
            self.label_63.setText(str(tb4_koef))
        else:
            self.label_62.setText('')
            self.label_63.setText('')

    def open_page_in_browser(self, row, column):
        """
        Открывает страницу в браузере
        :param row:
        :param column:
        :return:
        """
        if column == 9:
            url = self.tableWidget.item(row, 8).text()
            webbrowser.open(url)

    @eror_handler_args
    def open_excel_file(self, row, column):
        if column == 10:
            url = self.tableWidget.item(row, 8).text()
            data = self.get_data(url)
            save_data_in_file(data, url)

    def get_data(self, url):
        print(url)
        con = sqlite3.connect(self.db)
        cur = con.cursor()
        query = 'SELECT book.name, b.p1, b.x, b.p2, b.open_time, g.sport,' \
                ' g.country, g.command1, g.command2, g.liga, g.result, g.date, g.timematch  ' \
                ' FROM bet b' \
                ' JOIN bookmaker book ON b.bookmaker_id = book.id JOIN game g ON b.game_id = g.id ' \
                'WHERE g.url = ?'
        cur.execute(query, [url])
        data = cur.fetchall()
        cur.close()
        con.close()
        return data


def main():
    try:
        app = QtWidgets.QApplication(sys.argv)
        window = MainApp()
        window.show()
        app.exec_()
    except Exception as ex:
        print(ex)
        print(traceback.format_exc())


if __name__ == '__main__':
    main()
