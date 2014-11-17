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



def hashfile(path):
    hasher = hashlib.sha512()
    blocksize = 65536

    afile = open(path, 'rb')
    buf = afile.read(blocksize)
    while len(buf) > 0:
        hasher.update(buf)
        buf = afile.read(blocksize)
    return hasher.hexdigest()



class DatasetListTest(BasicSkygridTest):

    def test_upload_csv(self):
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

        print r['hash']
        self.assertEqual(r['name'], payload['name'])
        self.assertEqual(r['type'], payload['type'])

        self.assertEqual(
            r['hash'],
            hashfile('test_data.csv')
        )

        r = requests.delete(
            os.path.join(self.datasets_url, r['id'])
        ).json()

        self.assertEqual(r, {})


if __name__ == '__main__':
    unittest.main()