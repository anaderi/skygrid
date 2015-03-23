import os
import time
import traceback

import harbor

import util
import logic

from ..config import config
from ..log import logger


def do_docker_job(job):
    logger.debug("Got descriptor: {}".format(job.descriptor))
    try:
        job.update_status("running")
        process(job)
        job.update_status("completed")
        logger.debug("Finished")
    except Exception, e:
        job.update_status("failed")
        # job.descriptor['exception'] = str(e) # TODO: add error field to job in metascheduler
        # job.update_descriptor(job.descriptor)

        logger.error(str(e))
        logger.error(traceback.format_exc())
        raise e


def process(job):
    util.descriptor_correct(job)

    job_dir, in_dir, out_dir = logic.create_workdir(job)

    logic.get_input_files(job, in_dir)
    mounted_ids, container_id = logic.create_containers(job, in_dir, out_dir)

    while harbor.is_running(container_id):
        logger.debug("Container is running. Sleeping for {} sec.".format(config.SLEEP_TIME))
        time.sleep(config.SLEEP_TIME)

    logic.write_std_output(container_id, out_dir)

    logic.upload_output_files(job, out_dir)

    logic.cleanup(job_dir, mounted_ids + [container_id])
