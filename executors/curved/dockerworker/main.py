import json

from libscheduler.worker import WorkerMS

from config import config
from worker import do_docker_job
from log import logger
from worker.harbor import kill_all_containers

import signal

def sigquit_handler(n, f, worker):
    worker.fail_all()

    if config.SIGQUIT_DOCKER_KILLALL:
        kill_all_containers()


def main():
    worker = WorkerMS(
        config.METASCHEDULER_URL,
        config.WORK_QUEUE,
        do_docker_job,
        threads_num=config.THREADS_NUM,
        sleep_time=config.SLEEP_TIME,
    )

    signal.signal(signal.SIGQUIT, lambda n,f: sigquit_handler(n, f, worker))

    logger.debug("Starting worker...")
    worker.start()



if __name__ == '__main__':
    main()
