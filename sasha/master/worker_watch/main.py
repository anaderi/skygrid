from time import time, sleep

from ..generic.models import Worker

SLEEP_TIME = 2
ROT_TIME = 5


def main():
    while True:
        sleep(SLEEP_TIME)

        workers = Worker.objects(
            last_seen__lte=(time() - ROT_TIME),
            active=True
        )

        for worker in workers:
            print "<Worker: {}> has rotten!".format(worker)
            worker.active = False
            worker.save()


if __name__ == "__main__":
    main()