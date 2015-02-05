import os
import re
import json
import time
import shutil
import argparse
import datetime
import logging
import traceback
from util import sh, test_sh, SUCCESS, ERROR_EXCEPTION
from lockfile import LockFile

from ..config import config
from ..log import logger

DELAY_WAIT_DOCKER_MIN = 0.1
DELAY_WAIT_DOCKER_MAX = 10.0


def do_mc_job(job):
    logger.debug("Got job #{} with descriptor: {}".format(job.job_id, job.descriptor))
    try:
        process(job)
        job.update_status("completed")
    except Exception, e:
        job.update_status("failed")
        job.descriptor['exception'] = str(e)
        job.update_descriptor(job.descriptor)

        logger.error(str(e))
        logger.error(traceback.format_exc())
        raise e



def getargs(jd, subst):
    args = []
    kw_keys = [k for k in jd["args"].keys() if k.startswith("-")]
    for k in kw_keys:
        v = jd["args"][k]
        if v is True:
            args.append(k)
        else:
            args.append("%s=%s" % (k, str(v)))
    pos_keys = sorted([k for k in jd["args"].keys() if k.startswith("__POS")])
    for k in pos_keys:
        v = jd["args"][k]
        if type(v) == str or type(v) == unicode:
            args.append(v)
        else:
            args.extend(v)
    s = " ".join(args)
    for k, v in subst.iteritems():
        s = s.replace(k, str(v))
    return s


def docker_pull_image(image):
    with LockFile("/tmp/jeeves_lock_pull_%s" % re.sub("[:/]", "_", image)):
        result = execute("sudo docker pull %s" % image)


def docker_is_running(container, verbose=False):
    tempfile = "/tmp/jeeves.%d" % os.getpid()
    result = execute("sudo docker ps -a", verbose=verbose, logout=tempfile)
    os.remove(tempfile)


    return container in result["out"]


def execute(command, *args, **kwargs):
    logger.debug("Executing: {}".format(command))
    result = sh(command, *args, **kwargs)

    if result['rc'] != SUCCESS:
        raise Exception("Error executing `{}`. result=`{}`, status=`{}`".format(command, result['rc'], result['status']))
    return result


def is_container_running(containerID):
    result = False
    check_result = sh("sudo docker ps", verbose=False)
    assert len(check_result['err']) == 0, "got error while 'docker ps': %s" % check_result['err']
    assert check_result['rc'] == 0, "got non-zero result while 'docker ps'"
    result = containerID[:12] in check_result['out']
    return result


def process(job):
    jd = job.descriptor
    JOB_ID = job.job_id
    JOB_TAG = jd["app_container"]["name"]
    JOB_SUPER_ID = jd["job_super_id"]
    APP_CONTAINER = "JOB_%s_CNT" % JOB_SUPER_ID
    ENV_CONTAINER = jd["env_container"]["name"]
    WORK_DIR = jd["env_container"]["workdir"]
    CMD = jd["cmd"]
    ENV_VOLUMES = []
    QUOTE_CMD = True
    if 'quote_cmd' in jd:
        QUOTE_CMD = jd['quote_cmd']
    JOB_OUTPUT_DIR = os.path.abspath("%s/%s" % (config.OUTPUT_DIR, JOB_ID))
    if "data_volume" in jd["env_container"]:
        ENV_VOLUMES.append(jd["env_container"]["data_volume"])

    ARGS = getargs(jd,
        {
            "$DATA_DIR": "/data",
            "$OUTPUT_DIR": "/output",
            "$JOB_ID": JOB_ID,
            "$TIMEHASH": hash(time.time())
        }
    )

    if os.path.exists(JOB_OUTPUT_DIR):
        if config.FORCE:
            logger.warning("WARN: Removing '%s'" % JOB_OUTPUT_DIR)
            shutil.rmtree(JOB_OUTPUT_DIR)
        else:
            raise Exception("directory '%s' exists" % JOB_OUTPUT_DIR)
    else:
        os.makedirs(JOB_OUTPUT_DIR)

    docker_pull_image(jd["app_container"]["name"])
    if not docker_is_running(APP_CONTAINER):
        execute(
            "sudo docker run -d -v %s --name %s %s echo %s app" % (
                WORK_DIR,
                APP_CONTAINER,
                JOB_TAG,
                APP_CONTAINER
            ),
            verbose=config.VERBOSE
        )

    ENV_VOLUMES.append("%s:/output" % JOB_OUTPUT_DIR)
    cmd_args = "{cmd} {args}".format(cmd=CMD, args=ARGS)
    if QUOTE_CMD:
        cmd_args = "'%s'" % cmd_args

    docker_cmd = "sudo docker run -d --volumes-from {app} -v {volumes} -w {workdir} {env} {cmd_args}".format(
        app=APP_CONTAINER,
        volumes=" -v ".join(ENV_VOLUMES),
        env=ENV_CONTAINER,
        workdir=WORK_DIR,
        cmd_args=cmd_args
    )

    time0 = datetime.datetime.now()
    docker_pull_image(ENV_CONTAINER)
    result = execute(docker_cmd, verbose=config.VERBOSE)

    containerID = result['out'].strip()
    while True:
        is_running = is_container_running(containerID)
        execute(
            "sudo docker logs %s" % containerID,
            logout="%s/out.log" % JOB_OUTPUT_DIR,
            logerr="%s/err.log" % JOB_OUTPUT_DIR,
            verbose=False
        )

        if not is_running:
            if config.VERBOSE:
                execute(
                    "sudo docker logs %s" % containerID,
                    logout="%s/out.log" % JOB_OUTPUT_DIR,
                    logerr="%s/err.log" % JOB_OUTPUT_DIR,
                    verbose=True
                )
            execute("sudo docker rm %s" % containerID)
            break

        time1 = datetime.datetime.now()
        delay = max(DELAY_WAIT_DOCKER_MIN, min(DELAY_WAIT_DOCKER_MAX, (time1-time0).seconds * 0.1))
        logger.debug("DELAY: {}".format(delay))
        time.sleep(delay)
