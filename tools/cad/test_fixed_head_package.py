"""Stock rounding is conservative and cannot silently multiply JR products."""
import unittest
from package_fixed_head_interface import blank

class HeadStock(unittest.TestCase):
    def test_source_preparation_and_trim_are_counted_once(self):
        self.assertEqual(blank(303.7108000527435,8),375)
        self.assertEqual(blank(349.35395080542844,11),425)
        self.assertEqual(blank(581.2683034585414,8),650)
    def test_never_rounds_below_guide_plus_allowances(self):
        for guide in (0,1.1,109,303.71,581.269):
            self.assertGreaterEqual(blank(guide,11),guide+71)
            self.assertLess(blank(guide,11),guide+76)

if __name__=='__main__':unittest.main()
