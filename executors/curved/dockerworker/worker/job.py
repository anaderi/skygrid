import os
import socket
import time
import traceback

import harbor

import util
import logic

from ..config import config
from ..log import logger, capture_exception

from lockfile import LockFile

def do_docker_job(job):
    logger.debug("Got descriptor: {}".format(job.descriptor))
    try:
        job.update_status("running")
        process(job)
        job.update_status("completed")
        logger.debug("Finished")
    except BaseException, e:
        capture_exception()
        job.update_status("failed")

        if config.DEBUG:
            job.update_debug({
                "hostname": socket.gethostname(),
                "exception": str(e),
                "traceback": traceback.format_exc()
            })

        logger.error(str(e))
        logger.error(traceback.format_exc())
        raise e


def process(job):
    util.descriptor_correct(job)

    job_dir, in_dir, out_dir = logic.create_workdir(job)

    mounted_ids = []
    container_id = None
    try:
        logic.get_input_files(job, in_dir)

        with LockFile(config.LOCK_FILE):
            mounted_ids, container_id = logic.create_containers(job, in_dir, out_dir)

        while harbor.is_running(container_id):
            logger.debug("Container is running. Sleeping for {} sec.".format(config.CONTAINER_CHECK_INTERVAL))
            time.sleep(config.CONTAINER_CHECK_INTERVAL)

        logic.write_std_output(container_id, out_dir)

        logic.upload_output_files(job, out_dir)
    except Exception, e:
        capture_exception()
        raise e
    finally:
        logic.cleanup_dir(job_dir)

        cnt_to_remove = mounted_ids
        if container_id:
            cnt_to_remove += [container_id]

        with LockFile(config.LOCK_FILE):
            logic.cleanup_containers(cnt_to_remove)
