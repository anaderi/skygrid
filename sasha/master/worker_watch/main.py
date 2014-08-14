from time import time, sleep

from ..generic.models import Worker

SLEEP_TIME = 2
ROT_TIME = 10


def main():
    while True:
        sleep(SLEEP_TIME)

        for worker in Worker.objects():
            if abs(time() - worker.last_seen) > ROT_TIME:
                print "<Worker: {}> has rotten!".format(worker)


if __name__ == "__main__":
    main()