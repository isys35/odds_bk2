#!/usr/bin/python3
# -*- coding: utf-8 -*-
import traceback
import sys
from PyQt5 import QtGui, QtWidgets
from PyQt5.QtCore import QThread
import sqlite3
import mainwindow
import dialog
from parser_odds import Parser
import webbrowser
import json


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


class MainApp(QtWidgets.QMainWindow, mainwindow.Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.db = 'oddsportal.db'
        self.parsing = False
        self.logotypes_path = self.get_logotype_path()
        self.data_bookmaker = []
        self.checkboxlist = []
        self.update_bookmakers()
        self.update_label3()
        self.matches_finded = []
        self.games = []
        self.pushButton_2.clicked.connect(self.open_dialog)
        self.pushButton_4.clicked.connect(lambda: self.start_thread_parsing('start'))
        self.pushButton_3.clicked.connect(lambda: self.start_thread_parsing('continue'))
        self.pushButton_5.clicked.connect(lambda: self.start_thread_parsing('lastyear'))
        self.tableWidget.cellClicked.connect(lambda row, column: self.open_page_in_browser(row, column))
        self.parser = Parser(label_info=self.label_8, label_info2=self.label_9, label_info3=self.label_11)

    @staticmethod
    def get_logotype_path():
        with open("logotypepath.json", "r") as read_file:
            return json.load(read_file)

    def update_bookmakers(self):
        """
        Обновление окна букмекеров
        :return:
        """
        print('[INFO] Берём из базы букмекерские конторы')
        con = sqlite3.connect(self.db)
        cur = con.cursor()
        query = 'SELECT * FROM bookmaker'
        cur.execute(query)
        self.data_bookmaker = [[bookmaker[0], bookmaker[1]] for bookmaker in cur.fetchall()]
        data_bookmaker_checklist = []
        print('[INFO] Получаем кол-во матчей для каждого букмекера')
        for bookmaker in self.data_bookmaker:
            query = 'SELECT * FROM bet WHERE bookmaker_id = ?'
            cur.execute(query, [bookmaker[0]])
            count_bookmaker_match = len(cur.fetchall())
            data_bookmaker_checklist.append([count_bookmaker_match, bookmaker[1]])
        cur.close()
        con.close()
        data_bookmaker_checklist.sort(reverse=True)
        print('[INFO] Строим виджеты CheckBox')
        self.checkboxlist = []
        for bookmaker in data_bookmaker_checklist:
            label = QtWidgets.QLabel(self.scrollAreaWidgetContents)
            if bookmaker[1] in self.logotypes_path:
                label.setPixmap(QtGui.QPixmap(self.logotypes_path[bookmaker[1]]))
                self.formLayout_2.setWidget(data_bookmaker_checklist.index(bookmaker),
                                            QtWidgets.QFormLayout.LabelRole, label)
            check_box = QtWidgets.QCheckBox(self.scrollAreaWidgetContents)
            check_box.setText('{} ({})'.format(str(bookmaker[1]), str(bookmaker[0])))
            self.checkboxlist.append(check_box)
            self.formLayout_2.setWidget(data_bookmaker_checklist.index(bookmaker),
                                        QtWidgets.QFormLayout.FieldRole, check_box)
            self.verticalLayout.addLayout(self.formLayout_2)
        for check_box in self.checkboxlist:
            check_box.clicked.connect(lambda state, chck=check_box: self.unselect_allcheckbox(chck))
        self.pushButton.clicked.connect(self.find_match)

    def update_label3(self):
        """
        Обновление счётчика " всего игр в базе"
        :return:
        """
        con = sqlite3.connect(self.db)
        cur = con.cursor()
        query = 'SELECT id FROM game'
        cur.execute(query)
        all_game_count = len(cur.fetchall())
        self.label_11.setText('Всего игр в базе: ' + str(all_game_count))
        cur.close()
        con.close()

    @eror_handler
    def find_match(self):
        """
        поиск совпадений
        :return:
        """
        select_bk = None
        for check_box in self.checkboxlist:
            if check_box.isChecked():
                select_bk = check_box.text().rsplit(' ', maxsplit=1)[0]
        bookmaker_id = None
        for bk in self.data_bookmaker:
            if bk[1] == select_bk:
                bookmaker_id = bk[0]
                break
        if not select_bk:
            print('[WARNING] Не выбрана букмекерская контора')
            return
        # Добавить разные инфо если не введени какие нибудь из значений
        p1 = self.lineEdit.text()
        x = self.lineEdit_2.text()
        p2 = self.lineEdit_3.text()
        if not p1 or not x or not p2:
            print('[WARNING] Введенны не все коэф-ты')
            return
        print('[INFO] Поиск в базе игры с букмекером {} П1 = {} X = {} П2 = {}'.format(select_bk, p1, x, p2))
        con = sqlite3.connect(self.db)
        cur = con.cursor()
        query = 'SELECT game_id FROM bet WHERE bookmaker_id = ? AND p1 = ? AND x = ? AND p2 = ?'
        cur.execute(query, [bookmaker_id, p1, x, p2])
        self.matches_finded = []
        for match_id in cur.fetchall():
            if match_id[0] not in self.matches_finded:
                self.matches_finded.append(match_id[0])
        self.label.setText('Найдено матчей: ' + str(len(self.matches_finded)))
        print('[INFO] Найдено матчей: ' + str(len(self.matches_finded)))
        self.games = []
        if self.matches_finded:
            for game_id in self.matches_finded:
                query = 'SELECT * FROM game WHERE id = ?'
                cur.execute(query, [game_id])
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
                             'champ': data_list[9]}
                self.games.append(data_dict)
            p1_out = 0
            p2_out = 0
            x_out = 0
            for game in self.games:
                result = game['result']
                p1_r, p2_r = self.get_point_result(result)
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
            self.label_6.setText('П1: ' + str(round(p1_out_percent)) + '% (' + str(round(p1_out)) + ')')
            self.label_5.setText('X: ' + str(round(x_out_percent)) + '% (' + str(round(x_out)) + ')')
            self.label_7.setText('П2: ' + str(round(p2_out_percent)) + '% (' + str(round(p2_out)) + ')')
        else:
            self.label_6.setText('П1:')
            self.label_5.setText('X:')
            self.label_7.setText('П2:')
        self.update_table()
        cur.close()
        con.close()

    @staticmethod
    def get_point_result(result):
        """
        Получить результат матчей в числах
        :param result:
        Результат из базы
        :return:
        p1,p2 - количество очков у комманд
        """
        if 'awarded' in result:
            return 0, 0
        if '(' in result:
            time_results = result.split('(')[1].split(')')[0].split(', ')
            if len(time_results) == 2:
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

    def unselect_allcheckbox(self, check_box):
        """
        снять выеделение со всех check_box
        :param check_box:
        :return:
        """
        for check in self.checkboxlist:
            if check != check_box:
                check.setChecked(False)

    @eror_handler
    def open_dialog(self):
        """
        Открыть диалоговое окно
        :return:
        """
        dialog = Dialog()
        dialog.games = self.games
        dialog.update_table_games(self.games)
        dialog.exec_()

    def start_thread_parsing(self, method):
        """
        Запуск потока парсера
        :param method:
        :return:
        """
        self.parsing = ParsingThread(self.parser, method)
        self.parsing.start()

    def update_table(self):
        """
        Обновление таблицы
        :return:
        """
        self.tableWidget.clearContents()
        self.tableWidget.setRowCount(len(self.games))
        for game in self.games:
            item_command1 = QtWidgets.QTableWidgetItem()
            item_command1.setText(game['command1'])
            self.tableWidget.setItem(self.games.index(game), 2, item_command1)
            item_command2 = QtWidgets.QTableWidgetItem()
            item_command2.setText(game['command2'])
            self.tableWidget.setItem(self.games.index(game), 3, item_command2)
            item_date = QtWidgets.QTableWidgetItem()
            item_date.setText(game['date'])
            self.tableWidget.setItem(self.games.index(game), 0, item_date)
            self.tableWidget.resizeColumnToContents(2)
            item_country = QtWidgets.QTableWidgetItem()
            item_country.setText(game['country'])
            self.tableWidget.setItem(self.games.index(game), 1, item_country)
            self.tableWidget.resizeColumnToContents(3)
            item_result = QtWidgets.QTableWidgetItem()
            item_result.setText(game['result'])
            self.tableWidget.setItem(self.games.index(game), 4, item_result)
            self.tableWidget.resizeColumnToContents(4)
            item_clicked = QtWidgets.QTableWidgetItem()
            item_clicked.setText('Перейти на сайт')
            self.tableWidget.setItem(self.games.index(game), 5, item_clicked)
            self.tableWidget.resizeColumnToContents(5)

    def open_page_in_browser(self, row, column):
        """
        Открыть игру в браузере
        :param row:
        ряд, а также номер игры в листе self.games
        :param column:
        колонка на которую следует нажать
        :return:
        """
        if column == 5:
            url = self.games[row]['url']
            print(url)
            webbrowser.open(url)


class Dialog(QtWidgets.QDialog, dialog.Ui_Dialog):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.games = []
        self.lineEdit.textChanged.connect(self.change_filter)
        self.lineEdit_2.textChanged.connect(self.change_filter)
        self.lineEdit_3.textChanged.connect(self.change_filter)
        self.tableWidget.cellClicked.connect(lambda row, column: self.open_page_in_browser(row, column))

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
            item_command1.setText(game['command1'])
            self.tableWidget.setItem(games.index(game), 5, item_command1)
            item_command2 = QtWidgets.QTableWidgetItem()
            item_command2.setText(game['command2'])
            self.tableWidget.setItem(games.index(game), 6, item_command2)
            item_url = QtWidgets.QTableWidgetItem()
            item_url.setText(game['url'])
            self.tableWidget.setItem(games.index(game), 8, item_url)
            item_date = QtWidgets.QTableWidgetItem()
            if game['date']:
                item_date.setText(game['date'].rsplit(' ', 1)[0])
            self.tableWidget.setItem(games.index(game), 1, item_date)
            self.tableWidget.resizeColumnToContents(1)
            item_year = QtWidgets.QTableWidgetItem()
            if game['date']:
                item_year.setText(game['date'].rsplit(' ', 1)[1])
            self.tableWidget.setItem(games.index(game), 0, item_year)
            self.tableWidget.resizeColumnToContents(0)
            item_time = QtWidgets.QTableWidgetItem()
            item_time.setText(game['time'])
            self.tableWidget.setItem(games.index(game), 2, item_time)
            self.tableWidget.resizeColumnToContents(2)
            item_result = QtWidgets.QTableWidgetItem()
            item_result.setText(game['result'])
            self.tableWidget.setItem(games.index(game), 7, item_result)
            self.tableWidget.resizeColumnToContents(7)
            item_country = QtWidgets.QTableWidgetItem()
            item_country.setText(game['country'])
            self.tableWidget.setItem(games.index(game), 3, item_country)
            self.tableWidget.resizeColumnToContents(3)
            item_liga = QtWidgets.QTableWidgetItem()
            item_liga.setText(game['champ'])
            self.tableWidget.setItem(games.index(game), 4, item_liga)
            item_click = QtWidgets.QTableWidgetItem()
            item_click.setText('Перейти на сайт')
            self.tableWidget.setItem(games.index(game), 9, item_click)
            self.tableWidget.resizeColumnToContents(9)

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


class ParsingThread(QThread):
    def __init__(self, parser, method):
        super().__init__()
        self.parser = parser
        self.method = method

    def update_db(self):
        print('[INFO] Запускаем парсер')
        if self.method == 'start':
            self.parser.start('soccer')
        elif self.method == 'continue':
            self.parser.start('soccer', continue_parsing=True)
        elif self.method == 'lastyear':
            self.parser.start('soccer', last_year=True)
        else:
            print('[WARNING] Метод {} не найден '.format(self.method))

    def run(self):
        self.update_db()


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
