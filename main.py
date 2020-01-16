#!/usr/bin/python3
# -*- coding: utf-8 -*-
import traceback
import sys
import sqlite3
from PyQt5 import QtGui, QtWidgets
from PyQt5.QtCore import QThread
import sqlite3
import mainwindow
import dialog
from parser_odds import Parser
import webbrowser
import json


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
        self.liga_dict = {}
        # self.comboBox_2.popupAboutToBeShown.connect(self.update_combobox)
        # self.pushButton_3.clicked.connect(self.filtered)
        self.pushButton_2.clicked.connect(self.open_dialog)
        self.pushButton_4.clicked.connect(self.start_thread_parsing)
        self.pushButton_3.clicked.connect(self.continue_thread_parsing)
        self.pushButton_5.clicked.connect(self.last_year_thread_parsing)
        self.tableWidget.cellClicked.connect(lambda row, column: self.open_page_in_browser(row, column))

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
            checkBox = QtWidgets.QCheckBox(self.scrollAreaWidgetContents)
            checkBox.setText('{} ({})'.format(str(bookmaker[1]), str(bookmaker[0])))
            self.checkboxlist.append(checkBox)
            self.formLayout_2.setWidget(data_bookmaker_checklist.index(bookmaker),
                                        QtWidgets.QFormLayout.FieldRole, checkBox)
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
        query = 'SELECT * FROM game'
        cur.execute(query)
        all_game_count = len(cur.fetchall())
        self.label_11.setText('Всего игр в базе: ' + str(all_game_count))
        cur.close()
        con.close()

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
        self.update_table()

        #     for game in self.games:
        #         result = game[6]
        #         p1_r, p2_r = self.result_cleaning(result)
        #         if float(p1_r) > float(p2_r):
        #             p1_out += 1
        #         elif float(p1_r) < float(p2_r):
        #             p2_out += 1
        #         elif float(p1_r) == float(p2_r):
        #             x_out += 1
        #     all_out = p1_out + p2_out + x_out
        #     p1_out_ = 0
        #     x_out_ = 0
        #     p2_out_ = 0
        #     if all_out:
        #         p1_out_ = 100 * p1_out / all_out
        #         p2_out_ = 100 * p2_out / all_out
        #         x_out_ = 100 * x_out / all_out
        #     self.label_6.setText('П1: ' + str(round(p1_out_)) + '% (' + str(round(p1_out)) + ')')
        #     self.label_5.setText('X: ' + str(round(x_out_)) + '% (' + str(round(x_out)) + ')')
        #     self.label_7.setText('П2: ' + str(round(p2_out_)) + '% (' + str(round(p2_out)) + ')')
        #     countrys = []
        #     self.liga_dict = {}
        #     for game in self.games:
        #         if game[8] not in countrys:
        #             countrys.append(game[8])
        #         if game[8] not in self.liga_dict:
        #             self.liga_dict[game[8]] = [game[9]]
        #         else:
        #             if game[9] not in self.liga_dict[game[8]]:
        #                 self.liga_dict[game[8]].append(game[9])
        # con.close()
        # cur.close()

    def get_point_result(self, result: str):
        """
        Получить результат матчей в числах
        :param result:
        Результат из базы
        :return:
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
                p1 = time_results[0].split(':')[0]
                p2 = time_results[0].split(':')[1]
                return float(p1), float(p2)
        elif 'Final result ' in result:
            result_out = result.replace('Final result ', '').split(' ')[0]
            p1 = result_out.split(':')[0]
            p2 = result_out.split(':')[1]
            return p1, p2

    def unselect_allcheckbox(self, check_box):
        for check in self.checkboxlist:
            if check != check_box:
                check.setChecked(False)

    def open_dialog(self):
        try:
            dialog = Dialog()
            dialog.games = self.games
            dialog.update_games(self.games)
            dialog.exec_()
        except Exception:
            print(traceback.format_exc())

    def start_thread_parsing(self):
        self.parsing = ParsingThread(self.label_8, self.label_9, self.label_11)
        self.parsing.start()

    def continue_thread_parsing(self):
        self.parsing = ParsingThreadContinue(self.label_8, self.label_9, self.label_11)
        self.parsing.start()

    def last_year_thread_parsing(self):
        self.parsing = ParsingThreadLastYear(self.label_8, self.label_9, self.label_11)
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
        self.lineEdit.textChanged.connect(lambda: self.change_year(self.lineEdit.text()))
        self.lineEdit_2.textChanged.connect(lambda: self.change_country(self.lineEdit_2.text()))
        self.lineEdit_3.textChanged.connect(lambda: self.change_champ(self.lineEdit_3.text()))
        self.tableWidget.cellClicked.connect(lambda row, column: self.open_page_in_browser(row, column))

    def update_games(self, games):
        self.tableWidget.clearContents()
        self.tableWidget.setRowCount(len(games))
        for game in games:
            item_index = QtWidgets.QTableWidgetItem()
            item_index.setText(str(games.index(game)))
            self.tableWidget.setVerticalHeaderItem(games.index(game), item_index)
            item_command1 = QtWidgets.QTableWidgetItem()
            item_command1.setText(game[1])
            self.tableWidget.setItem(games.index(game), 5, item_command1)
            item_command2 = QtWidgets.QTableWidgetItem()
            item_command2.setText(game[2])
            self.tableWidget.setItem(games.index(game), 6, item_command2)
            item_url = QtWidgets.QTableWidgetItem()
            item_url.setText(game[3])
            self.tableWidget.setItem(games.index(game), 8, item_url)
            item_date = QtWidgets.QTableWidgetItem()
            if game[4]:
                item_date.setText(game[4].rsplit(' ', 1)[0])
            self.tableWidget.setItem(games.index(game), 1, item_date)
            self.tableWidget.resizeColumnToContents(1)
            item_year = QtWidgets.QTableWidgetItem()
            if game[4]:
                item_year.setText(game[4].rsplit(' ', 1)[1])
            self.tableWidget.setItem(games.index(game), 0, item_year)
            self.tableWidget.resizeColumnToContents(0)
            item_time = QtWidgets.QTableWidgetItem()
            item_time.setText(game[5])
            self.tableWidget.setItem(games.index(game), 2, item_time)
            self.tableWidget.resizeColumnToContents(2)
            item_result = QtWidgets.QTableWidgetItem()
            item_result.setText(game[6])
            self.tableWidget.setItem(games.index(game), 7, item_result)
            self.tableWidget.resizeColumnToContents(7)
            item_country = QtWidgets.QTableWidgetItem()
            item_country.setText(game[8])
            self.tableWidget.setItem(games.index(game), 3, item_country)
            self.tableWidget.resizeColumnToContents(3)
            item_liga = QtWidgets.QTableWidgetItem()
            item_liga.setText(game[9])
            self.tableWidget.setItem(games.index(game), 4, item_liga)
            item_click = QtWidgets.QTableWidgetItem()
            item_click.setText('Перейти на сайт')
            self.tableWidget.setItem(games.index(game), 9, item_click)
            self.tableWidget.resizeColumnToContents(9)

    def change_year(self, year):
        games_filt = []
        for game in self.games:
            year_in_game = game[4].split(' ')[-1]
            if year in year_in_game:
                games_filt.append(game)
        self.update_games(games_filt)

    def change_country(self, country):
        games_filt = []
        for game in self.games:
            country_in_game = game[8].lower()
            if country.lower() in country_in_game:
                games_filt.append(game)
        self.update_games(games_filt)

    def change_champ(self, champ):
        games_filt = []
        for game in self.games:
            champ_in_game = game[9].lower()
            if champ.lower() in champ_in_game:
                games_filt.append(game)
        self.update_games(games_filt)

    def open_page_in_browser(self, row, column):
        if column == 9:
            url = self.tableWidget.item(row, 8).text()
            webbrowser.open(url)


class ParsingThread(QThread):
    def __init__(self, label, label2, label3):
        super().__init__()
        self.parser = None
        self.label = label
        self.label2 = label2
        self.label3 = label3

    def update_db(self):
        print('[INFO] Запускаем парсер')
        self.parser = Parser(self.label, self.label2, self.label3)
        # noinspection PyBroadException
        try:
            self.parser.start()
        except Exception:
            print(traceback.format_exc())

    def run(self):
        self.update_db()


class ParsingThreadContinue(QThread):
    def __init__(self, label, label2, label3):
        super().__init__()
        self.parser = None
        self.label = label
        self.label2 = label2
        self.label3 = label3

    def update_db(self):
        print('[INFO] Запускаем парсер')
        self.parser = Parser(self.label, self.label2, self.label3)
        # noinspection PyBroadException
        try:
            self.parser.continue_parsing()
        except Exception:
            print(traceback.format_exc())

    def run(self):
        self.update_db()


class ParsingThreadLastYear(QThread):
    def __init__(self, label, label2, label3):
        super().__init__()
        self.parser = None
        self.label = label
        self.label2 = label2
        self.label3 = label3

    def update_db(self):
        print('[INFO] Запускаем парсер')
        self.parser = Parser(self.label, self.label2, self.label3)
        # noinspection PyBroadException
        try:
            # имена в модули очень похожи, будет путаница
            self.parser.last_year_pars()
        except Exception:
            print(traceback.format_exc())

    def run(self):
        self.update_db()


def main():
    try:
        app = QtWidgets.QApplication(sys.argv)
        window = MainApp()
        window.show()
        app.exec_()
    except Exception:
        print(traceback.format_exc())


if __name__ == '__main__':
    main()
