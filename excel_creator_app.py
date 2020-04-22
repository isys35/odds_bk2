from PyQt5 import QtGui, QtWidgets
import excel_creator
import sys
from async_parser import Parser
import xlwt
import subprocess
import traceback
import time


def save_data_in_file(data):
    file_name = 'info.xls'
    wb = xlwt.Workbook()
    ws = wb.add_sheet('sheet')
    aligment = xlwt.Alignment()
    aligment.horz = xlwt.Alignment.HORZ_CENTER
    style_centr_aligment = xlwt.XFStyle()
    style_centr_aligment.alignment = aligment
    pattern_y = xlwt.Pattern()
    pattern_y.pattern = xlwt.Pattern.SOLID_PATTERN
    pattern_y.pattern_fore_colour = xlwt.Style.colour_map['yellow']
    style_yellow = xlwt.XFStyle()
    style_yellow.pattern = pattern_y
    style_yellow.alignment = aligment
    pattern_o = xlwt.Pattern()
    pattern_o.pattern = xlwt.Pattern.SOLID_PATTERN
    pattern_o.pattern_fore_colour = xlwt.Style.colour_map['aqua']
    style_orange = xlwt.XFStyle()
    style_orange.pattern = pattern_o
    style_orange.alignment = aligment
    pattern_r = xlwt.Pattern()
    pattern_r.pattern = xlwt.Pattern.SOLID_PATTERN
    pattern_r.pattern_fore_colour = xlwt.Style.colour_map['red']
    style_red = xlwt.XFStyle()
    style_red.pattern = pattern_r
    style_red.alignment = aligment
    pattern_g = xlwt.Pattern()
    pattern_g.pattern = xlwt.Pattern.SOLID_PATTERN
    pattern_g.pattern_fore_colour = xlwt.Style.colour_map['green']
    style_green = xlwt.XFStyle()
    style_green.pattern = pattern_g
    style_green.alignment = aligment
    ws.col(0).width = 4000
    ws.col(10).width = 6000
    #ws.col(6).width = 6000
    print(len(data[0]))
    if len(data[0]) == 13:
        ws.write(0, 0, str(data[0][5]))
        ws.write(0, 1, str(data[0][6]))
        ws.write(0, 3, str(data[0][7]))
        ws.write(0, 4, str(data[0][8]))
        ws.write(0, 2, str(data[0][9]))
        ws.write(1, 0, str(data[0][11]))
        ws.write(1, 1, str(data[0][12]))
        ws.write(2, 0, str(data[0][10]))
        ws.write(4, 0, 'Букмекер')
        ws.write(4, 1, 'П1', style_centr_aligment)
        ws.write(4, 2, 'X', style_centr_aligment)
        ws.write(4, 3, 'П2', style_centr_aligment)
        ws.write(4, 10, 'Время', style_centr_aligment)
        ws.write(4, 11, 'Маржа', style_centr_aligment)
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
            major = ((1 / el[1] * 100)
                     + (1 / el[2] * 100)
                     + (1 / el[3] * 100)) - 100
            el.append(major)
        p1_sum = 0
        x_sum = 0
        p2_sum = 0
        p1_sum_real = 0
        x_sum_real = 0
        p2_sum_real = 0
        p1_lst = []
        x_lst = []
        p2_lst = []
        p1_real_lst = []
        x_real_lst = []
        p2_real_lst = []
        for el in list_for_excel:
            ws.write(target_row, 0, el[0])
            ws.write(target_row, 1, el[1], style_centr_aligment)
            p1_lst.append(el[1])
            p1_sum += el[1]
            ws.write(target_row, 10, str(time.ctime(el[4])).split(' ', 1)[1])
            ws.write(target_row, 2, el[2], style_centr_aligment)
            x_sum += el[2]
            x_lst.append(el[2])
            ws.write(target_row, 3, el[3], style_centr_aligment)
            p2_sum += el[3]
            p2_lst.append(el[3])
            ws.write(target_row, 11, round(el[5], 2), style_centr_aligment)
            p1_real = el[1] * (1 + el[5]/100)
            p1_real_lst.append(p1_real)
            p1_sum_real += p1_real
            x_real = el[2] * (1 + el[5] / 100)
            x_real_lst.append(x_real)
            x_sum_real += x_real
            p2_real = el[3] * (1 + el[5] / 100)
            p2_real_lst.append(p2_real)
            p2_sum_real += p2_real
            ws.write(target_row, 4, round(p1_real, 2), style_centr_aligment)
            ws.write(target_row, 5, round(x_real, 2), style_centr_aligment)
            ws.write(target_row, 6, round(p2_real, 2), style_centr_aligment)
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
            ws.write(target_row, 7, p1delta, style_centr_aligment)
            ws.write(target_row, 8, xdelta, style_centr_aligment)
            ws.write(target_row, 9, p2delta, style_centr_aligment)
            target_row += 1
        p1_average = round(p1_sum/ len(list_for_excel), 2)
        x_average = round(x_sum / len(list_for_excel), 2)
        p2_average = round(p2_sum / len(list_for_excel), 2)
        p1_max = max(p1_lst)
        x_max = max(x_lst)
        p2_max = max(p2_lst)
        p1_min = min(p1_lst)
        x_min = min(x_lst)
        p2_min = min(p2_lst)
        print(p1_max, x_max, p2_max)
        ws.write(target_row, 14, p1_average, style_centr_aligment)
        ws.write(target_row, 15, x_average, style_centr_aligment)
        ws.write(target_row, 16, p2_average, style_centr_aligment)
        p1_average_real = round(p1_sum_real / len(list_for_excel), 2)
        x_average_real = round(x_sum_real / len(list_for_excel), 2)
        p2_average_real = round(p2_sum_real / len(list_for_excel), 2)
        p1_real_max = round(max(p1_real_lst), 2)
        x_real_max = round(max(x_real_lst), 2)
        p2_real_max = round(max(p2_real_lst), 2)
        p1_real_min = round(min(p1_real_lst), 2)
        x_real_min = round(min(x_real_lst), 2)
        p2_real_min = round(min(p2_real_lst), 2)
        ws.write(target_row, 17, p1_average_real, style_centr_aligment)
        ws.write(target_row, 18, x_average_real, style_centr_aligment)
        ws.write(target_row, 19, p2_average_real, style_centr_aligment)
        list_for_excel.sort(key=lambda i: i[5])
        target_row = 5
        for el in list_for_excel:
            ws.write(target_row, 13, el[0])
            if el[1] == p1_max:
                ws.write(target_row, 14, el[1], style_red)
            elif el[1] == p1_min:
                ws.write(target_row, 14, el[1], style_green)
            else:
                if el[1] < p1_average:
                    ws.write(target_row, 14, el[1], style_yellow)
                elif el[1] == p1_average:
                    ws.write(target_row, 14, el[1], style_orange)
                else:
                    ws.write(target_row, 14, el[1], style_centr_aligment)

            if el[2] == x_max:
                ws.write(target_row, 15, el[2], style_red)
            elif el[2] == x_min:
                ws.write(target_row, 15, el[2], style_green)
            else:
                if el[2] < x_average:
                    ws.write(target_row, 15, el[2], style_yellow)
                elif el[2] == x_average:
                    ws.write(target_row, 15, el[2], style_orange)
                else:
                    ws.write(target_row, 15, el[2], style_centr_aligment)

            if el[3] == p2_max:
                ws.write(target_row, 16, el[3], style_red)
            elif el[3] == p2_min:
                ws.write(target_row, 16, el[3], style_green)
            else:
                if el[3] < p2_average:
                    ws.write(target_row, 16, el[3], style_yellow)
                elif el[3] == p2_average:
                    ws.write(target_row, 16, el[3], style_orange)
                else:
                    ws.write(target_row, 16, el[3], style_centr_aligment)
            ws.write(target_row, 23, str(time.ctime(el[4])).split(' ', 1)[1])
            ws.write(target_row, 24, round(el[5], 2), style_centr_aligment)
            p1_real = el[1] * (1 + el[5]/100)
            x_real = el[2] * (1 + el[5] / 100)
            p2_real = el[3] * (1 + el[5] / 100)

            if round(p1_real, 2) == p1_real_max:
                ws.write(target_row, 17, round(p1_real, 2), style_red)
            elif round(p1_real, 2) == p1_real_min:
                ws.write(target_row, 17, round(p1_real, 2), style_green)
            else:
                if round(p1_real, 2) < p1_average_real:
                    ws.write(target_row, 17, round(p1_real, 2), style_yellow)
                elif round(p1_real, 2) == p1_average_real:
                    ws.write(target_row, 17, round(p1_real, 2), style_orange)
                else:
                    ws.write(target_row, 17, round(p1_real, 2), style_centr_aligment)

            if round(x_real, 2) == x_real_max:
                ws.write(target_row, 18, round(x_real, 2), style_red)
            elif round(x_real, 2) == x_real_min:
                ws.write(target_row, 18, round(x_real, 2), style_green)
            else:
                if round(x_real, 2) < x_average_real:
                    ws.write(target_row, 18, round(x_real, 2), style_yellow)
                elif round(x_real, 2) == x_average_real:
                    ws.write(target_row, 18, round(x_real, 2), style_orange)
                else:
                    ws.write(target_row, 18, round(x_real, 2), style_centr_aligment)

            if round(p2_real, 2) == p2_real_max:
                ws.write(target_row, 19, round(p2_real, 2), style_red)
            elif round(p2_real, 2) == p2_real_min:
                ws.write(target_row, 19, round(p2_real, 2), style_green)
            else:
                if round(p2_real, 2) < p2_average_real:
                    ws.write(target_row, 19, round(p2_real, 2), style_yellow)
                elif round(p2_real, 2) == p2_average_real:
                    ws.write(target_row, 19, round(p2_real, 2), style_orange)
                else:
                    ws.write(target_row, 19, round(p2_real, 2), style_centr_aligment)

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
            ws.write(target_row, 20, p1delta, style_centr_aligment)
            ws.write(target_row, 21, xdelta, style_centr_aligment)
            ws.write(target_row, 22, p2delta, style_centr_aligment)
            target_row += 1
    elif len(data[0]) == 12:
        ws.write(0, 0, str(data[0][4]))
        ws.write(0, 1, str(data[0][5]))
        ws.write(0, 3, str(data[0][6]))
        ws.write(0, 4, str(data[0][7]))
        ws.write(0, 2, str(data[0][8]))
        ws.write(1, 0, str(data[0][10]))
        ws.write(1, 1, str(data[0][11]))
        ws.write(2, 0, str(data[0][9]))
        ws.write(4, 0, 'Букмекер')
        ws.write(4, 1, 'П1', style_centr_aligment)
        ws.write(4, 2, 'П2', style_centr_aligment)
        ws.write(4, 7, 'Время', style_centr_aligment)
        ws.write(4, 8, 'Маржа', style_centr_aligment)
        target_row = 5
        list_for_excel = []
        for bookmaker in data:
            list_for_excel.append([bookmaker[0],
                                   bookmaker[1],
                                   bookmaker[2],
                                   bookmaker[3]])
        list_for_excel.sort(key=lambda i: i[3])
        for el in list_for_excel:
            major = ((1 / el[1] * 100)
                     + (1 / el[2] * 100)) - 100
            el.append(major)
        p1_sum = 0
        p2_sum = 0
        p1_sum_real = 0
        p2_sum_real = 0
        p1_lst = []
        p2_lst = []
        p1_real_lst = []
        p2_real_lst = []
        for el in list_for_excel:
            ws.write(target_row, 0, el[0])
            ws.write(target_row, 1, el[1], style_centr_aligment)
            p1_lst.append(el[1])
            p1_sum += el[1]
            ws.write(target_row, 7, str(time.ctime(el[3])).split(' ', 1)[1])
            ws.write(target_row, 2, el[2], style_centr_aligment)
            p2_sum += el[2]
            p2_lst.append(el[2])
            ws.write(target_row, 8, round(el[4], 2), style_centr_aligment)
            p1_real = round(el[1] * (1 + el[4]/100), 2)
            p1_real_lst.append(p1_real)
            p1_sum_real += p1_real
            p2_real = round(el[2] * (1 + el[4] / 100),2)
            p2_real_lst.append(p2_real)
            p2_sum_real += p2_real
            ws.write(target_row, 3, p1_real, style_centr_aligment)
            ws.write(target_row, 4, p2_real, style_centr_aligment)
            p1delta = p1_real-el[1]
            if p1_real > el[1]:
                p1delta = '+' + str(round(p1delta, 2))
            else:
                p1delta = '-' + str(round(p1delta, 2))
            p2delta = p2_real - el[2]
            if p2_real > el[2]:
                p2delta = '+' + str(round(p2delta, 2))
            else:
                p2delta = '-' + str(round(p2delta, 2))
            ws.write(target_row, 5, p1delta, style_centr_aligment)
            ws.write(target_row, 6, p2delta, style_centr_aligment)
            target_row += 1
        p1_average = round(p1_sum / len(list_for_excel), 2)
        p2_average = round(p2_sum / len(list_for_excel), 2)
        p1_max = max(p1_lst)
        p2_max = max(p2_lst)
        p1_min = min(p1_lst)
        p2_min = min(p2_lst)
        print(p1_max, p2_max)
        ws.write(target_row, 11, p1_average, style_centr_aligment)
        ws.write(target_row, 12, p2_average, style_centr_aligment)
        p1_average_real = round(p1_sum_real / len(list_for_excel), 2)
        p2_average_real = round(p2_sum_real / len(list_for_excel), 2)
        p1_real_max = max(p1_real_lst)
        p2_real_max = max(p2_real_lst)
        p1_real_min = min(p1_real_lst)
        p2_real_min = min(p2_real_lst)
        ws.write(target_row, 13, p1_average_real, style_centr_aligment)
        ws.write(target_row, 14, p2_average_real, style_centr_aligment)
        list_for_excel.sort(key=lambda i: i[4])
        target_row = 5
        for el in list_for_excel:
            ws.write(target_row, 10, el[0])
            if el[1] == p1_max:
                ws.write(target_row, 11, el[1], style_red)
            elif el[1] == p1_min:
                ws.write(target_row, 11, el[1], style_green)
            else:
                if el[1] < p1_average:
                    ws.write(target_row, 11, el[1], style_yellow)
                elif el[1] == p1_average:
                    ws.write(target_row, 11, el[1], style_orange)
                else:
                    ws.write(target_row, 11, el[1], style_centr_aligment)

            if el[2] == p2_max:
                ws.write(target_row, 12, el[2], style_red)
            elif el[2] == p2_min:
                ws.write(target_row, 12, el[2], style_green)
            else:
                if el[2] < p2_average:
                    ws.write(target_row, 12, el[2], style_yellow)
                elif el[2] == p2_average:
                    ws.write(target_row, 12, el[2], style_orange)
                else:
                    ws.write(target_row, 12, el[2], style_centr_aligment)

            ws.write(target_row, 17, str(time.ctime(el[3])).split(' ', 1)[1])
            ws.write(target_row, 18, round(el[4], 2), style_centr_aligment)
            p1_real = round(el[1] * (1 + el[4] / 100), 2)
            p2_real = round(el[2] * (1 + el[4] / 100), 2)
            print(p1_real, p1_real_min)
            if p1_real == p1_real_max:
                ws.write(target_row, 13, p1_real, style_red)
            elif p1_real == p1_real_min:
                ws.write(target_row, 13, p1_real, style_green)
            else:
                if p1_real < p1_average_real:
                    ws.write(target_row, 13, p1_real, style_yellow)
                elif p1_real == p1_average_real:
                    ws.write(target_row, 13, p1_real, style_orange)
                else:
                    ws.write(target_row, 13, p1_real, style_centr_aligment)

            if p2_real == p2_real_max:
                ws.write(target_row, 14, p2_real, style_red)
            elif p2_real == p2_real_min:
                ws.write(target_row, 14, p2_real, style_green)
            else:
                if p2_real < p2_average_real:
                    ws.write(target_row, 14, p2_real, style_yellow)
                elif p2_real == p2_average_real:
                    ws.write(target_row, 14, p2_real, style_orange)
                else:
                    ws.write(target_row, 14, p2_real, style_centr_aligment)

            p1delta = p1_real-el[1]
            if p1_real > el[1]:
                p1delta = '+' + str(round(p1delta, 2))
            else:
                p1delta = '-' + str(round(p1delta, 2))
            p2delta = p2_real - el[2]
            if p2_real > el[2]:
                p2delta = '+' + str(round(p2delta, 2))
            else:
                p2delta = '-' + str(round(p2delta, 2))
            ws.write(target_row, 15, p1delta, style_centr_aligment)
            ws.write(target_row, 16, p2delta, style_centr_aligment)
            target_row += 1
    wb.save(file_name)
    with subprocess.Popen(["start", "/WAIT", file_name], shell=True) as doc:
        doc.poll()


class App(QtWidgets.QMainWindow, excel_creator.Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.pushButton.clicked.connect(self.create_excel_for_game)

    def create_excel_for_game(self):
        url = self.lineEdit.text()
        parser = Parser()
        try:
            data, info = parser.get_match_data(url)
        except Exception as ex:
            print(ex)
            print(traceback.format_exc())
        for key in data:
            if None in data[key]:
                data[key].remove(None)
        try:
            data_out = []
            bookmakers_exteptions = ['Betfair', 'Betfair Exchange', 'Matchbook']
            for key in data:
                if key in bookmakers_exteptions:
                    continue
                if len(data[key]) == 4:
                    data_el = [key, data[key][0], data[key][1], data[key][2], data[key][3], info['sport'], info['country'],
                            info['command1'], info['command2'], info['champ'], info['result'], info['date'], info['time']]
                else:
                    data_el = [key, data[key][0], data[key][1], data[key][2], info['sport'],
                               info['country'],
                               info['command1'], info['command2'], info['champ'], info['result'], info['date'],
                               info['time']]
                data_out.append(data_el)
            save_data_in_file(data_out)
        except Exception as ex:
            print(ex)
            print(traceback.format_exc())


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = App()
    window.show()
    app.exec_()