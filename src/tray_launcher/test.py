import time as _t

def main():
    last = 60
    count = 1
    while (count < last):
        print(_t.time())
        count += 1
        _t.sleep(3)