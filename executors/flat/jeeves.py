#!/usr/bin/env python
"""
    runner of a job by job descriptor
"""
import os
import json
import shutil
import shlex
import argparse
import traceback
import subprocess

SUCCESS = 0
ERROR = 254
verbose = False


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


def test_sh():
    result = sh("ls -l", verbose=False)
    assert result['rc'] == 0, result
    filename = result['out'].split("\n")[2].split()[8]
    print "FILENAME:", filename
    result = sh("ls -l", verbose=True)
    assert result['rc'] == 0
    assert filename in result['out']
    result = sh("ls -l", verbose=True, logout="log.log")
    assert result['rc'] == 0
    assert os.path.exists("log.log")
    result = sh("rm log1.log", verbose=True, logerr="err.log")
    assert result['rc'] != 0
    assert os.path.exists("err.log")
    result = sh("rm log.log", verbose=True)
    assert result['rc'] == 0
    result = sh("rm err.log", verbose=True)
    assert result['rc'] == SUCCESS
    result = sh("xxx err.log", verbose=True)
    assert result['rc'] == ERROR
    print "ERR:", result['status']
    result = sh("echo 'no split single quotes'", verbose=True)
    assert result["rc"] == 0
    assert result["out"].strip() == "no split single quotes"


def sh(cmd, input=None, verbose=False, logout=None, logerr=None):
    if verbose: print "`%s`" % cmd
    cmd_args = shlex.split(cmd.encode('ascii'))
    result = {
        'status': "",
        'out': None,
        'err': None,
        'rc': 0
    }
    try:
        fh_out, fh_err = (subprocess.PIPE, subprocess.PIPE)
        if logout is not None:
            fh_out = open(logout, "w")
        if logerr is not None:
            fh_err = open(logerr, "w")
        proc = subprocess.Popen(cmd_args, stdout=fh_out, stderr=fh_err)
        proc.wait()

        if fh_out != subprocess.PIPE:
            fh_out.close()
            with open(logout, "r") as fh_out:
                out = fh_out.read()
        else:
            out = proc.stdout.read()
        if fh_err != subprocess.PIPE:
            fh_err.close()
            with open(logerr, "r") as fh:
                err = fh.read()
        else:
            err = proc.stderr.read()

        if out is not None and len(out) > 0:
            if verbose:
                print "===OUT===\n%s" % out
            if logout is not None:
                with open(logout, "a") as fh:
                    fh.write(out)
        if err is not None and len(err) > 0:
            if verbose:
                print "===ERR===\n%s" % err
            if logerr is not None:
                with open(logerr, "a") as fh:
                    fh.write(err)
        result['rc'] = proc.returncode
        result['out'] = out
        result['err'] = err
    except Exception:
        result['status'] = traceback.format_exc()
        result['rc'] = ERROR
    return result


def docker_is_running(container, verbose=False):
    result = sh("docker ps -a", verbose=verbose)
    if result["rc"] == ERROR:
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
        s = s.replace(k, v)
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
    if not docker_is_running(APP_CONTAINER):
        result = sh("docker run -d -v %s --name %s %s echo %s app" % 
                    (WORK_DIR, APP_CONTAINER, JOB_TAG, APP_CONTAINER),
                    verbose=verbose)
        if result['rc'] != SUCCESS:
            halt("error running app container %s (%d, %s)" % (APP_CONTAINER, result['rc'], result['status']))
    os.makedirs(JOB_OUTPUT_DIR)
    ENV_VOLUMES.append("%s:/output" % JOB_OUTPUT_DIR)
    docker_cmd = "docker run --rm -t --volumes-from {app} -v {volumes} -w {workdir} {env} '{cmd} {args}'".format(
        app=APP_CONTAINER, volumes=" -v".join(ENV_VOLUMES), 
        env=ENV_CONTAINER, cmd=CMD, args=ARGS, workdir=WORK_DIR)
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
