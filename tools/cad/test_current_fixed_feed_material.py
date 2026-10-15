import unittest
from current_fixed_feed_material import prepare


class FixedFeedMaterialTests(unittest.TestCase):
    def test_all_six_components_and_geometry_provenance_without_live_macro_self_pin(self):
        material,pins=prepare()
        self.assertEqual(len(material),6)
        self.assertIn('FixedFeed/FL_G/body',material)
        self.assertIn('FixedFeed/BUS_G/band',material)
        self.assertFalse(any(n.endswith('body36-shared-macro-layout.json') for n in pins))
        self.assertTrue(any(n.endswith('remaining-fixed-feed-checks.json') for n in pins))
        self.assertTrue(all(s.isValid() for s in material.values()))


if __name__=='__main__':unittest.main()
