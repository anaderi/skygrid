import json
import os
import random
import unittest
import uuid
import hashlib

from time import sleep

import requests
from testconfig import config

class BasicSkygridTest(unittest.TestCase):
    def setUp(self):
        self.api_url = config['api']['url']
        self.datasets_url = os.path.join(config['api']['url'], 'datasets')
        self.classifiers_url = os.path.join(config['api']['url'], 'classifiers')
        self.json_headers =  {'content-type': 'application/json'}




class DatasetTest(BasicSkygridTest):
    def hashfile(self, path):
        hasher = hashlib.sha512()
        blocksize = 65536

        afile = open(path, 'rb')
        buf = afile.read(blocksize)
        while len(buf) > 0:
            hasher.update(buf)
            buf = afile.read(blocksize)
        return hasher.hexdigest()

    def test_upload_and_delete_csv(self):
        payload = dict(
            name=str(uuid.uuid4().hex),
            type="csv"
        )
        files = {'dataset': open('test_data.csv', 'rb')}

        r = requests.put(
            self.datasets_url,
            data=payload,
            files=files
        ).json()

        self.assertTrue(r['success'])
        data = r['data']

        self.assertEqual(data['name'], payload['name'])
        self.assertEqual(data['type'], payload['type'])

        self.assertEqual(
            data['hash'],
            self.hashfile('test_data.csv')
        )

        r = requests.delete(
            os.path.join(self.datasets_url, data['id'])
        ).json()

        self.assertTrue(r['success'])


class ClassifierTest(BasicSkygridTest):
    def upload_ds(self):
        payload = dict(
            name=str(uuid.uuid4().hex),
            type="csv"
        )
        files = {'dataset': open('test_data.csv', 'rb')}

        r = requests.put(
            self.datasets_url,
            data=payload,
            files=files
        ).json()
        return r['data']['id']

    def delete_ds(self, ds_id):
        requests.delete(os.path.join(self.datasets_url, ds_id))

    def test_create(self):
        ds_id = self.upload_ds()
        payload = {
            'name' : str(uuid.uuid4().hex),
            'type' : "mn",
            'parameters' : {'a': 'b'},
            'dataset': ds_id
        }

        r = requests.put(
            self.classifiers_url,
            data=json.dumps(payload),
            headers=self.json_headers
        ).json()

        self.assertTrue(r['success'])
        data = r['data']

        self.assertEqual(data['name'], payload['name'])
        self.assertEqual(data['type'], payload['type'])
        self.assertEqual(data['parameters'], payload['parameters'])


        r = requests.delete(
            os.path.join(self.classifiers_url, data['id'])
        ).json()

        self.assertTrue(r['success'])

        self.delete_ds(ds_id)



if __name__ == '__main__':
    unittest.main()