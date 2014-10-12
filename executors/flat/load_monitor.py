#!/usr/bin/env python
import re
import glob
import util
import shutil
import datetime
import argparse


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--hosts", default=None, required=True)
    parser.add_argument("--min_load", type=float, default=20.0)
    parser.add_argument("--min_hosts", type=int, default=15)
    parser.add_argument("--email", default="anaderi@yandex-team.ru")
    parser.add_argument("--log", default=None)
    args = parser.parse_args()
    return args


def notify(email, avg_load, num_hosts):
    util.sh("/root/bin/notify.sh 'MC load average' load_avg: %f, hosts: %d" % (avg_load, num_hosts), verbose=True)


def log(log, avg_load, num_hosts):
    if log is not None:
        with open(log, "a") as fh:
            fh.write("%s\t%f\t%d\n" % (datetime.datetime.now(), avg_load, num_hosts))


def main(args):
    dir = "temp_uptime"
    util.sh("pssh -h %s -o %s uptime" % (args.hosts, dir))
    f = glob.glob("%s/*" % dir)
    r = util.sh("cat " + " ".join(f))
    ll = r['out'].strip().split('\n')
    avgs = map(lambda l: float(re.search("average: ([\d.]*)", l).groups()[0]), ll)
    shutil.rmtree(dir)
    num_hosts = len(avgs)
    avg_load = sum(avgs)/num_hosts

    log(args.log, avg_load, num_hosts)
    if num_hosts < args.min_hosts or avg_load < args.min_load:
        notify(args.email, avg_load, num_hosts)


if __name__ == '__main__':
    main(parse_args())
