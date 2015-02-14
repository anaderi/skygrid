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
        self.montecarlo_url = os.path.join(config['api']['url'], 'montecarlo')
        self.json_headers =  {'content-type': 'application/json'}

