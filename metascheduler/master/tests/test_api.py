import json
import os
import random
import unittest
import uuid

from time import sleep

import requests
from testconfig import config

class BasicQueueTest(unittest.TestCase):
    def setUp(self):
        self.api_url = config['api']['url']
        self.queue_name = uuid.uuid4().hex

        self.all_queues_url = os.path.join(self.api_url, 'queues')
        self.all_jobs_url = os.path.join(self.api_url, 'jobs')
        self.queue_url = os.path.join(self.all_queues_url, self.queue_name)
        self.queue_info_url = os.path.join(self.queue_url, 'info')
        self.delete_queue() # ensure that queue would not exist

    def tearDown(self):
        self.delete_queue() # keep it clean

    def create_queue(self):
        create_payload = {
            'job_type': self.queue_name
        }
        r = requests.put(self.all_queues_url, data=json.dumps(create_payload))
        result_create = r.json()

        return result_create

    def delete_queue(self):
        return requests.delete(self.queue_url).json()


class QueueManagementTest(BasicQueueTest):
    def test_create_and_delete(self):
        result_create = self.create_queue()
        

        self.assertEqual(result_create['success'], True)
        self.assertEqual(result_create['queue']['name'], self.queue_name)
        self.assertEqual(result_create['queue']['use_timeout'], False)

        result_delete = self.delete_queue()
        self.assertEqual(result_delete['success'], True)

        r = requests.get(self.queue_info_url)
        result_get = r.json()

        self.assertEqual(result_get['success'], True)
        self.assertEqual(result_get['exists'], False)



    def test_delete_not_created(self):
        result_delete = self.delete_queue()
        self.assertEqual(result_delete['success'], False)


class QueueTest(BasicQueueTest):
    def setUp(self):
        super(QueueTest, self).setUp()

        self.create_queue()

    def test_add_element(self):
        TEST_OBJ = {"hello": "world"}
        
        r = requests.post(self.queue_url, data=json.dumps(TEST_OBJ))
        result_create = r.json()

        self.assertEqual(result_create['success'], True)
        self.assertEqual(result_create['job']['descriptor'], TEST_OBJ)
        self.assertEqual(result_create['job']['status'], "pending")

        r = requests.get(self.queue_url)
        result_get = r.json()


        self.assertEqual(result_get['success'], True)
        self.assertEqual(result_get['job']['descriptor'], TEST_OBJ)
        self.assertEqual(result_get['job']['status'], "pending")

    def test_sequence(self):
        TEST_OBJ =[
            {"a": "b"},
            {"c": "d"}
        ]
        IDS = []

        for obj in TEST_OBJ:
            r = requests.post(self.queue_url, data=json.dumps(obj))
            result_create = r.json()
            job = result_create['job']
            IDS.append(job['job_id'])

            self.assertEqual(result_create['success'], True)
            self.assertEqual(job['descriptor'], obj)
            self.assertEqual(job['status'], "pending")
            sleep(0.5) # To prevent equal times inside MS database

        get_created_jobs_url = os.path.join(self.all_jobs_url, ','.join(IDS))
        r = requests.get(get_created_jobs_url)
        result = r.json()

        self.assertTrue(result['success'])


        for obj in TEST_OBJ:
            r = requests.get(self.queue_url)
            result_get = r.json()

            self.assertEqual(result_get['success'], True)
            self.assertEqual(result_get['job']['descriptor'], obj)


class NoQueueTest(BasicQueueTest):
    def test_add_no_queue(self):
        TEST_OBJ = {"hello": "world"}
            
        r = requests.post(self.queue_url, data=json.dumps(TEST_OBJ))
        result_create = r.json()

        self.assertFalse(result_create['success'])




if __name__ == '__main__':
    unittest.main()