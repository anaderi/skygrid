#!/usr/bin/env python

import os
import argparse
import logging
from util import QueueDir

logger = logging.getLogger()
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.INFO)

NAME = 'name'
SUCC = 'success'
FAIL = 'fail'
WORK = 'work'
ORIG = 'orig'
FAILRATE = 'f-rate'
SUCCRATE = 'succrate'
TOTAL = 'total'

queue_exts = {
    ORIG: '',
    SUCC: '.success',
    FAIL: '.fail',
    WORK: '.work'
}


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--ids", "-i", help="hosts ids for stat")
    p.add_argument("--queues", "-q", help="list of queues to compute stats for")
    p.add_argument("--basedir", "-b", help="basedir", default=".")
    p.add_argument("--verbose", "-v", action='store_true', default=False)
    args = p.parse_args()
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    assert not ((args.ids is not None) and (args.queues is not None)) , "shouldn't specify both"
    return args


def stat_host(basedir, name):
    stat = {}
    total_count = 0
    for key, suff in queue_exts.iteritems():
        queue_dir = "%s/%s%s" % (basedir, name, suff)
        if os.path.exists(queue_dir):
            q = QueueDir(queue_dir)
            stat[key] = q.qsize()
            total_count += stat[key]
        else:
            stat[key] = 0

    stat[TOTAL] = total_count
    if total_count > 0:
        stat[FAILRATE] = 100. * stat[FAIL] / stat[TOTAL]
        stat[SUCCRATE] = 100. * stat[SUCC] / stat[TOTAL]
    else:
        stat[FAILRATE] = None
        stat[SUCCRATE] = None
    stat['name'] = name
    return stat


def print_stat(group_stat):
    keys = [NAME, SUCC, FAIL, ORIG, TOTAL, FAILRATE, SUCCRATE]
    header = "\t".join(keys)
    print header
    for stat in group_stat:
        row = "\t".join([str(stat[k]) for k in keys])
        print row


def main(args):
    groups = map(lambda i: "mc%02d" % i, range(20))
    if args.ids:
        groups = map(lambda i: "mc%02d" % int(i), args.ids.split(','))
    if args.queues:
        groups = args.queues.split(",")

    group_stat = [stat_host(args.basedir, group) for group in groups]
    print_stat(group_stat)


if __name__ == '__main__':
    main(parse_args())
