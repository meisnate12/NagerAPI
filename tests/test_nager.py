import unittest
from datetime import datetime
from nagerapi import NagerObjectAPI

"""
import logging

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())
"""


class NagerTests(unittest.TestCase):
    nager = None

    @classmethod
    def setUpClass(cls):
        cls.nager = NagerObjectAPI(default_country="US")

    def test_country_info(self):
        self.assertEqual(self.nager.country().official, "United States of America")

    def test_available_countries(self):
        self.assertIn("US", self.nager.available_countries)
        self.assertIn("gb", self.nager.available_countries)

    def test_long_weekend(self):
        self.assertGreater(len(self.nager.long_weekends(datetime.now().year)), 0)

    def test_public_holidays(self):
        self.assertGreater(len(self.nager.public_holidays(datetime.now().year)), 0)

    def test_next_public_holidays(self):
        self.assertGreater(len(self.nager.next_public_holidays()), 0)

    def test_next_public_world_holiday(self):
        self.assertGreater(len(self.nager.next_public_worldwide_holidays()), 0)

    def test_version(self):
        self.assertEqual(self.nager.name, "Nager.Date")
