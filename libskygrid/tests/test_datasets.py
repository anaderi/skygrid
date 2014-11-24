import json
import os
import random
import unittest
import uuid
from time import sleep

import requests

from testconfig import config
from libskygrid.common import SkygridServerError
from libskygrid.dataset import Dataset, hashfile


class SkygridTest(unittest.TestCase):
    def setUp(self):
        self.api_url = config['api']['url']

class TestDataset(SkygridTest):
    def test_upload(self):
        ds1 = Dataset(self.api_url, path='test_data.csv')
        
        with self.assertRaises(Exception):
            ds1.delete()

        self.assertTrue(ds1.upload())

        self.assertIsNotNone(ds1.ds_id)
        self.assertEqual(ds1.filetype, 'csv')
        self.assertEqual(ds1.filehash, hashfile('test_data.csv'))
        
        ds2 = Dataset(self.api_url, ds_id=ds1.ds_id)

        self.assertEqual(ds1, ds2)

        ds1.delete()

        with self.assertRaises(SkygridServerError):
            ds2.delete()