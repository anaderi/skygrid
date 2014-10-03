import json
import os
import random
import unittest
import uuid
from time import sleep

import requests

from testconfig import config
from libscheduler import Metascheduler


class TestWithQueue(unittest.TestCase):
    def setUp(self):
        self.queue_name = uuid.uuid4().hex

        self.ms = Metascheduler(config['api']['url'])
        self.queue = self.ms.queue(self.queue_name)

        if not self.queue.empty():
            for el in q:
                print "Was on queue:", el

    def tearDown(self):
        self.queue._delete_queue()


class TestQueueMS(TestWithQueue):
    def test_sequence(self):
        TEST_OBJ =[
            {"a": "b"},
            {"c": "d"}
        ]

        for obj in TEST_OBJ:
            self.queue.put(obj)
            sleep(0.5)

        assert self.queue.qsize() == len(TEST_OBJ)

        for obj in TEST_OBJ:
            job = self.queue.get()

            self.assertEqual(job.descriptor, obj)
            self.assertTrue(job.delete())
