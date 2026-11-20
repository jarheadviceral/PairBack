import unittest
from locations import LOCATIONS, compose_location, location_key


class LocationTests(unittest.TestCase):
    def test_ranges(self):
        for building, last, excluded in [("MVP", "415", "416"), ("SOM", "402", "403"), ("F", "327", "328")]:
            self.assertIn(last, LOCATIONS[building])
            self.assertNotIn(excluded, LOCATIONS[building])
        self.assertIn("Roofdeck", LOCATIONS["MVP"])
        self.assertIn("Escaler Hall", LOCATIONS["SEC A"])
        self.assertEqual(len(LOCATIONS["New Rizal Library"]), 5)
        self.assertEqual(len(LOCATIONS["Old Rizal Library"]), 2)

    def test_format_and_matching(self):
        self.assertEqual(compose_location("MVP", "101"), "MVP · 101")
        self.assertEqual(compose_location("Arete"), "Arete")
        self.assertEqual(location_key("MVP 101"), location_key("MVP · Roofdeck"))
        self.assertNotEqual(location_key("G · 101"), location_key("Gonzaga Cafeteria · GONZ 1"))
        self.assertEqual(location_key("Legacy place"), "legacy place")
        with self.assertRaises(ValueError):
            compose_location("Unknown building")
