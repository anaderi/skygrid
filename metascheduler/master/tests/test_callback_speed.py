#!/usr/bin/env python

# measure time of this script to combplete


import timeit

from libscheduler import Metascheduler

ms = Metascheduler("http://localhost:5000/")
queue = ms.queue("dummy_cb_queue")

for x in xrange(10):
    j = queue.put({"descriptor": {"blah": 123}, "callback": "http://127.0.0.1:8877/"})
    jj = queue.get()
    print j, jj
    jj.update_status("running")
    jj.update_status("completed")



