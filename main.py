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
from parser import Parser
import webbrowser


class MainApp(QtWidgets.QMainWindow, mainwindow.Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.db = 'oddsportal.db'
        self.parsing = False
        self.logotypes_path = {
            '18bet': 'logotypes/18bet.png',
            '1xBet': 'logotypes/1xbet.png',
            '1xStavka.ru': 'logotypes/1xstavka.png',
            'Asianodds': 'logotypes/assianodds.png',
            'bet-at-home': 'logotypes/bet_at_home.png',
            'bet365': 'logotypes/bet365.png',
            'bet365.it': 'logotypes/bet365.png',
            'Bethard': 'logotypes/bethard.png',
            'bwin': 'logotypes/bwin.png',
            'bwin.es': 'logotypes/bwin.png',
            'bwin.fr': 'logotypes/bwin.png',
            'bwin.it': 'logotypes/bwin.png',
            'Coolbet': 'logotypes/coolbet.png',
            'Marathonbet': 'logotypes/marathon_bet.png',
            'MrGreen': 'logotypes/mrgreen.png',
            'Pinnacle': 'logotypes/pinnacle.png',
            'Unibet': 'logotypes/unibet.png',
            'Unibet.it': 'logotypes/unibet.png',
            'Unibet.fr': 'logotypes/unibet.png',
            'William Hill': 'logotypes/willian_hill.png',
            'WilliamHill.it': 'logotypes/willian_hill.png',
            'Chance.cz': 'logotypes/chance.png',
            'Tipsport.sk': 'logotypes/tipsport.png',
            'Tipsport.cz': 'logotypes/tipsport.png',
            'Betago': 'logotypes/betago.png',
            'Expekt': 'logotypes/expekt.png',
            'Betclic': 'logotypes/betclic.png',
            'Betclic.fr': 'logotypes/betclic.png',
            'STS.pl': 'logotypes/sts.png',
            'Interwetten': 'logotypes/interwetten.png',
            'Winline.ru': 'logotypes/winline.png',
            'Interwetten.es': 'logotypes/interwetten.png',
            'Leonbets': 'logotypes/leon.png',
            'Leon.ru': 'logotypes/leonru.png',
            'Oddsring': 'logotypes/oddsring.png',
            'Betfair': 'logotypes/betfair.png',
            'Intertops': 'logotypes/iterlops.png',
            'Jetbull': 'logotypes/jetbull.png',
            'BetVictor': 'logotypes/betvictor.png',
            'NordicBet': 'logotypes/nordicbet.png',
            'Betsson': 'logotypes/betsson.png',
            'Betsafe': 'logotypes/belsafe.png',
            'Betway': 'logotypes/betway.png',
            '10Bet': 'logotypes/IO.png',
            'ComeOn': 'logotypes/comeon.png',
            'SAZKAbet.cz': 'logotypes/sazkabet.png',
            'BoyleSports': 'logotypes/boukesports.png',
            'GGBET': 'logotypes/ggbet.png',
            'youwin': 'logotypes/youwin.png',
            '188BET': 'logotypes/188bet.png',
            'SBOBET': 'logotypes/sbobet.png',
            'Dafabet': 'logotypes/dafabet.png',
            'iFortuna.cz': 'logotypes/fortuna.png',
            'eFortuna.pl': 'logotypes/fortuna.png',
            'iFortuna.sk': 'logotypes/fortuna.png',
            'Betfair Exchange': 'logotypes/betfair.png',
            '888sport': 'logotypes/888.png',
            'Titanbet': 'logotypes/titanbet.png',
            'BetJOE': 'logotypes/betjoe.png',
            'Betfred': 'logotypes/betjoe.png',
            'France Pari': 'logotypes/france-pari.png',
            'Matchbook': 'logotypes/matchbook.png',
            'Sportingbet': 'logotypes/sportingbet.png',
            'Sportium.es': 'logotypes/sportium.png'
        }
        self.setupUi(self)
        self.con = None
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

    def update_bookmakers(self):
        print('[INFO] Берём из базы букмекерские конторы')
        self.con = sqlite3.connect(self.db)
        cur = self.con.cursor()
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
            checkBox.setText(bookmaker[1] + ' (' + str(bookmaker[0]) + ')')
            self.checkboxlist.append(checkBox)
            self.formLayout_2.setWidget(data_bookmaker_checklist.index(bookmaker),
                                        QtWidgets.QFormLayout.FieldRole, checkBox)
            self.verticalLayout.addLayout(self.formLayout_2)
        for check_box in self.checkboxlist:
            check_box.clicked.connect(lambda state, chck=check_box: self.unselect_allcheckbox(chck))
        self.pushButton.clicked.connect(self.find_match)

    def update_label3(self):
        con = sqlite3.connect(self.db)
        cur = con.cursor()
        query = 'SELECT * FROM game'
        cur.execute(query)
        all_game_count = len(cur.fetchall())
        self.label_11.setText('Всего игр в базе: ' + str(all_game_count))
        cur.close()
        con.close()

    def find_match(self):
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
        print('[INFO] Поиск в базе игры с букмекером {} П1 = {} X = {} П2 = {}'.format(select_bk, p1, x, p2))
        cur = self.con.cursor()
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
                game_data = [el for el in cur.fetchone()]
                self.games.append(game_data)
        try:
            self.update_table()
            p1_out = 0
            p2_out = 0
            x_out = 0
            if self.games:
                for game in self.games:
                    result = game[6]
                    p1_r, p2_r = self.result_cleaning(result)
                    if float(p1_r) > float(p2_r):
                        p1_out += 1
                    elif float(p1_r) < float(p2_r):
                        p2_out += 1
                    elif float(p1_r) == float(p2_r):
                        x_out += 1
            all_out = p1_out + p2_out + x_out
            p1_out_ = 0
            x_out_ = 0
            p2_out_ = 0
            if all_out:
                p1_out_ = 100 * p1_out / all_out
                p2_out_ = 100 * p2_out / all_out
                x_out_ = 100 * x_out / all_out
            self.label_6.setText('П1: ' + str(round(p1_out_)) + '% (' + str(round(p1_out)) + ')')
            self.label_5.setText('X: ' + str(round(x_out_)) + '% (' + str(round(x_out)) + ')')
            self.label_7.setText('П2: ' + str(round(p2_out_)) + '% (' + str(round(p2_out)) + ')')
            # self.comboBox.clear()
            countrys = []
            self.liga_dict = {}
            for game in self.games:
                if game[8] not in countrys:
                    countrys.append(game[8])
                if game[8] not in self.liga_dict:
                    self.liga_dict[game[8]] = [game[9]]
                else:
                    if game[9] not in self.liga_dict[game[8]]:
                        self.liga_dict[game[8]].append(game[9])
            # self.comboBox.addItems(countrys)
            cur.close()
        except Exception:
            print(traceback.format_exc())

    def result_cleaning(self, result: str):
        if 'awarded' in result:
            return 0, 0
        if 'penalties' in result:
            result_out = result.replace('Final result ', '').split(' ')[0]
            p1 = result_out.split(':')[0]
            p2 = result_out.split(':')[1]
            return p1, p2
        if '(' in result:
            t1 = result.split('(')[1].replace(')', ' ').split(',')[0]
            t2 = result.split('(')[1].replace(')', ' ').split(',')[1]
            t1_p1 = t1.split(':')[0]
            t1_p2 = t1.split(':')[1]
            t2_p1 = t2.split(':')[0]
            t2_p2 = t2.split(':')[1]
            p1 = float(t1_p1) + float(t2_p1)
            p2 = float(t1_p2) + float(t2_p2)
            return p1, p2
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
        self.tableWidget.clearContents()
        self.tableWidget.setRowCount(len(self.games))
        for game in self.games:
            item_command1 = QtWidgets.QTableWidgetItem()
            item_command1.setText(game[1])
            self.tableWidget.setItem(self.games.index(game), 2, item_command1)
            item_command2 = QtWidgets.QTableWidgetItem()
            item_command2.setText(game[2])
            self.tableWidget.setItem(self.games.index(game), 3, item_command2)
            item_date = QtWidgets.QTableWidgetItem()
            item_date.setText(game[4])
            self.tableWidget.setItem(self.games.index(game), 0, item_date)
            self.tableWidget.resizeColumnToContents(2)
            item_country = QtWidgets.QTableWidgetItem()
            item_country.setText(game[8])
            self.tableWidget.setItem(self.games.index(game), 1, item_country)
            self.tableWidget.resizeColumnToContents(3)
            item_result = QtWidgets.QTableWidgetItem()
            item_result.setText(game[6])
            self.tableWidget.setItem(self.games.index(game), 4, item_result)
            self.tableWidget.resizeColumnToContents(4)
            item_clicked = QtWidgets.QTableWidgetItem()
            item_clicked.setText('Перейти на сайт')
            self.tableWidget.setItem(self.games.index(game), 5, item_clicked)
            self.tableWidget.resizeColumnToContents(5)

    def open_page_in_browser(self, row, column):
        if column == 5:
            url = self.games[row][3]
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
