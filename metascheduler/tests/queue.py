#!/usr/bin/env python
import json
import requests


class QueueMS(object):
    URL_PATTERN = "http://test02cern.vs.os.yandex.net:5000/queues/{}"

    def __init__(self, queue_name):
        self.QUEUE_URL = self.URL_PATTERN.format(queue_name)

        
        self.LEN_URL = self.QUEUE_URL + "/length"

    def qsize(self):
        info = requests.get(self.LEN_URL).json()
        return info['length']

    def empty(self):
        return self.qsize() == 0

    def __iter__(self):
        return self

    def next(self):
        if self.empty():
            raise StopIteration
        return self.get()

    def extend(self, iterable):
        for i in iterable:
            self.put(i)

    def put(self, item):
        r = requests.post(self.QUEUE_URL, data=json.dumps(item))

    def get(self):
        response = requests.get(self.QUEUE_URL).json()
        jobs = response['jobs']
        if len(jobs) > 0:
            return response['jobs'][0]
        else:
            return None



def test_queue():
    q = QueueMS("test_queue")

    print "Extract everything from queue..."

    if not q.empty():
        for el in q:
            print "Was on queue:", el

    assert q.qsize() == 0
    print "Queue is empty"

    TEST_OBJ = {"a": "b"}
    print "Putting {} to queue.".format(TEST_OBJ)
    
    q.put(TEST_OBJ)
    assert q.qsize() == 1
    print "Object is in queue."

    item = q.get()
    assert item == TEST_OBJ
    print "Got same object form queue. Everything is OK."

if __name__ == '__main__':
    test_queue()
