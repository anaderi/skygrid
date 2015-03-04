import json

from libscheduler.worker import WorkerMS

from config import config
from worker import do_docker_job
from log import logger



def main():
    worker = WorkerMS(
        config.METASCHEDULER_URL,
        "montecarlo_queue",
        do_mc_job,
        threads_num=4,
        sleep_time=1
    )

    logger.debug("Starting worker...")
    worker.start()



if __name__ == '__main__':
    main()
