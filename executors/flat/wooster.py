#!/usr/bin/env python
"""
    run job pool
"""

import os
import time
import argparse
import subprocess
import multiprocessing
import itertools
# from functools import partial

SUCCESS = 0
ERROR = 1
verbose = False


def parse_args():
    global verbose
    p = argparse.ArgumentParser()
    p.add_argument("--dir", "-d", help="job descriptor pool", default="jobs")
    p.add_argument("--nworkers", "-n", help="number of workers", type=int, default=multiprocessing.cpu_count())
    p.add_argument("--output", "-o", help="output folder", default="output")
    p.add_argument("--verbose", "-v", action='store_true', default=False)
    args = p.parse_args()
    if not os.path.exists(args.dir):
        p.error("directory '%s' does not exists" % args.dir)
    verbose = args.verbose
    return args


def my_dir():
    my_dir = os.path.abspath(os.curdir)
    return os.path.dirname(os.path.join(my_dir, __file__))


def run_jd_wrapper(args):
    return run_jd(*args)


def run_jd(jd_filename, output, verbose=False):
    print "run", jd_filename, "out:", output
    result = {
        "rc": ERROR,
        "status": ""
    }
    try:
        runner = os.path.join(my_dir(), "jeeves.py")
        cmd = [runner, "--input", jd_filename, "--output", output]
        if verbose:
            print "CMD:", " ".join(cmd)
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        (out, err) = p.communicate()
        result["rc"] = p.returncode
    except Exception, e:
        result["status"] = e.__repr__()
    return result


def job_list(directory):
    job_list = os.listdir(directory)
    return [os.path.abspath("%s/%s" % (directory, f)) for f in job_list]


def main(args):
    p = multiprocessing.Pool(args.nworkers)
    file_list = job_list(args.dir)
    output_list = itertools.repeat(args.output)
    verbose_list = itertools.repeat(True)
    result = p.map(run_jd_wrapper, zip(file_list, output_list, verbose_list))
    print "Result:", result


if __name__ == '__main__':
    main(parse_args())
