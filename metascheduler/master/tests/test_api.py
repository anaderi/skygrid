import json
import os
import random
import unittest
import uuid

from time import sleep

import requests
from testconfig import config



class BasicMetaschedulerTest(unittest.TestCase):
    def setUp(self):
        self.api_url = config['api']['url']
        self.json_headers =  {'content-type': 'application/json'}


class StatusTest(BasicMetaschedulerTest):
    def setUp(self):
        super(StatusTest, self).setUp()
        self.status_url = os.path.join(config['api']['url'], 'status')

    def test_alive(self):
        r = requests.get(self.status_url).json()
        self.assertTrue(r['alive'])


class BasicQueueTest(BasicMetaschedulerTest):
    def setUp(self):
        super(BasicQueueTest, self).setUp()
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
        TEST_OBJ = {"descriptor": {"hello": "world"}}
        r = requests.post(
            self.queue_url,
            data=json.dumps(TEST_OBJ),
            headers=self.json_headers
        )
        result_create = r.json()

        self.assertEqual(result_create['success'], True)
        self.assertEqual(result_create['job']['descriptor'], TEST_OBJ['descriptor'])
        self.assertEqual(result_create['job']['status'], "pending")

        r = requests.get(self.queue_url)
        result_get = r.json()

        self.assertEqual(result_get['success'], True)
        self.assertEqual(result_get['job']['descriptor'], TEST_OBJ['descriptor'])
        self.assertEqual(result_get['job']['status'], "pulled")

    def test_add_element_with_callback(self):
        TEST_OBJ = {
            "descriptor": {"hello": "world"},
            "callback": "http://callback.site.com"
        }
        r = requests.post(
            self.queue_url,
            data=json.dumps(TEST_OBJ),
            headers=self.json_headers
        )
        result_create = r.json()

        self.assertEqual(result_create['success'], True)
        self.assertEqual(result_create['job']['descriptor'], TEST_OBJ['descriptor'])
        self.assertEqual(result_create['job']['status'], "pending")

        r = requests.get(self.queue_url)
        result_get = r.json()

        self.assertEqual(result_get['success'], True)
        self.assertEqual(result_get['job']['descriptor'], TEST_OBJ['descriptor'])
        self.assertEqual(result_get['job']['status'], "pulled")

    def test_sequence(self):
        TEST_OBJS =[
            {"descriptor": {"a": "b"}},
            {"descriptor": {"c": "d"}}
        ]
        IDS = []

        for obj in TEST_OBJS:
            r = requests.post(
                self.queue_url,
                data=json.dumps(obj),
                headers=self.json_headers
            )
            result_create = r.json()

            job = result_create['job']
            IDS.append(job['job_id'])

            self.assertEqual(result_create['success'], True)
            self.assertEqual(job['descriptor'], obj['descriptor'])
            self.assertEqual(job['status'], "pending")
            sleep(0.2) # To prevent equal times inside MS database

        get_created_jobs_url = os.path.join(self.all_jobs_url, ','.join(IDS))
        r = requests.get(get_created_jobs_url)
        result = r.json()

        self.assertTrue(result['success'])


        for obj in TEST_OBJS:
            r = requests.get(self.queue_url)
            result_get = r.json()

            self.assertEqual(result_get['success'], True)
            self.assertEqual(result_get['job']['descriptor'], obj['descriptor'])

    def test_add_replicated(self):
        N_OBJ = 5
        TEST_OBJ = {
            "descriptor": {"hello": "world"},
            "multiply": N_OBJ
        }

        r = requests.post(
            self.queue_url,
            data=json.dumps(TEST_OBJ),
            headers=self.json_headers
        )
        result_create = r.json()

        self.assertEqual(result_create['success'], True)
        self.assertEqual(len(result_create['job_ids']), N_OBJ)

        IDS = set(result_create['job_ids'])

        for _ in xrange(N_OBJ):
            r = requests.get(self.queue_url)
            result_get = r.json()

            self.assertEqual(result_get['success'], True)
            self.assertEqual(result_get['job']['descriptor'], TEST_OBJ['descriptor'])
            self.assertTrue(result_get['job']['job_id'] in IDS)

            IDS.remove(result_get['job']['job_id'])

        self.assertEqual(IDS, set([]))

    def test_job_with_input(self):
        TEST_OBJ = {
            "descriptor": {"hello": "world"},
            "input": ['root://blah/blah/blah/test.file', 'moosefs://1/2/3/file.txt']
        }

        r = requests.post(
            self.queue_url,
            data=json.dumps(TEST_OBJ),
            headers=self.json_headers
        )
        result_create = r.json()

        self.assertEqual(result_create['success'], True)
        self.assertEqual(result_create['job']['descriptor'], TEST_OBJ['descriptor'])
        self.assertEqual(result_create['job']['status'], "pending")
        self.assertEqual(result_create['job']['input'], TEST_OBJ['input'])


        r = requests.get(self.queue_url)
        result_get = r.json()

        self.assertEqual(result_get['success'], True)
        self.assertEqual(result_get['job']['descriptor'], TEST_OBJ['descriptor'])
        self.assertEqual(result_get['job']['status'], "pulled")
        self.assertEqual(result_create['job']['input'], TEST_OBJ['input'])


class NoQueueTest(BasicQueueTest):
    def test_add_no_queue(self):
        TEST_OBJ = {"hello": "world"}
        r = requests.post(self.queue_url, data=json.dumps(TEST_OBJ))
        result_create = r.json()

        self.assertFalse(result_create['success'])




if __name__ == '__main__':
    unittest.main()