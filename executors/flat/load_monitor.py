#!/usr/bin/env python
import re
import glob
import util
import shutil
import datetime
import tempfile
import argparse
from libscheduler.queue import QueueMS

API_URL = "http://mc03.h.cern.yandex.net:5000"

# Add the functions descriptions.
def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--hosts", default=None, required=True)
    parser.add_argument("--min_load", type=float, default=20.0)
    parser.add_argument("--min_hosts", type=int, default=15)
    parser.add_argument("--min_qsize", type=int, default=1000)
    parser.add_argument("--queue_name", default="queue5")
    parser.add_argument("--email", default="anaderi@yandex-team.ru")
    parser.add_argument("--log", default=None)
    args = parser.parse_args()
    return args


def queue_size(queue_name):
    queue = QueueMS(queue_name, api_url=API_URL)
    return queue.qsize()


def notify(email, avg_load, num_hosts):
    util.sh("/root/bin/notify.sh 'MC load average' load_avg: %f, hosts: %d" % (avg_load, num_hosts), verbose=True)


def notify_recharge(email, qsize):
    util.sh("/root/bin/notify.sh 'Recharge queue' current size: %d" % qsize, verbose=True)


def log(log, vals):
    if log is not None:
        with open(log, "a") as fh:
            fh.write("%s\t%s\n" % (datetime.datetime.now(), '\t'.join(map(str, vals))))


def main(args):
    dir = tempfile.mkdtemp()
    result = util.sh("pssh -h %s -o %s uptime" % (args.hosts, dir))
    if result['rc'] != 0:
        print "WARN: RC: %d, %s\n%s\n" % (result['rc'], result['out'], result['err'])
    f = glob.glob("%s/*" % dir)
    r = util.sh("cat " + " ".join(f))
    ll = r['out'].strip().split('\n')
    print dir, ll
    avgs = map(lambda l: float(re.search("average: ([\d.]*)", l).groups()[0]), ll)
    shutil.rmtree(dir)
    num_hosts = len(avgs)
    avg_load = sum(avgs)/num_hosts
    qsize = queue_size(args.queue_name)

    log(args.log, (avg_load, num_hosts, args.queue_name, qsize))
    if qsize == 0:
        return
    if qsize < args.min_qsize:
        notify_recharge(args.email, qsize)
    if num_hosts < args.min_hosts or avg_load < args.min_load:
        notify(args.email, avg_load, num_hosts)


if __name__ == '__main__':
    main(parse_args())
