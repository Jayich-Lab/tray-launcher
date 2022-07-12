import time as _t

def main():
    last = 60
    count = 0
    while (count < last):
        print(count, flush=True)
        count += 1
        _t.sleep(1)

if __name__ == "__main__":
    main()