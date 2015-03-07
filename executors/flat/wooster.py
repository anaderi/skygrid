#!/usr/bin/env python
"""
    run job pool
"""

import os
import sys
import json
import time
import socket
import logging
import smtplib
import cPickle
import datetime
import tempfile
import argparse
import itertools
import multiprocessing
from email.mime.text import MIMEText
from util import QueueDir, test_queue, sh, SUCCESS, ERROR_INTERRUPT, ERROR_EXCEPTION

MAILFROM = "Wooster@SkyGrid"
MAILHOST = "localhost"
SLEEP_DELAY = 1
HOSTNAME = socket.gethostname().split('.')[0]
logger = None


def parse_args():
    global logger
    p = argparse.ArgumentParser()
    p.add_argument("--dir", "-d", help="job descriptor pool", default="jobs")
    p.add_argument("--nworkers", "-n", help="number of workers", type=int, default=multiprocessing.cpu_count())
    p.add_argument("--niterations", help="number of iterations", type=int, default=None)
    p.add_argument("--output", "-o", help="output folder", default="output-%s" % HOSTNAME)
    p.add_argument("--verbose", "-v", action='store_true', default=False)
    p.add_argument("--test", "-t", action='store_true', default=False)
    p.add_argument("--mail", "-m", action='store_true', default=False)
    p.add_argument("--log", help="logfile name (wooster_HOSTNAME.log)", default="wooster_%s.log" % HOSTNAME)
    args = p.parse_args()
    if not os.path.exists(args.dir) and not args.test:
        p.error("directory '%s' does not exists" % args.dir)
    logging.basicConfig(filename=args.log, filemode='w', level=logging.INFO)
    logger = logging.getLogger()    
    args.dir = args.dir.rstrip("/")
    if args.verbose:
        logger.setLevel(logging.DEBUG)
        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setLevel(logging.DEBUG)
        logger.addHandler(stream_handler)
    if args.niterations == 0:
        args.niterations = None
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
    # TODO rndom delay before start
    try:
        with tempfile.NamedTemporaryFile() as fh:
            json.dump(jds, fh, indent=2, sort_keys=True)
            fh.flush()
            runner = os.path.join(my_dir(), "jeeves.py")
            cmd = "{runner} --input {file} --output {out} -v".format(
                runner=runner, file=fh.name, out=output_dir)
            logger.info("CMD: " + cmd)
            sh_result = sh(cmd, logout="jeeves_out_%d.log" % jds['job_id'],
                logerr="jeeves_err_%d.log" % jds['job_id'])
            result["rc"] = sh_result["rc"]
            if len(sh_result["status"]) > 0:
                result["status"] = sh_result["status"]
            if len(sh_result["out"]) > 0:
                result["status"] += sh_result["out"]
            if len(sh_result["err"]) > 0:
                result["status"] += sh_result["err"]
            logger.info("JEEVES_OUTPUT (JOB_ID={job})\n{sep}\n{out}\n{sep}".format(
                job=jds['job_id'], out=result['status'], sep='='*80))
    except Exception, e:
        result["status"] = "EXCEPTION: " + e.__repr__()
        logger.error(result['status'])
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


class ResultSlots(object):
    def __init__(self, count):
        self.slots = []
        for i in range(count):
            self.slots.append(None)

    def is_slot_available(self):
        return len([item for item in self.slots if item is None]) > 0

    def empty(self):
        return len([item for item in self.slots if item is not None]) == 0

    def get_empty_idx(self):
        for i, v in enumerate(self.slots):
            if v is None:
                return i
        return None

    def __getitem__(self, i):
        return self.slots[i]

    def __setitem__(self, i, v):
        self.slots[i] = v

    def __iter__(self):
        return self.slots.__iter__()

    def __repr__(self):
        return self.slots.__repr__()


def test_slots():
    print "## test slots"
    slots = ResultSlots(4)
    assert slots.is_slot_available()
    assert slots.get_empty_idx() == 0
    assert slots[0] is None
    slots[0] = 1
    assert slots[0] == 1
    assert slots.get_empty_idx() == 1
    assert slots.is_slot_available()
    slots[2] = 1
    assert slots.get_empty_idx() == 1
    slots[0] = None
    assert slots.get_empty_idx() == 0
    assert slots.is_slot_available()
    assert slots.empty() == False
    slots[2] = None
    assert slots.empty()
    for i in slots:
        print i
    print "OK"


def test_cache():
    name = "test.ext"
    if os.path.exists(name):
        os.remove(name)
    locker = Cache(name)
    assert not locker.exists()
    jd1 = {'job_id': 1}
    jd2 = {'job_id': 2}
    locker.lock(jd1)
    assert locker.load().keys()[0] == jd1['job_id']
    assert locker.unlock(jd1)
    assert not locker.unlock(jd2)
    assert not locker.exists()
    locker.lock(jd1)
    locker.clear()
    assert not locker.exists()


class Cache(object):
    def __init__(self, filename):
        self.filename = filename

    def exists(self):
        return os.path.exists(self.filename)

    def lock(self, jd):
        jds = self.load()
        assert jd['job_id'] not in jds
        jds[jd['job_id']] = jd
        self._dump(jds)

    def unlock(self, jd):
        jds = self.load()
        if jd['job_id'] not in jds:
            return False
        del jds[jd['job_id']]
        self._dump(jds)
        return True

    def _dump(self, jds):
        if len(jds) > 0:
            with open(self.filename, "w") as fh:
                cPickle.dump(jds, fh)
        else:
            os.remove(self.filename)

    def load(self):
        jds = {}
        if self.exists():
            with open(self.filename, "r") as fh:
                jds = cPickle.load(fh)
        return jds

    def clear(self):
        if self.exists():
            os.remove(self.filename)


def update_results(results, q_success, q_fail, locker, result_log):
    print "### update_result"
    for i, r in enumerate(results):
        if r is None:
            continue
        print "#### %d, %s, %s" % (i, r, r.ready())
        if r.ready():
            rd = r.get()
            if rd['rc'] == SUCCESS:
                rd['jd']['status'] = "SUCCESS"
                q_success.put(rd['jd'])
            else:
                rd['jd']['status'] = rd['rc']
                rd['jd']['status'] = rd['status']
                q_fail.put(rd['jd'])
                logger.warn("FAIL (%d):\nJD: %s\n%s" % (rd["rc"], rd["jd"], rd["status"]))
            unlock_result = locker.unlock(rd['jd'])
            assert unlock_result
            results[i] = None
            result_log.append(rd)


def main(args):
    if args.test:
        print args.niterations
        logger.setLevel(logging.DEBUG)
        test_queue()
        test_slots()
        test_cache()
        exit(1)
    pool = multiprocessing.Pool(args.nworkers)
    q_input = QueueDir(args.dir)
    q_fail = QueueDir(args.dir + ".fail", default_mask=q_input.mask)
    q_success = QueueDir(args.dir + ".success", default_mask=q_input.mask)
    locker = Cache(args.dir + ".locker")
    assert not locker.exists()

    time_start = datetime.datetime.now()
    result_async = ResultSlots(args.nworkers)
    result_log = []

    try:
        for jd in itertools.islice(q_input, args.niterations):
            locker.lock(jd)
            while not result_async.is_slot_available():
                time.sleep(SLEEP_DELAY)
                update_results(result_async, q_success, q_fail, locker, result_log)
            slot_id = result_async.get_empty_idx()
            result_async[slot_id] = pool.apply_async(run_jd, [jd, args.output])
        while not result_async.empty():
            print "## Non empty"
            print result_log 
            update_results(result_async, q_success, q_fail, locker, result_log)
            time.sleep(SLEEP_DELAY)

    except KeyboardInterrupt:
        logger.warn("Caught SIGINT (^C), terminating")
        logger.warn("Dumping jds")
        for jd in locker.load().values():
            jd['status'] = "INTERRUPT"
            result_log.append({'status': "^C", 'rc': ERROR_INTERRUPT, 'jd': jd})
            q_fail.put(jd)
        logger.warn("Terminate pool")
        pool.close()
        pool.terminate()
        logger.warn("Waiting for processes to stop")
        pool.join()

    time_end = datetime.datetime.now()
    time_run = time_end - time_start
    locker.clear()

    report = make_report(result_log, time_run, args.nworkers)
    logger.info(report)
    if args.mail and len(result_log) > 0 and result_log[0]["jd"]["email"] is not None:
        notify_email(result_log[0]["jd"]["email"], report)


if __name__ == '__main__':
    main(parse_args())
