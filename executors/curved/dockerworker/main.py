import os
import json
import signal

from libscheduler.worker import WorkerMS

from config import config
from worker import do_docker_job
from log import logger
from worker.harbor import kill_all_containers

from lockfile import LockFile


def break_lock():
    return LockFile(config.LOCK_FILE).break_lock()

def sigquit_handler(n, f, worker):
    worker.fail_all()

    if config.SIGQUIT_DOCKER_KILLALL:
        logger.debug("Killing all containers")
        kill_all_containers()

    break_lock()

def main():
    break_lock()

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
