from parser_odds import Grabber


def save_data_in_file(data):
    print(data)


def main():
    parser = Grabber()
    url_event = input('Введите ссылку')
    parser.get_event_data(url_event)


if __name__ == '__main__':
    main()