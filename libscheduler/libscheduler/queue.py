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


    def _construct_job(self, server_response):
        job_dict = server_response.get('job')

        if job_dict:
            job_dict['api_url'] = self.api_url
            job_dict.pop('callback', None)

            return JobMS(**job_dict)

    def put(self, item):
        response = ms_post(
            self.queue_url,
            data=json.dumps(item),
            headers=JSON_HEADERS
        )

        multipiler = item.get('multiply')
        if multipiler:
            if multipiler == 1:
                return [response['job']['job_id']]
            else:
                return response['job_ids']
        else:
            return self._construct_job(response)

    def get(self, **parameters):
        response = ms_get(self.queue_url, params=parameters)

        return self._construct_job(response)



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
