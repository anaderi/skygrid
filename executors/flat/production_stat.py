#!/usr/bin/env python

import os
import argparse
import logging
import cPickle
from util import QueueDir
import ordereddict


logger = logging.getLogger()
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.INFO)

NAME = 'name'
SUCC = 'success'
FAIL = 'fail'
WORK = 'work'
ORIG = 'orig'
MISSING = 'miss'
FAILRATE = 'fail-rate'
SUCCRATE = 'success-rate'
TOTAL = 'total'

queue_exts = {
    ORIG: '',
    SUCC: '.success',
    FAIL: '.fail',
    # WORK: '.work'
}

# Add the functions descriptions.
def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--ids", "-i", help="hosts ids for stat")
    p.add_argument("--queues", "-q", help="list of queues to compute stats for")
    p.add_argument("--basedir", "-b", help="basedir", default=".")
    p.add_argument("--sortby", "-s", help="sort table by (field name)")
    p.add_argument("--verbose", "-v", action='store_true', default=False)
    p.add_argument("--desc", "-d", action='store_true', default=False)
    p.add_argument("--exptotal", "-e", type=int, help="expected jds per group")
    args = p.parse_args()
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    assert not ((args.ids is not None) and (args.queues is not None)) , "shouldn't specify both"
    return args


def stat_host(basedir, name, exptotal=None):
    stat = {WORK: 0}
    total_count = 0
    for key, suff in queue_exts.iteritems():
        queue_dir = "%s/%s%s" % (basedir, name, suff)
        if os.path.exists(queue_dir):
            q = QueueDir(queue_dir)
            stat[key] = q.qsize()
            total_count += stat[key]
        else:
            stat[key] = 0
    if os.path.exists("%s/%s.locker" % (basedir, name)):
        with open("%s/%s.locker" % (basedir, name)) as fh:
            queue_work = cPickle.load(fh)
            stat[WORK] = len(queue_work)
            total_count += len(queue_work)

    stat[TOTAL] = total_count
    update_calc_stat(stat, exptotal)
    stat['name'] = name
    return stat


def update_calc_stat(stat, expected=None):
    if stat[TOTAL] > 0:
        stat[FAILRATE] = 100. * stat[FAIL] / stat[TOTAL]
        stat[SUCCRATE] = 100. * stat[SUCC] / stat[TOTAL]
    else:
        stat[FAILRATE] = -1.
        stat[SUCCRATE] = -1.
    if expected is not None:
        stat[MISSING] = expected - stat[TOTAL]


def print_stat(group_stat, sortby=None, sort_desc=False, expected_per_group=None):
    report = ordereddict.OrderedDict([
        (NAME, "%s"), 
        (SUCC, "%d"), 
        (FAIL, "%d"),
        (WORK, "%d"),
        (ORIG, "%d"),
        (TOTAL, "%d"),
        (FAILRATE, "%.1f\t"),
        (SUCCRATE, "%.1f\t")
    ])
    totals = {NAME: 'TOTAL'}
    if expected_per_group is not None:
        report[MISSING] = "%d"
    header = "\t".join(report.keys())
    print header
    if sortby is not None:
        group_stat = sorted(group_stat, key=lambda stat: stat[sortby], reverse=sort_desc)
    for stat in group_stat:
        row = "\t".join([format % stat[key] for key, format in report.iteritems()])
        print row
        for k in [SUCC, FAIL, WORK, ORIG, TOTAL]:
            if k in totals:
                totals[k] += stat[k]
            else:
                totals[k] = stat[k]
    if expected_per_group is None:
        update_calc_stat(totals, None)
    else:
        update_calc_stat(totals, len(group_stat) * expected_per_group)
    totals_row = "\t".join([format % totals[key] for key, format in report.iteritems()])
    print totals_row


def predict_expected_per_group(groups_stats):
    pass  # TODO


def main(args):
    groups = map(lambda i: "mc%02d" % i, range(1, 21))
    if args.ids:
        groups = map(lambda i: "mc%02d" % int(i), args.ids.split(','))
    if args.queues:
        groups = args.queues.split(",")

    group_stat = [stat_host(args.basedir, group, exptotal=args.exptotal) for group in groups]
    print_stat(group_stat, sortby=args.sortby, sort_desc=args.desc, expected_per_group=args.exptotal)


if __name__ == '__main__':
    main(parse_args())
