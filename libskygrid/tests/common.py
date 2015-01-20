import unittest

from testconfig import config

from libskygrid.common import SkygridServerError


class SkygridTest(unittest.TestCase):
    def setUp(self):
        self.api_url = config['api']['url']
