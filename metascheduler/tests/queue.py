#!/usr/bin/env python
import json
import requests


class QueueMS(object):
    URL = "http://test02cern.vs.os.yandex.net:5000/"

    def __init__(self, queue_name):
        self.queue_name = queue_name

        self.ADD_URL = self.URL + self.queue_name + "/add_job"
        self.GET_URL = self.URL + "get_jobs?job_type=" + self.queue_name
        self.LEN_URL = self.URL + self.queue_name + "/length"

    def qsize(self):
        r = requests.get(self.LEN_URL)
        return int(r.text)

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
        r = requests.post(self.ADD_URL, data=json.dumps(item))

    def get(self):
        r = requests.get(self.GET_URL)
        response = json.loads(r.text)
        item = response['jobs'][0]
        return item


def test_queue():
    q = QueueMS("test_queue")

    if not q.empty():
        for el in q:
            print el

    assert q.qsize() == 0

    q.put({"a": "b"})
    assert q.qsize() == 1

    item = q.get()
    assert item['a'] == 'b'

if __name__ == '__main__':
    test_queue()
