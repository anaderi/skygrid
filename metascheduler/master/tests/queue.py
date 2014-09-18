#!/usr/bin/env python
import os
import json
import unittest
from time import sleep

import requests

class QueueMS(object):
    def __init__(self, queue_name, api_url="http://localhost:5000/", autocreate=True):
        self.queue_name = queue_name

        self.QUEUE_MANAGEMENT_URL = self.QUEUE_URL = os.path.join(api_url, 'queues')
        self.QUEUE_URL = os.path.join(
            api_url,
            'queues',
            self.queue_name
        )
        
        self.INFO_URL = os.path.join(self.QUEUE_URL, "info")

        if autocreate and not self._exists():
            self._create_queue()


    def _get_info(self):
        return requests.get(self.INFO_URL).json()

    def qsize(self):
        info = self._get_info()
        assert info['success']
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

    def _create_queue(self):
        create_payload = {
            'job_type': self.queue_name
        }
        r = requests.put(self.QUEUE_MANAGEMENT_URL, data=json.dumps(create_payload))
        result = r.json()

        return result['success']

    def _delete_queue(self):
        return requests.delete(self.QUEUE_URL).json()['success']

    def _exists(self):
        info = self._get_info()
        return info['exists']


def test_queue():
    q = QueueMS("test_queue")

    print "Extract everything from queue..."

    if not q.empty():
        for el in q:
            print "Was on queue:", el

    assert q.qsize() == 0
    print "Queue is empty"

    TEST_OBJ =[
        {"a": "b"},
        {"c": "d"}
    ]

    for obj in TEST_OBJ:
        print "Putting {} to queue.".format(obj)
        q.put(obj)
        print "Sleep..."
        sleep(0.5)

    assert q.qsize() == len(TEST_OBJ)
    print "Objects is in queue."

    for obj in TEST_OBJ:
        item = q.get()
        print "Pulled object is: ", item

        try:
            assert item['description'] == obj
        except Exception, e:
            print "Something went wrong: ", e
        else:
            print "Object is fine."

    print "Got same objects form queue.\nEverything is OK."

if __name__ == '__main__':
    test_queue()
