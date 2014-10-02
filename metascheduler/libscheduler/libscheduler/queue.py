#!/usr/bin/env python
import os
import json
import unittest
from time import sleep

from .job import JobMS
from .common import *
        

class QueueMS(object):
    def __init__(self, queue_name, autocreate=True, api_url="http://localhost:5000/"):
        self.queue_name = queue_name
        self.api_url = api_url

        self.queue_management_url = self.queue_url = os.path.join(api_url, 'queues')
        self.queue_url = os.path.join(
            api_url,
            'queues',
            self.queue_name
        )
        
        self.INFO_URL = os.path.join(self.queue_url, "info")

        if autocreate and not self._exists():
            self._create_queue()


    def _get_info(self):
        return ms_get(self.INFO_URL)

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
        return ms_post(self.queue_url, data=json.dumps(item))

    def get(self):
        response = ms_get(self.queue_url)
        jobs = response['jobs']

        if len(jobs) == 1:
            job = jobs[0]
            job['api_url'] = self.api_url

            return JobMS(**jobs[0])
        else:
            return None

    def _create_queue(self):
        create_payload = {
            'job_type': self.queue_name
        }
        ms_put(self.queue_management_url, data=json.dumps(create_payload))

        return True

    def _delete_queue(self):
        return ms_delete(self.queue_url)

    def _exists(self):
        info = self._get_info()
        return info['exists']
