#!/usr/bin/env python

import os
import argparse
import logging
from util import QueueDir

logger = logging.getLogger()
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.INFO)

queue_exts = {
    'orig': '',
    'success': '.success',
    'fail': '.fail',
    'work': '.work'
}


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--ids", "-i", help="hosts ids for stat")
    p.add_argument("--basedir", "-b", help="basedir", default=".")
    p.add_argument("--verbose", "-v", action='store_true', default=False)
    args = p.parse_args()
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    return args


def stat_host(basedir, name):
    stat = {}
    for key, suff in queue_exts.iteritems():
        queue_dir = "%s/%s%s" % (basedir, name, suff)
        if os.path.exists(queue_dir):
            q = QueueDir(queue_dir)
            stat[key] = q.qsize()
        else:
            stat[key] = 0
    return stat


def main(args):
    ids = range(20)
    if args.ids:
        ids = map(int, args.ids.split(','))
    for i in ids:
        host = "mc%02d" % i
        print host, stat_host(args.basedir, host)


if __name__ == '__main__':
    main(parse_args())
