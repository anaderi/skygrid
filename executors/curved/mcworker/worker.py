import json

from libscheduler.worker import WorkerMS

import config
from mc import do_mc_job
from log import logger



def main():
    worker = WorkerMS(
        config.METASCHEDULER_URL,
        "queue6",
        do_mn_job,
        threads_num=4,
        sleep_time=1
    )

    logger.debug("Starting worker...")
    worker.start()



if __name__ == '__main__':
    main()
