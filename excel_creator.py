from parser_odds import Grabber
import xlwt, xlrd
import subprocess
import time
import numpy as np
from threading import Thread


# noinspection PyUnresolvedReferences
class ExcelWriter:
    def __init__(self):
        self.wb = xlwt.Workbook()
        self.ws = self.wb.add_sheet('sheet')
        self.style_horz_aligment = get_style('horz_aligment')
        self.style_little_value = get_style('little_value')
        self.style_average_value = get_style('average_value')
        self.style_max_value = get_style('max_value')
        self.style_min_value = get_style('min_value')
        self.exception_bookmakers = ['Betfair Exchange']

    def save_data_in_excel(self, data):
        self.ws.col(0).width = 4000
        if data['e1'] == 1:
            len_column_content = 10
        else:
            len_column_content = 7
        self.ws.col(0 + len_column_content).width = 4000
        self.ws.col(6 + len_column_content).width = 4000
        self.ws.col(6 + len_column_content * 2).width = 4000
        self.write_head(data)
        odds_data = data['open_odds']
        odds_data_list_sort = list(odds_data.items())
        odds_data_list_sort.sort(key=lambda i: i[1]['change_time'])
        self.calculate_additional_odds(odds_data_list_sort)
        dop_info = self.get_additional_info(odds_data_list_sort)
        self.build_table(0, odds_data_list_sort, dop_info=dop_info)
        magic_info = self.get_magic_info(odds_data_list_sort, dop_info)
        self.write_magic_info(1, 9 + len(odds_data_list_sort), magic_info)
        delta_info = self.get_delta_info(odds_data_list_sort)
        self.write_delta_info(2 + len_column_content, delta_info)
        odds_data_list_sort.sort(key=lambda i: i[1]['major'])
        self.build_table(6 + len_column_content, odds_data_list_sort, dop_info=dop_info)
        magic_info = self.get_magic_info(odds_data_list_sort, dop_info)
        self.write_magic_info(7 + len_column_content, 9 + len(odds_data_list_sort), magic_info)
        delta_info = self.get_delta_info(odds_data_list_sort)
        self.write_delta_info(8 + len_column_content * 2, delta_info)
        self.save_file()

    def save_file(self):
        save_thread = SaveThread(self.wb)
        save_thread.start()

    def write_magic_info(self, column, row, magic_info):
        for group in magic_info:
            target_column = magic_info.index(group) + column
            for p in group:
                if 'info' in p:
                    self.ws.write(row, target_column, str(p['index']) + p['info'], self.style_horz_aligment)
                else:
                    self.ws.write(row, target_column, str(p['index']), self.style_horz_aligment)
                target_column += 3

    def get_delta_info(self, data):
        delta_info_bookmakers = []
        for bookmaker_id in range(0, len(data) - 1):
            if data[bookmaker_id][0] in self.exception_bookmakers:
                continue
            delta_info_bookmaker = []
            for coef_index in range(0, len(data[bookmaker_id][1]['real_coef'])):
                value_delta = data[bookmaker_id][1]['real_coef'][coef_index] - \
                              data[bookmaker_id + 1][1]['real_coef'][coef_index]
                value_delta_change = data[bookmaker_id + 1][1]['delta_coef'][coef_index] - \
                                     data[bookmaker_id][1]['delta_coef'][coef_index]
                delta_info_bookmaker.append(round((value_delta + value_delta_change) * 100))
            delta_info_bookmakers.append(delta_info_bookmaker)
        delta_info_sum = [sum([el[0] for el in delta_info_bookmakers]), sum([el[1] for el in delta_info_bookmakers])]
        delta_info_bookmakers.append([None, None])
        delta_info_bookmakers.append(delta_info_sum)
        return delta_info_bookmakers

    def write_delta_info(self, column, data):
        target_row = 6
        for delta_list in data:
            target_column = column
            for delta in delta_list:
                self.ws.write(target_row, target_column, delta, self.style_horz_aligment)
                target_column += 1
            target_row += 1

    # noinspection PyTypeChecker
    @staticmethod
    def calculate_additional_odds(odds_data_list):
        for bookmaker in odds_data_list:
            major = sum([100 / coef for coef in bookmaker[1]['coef']]) - 100
            bookmaker[1]['major'] = round(major, 2)
            real_coef = [round(coef * (1 + bookmaker[1]['major'] / 100), 2) for coef in bookmaker[1]['coef']]
            bookmaker[1]['real_coef'] = real_coef
            delta_coef = [round(bookmaker[1]['real_coef'][index_len_coefs] - bookmaker[1]['coef'][index_len_coefs], 2)
                          for index_len_coefs in range(0, len(bookmaker[1]['coef']))]
            bookmaker[1]['delta_coef'] = delta_coef

    def transponse_coefs(self, odds_data_list):
        all_coef = [bookmaker[1]['coef'] for bookmaker in odds_data_list if
                    bookmaker[0] not in self.exception_bookmakers]
        all_real_coef = [bookmaker[1]['real_coef'] for bookmaker in odds_data_list if
                         bookmaker[0] not in self.exception_bookmakers]
        array_coef = np.array(all_coef)
        array_real_coef = np.array(all_real_coef)
        all_coef_transp = array_coef.transpose().tolist()
        all_real_coef_transp = array_real_coef.transpose().tolist()
        return all_coef_transp, all_real_coef_transp

    # noinspection PyTypeChecker
    def get_additional_info(self, odds_data_list):
        all_coef_transp, all_real_coef_transp = self.transponse_coefs(odds_data_list)
        coef_average = [round(sum(coef_p) / len(coef_p), 2) for coef_p in all_coef_transp]
        real_coef_average = [round(sum(coef_p) / len(coef_p), 2) for coef_p in all_real_coef_transp]
        coef_max = [max(coef_p) for coef_p in all_coef_transp]
        real_coef_max = [max(coef_p) for coef_p in all_real_coef_transp]
        coef_min = [min(coef_p) for coef_p in all_coef_transp]
        real_coef_min = [min(coef_p) for coef_p in all_real_coef_transp]
        return {'coef': {'average': coef_average, 'min': coef_min, 'max': coef_max},
                'real_coef': {'average': real_coef_average, 'min': real_coef_min, 'max': real_coef_max}}

    def build_table(self, column, data, dop_info=None):
        target_row = 6
        for bookmaker in data:
            if bookmaker[0] in self.exception_bookmakers:
                continue
            date = time.gmtime(bookmaker[1]['change_time'])
            target_column = column
            self.ws.write(target_row, target_column, bookmaker[0])
            target_column += 1
            for coef_index in range(0, len(bookmaker[1]['coef'])):
                if dop_info:
                    self.write_flag_cell(bookmaker[1]['coef'],
                                         dop_info['coef'],
                                         coef_index,
                                         target_row,
                                         target_column)
                else:
                    self.ws.write(target_row, target_column, bookmaker[1]['coef'][coef_index], self.style_horz_aligment)
                target_column += 1
            for coef_index in range(0, len(bookmaker[1]['real_coef'])):
                if dop_info:
                    self.write_flag_cell(bookmaker[1]['real_coef'],
                                         dop_info['real_coef'],
                                         coef_index,
                                         target_row,
                                         target_column)
                else:
                    self.ws.write(target_row, target_column, bookmaker[1]['real_coef'][coef_index],
                                  self.style_horz_aligment)
                target_column += 1
            for delta in bookmaker[1]['delta_coef']:
                self.ws.write(target_row, target_column, f'+{delta}', self.style_horz_aligment)
                target_column += 1
            self.ws.write(target_row, target_column, time.strftime('%d %B %H:%M', date), self.style_horz_aligment)
            target_column += 1
            self.ws.write(target_row, target_column, bookmaker[1]['major'], self.style_horz_aligment)
            target_column += 1
            target_row += 1
        if dop_info:
            target_column = column + 1
            for coef_average in dop_info['coef']['average']:
                self.ws.write(target_row, target_column, coef_average, self.style_horz_aligment)
                target_column += 1
            for coef_average in dop_info['real_coef']['average']:
                self.ws.write(target_row, target_column, coef_average, self.style_horz_aligment)
                target_column += 1

    def write_flag_cell(self, bookmaker_coef, dop_info_coef, coef_index, target_row, target_column):
        if bookmaker_coef[coef_index] == dop_info_coef['max'][coef_index]:
            self.ws.write(target_row, target_column, bookmaker_coef[coef_index], self.style_max_value)
        elif bookmaker_coef[coef_index] == dop_info_coef['min'][coef_index]:
            self.ws.write(target_row, target_column, bookmaker_coef[coef_index], self.style_min_value)
        else:
            if bookmaker_coef[coef_index] < dop_info_coef['average'][coef_index]:
                self.ws.write(target_row, target_column, bookmaker_coef[coef_index], self.style_little_value)
            elif bookmaker_coef[coef_index] == dop_info_coef['average'][coef_index]:
                self.ws.write(target_row, target_column, bookmaker_coef[coef_index], self.style_little_value)
            else:
                self.ws.write(target_row, target_column, bookmaker_coef[coef_index],
                              self.style_horz_aligment)

    # noinspection PyTypeChecker
    def get_magic_info(self, data, dop_info):
        coef_transp, real_coef_transp = self.transponse_coefs(data)
        first_magic_group = self.get_first_magic_group(real_coef_transp, dop_info['real_coef'])
        second_magic_group = self.get_first_magic_group(coef_transp, dop_info['coef'])
        third_magic_group = self.get_third_magic_group(first_magic_group, second_magic_group)
        return first_magic_group, second_magic_group, third_magic_group

    def get_third_magic_group(self, first_magic_group, second_magic_group):
        len_group = len(first_magic_group)
        group = [{'min_index': first_magic_group[index]['min_index'] - second_magic_group[index]['min_index'],
                  'max_index': first_magic_group[index]['max_index'] - second_magic_group[index]['max_index']} for
                 index in range(len_group)]
        for p in range(len(group)):
            group[p]['delta'] = abs(group[p]['min_index']) + abs(group[p]['max_index'])
            if group[p]['delta'] == 0:
                group[p]['info'] = '0'
            elif set(first_magic_group[p]['min_index_lst']).issubset(second_magic_group[p]['min_index_lst']) and \
                    set(first_magic_group[p]['max_index_lst']).issubset(second_magic_group[p]['max_index_lst']):
                group[p]['info'] = '0'
                group[p]['delta'] = 0
            else:
                if first_magic_group[p]['info'] != second_magic_group[p]['info']:
                    group[p]['info'] = 'п'
                    if first_magic_group[p]['min_index'] == second_magic_group[p]['min_index']:
                        group[p]['info'] = 'чз'
                    elif first_magic_group[p]['min_index'] in second_magic_group[p]['min_index_lst']:
                        group[p]['info'] = 'чз'
                    if first_magic_group[p]['max_index'] == second_magic_group[p]['max_index']:
                        group[p]['info'] = 'чк'
                    elif first_magic_group[p]['max_index'] in second_magic_group[p]['max_index_lst']:
                        group[p]['info'] = 'чк'
                else:
                    if first_magic_group[p]['min_index'] == second_magic_group[p]['min_index']:
                        group[p]['info'] = 'дк'
                    elif first_magic_group[p]['max_index'] == second_magic_group[p]['max_index']:
                        group[p]['info'] = 'дз'
                    else:
                        group[p]['info'] = 'дд'
        self.update_index_group(group)
        return group

    @staticmethod
    def update_index_group(group):
        set_group = set([p['delta'] for p in group])
        delta_group = list(set_group)
        delta_group.sort(reverse=True)
        for p in group:
            p['index'] = delta_group.index(p['delta']) + 1

    # noinspection PyTypeChecker
    def get_first_magic_group(self, list_coef, dop_info):
        group = [None for _ in range(len(list_coef))]
        # noinspection PyTypeChecker
        for p_coefs_index in range(len(list_coef)):
            min_index = None
            max_index = None
            min_index_lst = []
            max_index_lst = []
            all_possible_groups = []
            for coef_index in range(len(list_coef[p_coefs_index])):
                if list_coef[p_coefs_index][coef_index] == dop_info['min'][p_coefs_index]:
                    min_index = coef_index
                    min_index_lst.append(min_index)
                if list_coef[p_coefs_index][coef_index] == dop_info['max'][p_coefs_index]:
                    max_index = coef_index
                    max_index_lst.append(max_index)
                if max_index is not None and min_index is not None:
                    if max_index > min_index:
                        info = 'зк'
                    else:
                        info = 'кз'
                    all_possible_groups.append({'delta': abs(max_index - min_index),
                                                'info': info,
                                                'max_index': max_index,
                                                'min_index': min_index})
            minimum_delta = min([el['delta'] for el in all_possible_groups])
            for append_group in all_possible_groups:
                if append_group['delta'] == minimum_delta:
                    group[p_coefs_index] = append_group
                    break
            group[p_coefs_index]['max_index_lst'] = max_index_lst
            group[p_coefs_index]['min_index_lst'] = min_index_lst
        self.update_index_group(group)
        return group

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


class SaveThread(Thread):
    def __init__(self, wb):
        super().__init__()
        self.wb = wb

    def run(self):
        count_file = 0
        while True:
            try:
                self.wb.save(f'info{count_file}.xls')
                break
            except PermissionError:
                count_file += 1
        with subprocess.Popen(["start", "/WAIT", f'info{count_file}.xls'], shell=True) as doc:
            doc.poll()


def main():
    while True:
        parser = Grabber()
        url_event = input('Введите ссылку:')
        data = parser.get_event_data(url_event)
        excel = ExcelWriter()
        excel.save_data_in_excel(data)


if __name__ == '__main__':
    main()
