#!/usr/bin/env python

import os
import json
import argparse
import logging
from util import QueueDir
from copy import copy

logger = logging.getLogger()
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.INFO)

CMD_MV = "mv"
CMD_CP = "cp"
CMD_FILL = "fill"


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--from", "-f", dest='src', help="job descriptor input")
    p.add_argument("--to", "-t", help="output folder")
    p.add_argument("--count", "-c", help="count items", type=int, default=None)
    p.add_argument("--template", help="template jd file", default=None)
    p.add_argument("--verbose", "-v", action='store_true', default=False)
    p.add_argument("cmd", help="command")
    args = p.parse_args()
    print args
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    return args


def mv(src, dst, count=None, put_back=False):
    assert src is not None and dst is not None
    assert os.path.exists(src)
    q_src = QueueDir(src)
    q_dst = QueueDir(dst, default_mask=q_src.mask)
    if count is None:
        count = q_src.qsize()
    jds = q_src.get_n(count)
    q_dst.extend(jds)
    if put_back:
        q_src.extend(jds)


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


def main(args):
    if args.cmd == CMD_MV:
        mv(args.src, args.to, args.count)
    elif args.cmd == CMD_CP:
        mv(args.src, args.to, args.count, put_back=True)
    elif args.cmd == CMD_FILL:
        fill(args.to, args.template, args.count)


if __name__ == '__main__':
    main(parse_args())
