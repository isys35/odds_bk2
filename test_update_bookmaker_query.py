import time
import sqlite3
from collections import Counter
db = 'oddsportal.db'


def brenchmark(func):
    def wrapper(*args):
        start = time.time()
        func(*args)
        end = time.time()
        print('[INFO] Время ' + str(end - start))

    return wrapper


@brenchmark
def update_bookmaker():
    con = sqlite3.connect(db)
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
    print(data_bookmaker_checklist)
    cur.close()
    con.close()

update_bookmaker()
