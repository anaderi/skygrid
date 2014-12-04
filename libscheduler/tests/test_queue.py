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
            {'descriptor': {"a": "b"}},
            {'descriptor': {"c": "d"}}
        ]

        for obj in TEST_OBJ:
            self.queue.put(obj)
            sleep(0.2)

        self.assertEqual(self.queue.qsize(), len(TEST_OBJ))
        q_size = len(TEST_OBJ)

        for obj in TEST_OBJ:
            job = self.queue.get()

            q_size -= 1
            self.assertEqual(self.queue.qsize(), q_size)

            self.assertEqual(job.descriptor, obj['descriptor'])
            self.assertTrue(job.delete())

    def test_multiplication(self):
        N_OBJ = 5
        TEST_OBJ ={
            'descriptor': {"a": "b"},
            'multiply': N_OBJ
        }
        job_ids = self.queue.put(TEST_OBJ)
        q_size = N_OBJ

        self.assertEqual(self.queue.qsize(), q_size)
        self.assertIsInstance(job_ids, list)

        for jid in job_ids:
            job = self.queue.get()

            q_size -= 1
            self.assertEqual(self.queue.qsize(), q_size)

            self.assertEqual(job.descriptor, TEST_OBJ['descriptor'])
            self.assertEqual(job.job_id, jid)
            self.assertTrue(job.delete())

