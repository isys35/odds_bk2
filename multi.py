import os
from multiprocessing import Process


def primer():
    proc = os.getpid()
    print(proc)


if __name__ == '__main__':
    for i in range(0,20):
        proc = Process(target=primer)
        proc.start()