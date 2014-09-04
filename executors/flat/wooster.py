#!/usr/bin/env python
"""
    run job pool
"""

import os
import re
import json
import socket
import logging
import smtplib
import datetime
import tempfile
import argparse
import subprocess
import itertools
import multiprocessing
from email.mime.text import MIMEText

SUCCESS = 0
ERROR_EXCEPTION = 254
verbose = False
MAILFROM = "Wooster@SkyGrid"
MAILHOST = "localhost"

logger = logging.getLogger()
logger.addHandler(logging.StreamHandler())

logger.setLevel(logging.DEBUG)


class QueueDir(object):

    def __init__(self, dirname, default_mask="%d_job.json"):
        self.dirname = os.path.abspath(dirname)
        if os.path.exists(dirname):
            assert os.path.isdir(dirname), "%s is not a directory" % dirname
        else:
            os.makedirs(dirname)
        self.mask = self._detect_mask(default_mask)
        logger.debug(self)

    def __str__(self):
        return "QueueDir: %s, mask: %s, count: %d" % (self.dirname, self.mask, self.qsize())

    def _detect_mask(self, default_mask):
        masks = {default_mask: 0}
        for name in os.listdir(self.dirname):
            mgroups = re.match("(\D*)(\d+)(\D*)", name)
            if mgroups is not None:
                mask = "%s%%d%s" % (mgroups.groups()[0], mgroups.groups()[2])
                if mask in masks:
                    masks[mask] += 1
                else:
                    masks[mask] = 1
        sorted_keys = sorted(masks, key=masks.get)
        print sorted_keys, masks
        return sorted_keys[-1]

    def qsize(self):
        return len(self.__unsorted_list_name_id())

    def empty(self):
        return self.qsize() == 0

    def __get_max_id(self):
        name_id = self.__unsorted_list_name_id()
        if len(name_id) == 0:
            return 0
        sorted_name_id = sorted(name_id, key=lambda x: x[1])
        return sorted_name_id[-1][1]

    def __unsorted_list_name_id(self):
        m_re = self.mask.replace("%d", "(\d+)")
        name_id_list = [(name, int(re.match(m_re, name).groups()[0]))
                        for name in os.listdir(self.dirname) 
                        if re.match(m_re, name) is not None]
        return name_id_list

    def list_files(self):
        name_id = self.__unsorted_list_name_id()
        sorted_name_id = sorted(name_id, key=lambda x: x[1])
        return ["%s/%s" % (self.dirname, i[0]) for i in sorted_name_id]

    def __iter__(self):
        return self

    def next(self):
        if self.empty():
            raise StopIteration
        return self.get()

    def extend(self, iterable):
        for i in iterable:
            self.put(i)

    def put(self, item):
        i = self.__get_max_id() + 1
        filename = os.path.join(self.dirname, self.mask % i)
        logger.info("put: %s // %s" % (filename, item))
        with open(filename, "w") as fh:
            json.dump(item, fh, indent=2, sort_keys=True)

    def get(self):
        filename = self.list_files()[0]
        with open(filename) as fh:
            item = json.load(fh)
        if item is not None:
            os.remove(filename)
            logger.info("get: %s" % item)
        return item


def test_queue():
    import shutil
    dirs = ["_d1", "_d2"]
    for d in dirs:
        if os.path.exists(d):
            shutil.rmtree(d)
    q1 = QueueDir(dirs[0])
    assert q1.qsize() == 0
    assert q1.empty()
    i1 = {'key': 1}
    q1.put(i1)
    assert q1.qsize() == 1
    o1 = q1.get()
    assert i1 == o1
    assert q1.qsize() == 0
    os.makedirs(dirs[1])
    with open("%s/sub123" % dirs[1], "w") as fh:
        json.dump("123", fh)
    q2 = QueueDir(dirs[1])
    q2.put(i1)
    q2.put({'key': 2})
    assert q2.qsize() == 3
    l = []
    for i in q2:
        logger.info("iter: %s" % i)
        l.append(i)
    assert q2.empty()
    q1.extend(l)
    assert q1.qsize() == 3

    i1 = q1.get()
    q1.put(i1)
    assert q1.qsize() == 3, q1.qsize()
    for d in dirs:
        if os.path.exists(d):
            shutil.rmtree(d)


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
            cmd = [runner, "--input", fh.name, "--output", output_dir, "-v"]
            logger.info("CMD:" + " ".join(cmd))
            p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            (out, err) = p.communicate()
            result["rc"] = p.returncode
            if out is not None and len(out.strip()) > 0:
                result["status"] += "OUT: %s\n" % out
            if err is not None and len(err.strip()) > 0:
                result["status"] += "ERR: %s\n" % err
            logfile = "%s/%d/output.log" % (output_dir, jds["job_id"])
            with open(logfile, "w") as fh_log:
                fh_log.write(result["status"])
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
    failrate = "(n/a)"
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
    results = p.map(run_jd_wrapper,
                    zip(q_input, output_list))
    time_end = datetime.datetime.now()
    time_run = time_end - time_start
    for rd in results:
        if rd["rc"] == SUCCESS:
            q_success.put(rd["jd"])
        else:
            q_fail.put(rd["jd"])
            logger.warn("FAIL (%d):\nJD: %s\n%s" % (rd["rc"], rd["jd"], rd["status"]))

    report = make_report(results, time_run, args.nworkers)
    print report
    if args.mail and len(results) > 0:
        mailto = results[0]["jd"]["email"]
        notify_email(mailto, report)


if __name__ == '__main__':
    main(parse_args())
