import json
import os
import random
import unittest
import uuid

from time import sleep

import requests
from testconfig import config
from queue import QueueMS

class TestQueueMS(unittest.TestCase):
    def setUp(self):
        from testconfig import config
        self.queue_name = uuid.uuid4().hex
        self.queue = QueueMS(self.queue_name, config['api']['url'])

        if not self.queue.empty():
            for el in q:
                print "Was on queue:", el

    def tearDown(self):
        self.queue._delete_queue()

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
            item = self.queue.get()

            self.assertEqual(item['description'], obj)
            