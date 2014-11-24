import unittest

from testconfig import config


class SkygridTest(unittest.TestCase):
    def setUp(self):
        self.api_url = config['api']['url']
