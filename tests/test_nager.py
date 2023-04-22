import unittest
from datetime import datetime
from nagerapi import NagerObjectAPI, NagerException

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
        cls.nager2 = NagerObjectAPI()

    def test_country_info(self):
        ca = self.nager2.country("ca", load=False)
        self.assertFalse(ca._full)
        self.assertEqual(ca.region, "Americas")
        self.assertTrue(ca._full)
        self.assertEqual(self.nager.country(load=False).official, "United States of America")
        def attr_check():
            self.nager.name = "Bob"
        self.assertRaises(AttributeError, attr_check)
        def empty_check():
            return self.nager2.country()
        self.assertRaises(NagerException, empty_check)
        def invalid_code():
            return self.nager2.country("ZZ")
        self.assertRaises(NagerException, invalid_code)
        def invalid_code2():
            return self.nager.api.get_country_info("ZZ")
        self.assertRaises(NagerException, invalid_code2)
        def invalid_year():
            return self.nager.public_holidays(1800)
        self.assertRaises(NagerException, invalid_year)

    def test_available_countries(self):
        self.assertIn("US", self.nager.available_countries)
        self.assertIn("gb", self.nager.available_countries)
        us = self.nager.country("us", load=False)
        self.assertEqual(us.region, "Americas")
        self.assertEqual(f"{us}", "United States")
        self.assertEqual(us.__repr__(), "United States")
        def attr_check():
            us.region = "Bob"
        self.assertRaises(AttributeError, attr_check)
        self.assertIn(us, self.nager.available_countries)

    def test_long_weekend(self):
        weekends = self.nager.long_weekends(datetime.now().year)
        self.assertGreater(len(weekends), 0)
        self.assertIn("-->", f"{weekends[0]}")

    def test_public_holidays(self):
        holidays = self.nager.public_holidays(datetime.now().year)
        self.assertGreater(len(holidays), 0)
        self.assertIn(holidays[0].name, f"{holidays[0]}")

    def test_is_today_public_holiday(self):
        now = datetime.now()
        us = self.nager.country()
        expected_answer = False
        for holiday in us.public_holidays(now.year):
            if holiday.date.date() == now.date():
                expected_answer = True
                break
        if expected_answer:
            self.assertTrue(self.nager.is_today_public_holiday("US", offset=-5))
        else:
            self.assertFalse(self.nager.is_today_public_holiday("US", offset=-5))

    def test_next_public_holidays(self):
        self.assertGreater(len(self.nager.next_public_holidays()), 0)

    def test_next_public_world_holiday(self):
        self.assertGreater(len(self.nager.next_public_worldwide_holidays()), 0)

    def test_version(self):
        self.assertEqual(self.nager.name, "Nager.Date")
