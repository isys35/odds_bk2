from parser_odds import Grabber
import xlwt, xlrd


def save_data_in_excel(data):
    wb = xlwt.Workbook()
    ws = wb.add_sheet('sheet')
    style_horz_aligment = get_style('horz_aligment')
    style_little_value = get_style('little_value')
    style_average_value = get_style('average_value')
    style_max_value = get_style('max_value')
    style_min_value = get_style('min_value')
    ws.col(0).width = 4000
    if data['e1'] == 1:
        len_cilumn_content = 10
        ws.col(10).width = 6000
        ws.col(12).width = 4000
        ws.col(22).width = 6000
    else:
        len_cilumn_content = 7
        ws.col(7).width = 6000
        ws.col(9).width = 4000
        ws.col(16).width = 4000
    ws.col(0 + len_cilumn_content).width = 6000
    write_head(data)
    count_file = 0
    while True:
        try:
            wb.save(f'info{count_file}.xls')
            break
        except PermissionError:
            count_file += 1


def write_head(data):
    pass


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
    save_data_in_excel(data)


if __name__ == '__main__':
    main()