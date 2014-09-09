#!/usr/bin/env python

import sys
from util import filter_older_than


def parse_args():
    if len(sys.argv) < 2:
        print "USAGE: %s MAX_SECONDS" % sys.argv[0]
        sys.exit(1)
    max_seconds = int(sys.argv[1])
    return max_seconds


def main(max_seconds):
    filter_older_than(sys.stdin, sys.stdout, max_seconds)

if __name__ == '__main__':
    main(parse_args())
