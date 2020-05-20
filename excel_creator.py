from parser_odds import Grabber
import xlwt, xlrd
import subprocess
import time
import numpy as np


class ExcelWriter:
    def __init__(self):
        self.wb = xlwt.Workbook()
        self.ws = self.wb.add_sheet('sheet')
        self.style_horz_aligment = get_style('horz_aligment')
        self.style_little_value = get_style('little_value')
        self.style_average_value = get_style('average_value')
        self.style_max_value = get_style('max_value')
        self.style_min_value = get_style('min_value')

    def save_data_in_excel(self, data):
        self.ws.col(0).width = 4000
        if data['e1'] == 1:
            len_column_content = 10
        else:
            len_column_content = 7
        self.ws.col(0 + len_column_content).width = 6000
        self.ws.col(3 + len_column_content).width = 4000
        self.ws.col(2 + len_column_content * 2).width = 4000
        self.write_head(data)
        odds_data = data['open_odds']
        odds_data_list_sort_time = list(odds_data.items())
        odds_data_list_sort_time.sort(key=lambda i: i[1]['change_time'])
        self.calculate_additional_odds(odds_data_list_sort_time)
        dop_info = self.get_additional_info(odds_data_list_sort_time)
        self.build_table(0, odds_data_list_sort_time)
        count_file = 0
        while True:
            try:
                self.wb.save(f'info{count_file}.xls')
                break
            except PermissionError:
                count_file += 1
        with subprocess.Popen(["start", "/WAIT", f'info{count_file}.xls'], shell=True) as doc:
            doc.poll()

    # noinspection PyTypeChecker
    @staticmethod
    def calculate_additional_odds(odds_data_list):
        for bookmaker in odds_data_list:
            major = sum([100/coef for coef in bookmaker[1]['coef']]) - 100
            bookmaker[1]['major'] = round(major, 2)
            real_coef = [round(coef*(1 + bookmaker[1]['major']/100), 2) for coef in bookmaker[1]['coef']]
            bookmaker[1]['real_coef'] = real_coef
            delta_coef = [round(bookmaker[1]['real_coef'][index_len_coefs]-bookmaker[1]['coef'][index_len_coefs], 2) for index_len_coefs in range(0,len(bookmaker[1]['coef']))]
            bookmaker[1]['delta_coef'] = delta_coef

    @staticmethod
    def get_additional_info(odds_data_list):
        all_coef = [bookmaker[1]['coef'] for bookmaker in odds_data_list]
        all_real_coef = [bookmaker[1]['real_coef'] for bookmaker in odds_data_list]
        array_coef = np.array(all_coef)
        array_real_coef = np.array(all_real_coef)
        all_coef_transp = array_coef.transpose().tolist()
        all_real_coef_transp = array_real_coef.transpose().tolist()
        coef_average = [round(sum(coef_p) / len(coef_p), 2) for coef_p in all_coef_transp]
        real_coef_average = [round(sum(coef_p) / len(coef_p), 2) for coef_p in all_real_coef_transp]
        return {'coef_average': coef_average, 'real_coef_average': real_coef_average}

    def build_table(self, column, data, dop_info=None):
        target_row = 6
        print(data)
        for bookmaker in data:
            date = time.gmtime(bookmaker[1]['change_time'])
            target_column = column
            self.ws.write(target_row, target_column, bookmaker[0])
            target_column += 1
            for coef in bookmaker[1]['coef']:
                self.ws.write(target_row, target_column, coef, self.style_horz_aligment)
                target_column += 1
            for coef in bookmaker[1]['real_coef']:
                self.ws.write(target_row, target_column, coef, self.style_horz_aligment)
                target_column += 1
            for delta in bookmaker[1]['delta_coef']:
                self.ws.write(target_row, target_column, f'+{delta}', self.style_horz_aligment)
                target_column += 1
            self.ws.write(target_row, target_column, time.strftime('%d %B %H:%M', date), self.style_horz_aligment)
            target_column += 1
            self.ws.write(target_row, target_column, bookmaker[1]['major'], self.style_horz_aligment)
            target_column += 1
            target_row += 1

    def write_head(self, data):
        date = time.gmtime(data['date'])
        self.ws.write(0, 0, data['sport'])
        self.ws.write(0, 1, data['country'])
        self.ws.write(0, 2, data['command1'])
        self.ws.write(0, 3, data['command2'])
        self.ws.write(1, 0, time.strftime('%d %B %Y', date))
        self.ws.write(1, 1, time.strftime('%H:%M', date))
        self.ws.write(2, 0, data['result'])
        self.ws.write(5, 0, 'Букмекер')
        self.ws.write(5, 1, 'П1', self.style_horz_aligment)
        self.ws.write(5, 2, 'П2', self.style_horz_aligment)
        if data['e1'] == 1:
            self.ws.write(5, 3, 'П3', self.style_horz_aligment)
            self.ws.write(5, 10, 'Время', self.style_horz_aligment)
            self.ws.write(5, 11, 'Маржа', self.style_horz_aligment)
        else:
            self.ws.write(5, 7, 'Время', self.style_horz_aligment)
            self.ws.write(5, 8, 'Маржа', self.style_horz_aligment)


def get_style(style_name):
    aligment = xlwt.Alignment()
    aligment.horz = xlwt.Alignment.HORZ_CENTER
    style = xlwt.XFStyle()
    style.alignment = aligment
    if style_name == 'horz_aligment':
        return style
    pattern = xlwt.Pattern()
    pattern.pattern = xlwt.Pattern.SOLID_PATTERN
    if style_name == 'little_value':
        pattern.pattern_fore_colour = xlwt.Style.colour_map['yellow']
    elif style_name == 'average_value':
        pattern.pattern_fore_colour = xlwt.Style.colour_map['aqua']
    elif style_name == 'max_value':
        pattern.pattern_fore_colour = xlwt.Style.colour_map['red']
    elif style_name == 'min_value':
        pattern.pattern_fore_colour = xlwt.Style.colour_map['green']
    style.pattern = pattern
    return style


def main():
    parser = Grabber()
    url_event = input('Введите ссылку:')
    data = parser.get_event_data(url_event)
    excel = ExcelWriter()
    excel.save_data_in_excel(data)


if __name__ == '__main__':
    main()