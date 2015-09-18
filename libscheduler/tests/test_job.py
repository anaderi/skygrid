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

DBG = {'some': 'debug info'}

class TestJobMS(TestWithQueue):
    def test_update_and_delete(self):
        TEST_OBJ = {"descriptor": {"a": "b"}}

        self.queue.put(TEST_OBJ)


        job = self.queue.get()
        self.assertEqual(job.descriptor, TEST_OBJ['descriptor'])

        self.assertTrue(job.update_status('failed'))
        self.assertTrue(job.update_output(['hello', 'world']))

        self.assertRaises(Exception, job.update_status, 'some bad')

        if config['api']['ms_debug'] == 'true':
            self.assertTrue(job.update_debug(DBG))
            self.assertEqual(job.get_debug(), DBG)

        self.assertTrue(job.delete())
