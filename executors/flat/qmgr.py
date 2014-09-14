#!/usr/bin/env python

import os
import json
import glob
import argparse
import logging
import cPickle
import shutil
import multiprocessing
from util import QueueDir
from copy import copy

logger = logging.getLogger()
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.INFO)

CMD_MV = "mv"
CMD_CP = "cp"
CMD_FILL = "fill"
CMD_FIX_SPLIT = "fix_split"
CMD_FIX_INTERRUPT = "fix_int"
CMD_UNLOCK = "unlock"
CMD_CHECK_DUPES = "check_dupes"
CMD_RESET_FAIL = "reset_fail"
CMD_MISSING_IDS = "missing"
CMD_MISSING2FAIL = "missing2fail"
CMD_CREATE_SCRATCH = "create"
POOL_SIZE=20
JD_PER_DIR = 1000
EV_PER_JD = 5000


def parse_args():
    p = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter, epilog="""
Supported commands:
    mv QUEUE_FROM QUEUE_TO
    cp QUEUE_FROM QUEUE_TO
    fix_split QUEUE
    fix_int QUEUE.FAIL
    check_dupes QUEUE
    reset_fail QUEUE.fail
    missing
    missing2fail [-m missing.txt]
    create [-t TEMPLATE]

Example:
    qmgr.py mv mc01.fail mc01
        """)
    p.add_argument("--count", "-c", help="count items", type=int, default=None)
    p.add_argument("--start", help="start id", type=int, default=1010)
    p.add_argument("--stop", help="stop id", type=int, default=20010)
    p.add_argument("--template", "-t", help="template jd file", default=None)
    p.add_argument("--missing", "-m", help="missing ids file", default=None)
    p.add_argument("--verbose", "-v", action='store_true', default=False)
    p.add_argument("--remove", "-r", action='store_true', default=False)
    p.add_argument("cmd", help="command")
    p.add_argument("arg1", help="ARG1", nargs='?')
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


def _lock_ids(lockfile):
    jds = {}
    if os.path.exists(lockfile):
        with open(lockfile, "r") as fh:
            jds = cPickle.load(fh)
    return jds


def unlock(name):
    lockfile = "%s.locker" % name
    assert os.path.exists(name) and os.path.isdir(name)
    jds = _lock_ids(lockfile)
    assert len(jds) > 0
    queue_orig = QueueDir(name)
    queue_succ = QueueDir(name + ".success")
    for job_id, jd in jds.iteritems():
        if _has_output(name, jd):
            queue_succ.put(jd)
            logger.info("%d -> success" % job_id)
        else:
            queue_orig.put(jd)
            logger.info("%d -> orig" % job_id)
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
    queue_fail = QueueDir(name)
    queue_success = QueueDir(name.replace('fail', 'success'))
    restore_count = 0
    queue_fail_size = queue_fail.qsize()
    fail_files = queue_fail.list_files()

    success_cache = {}
    for i in range(queue_success.qsize()):
        jd = queue_success.peek(i)
        key = jd['job_id']
        jd_rec = {'jd': jd, 'id': i}
        success_cache[key] = jd_rec

    for i in range(queue_fail.qsize() - 1, -1, -1):
        jd = queue_fail.peek(i)
        if _has_output(name, jd):
            if jd['job_id'] in success_cache:
                print "WARN: already in success (%s)" % fail_files[i]
                continue
            print "seemsOK: %d" % jd['job_id']
            restore_count += 1
            queue_fail.remove(i)
            jd['ex_status'] = jd['status']
            jd['status'] = 'SUCCESS'
            queue_success.put(jd)
    print "restored %d JDs of %d" % (restore_count, queue_fail_size)


def check_dupes(name, do_remove=False):
    assert os.path.exists(name) and os.path.isdir(name)
    queue = QueueDir(name)
    queue_files = queue.list_files()
    jds = {}
    for i in range(queue.qsize()):
        jd = queue.peek(i)
        key = jd['job_id']
        jd_rec = {'file': queue_files[i], 'jd': jd, 'id': i}
        if key in (jds):
            jds[key].append(jd_rec)
        else:
            jds[key] = [jd_rec]
    for key, dupes in jds.iteritems():
        if len(dupes) > 1:
            print "Dupes: %s" % dupes
            if do_remove:
                for jd_rec in dupes[0:-1]:
                    print "remove: %s" % jd_rec['file']
                    os.remove(jd_rec['file'])  # hack


def reset_fail(name):
    assert os.path.exists(name) and os.path.isdir(name)
    name = name.rstrip('/')
    assert name.endswith('.fail')
    origname = name.replace('.fail', '')
    groupname = os.path.basename(origname)

    qfail = QueueDir(name)
    qorig = QueueDir(origname)
    for jd in qfail:
        outdir = 'output-%s/%d' % (groupname, jd['job_id'])
        if os.path.exists(outdir):
            shutil.rmtree(outdir)
        qorig.put(jd)


def _queue_ids(name):
    assert os.path.exists(name) and os.path.isdir(name)
    queue = QueueDir(name)
    ids = []
    for i in range(queue.qsize()):
        jd = queue.peek(i)
        job_id = jd['job_id']
        ids.append(job_id)
    return ids


def _group_job_ids(name):
    ids = _queue_ids(name)
    ids.extend(_queue_ids("%s.success" % name))
    ids.extend(_queue_ids("%s.fail" % name))
    ids.extend(_lock_ids("%s.locker" % name).keys())
    return ids


def print_missing(start_id, stop_id):
    pool = multiprocessing.Pool(POOL_SIZE)
    group_names = ["mc%02d" % i for i in range(1,21)]
    print group_names
    ids_list = pool.map(_group_job_ids, group_names)
    ids_full = {}
    for ids in ids_list:
        for id in ids:
            if id in ids_full:
                print "WARN: %d already in ids collection"
            ids_full[id] = 1
    for i in range(start_id, stop_id):
        if i not in ids_full:
            print i


def create_from_scratch(template):
    assert os.path.exists(template)
    with open(template) as fh:
        t = json.load(fh)
    t['args']['--num-events'] = EV_PER_JD

    for host_id in range(1, 21):
        dir = "mc{i:02d}".format(i=host_id)
        if os.path.exists(dir):
            shutil.rmtree(dir)
        os.makedirs(dir)
        for c in range(0, JD_PER_DIR):
            jd = copy(t)
            jd["job_id"] = 10 + host_id * JD_PER_DIR + c
            with open("%s/%d_job.json" % (dir, c), "w") as fh:
                json.dump(jd, fh, sort_keys=True, indent=2)


def missing2fail(template, missing):
    assert os.path.exists(missing)
    assert os.path.exists(template)
    ids = []
    with open(missing) as fh:
        ids = map(int, fh.readlines())
    with open(template) as fh:
        t = json.load(fh)
    t['args']['--num-events'] = EV_PER_JD
    restored_count = 0
    for host_id in range(1, 21):
        dir_fail = "mc{i:02d}.fail".format(i=host_id)
        if not os.path.exists(dir_fail):
            os.makedirs(dir_fail)
        for c in [id for id in ids if id >= 10 + host_id * JD_PER_DIR and id < 10 + (host_id + 1) * JD_PER_DIR]:
            jd = copy(t)
            jd["job_id"] = c
            print "%d -> %s" % (c, dir_fail)
            restored_count += 1
            # with open("%s/%d_job.json" % (dir_fail, c), "w") as fh:
            #     json.dump(jd, fh, sort_keys=True, indent=2)
    print "Restored %d jds out of %d" % (restored_count, len(ids))


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
    elif args.cmd == CMD_FIX_INTERRUPT:
        fix_interrupts(args.arg1)
    elif args.cmd == CMD_CHECK_DUPES:
        check_dupes(args.arg1, args.remove)
    elif args.cmd == CMD_RESET_FAIL:
        reset_fail(args.arg1)
    elif args.cmd == CMD_MISSING_IDS:
        print_missing(args.start, args.stop)
    elif args.cmd == CMD_CREATE_SCRATCH:
        create_from_scratch(args.template)
    elif args.cmd == CMD_MISSING2FAIL:
        missing2fail(args.template, args.missing)
    else:
        print "Unknown CMD: %s" % args.cmd


if __name__ == '__main__':
    main(parse_args())
