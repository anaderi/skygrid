#!/usr/bin/env python
import os
import json
import unittest
from time import sleep

import requests

from .job import JobMS
        

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
        r = requests.post(self.queue_url, data=json.dumps(item))

    def get(self):
        response = requests.get(self.queue_url).json()
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
        r = requests.put(self.queue_management_url, data=json.dumps(create_payload))
        result = r.json()

        return result['success']

    def _delete_queue(self):
        return requests.delete(self.queue_url).json()['success']

    def _exists(self):
        info = self._get_info()
        return info['exists']
