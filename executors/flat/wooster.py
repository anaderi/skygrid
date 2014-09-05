#!/usr/bin/env python
"""
    run job pool
"""

import os
import json
import socket
import logging
import smtplib
import datetime
import tempfile
import argparse
import itertools
import multiprocessing
from email.mime.text import MIMEText
from util import QueueDir, test_queue, sh, SUCCESS, ERROR_INTERRUPT, ERROR_EXCEPTION

verbose = False
MAILFROM = "Wooster@SkyGrid"
MAILHOST = "localhost"

logger = logging.getLogger()
logger.addHandler(logging.StreamHandler())

logger.setLevel(logging.DEBUG)


def parse_args():
    global verbose
    p = argparse.ArgumentParser()
    p.add_argument("--dir", "-d", help="job descriptor pool", default="jobs")
    p.add_argument("--nworkers", "-n", help="number of workers", type=int, default=multiprocessing.cpu_count())
    p.add_argument("--output", "-o", help="output folder", default="output")
    p.add_argument("--verbose", "-v", action='store_true', default=False)
    p.add_argument("--test", "-t", action='store_true', default=False)
    p.add_argument("--mail", "-m", action='store_true', default=False)
    args = p.parse_args()
    if not os.path.exists(args.dir):
        p.error("directory '%s' does not exists" % args.dir)
    args.dir = args.dir.rstrip("/")
    verbose = args.verbose
    return args


def my_dir():
    my_dir = os.path.abspath(os.curdir)
    return os.path.dirname(os.path.join(my_dir, __file__))


def run_jd_wrapper(args):
    return run_jd(*args)


def run_jd(jds, output_dir):
    result = {
        "rc": ERROR_EXCEPTION,
        "status": "",
        "jd": jds
    }
    try:
        with tempfile.NamedTemporaryFile() as fh:
            json.dump(jds, fh, indent=2, sort_keys=True)
            fh.flush()
            runner = os.path.join(my_dir(), "jeeves.py")
            cmd = "{runner} --input {file} --output {out} -v".format(
                runner=runner, file=fh.name, out=output_dir)
            logger.info("CMD: " + cmd)
            sh_result = sh(cmd)
            result["rc"] = sh_result["rc"]
            if len(sh_result["status"]) > 0:
                result["status"] = sh_result["status"]
            if len(sh_result["out"]) > 0:
                result["status"] += sh_result["out"]
            if len(sh_result["err"]) > 0:
                result["status"] += sh_result["err"]
    except Exception, e:
        result["status"] = "EXCEPTION: " + e.__repr__()
    return result


def notify_email(mailto, report):
    subject = "Wooster@SkyGrid process report"
    body = """\
%s

--
Faithfully Yours,
Wooster @ %s
""" % (report, socket.gethostname())
    try:
        msg = MIMEText(body)
        msg['To'] = mailto
        msg['From'] = MAILFROM
        msg['Subject'] = subject

        smtpObj = smtplib.SMTP(MAILHOST)
        smtpObj.sendmail(MAILFROM, mailto, msg.as_string())
        logger.info("Successfully sent email to %s" % mailto)
    except smtplib.SMTPException, e:
        logger.error("Error: unable to send email to '%s' (%s)" % (mailto, str(e)))


def make_report(results, time_run, nthreads):
    failset = set()
    failrate = 0
    for rd in results:
        if rd["rc"] != SUCCESS:
            failset.add(rd["jd"]["job_id"])
    if len(results) > 0:
        failrate = 100. * len(failset) / len(results)
    report = """
{jobs} job descriptors has been processed in {time} sec.
Host: '{host}'
Workers: {nthreads}
Failure rate: {failrate:0.1f}%
""".format(jobs=len(results), failrate=failrate, nthreads=nthreads,
           time=time_run, host=socket.gethostname())
    if len(failset) > 0:
        report += "\nFailed IDs ({n}): {failset}".format(n=len(failset), failset=list(failset))
    return report


def main(args):
    if args.test:
        test_queue()
        exit(1)
    p = multiprocessing.Pool(args.nworkers)
    q_input = QueueDir(args.dir)
    q_fail = QueueDir(args.dir + ".fail", default_mask=q_input.mask)
    q_success = QueueDir(args.dir + ".success", default_mask=q_input.mask)

    output_list = itertools.repeat(args.output)
    time_start = datetime.datetime.now()
    results = []
    while True:
        job_slice = q_input.get_n(args.nworkers)
        if job_slice is None:
            break
        try:
            results_slice = p.map(run_jd_wrapper,
                                  zip(job_slice, output_list))
            for rd in results_slice:
                results.append(rd)
                if rd["rc"] == SUCCESS:
                    rd['jd']['status'] = "SUCCESS"
                    q_success.put(rd["jd"])
                else:
                    rd['jd']['status'] = "FAIL"
                    q_fail.put(rd["jd"])
                    logger.warn("FAIL (%d):\nJD: %s\n%s" % (rd["rc"], rd["jd"], rd["status"]))
        except KeyboardInterrupt:
            for jd in job_slice:
                jd['status'] = "INTERRUPT"
                results.append({'status': "^C", 'rc': ERROR_INTERRUPT, 'jd': jd})
            q_fail.extend(job_slice)

    time_end = datetime.datetime.now()
    time_run = time_end - time_start

    report = make_report(results, time_run, args.nworkers)
    print report
    if args.mail and len(results) > 0 and results[0]["jd"]["email"] is not None:
        notify_email(results[0]["jd"]["email"], report)


if __name__ == '__main__':
    main(parse_args())
