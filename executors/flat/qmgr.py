#!/usr/bin/env python

import os
import json
import glob
import argparse
import logging
import cPickle
from util import QueueDir
from copy import copy

logger = logging.getLogger()
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.INFO)

CMD_MV = "mv"
CMD_CP = "cp"
CMD_FILL = "fill"
CMD_FIX_SPLIT = "fix_split"
CMD_UNLOCK = "unlock"


def parse_args():
    p = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter, epilog="""
Supported commands:
    mv QUEUE_FROM QUEUE_TO
    cp QUEUE_FROM QUEUE_TO
    fix_split QUEUE

Example:
    qmgr.py mv mc01.fail mc01
        """)
    p.add_argument("--count", "-c", help="count items", type=int, default=None)
    p.add_argument("--template", help="template jd file", default=None)
    p.add_argument("--verbose", "-v", action='store_true', default=False)
    p.add_argument("cmd", help="command")
    p.add_argument("arg1", help="ARG1")
    p.add_argument("arg2", help="ARG2", nargs='?')
    args = p.parse_args()
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    return args


def mv(src, dst, count=None, put_back=False):
    assert src is not None and dst is not None
    assert os.path.exists(src) and os.path.isdir(src)
    q_src = QueueDir(src)
    q_dst = QueueDir(dst, default_mask=q_src.mask)
    if count is None:
        count = q_src.qsize()
    if count > 0:
        jds = q_src.get_n(count)
        q_dst.extend(jds)
        if put_back:
            q_src.extend(jds)
    else:
        logger.warn("WARN: empty source queue")
    logger.info("SRC: %s" %  q_src)
    logger.info("DST: %s" %  q_dst)


def fill(dst, template, count):
    queue = QueueDir(dst)
    with open(template) as fh:
        jd_template = json.load(fh)
    jd_min = None
    if 'job_id' in jd_template:
        jd_min = jd_template['job_id']
    assert count > 0
    for i in range(count):
        jd = copy(jd_template)
        if jd_min is not None:
            jd['job_id'] = jd_min + i
        queue.put(jd)


def fix_split(name):
    assert os.path.exists(name) and os.path.isdir(name)
    queue = QueueDir(name)
    assert queue.qsize() == 1
    item_list = queue.get()
    queue.extend(item_list)
    logger.info(queue)


def unlock(name):
    lockfile = "%s.locker" % name
    assert os.path.exists(name) and os.path.isdir(name)
    assert os.path.exists(lockfile)
    jds = {}
    with open(lockfile, "r") as fh:
        jds = cPickle.load(fh)
    assert len(jds) > 0
    queue = QueueDir(name)
    queue.extend(jds)
    logger.info(queue)
    os.remove(lockfile)


def _has_output(name, jd):
    output_dir = "output-" + name.replace(".fail", '')
    root_out_dir = "%s/%d/root" % (output_dir, jd['job_id'])
    if not os.path.exists(root_out_dir):
        return False
    filelist = glob.glob("%s/pythia*.root" % root_out_dir)
    if len(filelist) != 1:
        return False
    size = os.stat(filelist[0]).st_size
    if size < 5000:
        return False
    return True


def fix_interrupts(name):
    assert os.path.exists(name) and os.path.isdir(name)
    assert name.endswith('fail')
    queue = QueueDir(name)
    queue_success = QueueDir(name.replace('fail', 'success'))
    restore_count = 0
    for i in range(queue.qsize(), 0, -1):
        jd = queue.peek(i)
        if _has_output(name, jd):
            print "seemsOK: %d" % jd['job_id']
            restore_count += 1
            continue
            # queue.remove(i)
            # jd['ex_status'] = jd['status']
            # jd['status'] = 'SUCCESS'
            # queue_success.put(jd)
    print "restored %d JDs" % restore_count


def main(args):
    if args.cmd == CMD_MV:
        mv(args.arg1, args.arg2, args.count)
    elif args.cmd == CMD_CP:
        mv(args.arg1, args.arg2, args.count, put_back=True)
    elif args.cmd == CMD_FILL:
        fill(args.arg1, args.arg2, args.count)
    elif args.cmd == CMD_FIX_SPLIT:
        fix_split(args.arg1)
    elif args.cmd == CMD_UNLOCK:
        unlock(args.arg1)


if __name__ == '__main__':
    main(parse_args())
