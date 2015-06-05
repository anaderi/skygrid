import json

from libscheduler.worker import WorkerMS

from config import config
from worker import do_docker_job
from log import logger

import signal

def main():
    worker = WorkerMS(
        config.METASCHEDULER_URL,
        config.WORK_QUEUE,
        do_docker_job,
        threads_num=config.THREADS_NUM,
        sleep_time=config.SLEEP_TIME,
    )

    signal.signal(signal.SIGQUIT, worker.fail_all)

    logger.debug("Starting worker...")
    worker.start()



if __name__ == '__main__':
    main()
