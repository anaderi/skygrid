import os
import re
import json
import time
import shutil
import argparse
import datetime
import logging
from util import sh, test_sh, SUCCESS, ERROR_EXCEPTION
from lockfile import LockFile

from .. import config
from ..log import logger

DELAY_WAIT_DOCKER_MIN = 0.1
DELAY_WAIT_DOCKER_MAX = 10.0


def do_mc_job(job):
    logger.debug("Got MC job:" + str(job.descriptor))
    try:
        process(job)
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
        result = execute("docker pull %s" % image)


def docker_is_running(container, verbose=False):
    tempfile = "/tmp/jeeves.%d" % os.getpid()
    result = execute("docker ps -a", verbose=verbose, logout=tempfile)
    os.remove(tempfile)


    return container in result["out"]


def execute(command, *args, **kwargs):
    result = sh(command, *args, **kwargs)

    if result['rc'] != SUCCESS:
        raise Exception("Error executing `{}`. result=`{}`, status=`{}`".format(APP_CONTAINER, result['rc'], result['status']))


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

    JOB_OUTPUT_DIR = os.path.join(config.OUTPUT_DIR, JOB_ID)
    if "data_volume" in jd["env_container"]:
        ENV_VOLUMES.append(jd["env_container"]["data_volume"])

    ARGS = getargs(jd,
        {
            "$DATA_DIR": "/data",
            "$OUTPUT_DIR": "/output",
            "$JOB_ID": JOB_ID
        }
    )

    if os.path.exists(JOB_OUTPUT_DIR):
        if force:
            print "WARN: Removing '%s'" % JOB_OUTPUT_DIR
            shutil.rmtree(JOB_OUTPUT_DIR)
        else:
            raise Exception("directory '%s' exists" % JOB_OUTPUT_DIR)
    else:
        os.makedirs(JOB_OUTPUT_DIR)

    if not docker_is_running(APP_CONTAINER):
        execute(
            "docker run -d -v %s --name %s %s echo %s app" % (
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

    docker_cmd = "docker run --rm -t --volumes-from {app} -v {volumes} -w {workdir} {env} {cmd_args}".format(
        app=APP_CONTAINER,
        volumes=" -v ".join(ENV_VOLUMES),
        env=ENV_CONTAINER,
        workdir=WORK_DIR,
        cmd_args=cmd_args
    )

    execute(
        docker_cmd,
        verbose=config.VERBOSE,
        logout=os.path.join(JOB_OUTPUT_DIR, "out.log"),
        logerr=os.path.join(JOB_OUTPUT_DIR, "err.log")
    )
