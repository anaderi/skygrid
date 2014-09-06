#!/usr/bin/env python
"""
    runner of a job by job descriptor
"""
import os
import json
import shutil
import argparse
import logging
from util import sh, test_sh, SUCCESS, ERROR_EXCEPTION

verbose = False
logger = logging.getLogger()
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)


def parse_args():
    global verbose
    p = argparse.ArgumentParser()
    p.add_argument("--input", "-i", help="job descriptor input", default="jd_lsmb.json")
    p.add_argument("--output", "-o", help="output folder", default="output")
    p.add_argument("--storage", "-s", help="output storage folder", default="storage")
    p.add_argument("--force", "-f", action='store_true', default=False)
    p.add_argument("--test", "-t", action='store_true', default=False)
    p.add_argument("--verbose", "-v", action='store_true', default=False)
    args = p.parse_args()
    if not os.path.exists(args.input) and not args.test:
        p.error("file '%s' does not exists" % args.input)
    verbose = args.verbose
    return args


def docker_is_running(container, verbose=False):
    result = sh("docker ps -a", verbose=verbose)
    if result["rc"] == ERROR_EXCEPTION:
        return False
    return container in result["out"]


def halt(msg):
    print "HALT: %s" % msg
    exit(1)


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


def run_jd(jd, output_basedir="output", force=False):
    global verbose
    JOB_ID = jd["job_id"]
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
    JOB_OUTPUT_DIR = os.path.abspath("%s/%s" % (output_basedir, JOB_ID))
    if "data_volume" in jd["env_container"]:
        ENV_VOLUMES.append(jd["env_container"]["data_volume"])
    ARGS = getargs(jd, {"$DATA_DIR": "/data", 
                   "$OUTPUT_DIR": "/output",
                   "$JOB_ID": JOB_ID
                        })

    if os.path.exists(JOB_OUTPUT_DIR):
        if force:
            print "WARN: Removing '%s'" % JOB_OUTPUT_DIR
            shutil.rmtree(JOB_OUTPUT_DIR)
        else:
            halt("directory '%s' exists" % JOB_OUTPUT_DIR)
    else:
        os.makedirs(JOB_OUTPUT_DIR)
    if not docker_is_running(APP_CONTAINER):
        result = sh("docker run -d -v %s --name %s %s echo %s app" % 
                    (WORK_DIR, APP_CONTAINER, JOB_TAG, APP_CONTAINER),
                    verbose=verbose)
        if result['rc'] != SUCCESS:
            halt("error running app container %s (%d, %s)" % (APP_CONTAINER, result['rc'], result['status']))
    ENV_VOLUMES.append("%s:/output" % JOB_OUTPUT_DIR)
    cmd_args = "{cmd} {args}".format(cmd=CMD, args=ARGS)
    if QUOTE_CMD:
        cmd_args = "'%s'" % cmd_args
    docker_cmd = "docker run --rm -t --volumes-from {app} -v {volumes} -w {workdir} {env} {cmd_args}".format(
        app=APP_CONTAINER, volumes=" -v ".join(ENV_VOLUMES), 
        env=ENV_CONTAINER, workdir=WORK_DIR, cmd_args=cmd_args)
    result = sh(docker_cmd, verbose=verbose, logout="%s/out.log" % JOB_OUTPUT_DIR, logerr="%s/err.log" % JOB_OUTPUT_DIR, )
    if result['rc'] != SUCCESS:
        halt("error running env container %s (%d, %s)" % (ENV_CONTAINER, result['rc'], result['status']))


def gather_output(jd, output_basedir, output_storage):
    JOB_ID = jd["job_id"]
    JOB_OUTPUT_DIR = os.path.abspath("%s/%s" % (output_basedir, JOB_ID))
    pass
    # shutil.copytree(JOB_OUTPUT_DIR, output_storage)


def main(args):
    if args.test:
        test_sh()
        exit(1)
    with open(args.input) as fh:
        jd = json.load(fh)
        run_jd(jd, output_basedir=args.output, force=args.force)
        gather_output(jd, output_basedir=args.output, output_storage=args.storage)


if __name__ == '__main__':
    main(parse_args())
