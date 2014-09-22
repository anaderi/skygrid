import json
import os
import random
import unittest
import uuid
from time import sleep

import requests
from testconfig import config
API_URL = config['api']['url']

from test_queue import TestWithQueue


class TestJobMS(TestWithQueue):
    def test_update_and_delete(self):
        TEST_DESCRIPTION ={"a": "b"}

        self.queue.put(TEST_DESCRIPTION)

        
        job = self.queue.get()
        self.assertEqual(job.description, TEST_DESCRIPTION)

        self.assertTrue(job.update_status('failed'))
        self.assertTrue(job.update_description({"b": "c"}))

        with self.assertRaises(ValueError):
            job.update_status('some bad status')

        self.assertTrue(job.delete())
