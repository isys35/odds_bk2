from parser_odds import Grabber
import xlwt, xlrd
import subprocess
import time


class ExcelWriter:
    def __init__(self):
        self.wb = xlwt.Workbook()
        self.ws = self.wb.add_sheet('sheet')
        self.style_horz_aligment = get_style('horz_aligment')

    def save_data_in_excel(self, data):
        style_little_value = get_style('little_value')
        style_average_value = get_style('average_value')
        style_max_value = get_style('max_value')
        style_min_value = get_style('min_value')
        self.ws.col(0).width = 4000
        if data['e1'] == 1:
            len_cilumn_content = 10
        else:
            len_cilumn_content = 7
        self.ws.col(0 + len_cilumn_content).width = 6000
        self.ws.col(2 + len_cilumn_content).width = 4000
        self.ws.col(2 + len_cilumn_content * 2).width = 4000
        self.write_head(data)
        odds_data = data['open_odds']
        odds_data_list_sort_time = list(odds_data.items())
        odds_data_list_sort_time.sort(key=lambda i: i[1]['change_time'])
        print(odds_data_list_sort_time)
        count_file = 0
        while True:
            try:
                self.wb.save(f'info{count_file}.xls')
                break
            except PermissionError:
                count_file += 1
        with subprocess.Popen(["start", "/WAIT", f'info{count_file}.xls'], shell=True) as doc:
            doc.poll()

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